import datetime
from collections import defaultdict
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic.edit import CreateView

from .filters import RecipeTextFilter
from .forms import CreateRecipeForm
from .models import Food, Ingredient, Recipe, RecipeStep, Tag, UnitOfMeasurement

# Create your views here.
def index(request):
    return render(request, 'index.html')

def recipe_detail(request, title):
    recipe = get_object_or_404(Recipe, title=title)
    ingredients = Ingredient.objects.filter(recipe=recipe).order_by('ingredient_category')

    ingredient_categories = set(ingred.ingredient_category for ingred in ingredients)
    ingredients_have_categories = ingredient_categories != {''}

    ingreds_by_category = defaultdict(list)
    for ingredient in ingredients:
        ingreds_by_category[ingredient.ingredient_category].append(ingredient)\
    
    steps = RecipeStep.objects.filter(recipe=recipe).order_by('order_number')
    for step in steps:
        # increment by one to make the base-zero index look human-friendly
        step.order_number += 1

    context = {
        'recipe': recipe,
        'ingredients_have_categories': ingredients_have_categories,
        'ingredient_categories': ingredient_categories,
        'ingredients': dict(ingreds_by_category),
        'steps': steps,
    }
    return render(request, 'recipe_detail.html', context)

def add_recipe(request):
    
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        extra_ingred_count = int(request.POST.get('extra_ingred_count'))
        total_ingred_count = extra_ingred_count + 1

        extra_step_count = int(request.POST.get('extra_step_count'))
        total_step_count = extra_step_count + 1
        create_recipe_form = CreateRecipeForm(request.POST, extra_ingreds=extra_ingred_count, extra_steps=extra_step_count)

        # Adding a new tag does not require the form to be valid
        if create_recipe_form.data.get('new_tag'):
            
            tag_instance = Tag(name=create_recipe_form.data['new_tag'])
            tag_instance.save()

            # Refresh the page
            return HttpResponseRedirect(reverse('add_recipe'))

        # Check if the form is valid:
        elif create_recipe_form.is_valid():
            # Parse servings field into the two model fields
            (servings_min, servings_max) = create_recipe_form.cleaned_data['servings']
            create_recipe_form.cleaned_data.pop('servings')
            create_recipe_form.cleaned_data['servings_min'] = servings_min
            create_recipe_form.cleaned_data['servings_max'] = servings_max
            
            recipe_instance = Recipe(
                title=create_recipe_form.cleaned_data['title'],
                url=create_recipe_form.cleaned_data.get('url'),
                duration_minutes=create_recipe_form.cleaned_data['duration_minutes'],
                servings_min=servings_min,
                servings_max=servings_max,
                calories_per_serving=create_recipe_form.cleaned_data.get('calories_per_serving'),
                notes=create_recipe_form.cleaned_data.get('notes'),
            )
            recipe_instance.save()

            # Extract tags from form data and create the relationship from tag -> recipe
            tags = create_recipe_form.cleaned_data['tags']
            
            if tags:
                for tag in tags:
                    tag_instance = Tag.objects.get(name=tag)
                    tag_instance.recipes.add(recipe_instance)
                    tag_instance.save()

            # For each ingredient
            for i in range(total_ingred_count):
                # Gather ingredients fields together
                ingred = {field: create_recipe_form.cleaned_data[f'ingred_{i}_{field}'] for field in ['food', 'unit_of_measurement', 'quantity', 'ingredient_category']}

                # Check if food specified in ingredient already exists. If not, create it.
                existing_foods = [food.name for food in Food.objects.all()]
                selected_food = ingred['food']
                if selected_food not in existing_foods:
                    new_food = Food(name=selected_food)
                    new_food.save()
                
                # Same for unit of measurement
                existing_units = [unit.name for unit in UnitOfMeasurement.objects.all()]
                selected_unit = ingred['unit_of_measurement']
                if selected_unit not in existing_units:
                    new_unit = UnitOfMeasurement(name=selected_unit)
                    new_unit.save()
                
                # Save ingredient
                ingredient_instance = Ingredient(
                    food=Food.objects.get(name=selected_food),
                    recipe=recipe_instance,
                    unit_of_measurement=UnitOfMeasurement.objects.get(name=selected_unit),
                    quantity=ingred['quantity'],
                    ingredient_category=ingred.get('ingredient_category', ''),
                )
                ingredient_instance.save()

            # Now, for each step
            for i in range(total_step_count):
                step_description = create_recipe_form.cleaned_data[f'step_{i}_description']
                step_instance = RecipeStep(
                    recipe=recipe_instance,
                    order_number=i,
                    description=step_description,
                )
                step_instance.save()

            # redirect to a new URL:
            return redirect('recipe_detail', title=create_recipe_form.cleaned_data['title'])


    # If this is a GET (or any other method) create the default form.
    else:
        create_recipe_form = CreateRecipeForm(initial={'title': 'My cool new recipe!'})
        existing_foods = [food.name for food in Food.objects.all()]
        existing_units = [unit.name for unit in UnitOfMeasurement.objects.all()]

    context = {
        'mode': 'add',
        'create_recipe_form': create_recipe_form,
        'ingredient_list': [
            {'food': '', 'unit_of_measurement': '', 'quantity': None, 'ingredient_category': ''},
        ],
        'step_list': [
            {'description': ''},
        ],
        'food_list': existing_foods,
        'unit_list': existing_units,
    }

    return render(request, 'add_edit_recipe.html', context)

def search(request):
    text_search = RecipeTextFilter(request.GET, queryset=Recipe.objects.all())
    context = {
        'text_search': text_search
    }
    return render(request, 'search.html', context)



def edit_recipe(request, title):
    recipe_instance = get_object_or_404(Recipe, title=title)

    # If this is a POST request then process the Form data similarly to an add_recipe request, 
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        extra_ingred_count = int(request.POST.get('extra_ingred_count'))
        total_ingred_count = extra_ingred_count + 1

        extra_step_count = int(request.POST.get('extra_step_count'))
        total_step_count = extra_step_count + 1
        create_recipe_form = CreateRecipeForm(request.POST, extra_ingreds=extra_ingred_count, extra_steps=extra_step_count)

        # Adding a new tag does not require the form to be valid
        if create_recipe_form.data.get('new_tag'):
            
            tag_instance = Tag(name=create_recipe_form.data['new_tag'])
            tag_instance.save()

            # Refresh the page
            return HttpResponseRedirect(reverse('add_recipe'))

        # Check if the form is valid:
        elif create_recipe_form.is_valid():
            
            # Parse servings field into the two model fields
            (servings_min, servings_max) = create_recipe_form.cleaned_data['servings']
            create_recipe_form.cleaned_data.pop('servings')
            create_recipe_form.cleaned_data['servings_min'] = servings_min
            create_recipe_form.cleaned_data['servings_max'] = servings_max

            # Update the recipe instance with the new data
            recipe_instance.title=create_recipe_form.cleaned_data['title'],
            recipe_instance.url=create_recipe_form.cleaned_data.get('url'),
            recipe_instance.duration_minutes=create_recipe_form.cleaned_data['duration_minutes'],
            recipe_instance.servings_min=servings_min,
            recipe_instance.servings_max=servings_max,
            recipe_instance.calories_per_serving=create_recipe_form.cleaned_data.get('calories_per_serving'),
            recipe_instance.notes=create_recipe_form.cleaned_data.get('notes'),

            recipe_instance.save()

            # Remove any existing tags from the recipe
            existing_tags = Tag.objects.filter(recipes=recipe_instance)
            for tag in existing_tags:
                tag.recipes.remove(recipe_instance)
                tag.save()
            
            # Extract tags from form data and create new relationships from tag -> recipe
            tags = create_recipe_form.cleaned_data['tags']
            if tags:
                for tag in tags:
                    tag_instance = Tag.objects.get(name=tag)
                    tag_instance.recipes.add(recipe_instance)
                    tag_instance.save()

            # Remove any existing ingredients and steps from the recipe
            existing_ingreds = Ingredient.objects.filter(recipes=recipe_instance)
            for ingred in existing_ingreds:
                ingred.delete()

            existing_steps = RecipeStep.objects.filter(recipes=recipe_instance)
            for step in existing_steps:
                step.delete()

            # For each ingredient in the form
            for i in range(total_ingred_count):
                # Gather ingredients fields together
                ingred = {field: create_recipe_form.cleaned_data[f'ingred_{i}_{field}'] for field in ['food', 'unit_of_measurement', 'quantity', 'ingredient_category']}

                # Check if food specified in ingredient already exists. If not, create it.
                existing_foods = [food.name for food in Food.objects.all()]
                selected_food = ingred['food']
                if selected_food not in existing_foods:
                    new_food = Food(name=selected_food)
                    new_food.save()
                
                # Same for unit of measurement
                existing_units = [unit.name for unit in UnitOfMeasurement.objects.all()]
                selected_unit = ingred['unit_of_measurement']
                if selected_unit not in existing_units:
                    new_unit = UnitOfMeasurement(name=selected_unit)
                    new_unit.save()
                
                # Save ingredient
                ingredient_instance = Ingredient(
                    food=Food.objects.get(name=selected_food),
                    recipe=recipe_instance,
                    unit_of_measurement=UnitOfMeasurement.objects.get(name=selected_unit),
                    quantity=ingred['quantity'],
                    ingredient_category=ingred.get('ingredient_category', ''),
                )
                ingredient_instance.save()

            # Now, for each step in the form
            for i in range(total_step_count):
                step_description = create_recipe_form.cleaned_data[f'step_{i}_description']
                step_instance = RecipeStep(
                    recipe=recipe_instance,
                    order_number=i,
                    description=step_description,
                )
                step_instance.save()

            # redirect to a new URL:
            return redirect('recipe_detail', title=create_recipe_form.cleaned_data['title'])


    # If this is a GET (or any other method), populate the form with the recipe's existing info.
    else:
        related_tags = [tag.name for tag in Tag.objects.filter(recipes=recipe_instance)]
        related_ingredients = Ingredient.objects.filter(recipe=recipe_instance).order_by('ingredient_category')
        related_steps = RecipeStep.objects.filter(recipe=recipe_instance).order_by('order_number')

        existing_foods = [food.name for food in Food.objects.all()]
        existing_units = [unit.name for unit in UnitOfMeasurement.objects.all()]
        
        create_recipe_form = CreateRecipeForm(
            initial=recipe_instance.__dict__,
            extra_ingreds=len(related_ingredients) - 1,
            extra_steps=len(related_steps) - 1,
        )
        create_recipe_form.fields['tags'].initial = [tag.name for tag in Tag.objects.filter(recipes=recipe_instance)]  # doesn't really do anything because the tags that get checked are set in context
        create_recipe_form.fields['servings'].initial = str(recipe_instance.servings_min) + " - " + str(recipe_instance.servings_max)

        # Prepping ingredients and steps as dictionaries to be passed to the template, rather than setting inital fields,
        # because the template cannot dyanmically access dictionary keys (i.e. cannot do this: create_recipe_form['ingred_' + number + '_food'].value)
        ingredient_list = []
        for i, ingredient in enumerate(related_ingredients):
            ingredient_data = {}
            for field in ['food', 'unit_of_measurement', 'quantity', 'ingredient_category']:
                # create_recipe_form.fields[f'ingred_{i}_{field}'].initial = getattr(ingredient, field)  # what you would set if using initial values
                ingredient_data[field] = getattr(ingredient, field)
            ingredient_list.append(ingredient_data)

        step_list = []
        for i, step in enumerate(related_steps):
            step_data = {}
            for field in ['description']:
                # create_recipe_form.fields[f'step_{i}_{field}'].initial = getattr(step, field)
                step_data[field] = getattr(step, field)
            step_list.append(step_data)
        


    context = {
        'mode': 'edit',
        'create_recipe_form': create_recipe_form,
        'checked_tags': related_tags,
        'ingredient_list': ingredient_list,
        'step_list': step_list,
        'food_list': existing_foods,
        'unit_list': existing_units,
    }

    return render(request, 'add_edit_recipe.html', context)