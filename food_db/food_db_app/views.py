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

    context = {
        'create_recipe_form': create_recipe_form,
    }

    return render(request, 'add_edit_recipe.html', context)

def search(request):
    text_search = RecipeTextFilter(request.GET, queryset=Recipe.objects.all())
    context = {
        'text_search': text_search
    }
    return render(request, 'search.html', context)
