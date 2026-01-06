import os
import re
from collections import defaultdict, OrderedDict
from datetime import datetime
from decimal import Decimal
from django.forms.models import model_to_dict
from math import floor

from food_db_app.models import *
from food_db_app.cloud_sync.s3 import S3_SYNC_ENABLED, S3Sync
from .tutorial_steps import get_step_by_id

LAST_DEBUG_LOG_START_TIME = None
LAST_DEBUG_LOG_TIME = None

class RecipeIngredientData:
    """Assembles lists and dicts needed to display ingredients in the recipe detail view."""
    def __init__(self, recipe, multiplier):
        self.recipe = recipe
        self.multiplier = multiplier

        self.has_ingredients = recipe.has_ingredients

        # Get list of ingredient categories
        ingredient_category_instances = IngredientCategory.objects.filter(recipe=recipe).order_by('order_number')
        self.ingredients_have_categories = [cat.name or '' for cat in ingredient_category_instances if cat] != ['']

        # Store ingredients in ingreds_by_category, where keys are the ingredient category
        self.ingreds_by_category = OrderedDict()  # use an ordered dict to preserve the order of ingredient categories
        for cat in ingredient_category_instances:
            ingred_instances = list(Ingredient.objects.filter(recipe=recipe, ingredient_category=cat))
            ingreds = [
                {
                    'quantity': self.stringify_ingredient_quantity(ingred.quantity, ingred.unit_of_measurement.name or '', self.multiplier),  # set a stringified quantity that can be displayed in web template
                    'quantity_raw': ingred.quantity if ingred.quantity else 0,  # leave raw quantity for grocery list calculation
                    'unit_of_measurement': ingred.unit_of_measurement.name if ingred.unit_of_measurement else '',
                    'food': ingred.food.name,
                    'notes': ingred.notes,
                    'food_category': ingred.food.food_category.name if ingred.food.food_category else '',
                    'id': ingred.id,
                }
                for ingred in ingred_instances
            ]
            self.ingreds_by_category[cat.name] = ingreds
        
        # Assemble grocery list (foods by food category)
        self.grocery_list_dict = defaultdict(list)
        for ingred_list in self.ingreds_by_category.values():
            for ingred in ingred_list:
                self.grocery_list_dict[ingred['food_category']].append(ingred)
    
    @staticmethod
    def stringify_ingredient_quantity(quantity, unit, multiplier):
        if quantity:
            # Apply multiplier to ingredient quantities
            quant = str(round(quantity * Decimal(multiplier),2)).rstrip('0').rstrip('.')
            return f"{quant} {unit}{'s' if quantity > 1 and unit != '' else ''}"
        else:
            return ''

class GroceryList:
    """Converts ingredient data from one or many recipes into a grocery list,
    represented as a string."""
    def __init__(self, ingred_data_list: list[RecipeIngredientData], multiplier):
        self.grocery_list_dict = defaultdict(list)  # food_category -> list of ingredients, after quantities are summed
        self.multiplier = multiplier

        self._sum_food_quantities(ingred_data_list)
        self._set_grocery_list_str()

    def _sum_food_quantities(self, ingred_data_list: list[RecipeIngredientData]):
        food_quantity_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))  # food_category -> food -> unit of measurement -> list of quantities. This is the raw quantities to sum.
        for ingred_data in ingred_data_list:
            # first, gather foods by food category, and if there are multiple ingredients with the same food, record each quantity
            for ingred_list in ingred_data.ingreds_by_category.values():
                for ingred in ingred_list:
                    food_quantity_dict[ingred['food_category']][ingred['food']][ingred['unit_of_measurement']].append(ingred['quantity_raw'])

        # for cases where there are multiple ingredients with the same food and unit of measurement, sum the quantities
        for food_category, food_dict in dict(food_quantity_dict).items():
            for food, units in dict(food_dict).items():
                for unit_of_measurement, quantities in dict(units).items():
                    summed_quantity = sum(quantities)
                    self.grocery_list_dict[food_category].append({
                        'food': food,
                        'quantity': RecipeIngredientData.stringify_ingredient_quantity(summed_quantity, unit_of_measurement, self.multiplier),
                    })

    def _set_grocery_list_str(self):
        # convert grocery list dictionary into string
        self.grocery_list_str = ''
        for i, (food_category, ingred_list_unsorted) in enumerate(self.grocery_list_dict.items()):
            ingred_list = sorted(ingred_list_unsorted, key=lambda x: x['food'].lower())  # sort by food name
            if food_category == '':
                food_category = 'Unknown'
            self.grocery_list_str += f'{food_category}:\n'
            self.grocery_list_str += '\n'.join([f'- {ingred["quantity"] + " " if ingred["quantity"] != "" else ""}{ingred["food"]}' for ingred in ingred_list])
            # add double line breaks on all but final food category
            if i < len(self.grocery_list_dict) - 1:
                self.grocery_list_str += '\n\n'

class DerivedTagRule:
    def __init__(
        self,
        tag_name,
        ingredient_regex_patterns=[],
        step_regex_patterns=[],
        recipe_attributes={},
    ):
        self.skip = False
        self.tag_name = tag_name
        self.ingredient_regex_patterns = ingredient_regex_patterns
        self.step_regex_patterns = step_regex_patterns
        self.recipe_attributes = recipe_attributes
        assert ingredient_regex_patterns or step_regex_patterns or recipe_attributes, "You must define at least one of: ingredient_regex_patterns, step_regex_patterns, recipe_attributes"

        # This code would strictly enforce tag rules
        # try:
        #     tag = Tag.objects.get(name=tag_name)
        # except Tag.DoesNotExist as err:
        #     err.args = (f"You tried to create a DerivedTagRule for a tag named '{tag_name}' in {__file__}, but it does not yet exist. Create and save it in the database first.",)
        #     raise err

        # Instead this just skips the rule if the tag does not exist
        try:
            tag = Tag.objects.get(name=tag_name)
        except Tag.DoesNotExist as err:
            self.skip = True


    def _check_ingredients(self, recipe):
        for ingred in Ingredient.objects.filter(recipe=recipe):
            for pattern in self.ingredient_regex_patterns:
                if re.search(pattern, ingred.food.name, re.IGNORECASE):
                    print("pattern ", pattern)
                    print("food ", ingred.food.name)
                    
                    return True
        return False

    def _check_steps(self, recipe):
        for step in RecipeStep.objects.filter(recipe=recipe):
            for pattern in self.ingredient_regex_patterns:
                if re.search(pattern, step.description, re.IGNORECASE):
                    return True
        return False

    def _check_attributes(self, recipe):
        recipe_dict = model_to_dict(recipe)
        for attr, value in self.recipe_attributes.items():
            assert attr in recipe_dict.keys(), f'Invalid attribute specified in DerivedTagRule: {attr}'
            if recipe_dict[attr] != value:
                return False
        return True
    
    def check(self, recipe):
        if not self.skip:
            print(f"Checking recipe to see if it should be tagged with {self.tag_name}")
            ingred_match = self._check_ingredients(recipe)
            step_match = self._check_steps(recipe)
            attr_match = self._check_attributes(recipe)

            match_dict = {key: True for key in ('ingred', 'step', 'attr')}

            if self.ingredient_regex_patterns:
                match_dict['ingred'] = ingred_match
            if self.step_regex_patterns:
                match_dict['step'] = step_match
            if self.recipe_attributes:
                match_dict['attr'] = attr_match

            return all(match_dict.values())  # returns True only if all values are True
        else:
            print(f"Skipping DerivedTagRule for tag {self.tag_name} because it does not exist")
            return False

def convert_minutes_to_string(minutes: int):
    '''Convert minutes into string with hours and minutes'''
    hours = floor(float(minutes)/60.0)
    minutes = minutes % 60
    duration_str = ''
    if hours == 1:
        duration_str += f'{hours} hour '
    elif hours > 1:
        duration_str += f'{hours} hours '
    if minutes > 0:
        duration_str += f'{minutes} minutes'
    return duration_str

def sanitize_string(raw_string: str):
    trimmed = raw_string.lower().strip()
    remove_common_chars = re.sub(r'''[:,'!"&\(\)]''', '', trimmed)
    clean_string = re.sub(r'[^a-z0-9]', '-', remove_common_chars)

    return clean_string

def capitalize_title(raw_title: str):
    raw_parts = raw_title.split(' ')
    capital_parts = []
    for i, word in enumerate(raw_parts):
        if i == 0 or word not in ['and', 'or', 'the', 'a', 'an', 'but', 'nor', 'for', 'yet', 'so', 'in', 'on', 'at', 'to', 'of', 'with', 'by', 'as', 'from', 'aka']:
            capital_parts.append(word.capitalize())
        else:
            capital_parts.append(word)
    return ' '.join(capital_parts)

def remove_dupes_preserve_order(sequence):
    '''As the name implies, this removes duplicates from a list
    while preserving the order in which they first appeared.'''
    seen = set()
    return [x for x in sequence if x not in seen and not seen.add(x)]

def log_debug_message(message, restart_timer=False):
    now = datetime.now()
    global LAST_DEBUG_LOG_START_TIME
    global LAST_DEBUG_LOG_TIME
    if not LAST_DEBUG_LOG_START_TIME or restart_timer:
        LAST_DEBUG_LOG_START_TIME = now
        LAST_DEBUG_LOG_TIME = now
        diff_from_start = 0
        diff_from_last = 0
        print(f'START - {message}')
    else:
        diff_from_start = (now - LAST_DEBUG_LOG_START_TIME).total_seconds()
        diff_from_last = round((now - LAST_DEBUG_LOG_TIME).total_seconds() * 1000)
        print(f'{diff_from_last} ms from last - {diff_from_start} sec from start - {message}')
    
    LAST_DEBUG_LOG_TIME = now

def get_only_relevant_tags(recipe, tag_name_list):
    """If the recipe is a baking recipe, any tags that are only for cooking (this does not include tags that apply to both
    cooking and baking) should be unchecked, and vice versa. Tags for the opposite mode can remain checked if you check
    them in the form, but then switch between cooking and baking, thus hiding them from view but leaving them checked.
    
    This function takes in a list of names (strings) of the tags that were checked in the form, and returns a list of Tag
    instances that are relevant to the recipe type (cooking or baking)."""

    is_baking_recipe = recipe.is_baking_recipe
    return_tags = []

    for tag_name in tag_name_list:
        tag = Tag.objects.get(name=tag_name)

        if is_baking_recipe and tag.is_baking_tag:
            return_tags.append(tag)
        elif not is_baking_recipe and tag.is_cooking_tag:
            return_tags.append(tag)
    
    return return_tags

def get_derived_tags(recipe_instance):
    """Return tags that are automatically associated with a recipe based on its ingredients, steps, or other attributes"""
    tag_rules = [
        DerivedTagRule(
            "Grain",
            ingredient_regex_patterns=[
                r"rice$",  # dollar sign means end of phrase, so it doesn't trigger on "rice vinegar", for example
                r"farro",
                r"barley$",
                r"quinoa",
                r"bulgur",
            ]
        ),
        DerivedTagRule(
            "Cookies",
            recipe_attributes={'is_cookie_recipe': True}
        )
    ]
    return [Tag.objects.get(name=rule.tag_name) for rule in tag_rules if rule.check(recipe_instance)]

def get_is_baking_cookie(request):
    """Get the value of the is_baking_mode cookie, which is used to determine whether the user is in baking mode or cooking mode.
    This persists the status of the baking/cooking switch as the user navigates across pages. This variable is only used on page
    load."""
    return str(request.session.get('is_baking_mode', False))

def get_cart(request):
    """Get the cart from the session, or or initialize it as an empty list."""
    cart = request.session.get('cart', [])
    print(f"Current cart: {cart}")
    
    # If cart is None or contains None, reset it
    if cart is None or (isinstance(cart, list) and None in cart):
        cart = []
        print("Reset cart due to None values")
    
    return cart

def get_view_config_key(request):
    """Get the value of the view_config_key from the session, which is used to determine which Bulk Prep View config is selected.
    This persists the selected view config as the user navigates across pages. This variable is only used on page load."""
    return request.session.get('view_config_key', None)

def get_tutorial_state(request):
    """Get the tutorial state from the session.
    This persists the tutorial state as the user navigates across pages.
    
    Returns:
        dict: Dictionary with keys:
            - 'tutorial_active' (bool): Whether the tutorial is currently active
            - 'current_step_id' (str or None): The step_id of the current tutorial step, or None if no step is active
    """
    return {
        'tutorial_active': request.session.get('tutorial_active', False),
        'current_step_id': request.session.get('tutorial_current_step_id', None)
    }

def set_tutorial_state(request, step_id=None, active=False):
    """Set the tutorial state in the session.
    
    Args:
        request: The Django request object
        step_id (str, optional): The step_id to set as the current step. If None, clears the current step.
        active (bool): Whether the tutorial should be active. Defaults to False.
    """
    request.session['tutorial_active'] = active
    if step_id is not None:
        request.session['tutorial_current_step_id'] = step_id
    elif not active:
        # If setting active to False, also clear the step_id
        request.session['tutorial_current_step_id'] = None

def clear_tutorial_state(request):
    """Clear the tutorial state from the session."""
    request.session['tutorial_active'] = False
    request.session['tutorial_current_step_id'] = None

def get_current_step_data(request):
    """Get the current tutorial step data with resolved URL.
    
    Returns:
        dict: Dictionary containing step data with resolved URL, or None if no active step.
            Includes: step_id, title, page_url, scroll_target, tooltip_content, order, url
    """
    tutorial_state = get_tutorial_state(request)
    if not tutorial_state['tutorial_active'] or not tutorial_state['current_step_id']:
        return None
    
    step = get_step_by_id(tutorial_state['current_step_id'])
    if step is None:
        return None
    
    # Convert TutorialStep object to dictionary using the class method
    return step.to_dict_with_url()

def context(request, **kwargs):
    tutorial_state = get_tutorial_state(request)
    context_values = {
        'current_is_baking_mode': get_is_baking_cookie(request),
        'cart': get_cart(request),
        'timing_types': TIMING_TYPE_CHOICES,
        'cookie_style_choices': COOKIE_STYLE_CHOICES,
        'tutorial_state': tutorial_state,
        'tutorial_current_step': get_current_step_data(request) if tutorial_state['tutorial_active'] else None,
        'cloud_sync_enabled': S3_SYNC_ENABLED,
        'cloud_url': S3Sync().bucket_url if S3_SYNC_ENABLED else None,
        'potty_mouth': os.getenv('POTTY_MOUTH', 'false').lower() == 'true',
    }
    context_values.update(kwargs)
    return context_values