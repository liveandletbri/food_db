def convert_recipe_to_html(recipe_instance, bucket_url):
    from food_db_app.models import Ingredient, RecipeStep
    
    related_ingredients = Ingredient.objects.filter(recipe=recipe_instance).order_by('ingredient_category')
    related_steps = RecipeStep.objects.filter(recipe=recipe_instance).order_by('order_number')
    
    # Create a new HTML file for the recipe
    recipe_html = f'<html><a href="http://{bucket_url}">Back to Home</a>'
    recipe_html += f'<head><title>{recipe_instance.title}</title></head><body>'
    recipe_html += f'<h1>{recipe_instance.title}</h1>'
    if recipe_instance.notes != '':
        recipe_html += f'<h2>Notes</h2>{recipe_instance.notes}'
    recipe_html += f'<h2>Ingredients</h2>'
    recipe_html += '<ul>'
    for ingredient in related_ingredients:
        quantity = ingredient.quantity
        unit = ingredient.unit_of_measurement.name
        food = ingredient.food.name
        if quantity is None:
            number_units = ''
        elif float(quantity) == 1 and unit != '':
            number_units = f'{quantity} {unit} '
        elif float(quantity) == 1 and unit != '':
            number_units = f'{quantity} {unit}s '
        elif unit == '':
            number_units = f'{quantity} '
        else:
            number_units = f'{quantity} {unit}s '
        recipe_html += f'<li>{number_units}{food}</li>'
    recipe_html += '</ul>'
    recipe_html += f'<h2>Steps</h2>'
    recipe_html += '<ol>'
    for step in related_steps:
        recipe_html += f'<li>{step.description}</li>'
    recipe_html += '</ol>'
    recipe_html += '</body></html>'
    return recipe_html