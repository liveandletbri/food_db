from django import template
from django.template.defaultfilters import stringfilter
import re

import markdown as md

register = template.Library()

@register.filter()
@stringfilter
def markdown(value):
    # Process custom ingredient links before passing to markdown
    processed_value = _process_ingredient_links(value)
    return md.markdown(processed_value, extensions=['markdown.extensions.fenced_code'])

def _process_ingredient_links(text):
    """
    Process custom ingredient links in the format [text](!ingredient_id)
    and replace them with HTML spans that include tooltip data.
    """
    # Pattern to match [text](!ingredient_id)
    pattern = r'\[([^\]]+)\]\(!(\d+)\)'
    
    def replace_ingredient_link(match):
        link_text = match.group(1)
        ingredient_id = match.group(2)
        
        try:
            # Import here to avoid circular imports
            from .models import Ingredient
            
            ingredient = Ingredient.objects.select_related('food', 'unit_of_measurement').get(id=ingredient_id)
            
            # Build tooltip content
            tooltip_parts = []
            if ingredient.food:
                tooltip_parts.append(ingredient.food.name)
            
            if ingredient.quantity and ingredient.unit_of_measurement:
                tooltip_parts.append(f"{ingredient.quantity} {ingredient.unit_of_measurement.name}")
            elif ingredient.quantity:
                tooltip_parts.append(str(ingredient.quantity))
            elif ingredient.unit_of_measurement:
                tooltip_parts.append(ingredient.unit_of_measurement.name)
            
            if ingredient.notes:
                tooltip_parts.append(ingredient.notes)
            
            tooltip_content = " - ".join(tooltip_parts)
            
            # Return HTML span with tooltip attributes
            return f'<span class="ingredient-link" data-tooltip="{tooltip_content}">{link_text}</span>'
            
        except Ingredient.DoesNotExist:
            # If ingredient doesn't exist, return the original text
            return match.group(0)
        except Exception:
            # If any other error occurs, return the original text
            return match.group(0)
    
    return re.sub(pattern, replace_ingredient_link, text)