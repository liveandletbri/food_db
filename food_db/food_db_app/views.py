import json
import re
import requests

from collections import defaultdict
from decimal import Decimal
from django.forms import formset_factory
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView

from .filters import RecipeTextFilter
from .forms import CreateRecipeForm
from .models import CookedMeal, Food, Ingredient, Recipe, RecipeBook, RecipeStep, Tag, UnitOfMeasurement

def sanitize_string(raw_string: str):
    trimmed = raw_string.lower().strip()
    remove_common_chars = re.sub(r'''[:,'!"&\(\)]''', '', trimmed)
    clean_string = re.sub(r'[^a-z0-9]', '-', remove_common_chars)

    return clean_string

# Create your views here.
def index(request):
    return render(request, 'index.html')

def recipe_detail(request, key):
    # assert isinstance(multiplier, float) and multiplier > 0, "Multiplier must be a positive number"
    
    recipe = get_object_or_404(Recipe, clean_key=key)
    multiplier = float(request.GET.get('multiplier', 1))
    if recipe.servings_min:
        recipe.servings_min = str(Decimal(recipe.servings_min * multiplier))  # using Decimal will show decimal point when needed but hides the .0 when the value is an integer
        
    if recipe.servings_max:
        recipe.servings_max = str(Decimal(recipe.servings_max * multiplier))

    ingredients = Ingredient.objects.filter(recipe=recipe).order_by('ingredient_category')

    ingredient_categories = set(ingred.ingredient_category for ingred in ingredients)
    ingredients_have_categories = ingredient_categories != {''}

    ingreds_by_category = defaultdict(list)
    for ingredient in ingredients:
        if ingredient.quantity:
            ingredient.quantity = str(round(ingredient.quantity * Decimal(multiplier),2)).rstrip('0').rstrip('.')
        ingreds_by_category[ingredient.ingredient_category].append(ingredient)
    
    steps = RecipeStep.objects.filter(recipe=recipe).order_by('order_number')
    for step in steps:
        # increment by one to make the base-zero index look human-friendly
        step.order_number += 1

    total_cooked_meal_counts = CookedMeal.objects.filter(recipe=recipe).count()

    last_cooked_meal = CookedMeal.objects.filter(recipe=recipe).order_by('date_cooked').last()
    if last_cooked_meal:
        last_cooked_date = last_cooked_meal.date_cooked.strftime('%b %d, %Y')
    else:
        last_cooked_date = ''

    context = {
        'recipe': recipe,
        'ingredients_have_categories': ingredients_have_categories,
        'ingredient_categories': ingredient_categories,
        'ingredients': dict(ingreds_by_category),
        'steps': steps,
        'multiplier': multiplier,
        'total_cooked_meal_counts': total_cooked_meal_counts,
        'last_cooked_date': last_cooked_date,
    }
    return render(request, 'recipe_detail.html', context)

def add_recipe(request):
    existing_foods = [food.name for food in Food.objects.all()]
    existing_units = [unit.name for unit in UnitOfMeasurement.objects.all()]
    existing_books = [book.name for book in RecipeBook.objects.all()]

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
                clean_key=sanitize_string(create_recipe_form.cleaned_data['title']),
                title=create_recipe_form.cleaned_data['title'],
                url=create_recipe_form.cleaned_data.get('url'),
                recipe_book_page=create_recipe_form.cleaned_data.get('recipe_book_page', ''),
                duration_minutes=create_recipe_form.cleaned_data['duration_minutes'],
                servings_min=servings_min,
                servings_max=servings_max,
                calories_per_serving=create_recipe_form.cleaned_data.get('calories_per_serving'),
                notes=create_recipe_form.cleaned_data.get('notes'),
            )

            if create_recipe_form.cleaned_data['recipe_book'] != '':
                try:
                    book_instance = RecipeBook.objects.get(name=create_recipe_form.cleaned_data['recipe_book'])
                except RecipeBook.DoesNotExist:
                    book_instance = RecipeBook(name=create_recipe_form.cleaned_data['recipe_book'])
                    book_instance.save()
                recipe_instance.recipe_book = book_instance
                
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
                if create_recipe_form.cleaned_data['ingred_0_food'] != '':  # ingredients were entered for this recipe
                    # Gather ingredients fields together
                    ingred = {field: create_recipe_form.cleaned_data[f'ingred_{i}_{field}'] for field in ['food', 'unit_of_measurement', 'quantity', 'ingredient_category', 'notes']}

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
                        notes=ingred.get('notes', ''),
                    )
                    ingredient_instance.save()

            # Now, for each step
            for i in range(total_step_count):
                if create_recipe_form.cleaned_data['step_0_description'] != '':  # steps were entered for this recipe
                    step_description = create_recipe_form.cleaned_data[f'step_{i}_description']
                    step_instance = RecipeStep(
                        recipe=recipe_instance,
                        order_number=i,
                        description=step_description,
                    )
                    step_instance.save()

            # redirect to a new URL:
            return redirect('recipe_detail', title=create_recipe_form.cleaned_data['title'])
        else:
            # import pdb; pdb.set_trace()
            print(create_recipe_form.errors)

    # If this is a GET (or any other method) create the default form.
    else:
        create_recipe_form = CreateRecipeForm(initial={'title': 'My cool new recipe!'})

    context = {
        'mode': 'add',
        'create_recipe_form': create_recipe_form,
        'ingredient_list': [
            {'food': '', 'unit_of_measurement': '', 'quantity': None, 'ingredient_category': '', 'notes': ''},
        ],
        'step_list': [
            {'description': ''},
        ],
        'food_list': existing_foods,
        'unit_list': existing_units,
        'book_list': existing_books,
    }

    return render(request, 'add_edit_recipe.html', context)

def search(request):
    text_search_form = RecipeTextFilter(request.GET, queryset=Recipe.objects.all().order_by('-_date_created'))
    found_recipes = text_search_form.qs
    recipe_data = {recipe.title : {} for recipe in found_recipes}
    for recipe in found_recipes:
        recipe_data[recipe.title]['tags'] = [tag.name for tag in Tag.objects.filter(recipes=recipe)]
        recipe_data[recipe.title]['date_created'] = recipe._date_created.strftime('%b %d, %Y')
        cooked_count = CookedMeal.objects.filter(recipe=recipe).count()
        last_cooked_meal = CookedMeal.objects.filter(recipe=recipe).order_by('date_cooked').last()
        if cooked_count > 0:
            recipe_data[recipe.title]['times_cooked'] = str(cooked_count)
            recipe_data[recipe.title]['last_cooked'] = last_cooked_meal.date_cooked.strftime('%b %d, %Y')
        else:
            recipe_data[recipe.title]['times_cooked'] = ''
            recipe_data[recipe.title]['last_cooked'] = ''
    
    # Separate out the list of tags from the form so we have more control over them in the HTML
    tags = text_search_form.filters['tag'].extra['choices']
    context = {
        'text_search': text_search_form,
        'recipe_data': recipe_data,
        'tags': tags,
    }
    return render(request, 'search.html', context)



def edit_recipe(request, key):
    recipe_instance = get_object_or_404(Recipe, clean_key=key)

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
            recipe_instance.clean_key=sanitize_string(create_recipe_form.cleaned_data['title'])
            recipe_instance.title=create_recipe_form.cleaned_data['title']
            recipe_instance.url=create_recipe_form.cleaned_data.get('url')
            recipe_instance.recipe_book_page=create_recipe_form.cleaned_data.get('recipe_book_page')
            recipe_instance.duration_minutes=create_recipe_form.cleaned_data['duration_minutes']
            recipe_instance.calories_per_serving=create_recipe_form.cleaned_data.get('calories_per_serving')
            recipe_instance.notes=create_recipe_form.cleaned_data.get('notes')

            if servings_min:
                recipe_instance.servings_min=servings_min
                recipe_instance.servings_max=servings_max

            if create_recipe_form.cleaned_data['recipe_book'] != '':
                try:
                    book_instance = RecipeBook.objects.get(name=create_recipe_form.cleaned_data['recipe_book'])
                except RecipeBook.DoesNotExist:
                    book_instance = RecipeBook(name=create_recipe_form.cleaned_data['recipe_book'])
                    book_instance.save()
                recipe_instance.recipe_book = book_instance
            else:
                recipe_instance.recipe_book = None

            recipe_instance.save()

            # Remove any existing tags from the recipe
            existing_tags = Tag.objects.filter(recipes=recipe_instance)
            for tag in existing_tags:
                tag.recipes.remove(recipe_instance)
                tag.save()
            
            # Extract tags from form data and create new relationships from tag -> recipe
            tags = request.POST.getlist('tag')
            if tags:
                for tag in tags:
                    tag_instance = Tag.objects.get(name=tag)
                    tag_instance.recipes.add(recipe_instance)
                    tag_instance.save()

            # Remove any existing ingredients and steps from the recipe
            existing_ingreds = Ingredient.objects.filter(recipe=recipe_instance)
            for ingred in existing_ingreds:
                ingred.delete()

            existing_steps = RecipeStep.objects.filter(recipe=recipe_instance)
            for step in existing_steps:
                step.delete()

            # For each ingredient in the form
            for i in range(total_ingred_count):
                # Gather ingredients fields together
                ingred = {field: create_recipe_form.cleaned_data[f'ingred_{i}_{field}'] for field in ['food', 'unit_of_measurement', 'quantity', 'ingredient_category', 'notes']}

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
                    notes=ingred.get('notes', ''),
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

        else:
            # import pdb; pdb.set_trace()
            print(create_recipe_form.errors)

    # If this is a GET (or any other method), populate the form with the recipe's existing info.
    else:
        related_tags = [tag.name for tag in Tag.objects.filter(recipes=recipe_instance)]
        related_ingredients = Ingredient.objects.filter(recipe=recipe_instance).order_by('ingredient_category')
        related_steps = RecipeStep.objects.filter(recipe=recipe_instance).order_by('order_number')

        existing_foods = [food.name for food in Food.objects.all()]
        existing_units = [unit.name for unit in UnitOfMeasurement.objects.all()]
        existing_books = [book.name for book in RecipeBook.objects.all()]
        
        create_recipe_form = CreateRecipeForm(
            initial=recipe_instance.__dict__,
            extra_ingreds=len(related_ingredients) - 1,
            extra_steps=len(related_steps) - 1,
        )
        create_recipe_form.fields['tags'].initial = [tag.name for tag in Tag.objects.filter(recipes=recipe_instance)]  # doesn't really do anything because the tags that get checked are set in context via related_tags
        create_recipe_form.fields['servings'].initial = str(recipe_instance.servings_min)
        if recipe_instance.servings_max:
            create_recipe_form.fields['servings'].initial+= " - " + str(recipe_instance.servings_max)

        # Prepping ingredients and steps as dictionaries to be passed to the template, rather than setting inital fields,
        # because the template cannot dyanmically access dictionary keys (i.e. cannot do this: create_recipe_form['ingred_' + number + '_food'].value)
        ingredient_list = []
        for i, ingredient in enumerate(related_ingredients):
            ingredient_data = {}
            for field in ['food', 'unit_of_measurement', 'quantity', 'ingredient_category', 'notes']:
                # create_recipe_form.fields[f'ingred_{i}_{field}'].initial = getattr(ingredient, field)  # what you would set if using initial values
                ingredient_data[field] = getattr(ingredient, field)
            ingredient_list.append(ingredient_data)

        step_list = []
        for step in related_steps:
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
        'book_list': existing_books,
    }

    return render(request, 'add_edit_recipe.html', context)

@csrf_exempt
def ingredient_parse_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        response = requests.post('http://ingredient_parse:5000/parse', data['text'])

        return HttpResponse(response)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])

@csrf_exempt
def cook_meal(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recipe_instance = Recipe.objects.get(title=data['title'])
        cooked_meal_instance = CookedMeal(recipe=recipe_instance)
        cooked_meal_instance.save()

        total_cooked_meal_counts = CookedMeal.objects.filter(recipe=recipe_instance).count()

        return HttpResponse(str(total_cooked_meal_counts))
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])