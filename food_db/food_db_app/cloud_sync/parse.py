def convert_recipe_to_html(recipe_instance, bucket_url):
    # Import happens here, not at top of page, so it's after Django is set up
    from food_db_app.models import Ingredient, RecipeStep
    
    related_ingredients = Ingredient.objects.filter(recipe=recipe_instance).order_by('ingredient_category')
    related_steps = RecipeStep.objects.filter(recipe=recipe_instance).order_by('order_number')
    
    # Create a new HTML file for the recipe
    recipe_html = f'''
    <html><a href="http://{bucket_url}">Back to Home</a>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>{recipe_instance.title}</title>
    </head>
    <body style="font-size:16pt;">
    <h1>{recipe_instance.title}</h1>'''

    if recipe_instance.notes != '':
        recipe_html += f'<h2>Notes</h2>{recipe_instance.notes}'
    
    recipe_html += f'''<h2>Ingredients</h2>
    <table style="font-size:inherit;text-align:left;word-wrap:break-word;border-collapse:collapse;width:800;table-layout:fixed;">
    <thead>
        <tr><th>Ingredient</th><th>Notes</th></tr>
    </thead>'''

    for ingredient in related_ingredients:
        recipe_html += '<tr style="border-style:solid;border-width:thin;">'
        quantity = ingredient.quantity
        if quantity:
            quantity_str = str(quantity).rstrip('0').rstrip('.')
        else:
            quantity_str = ''
        unit = ingredient.unit_of_measurement.name
        food = ingredient.food.name
        if quantity is None:
            number_units = ''
        elif float(quantity) == 1 and unit != '':
            number_units = f'{quantity_str} {unit} '
        elif float(quantity) == 1 and unit != '':
            number_units = f'{quantity_str} {unit}s '
        elif unit == '':
            number_units = f'{quantity_str} '
        else:
            number_units = f'{quantity_str} {unit}s '
        recipe_html += f'<td>{number_units}{food}</td>'
        recipe_html += f'<td>{ingredient.notes}</td></tr>'
    recipe_html += '''</table>
    <h2>Steps</h2>
    <ol style="width:750;">'''
    
    for step in related_steps:
        recipe_html += f'<li style="padding:7;">{step.description}</li>'

    recipe_html += '</ol></body></html>'
    return recipe_html