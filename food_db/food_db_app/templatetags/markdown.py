from django import template
from django.template.defaultfilters import stringfilter
import re

import markdown as md

register = template.Library()

@register.filter()
@stringfilter
def markdown(value, recipe_title):
    # Process custom ingredient links before passing to markdown
    processed_value = process_ingredient_links(value, recipe_title)
    return md.markdown(processed_value, extensions=['markdown.extensions.fenced_code'])

def process_ingredient_links(text, recipe_title):
    """
    Process custom ingredient links in the format [text](!ingredient name;ingredient category)
    and replace them with HTML spans that include tooltip data.
    """
    # Pattern to match [ingredient name] or [text](!ingredient name) or [text](!ingredient name;ingredient category)
    pattern = r"\[([^\]]+)\](\(!([\w '\-%]+)(;[\w ]+)?\))?"
    
    def replace_ingredient_link(match):
        link_text = match.group(1)
        # The following may be None
        parentheses_clause = match.group(2)
        ingredient_name = match.group(3)
        ingredient_category = match.group(4)
        
        try:
            # Import here to avoid circular imports
            from food_db_app.models import Ingredient
            from food_db_app.views import RecipeIngredientData

            # First case is the ingredient name written just in brackets, like [ingredient name]
            if not parentheses_clause:
                ingredient = Ingredient.objects.get(recipe__title=recipe_title, food__name=link_text)
            else:
                # In this case, both brackets and parenetheses were used
                # Checking the second case: [visible text](!ingredient name)
                # We don't want to require the specification of ingredient_category, even if the ingredient does have a category. So try to find it first without filtering on category.
                try:
                    ingredient = Ingredient.objects.get(recipe__title=recipe_title, food__name__iexact=ingredient_name)
                except Ingredient.MultipleObjectsReturned:
                    # The same food was used for multiple ingredients in this recipe, so an ingredient category is required. The full syntax for specifying this is [visible text](!ingredient name;category name)
                    cat = ingredient_category or ''  # if no category was specified, try searching with a blank string (which is what happens when no category is attached to the ingredient)
                    cat = cat.replace(';','').strip()  # if a category was specified, remove leading whitespace and the semicolon from the regular expression match
                    ingredient = Ingredient.objects.get(recipe__title=recipe_title, food__name__iexact=ingredient_name, ingredient_category__name__iexact=cat)
                
            quantity = RecipeIngredientData.stringify_ingredient_quantity(ingredient.quantity, ingredient.unit_of_measurement.name or '', 1)  # FIXME: gotta work dynamically with the multiplier, right now it's set to 1
            
            tooltip_content = f'{quantity} {ingredient.food.name}'
            
            if ingredient.quantity != 1 and not ingredient.unit_of_measurement and not ingredient.food.name.endswith('s'):
                tooltip_content += 's'
            
            if ingredient.notes:
                tooltip_content += f' - {ingredient.notes}'
            
            # Return HTML span with tooltip attributes
            return f'<span class="ingredient_link" data-ingredient_id="{ingredient.id}" data-tooltip="{tooltip_content}">{link_text}</span>'
            
        except Exception as e:
            if isinstance(e, Ingredient.DoesNotExist):
                error_message = ' <linked ingredient not found>'
            elif isinstance(e, Ingredient.MultipleObjectsReturned):
                error_message = ' <multiple linked ingredients found; try specifying category>'
            else:
                error_message = ' <link error>'
            return match.group(1) + error_message
    
    return re.sub(pattern, replace_ingredient_link, text, flags=re.IGNORECASE)