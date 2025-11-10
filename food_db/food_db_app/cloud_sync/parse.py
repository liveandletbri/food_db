def convert_recipe_to_html(recipe_instance, bucket_url):
    # Import happens here, not at top of page, so it's after Django is set up
    from food_db_app.models import Ingredient, RecipeStep
    from food_db_app.templatetags.markdown import process_ingredient_links
    
    # Create a new HTML file for the recipe
    recipe_html = f'''
    <html><a href="{bucket_url}">Back to Home</a>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>{recipe_instance.title}</title>
    </head>
    <body style="font-size:16pt;">
    <h1>{recipe_instance.title}</h1>'''

    if recipe_instance.notes != '':
        recipe_html += f'<h2>Notes</h2>{recipe_instance.notes}'

    recipe_html += '<h2>Ingredients</h2>'

    recipes = []
    has_children = recipe_instance.has_children
    if has_children:
        recipes.extend(recipe_instance.child_recipes)
    recipes.append(recipe_instance)
        
    
    for rec in recipes:
        if rec.has_ingredients:
            related_ingredients = Ingredient.objects.filter(recipe=rec).order_by('ingredient_category__name')

            if has_children:
                recipe_html += f'<h3>Ingredients for {rec.title}</h3>'
            
            recipe_html += f'''
            <table style="font-size:inherit;text-align:left;word-wrap:break-word;border-collapse:collapse;width:800;table-layout:fixed;">
            <thead>
                <tr><th>Ingredient</th><th>Notes</th><th>Category</th></tr>
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
                recipe_html += f'<td>{ingredient.notes}</td>'
                recipe_html += f'<td>{ingredient.ingredient_category.name}</td></tr>'
            recipe_html += '</table>'
    
    recipe_html += '<h2>Steps</h2>'

    for rec in recipes:
        if rec.has_steps:
            related_steps = RecipeStep.objects.filter(recipe=rec).order_by('order_number')

            if has_children:
                recipe_html += f'<h3>Steps for {rec.title}</h3>'

            recipe_html += '''
            <ol style="width:750;">'''
            
            for step in related_steps:
                step_description = process_ingredient_links(step.description, rec.title)
                recipe_html += f'<li style="padding:7;">{step_description}</li>'

            recipe_html += '</ol>'

    recipe_html += '</body></html>'
    return recipe_html