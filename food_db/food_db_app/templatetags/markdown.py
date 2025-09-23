from django import template
from django.template.defaultfilters import stringfilter
import re

import markdown as md

register = template.Library()

@register.filter()
@stringfilter
def markdown(value, recipe_title):
    # Process custom ingredient links before passing to markdown
    processed_value = _process_ingredient_links(value, recipe_title)
    return md.markdown(processed_value, extensions=['markdown.extensions.fenced_code'])

def _process_ingredient_links(text, recipe_title):
    """
    Process custom ingredient links in the format [text](!ingredient_name;ingredient_category)
    and replace them with HTML spans that include tooltip data.
    """
    # Pattern to match [text](!ingredient_name) or [text](!ingredient_name;ingredient_category)
    pattern = r'\[([^\]]+)\]\(!([\w ]+)(;[\w ]+)?\)'
    
    def replace_ingredient_link(match):
        link_text = match.group(1)
        ingredient_name = match.group(2)
        ingredient_category = match.group(3)  # None if not specified
        
        try:
            # Import here to avoid circular imports
            from food_db_app.models import Ingredient
            from food_db_app.views import RecipeIngredientData
            
            # We don't want to require the specification of ingredient_category, even if the ingredient does have a category. So try to find it first without filtering on category.
            try:
                ingredient = Ingredient.objects.get(recipe__title=recipe_title, food__name=ingredient_name)
            except Ingredient.MultipleObjectsReturned:
                ingredient = Ingredient.objects.get(recipe__title=recipe_title, food__name=ingredient_name, ingredient_category__name=ingredient_category or '')
                
            quantity = RecipeIngredientData.stringify_ingredient_quantity(ingredient.quantity, ingredient.unit_of_measurement.name or '', 1)  # FIXME: gotta work dynamically with the multiplier, right now it's set to 1
            
            tooltip_content = f'{quantity} {ingredient.food.name}'
            
            if ingredient.quantity != 1 and not ingredient.unit_of_measurement and not ingredient.food.name.endswith('s'):
                tooltip_content += 's'
            
            if ingredient.notes:
                tooltip_content += f' - {ingredient.notes}'
            
            # Return HTML span with tooltip attributes
            return f'<span class="ingredient_link" data-tooltip="{tooltip_content}">{link_text}</span>'
            
        except Ingredient.DoesNotExist:
            # If ingredient doesn't exist, return the hyperlink text (without the link formatting around it) plus an error
            return match.group(1) + ' <linked ingredient not found>'
        except Ingredient.MultipleObjectsReturned:
            return match.group(1) + ' <multiple linked ingredients found; try specifying category>'
        except Exception:
            return match.group(1) + ' <link error>'
    
    return re.sub(pattern, replace_ingredient_link, text)