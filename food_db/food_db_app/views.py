import json
import re
import requests

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from math import floor
from pytz import timezone

from .filters import RecipeTextFilter, FoodTextFilter, FoodCategoryTextFilter
from .forms import CreateRecipeForm
from .models import CookedMeal, Food, Ingredient, Recipe, RecipeBook, RecipeStep, Tag, UnitOfMeasurement, RecipeImage, IngredientCategory, FoodCategory
from .cloud_sync.s3 import S3_SYNC_ENABLED, S3Sync

LAST_DEBUG_LOG_START_TIME = None
LAST_DEBUG_LOG_TIME = None

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

# Create your views here.
def index(request):
    return render(request, 'index.html')

def recipe_detail(request, key):
    # assert isinstance(multiplier, float) and multiplier > 0, "Multiplier must be a positive number"
    
    recipe = get_object_or_404(Recipe, clean_key=key)
    multiplier = float(request.GET.get('multiplier', 1))
    
    # Calculate calories per serving before applying the multiplier (values won't change after the multiplier and it's easier before the servings are converted to strings)
    if recipe.servings_min and recipe.calories_per_recipe:
        calories_max = round(recipe.calories_per_recipe / recipe.servings_min)
    else:
        calories_max = None
    
    if recipe.servings_max and recipe.calories_per_recipe:
        calories_min = round(recipe.calories_per_recipe / recipe.servings_max)
    else:
        calories_min = None

    if calories_min and calories_max:
        calorie_string = f'{calories_min} - {calories_max} per serving'
    elif calories_max:
        calorie_string = f'{calories_max} per serving'
    elif recipe.calories_per_recipe:
        calorie_string = f'{recipe.calories_per_recipe} total calories in recipe'
    else:
        calorie_string = ''

    # Apply multipliers to serving counts
    if recipe.servings_min:
        recipe.servings_min = str(Decimal(recipe.servings_min * multiplier))  # using Decimal will show decimal point when needed but hides the .0 when the value is an integer
        
    if recipe.servings_max:
        recipe.servings_max = str(Decimal(recipe.servings_max * multiplier))

    if recipe.duration_minutes:
        recipe.duration_minutes = convert_minutes_to_string(recipe.duration_minutes)

    images = [recipe_image.image for recipe_image in RecipeImage.objects.filter(recipe=recipe)]

    # Get list of ingredient categories
    ingredient_category_instances = IngredientCategory.objects.filter(recipe=recipe).order_by('order_number')
    ingredient_categories = [cat.name or '' for cat in ingredient_category_instances if cat]
    ingredients_have_categories = ingredient_categories != ['']

    def stringify_ingredient_quantity(ingred):
        if ingred.quantity:
            # Apply multiplier to ingredient quantities
            quant = str(round(ingred.quantity * Decimal(multiplier),2)).rstrip('0').rstrip('.')
            return f"{quant} {ingred.unit_of_measurement.name or ''}{'s' if ingred.quantity > 1 and ingred.unit_of_measurement.name != '' else ''}"
        else:
            return ''

    # Store ingredients in ingreds_by_category, where keys are the ingredient category
    ingreds_by_category = {}
    for cat in ingredient_category_instances:
        ingred_instances = list(Ingredient.objects.filter(recipe=recipe, ingredient_category=cat))
        ingreds = [
            {
                'quantity': stringify_ingredient_quantity(ingred),
                'food': ingred.food.name,
                'notes': ingred.notes,
                'food_category': ingred.food.food_category.name if ingred.food.food_category else '',
            }
            for ingred in ingred_instances
        ]
        ingreds_by_category[cat.name] = ingreds
    
    # Assemble grocery list (foods by food category)
    grocery_list_dict = defaultdict(list)
    for ingred_list in ingreds_by_category.values():
        for ingred in ingred_list:
            grocery_list_dict[ingred['food_category']].append(ingred)
    
    # convert grocery list dictionary into string
    grocery_list_str = ''
    for i, (food_category, ingred_list) in enumerate(grocery_list_dict.items()):
        if food_category == '':
            food_category = 'Unknown'
        grocery_list_str += f'{food_category}:\n'
        grocery_list_str += '\n'.join([f'- {ingred["quantity"] + " " if ingred["quantity"] != "" else ""}{ingred["food"]}' for ingred in ingred_list])
        # add double line breaks on all but final food category
        if i < len(grocery_list_dict) - 1:
            grocery_list_str += '\n\n'

    # Order steps and increment the base-zero order_number 
    steps = RecipeStep.objects.filter(recipe=recipe).order_by('order_number')
    for step in steps:
        # increment by one to make the base-zero index look human-friendly
        step.order_number += 1
    
    if steps.count() == 1 and steps[0].description == '':
        # If there is only one step and it is blank, then there aren't actually any steps. Not totally sure why this happens.
        has_steps = False
    elif steps.count() == 0:
        # This is what I'd expect to happen if there are no steps.
        has_steps = False
    else:
        has_steps = True


    total_cooked_meal_counts = CookedMeal.objects.filter(recipe=recipe).count()

    last_cooked_meal = CookedMeal.objects.filter(recipe=recipe).order_by('date_cooked').last()
    if last_cooked_meal:
        last_cooked_date = last_cooked_meal.date_cooked.astimezone(timezone('US/Pacific')).strftime('%b %d, %Y')
    else:
        last_cooked_date = ''

    context = {
        'recipe': recipe,
        'calorie_string': calorie_string,
        'images': images,
        'ingredients_have_categories': ingredients_have_categories,
        'ingredient_categories': ingredient_categories,
        'ingredients': dict(ingreds_by_category),
        'grocery_list': grocery_list_str,
        'steps': steps,
        'multiplier': multiplier,
        'total_cooked_meal_counts': total_cooked_meal_counts,
        'last_cooked_date': last_cooked_date,
        'has_steps': has_steps,
    }
    return render(request, 'recipe_detail.html', context)

def add_recipe(request):
    log_debug_message('add_recipe() called', restart_timer=True)
    existing_foods = [food.name for food in Food.objects.all()]
    existing_units = [unit.name for unit in UnitOfMeasurement.objects.all()]
    existing_books = [book.name for book in RecipeBook.objects.all()]
    existing_tags = [tag for tag in Tag.objects.all().order_by('name')]

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        log_debug_message('is POST')
        # Create a form instance and populate it with data from the request (binding):
        extra_ingred_count = int(request.POST.get('extra_ingred_count'))
        total_ingred_count = extra_ingred_count + 1

        extra_step_count = int(request.POST.get('extra_step_count'))
        total_step_count = extra_step_count + 1
        create_recipe_form = CreateRecipeForm(request.POST, request.FILES, extra_ingreds=extra_ingred_count, extra_steps=extra_step_count)

        log_debug_message('is valid?')

        # Check if the form is valid:
        if create_recipe_form.is_valid():
            log_debug_message('is valid.')
            # Parse servings field into the two model fields
            (servings_min, servings_max) = create_recipe_form.cleaned_data['servings']
            create_recipe_form.cleaned_data.pop('servings')
            create_recipe_form.cleaned_data['servings_min'] = servings_min
            create_recipe_form.cleaned_data['servings_max'] = servings_max
            
            clean_key = sanitize_string(create_recipe_form.cleaned_data['title'])
            capital_title = capitalize_title(create_recipe_form.cleaned_data['title'])
            
            recipe_instance = Recipe(
                clean_key=clean_key,
                title=capital_title,
                url=create_recipe_form.cleaned_data.get('url'),
                recipe_book_page=create_recipe_form.cleaned_data.get('recipe_book_page', ''),
                duration_minutes=create_recipe_form.cleaned_data['duration_minutes'],
                servings_min=servings_min,
                servings_max=servings_max,
                calories_per_recipe=create_recipe_form.cleaned_data.get('calories_per_recipe'),
                notes=create_recipe_form.cleaned_data.get('notes'),
                is_baking_recipe=create_recipe_form.cleaned_data.get('is_baking_recipe', False),
            )

            log_debug_message('made recipe instance')

            recipe_book_title = create_recipe_form.cleaned_data['recipe_book']
            if recipe_book_title != '':
                try:
                    book_instance = RecipeBook.objects.get(name=recipe_book_title)
                except RecipeBook.DoesNotExist:
                    book_instance = RecipeBook(
                        name=recipe_book_title,
                        clean_key=sanitize_string(recipe_book_title)
                    )
                    book_instance.save()
                recipe_instance.recipe_book = book_instance
                
            recipe_instance.save()

            log_debug_message('saved book')

            # Extract tags from form data and create the relationship from tag -> recipe
            tags = get_only_relevant_tags(recipe_instance, request.POST.getlist('tag'))
            
            if tags:
                # Using a for loop instead of bulk_update because it can't update many-to-many relationship fields
                for tag_instance in tags:
                    tag_instance.recipes.add(recipe_instance)
                    tag_instance.save()
            
            log_debug_message('saved tags')

            recipe_images = request.FILES.getlist('images')
            if recipe_images:
                # Using a for loop instead of bulk_create to ensure RecipeImage.save() is triggered
                for recipe_image in recipe_images:
                    recipe_image_instance = RecipeImage(
                        recipe=recipe_instance,
                        image=recipe_image,
                    )
                    recipe_image_instance.save()

            log_debug_message('saved pics')

            # Establish ingredient categories
            ingredient_ids = {re.search(r'ingred_(\d+)', input_name).group() for input_name in create_recipe_form.cleaned_data.keys() if input_name.startswith('ingred_')}  # Creates a distinct set of ingredient ID prefixes, e.g. {ingred_0, ingred_1}
            ingredient_categories = remove_dupes_preserve_order([create_recipe_form.cleaned_data[f'{ingred_id_prefix}_ingredient_category'] or '' for ingred_id_prefix in sorted(ingredient_ids)])

            ingredient_instances = []
            step_instances = []

            if create_recipe_form.cleaned_data['ingred_0_food'] != '':  # ingredients were entered for this recipe
                # For each ingredient in the form
                for ingred_id_prefix in sorted(ingredient_ids):
                    
                    log_debug_message(f'start ingredient {ingred_id_prefix}')

                    # Gather ingredients fields together
                    ingred = {field: create_recipe_form.cleaned_data[f'{ingred_id_prefix}_{field}'] for field in ['food', 'unit_of_measurement', 'quantity', 'ingredient_category', 'notes']}

                    # Check if food specified in ingredient already exists. If not, create it.
                    existing_foods = [food.clean_key for food in Food.objects.all()]
                    selected_food = sanitize_string(ingred['food'])
                    if 'salt' in selected_food and 'pepper' in selected_food:
                        selected_food = 'salt-and-pepper'
                    if selected_food not in existing_foods:
                        new_food = Food(
                            name=ingred['food'],
                            clean_key=selected_food,
                        )
                        new_food.save()
                    
                    # Same for unit of measurement
                    existing_units = [unit.clean_key for unit in UnitOfMeasurement.objects.all()]
                    raw_unit = ingred['unit_of_measurement']
                    if raw_unit.endswith('s'):
                        raw_unit = raw_unit[:-1]
                    selected_unit = sanitize_string(raw_unit)
                    if selected_unit not in existing_units:
                        new_unit = UnitOfMeasurement(
                            name=raw_unit,
                            clean_key=selected_unit,
                        )
                        new_unit.save()

                    # Same for ingredient category
                    existing_categories = [cat.name for cat in IngredientCategory.objects.filter(recipe=recipe_instance)]
                    category_name = ingred['ingredient_category']
                    if category_name not in existing_categories:
                        ingredient_category_instance = IngredientCategory(
                            recipe=recipe_instance,
                            name=category_name,
                            order_number=sorted(ingredient_categories).index(category_name),  # when adding a new recipe, categories are sorted alphabetically
                        )
                        ingredient_category_instance.save()
                    else:
                        ingredient_category_instance = IngredientCategory.objects.get(recipe=recipe_instance, name=category_name)
                    
                    # Save ingredient
                    ingredient_instance = Ingredient(
                        food=Food.objects.get(clean_key=selected_food),
                        recipe=recipe_instance,
                        unit_of_measurement=UnitOfMeasurement.objects.get(clean_key=selected_unit),
                        quantity=ingred['quantity'],
                        ingredient_category=ingredient_category_instance,
                        notes=ingred.get('notes', ''),
                    )
                    ingredient_instances.append(ingredient_instance)
                
                Ingredient.objects.bulk_create(ingredient_instances)

            if create_recipe_form.cleaned_data['step_0_description'] != '':  # steps were entered for this recipe
                # Now, for each step
                step_ids = {re.search(r'step_(\d+)', input_name).group() for input_name in create_recipe_form.cleaned_data.keys() if input_name.startswith('step_')}  # Creates a distinct set of step ID prefixes, e.g. {step_0, step_1}
                for i, step_id_prefix in enumerate(sorted(step_ids)):
                    step_description = create_recipe_form.cleaned_data[f'{step_id_prefix}_description']
                    step_instance = RecipeStep(
                        recipe=recipe_instance,
                        order_number=i,
                        description=step_description,
                    )
                    step_instances.append(step_instance)
                
                RecipeStep.objects.bulk_create(step_instances)
            log_debug_message(f'finished steps')

            # if cloud sync is enabled, sync now
            if S3_SYNC_ENABLED:
                s3 = S3Sync()
                s3.upload_recipe(recipe_instance)
                log_debug_message(f'uploaded to S3')

            # redirect to a new URL:
            return redirect('recipe_detail', key=clean_key)
        else:
           return(HttpResponseBadRequest(create_recipe_form.errors))

    # If this is a GET (or any other method) create the default form.
    else:
        create_recipe_form = CreateRecipeForm()

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
        'tag_list': existing_tags,
    }

    return render(request, 'add_edit_recipe.html', context)

def search(request):
    search_params = request.GET.copy()
    if 'is_baking_recipe' not in search_params:
        # The lack of this key means we should filter to cooking recipes only
        search_params['is_baking_recipe'] = 'False'

    text_search_form = RecipeTextFilter(search_params, queryset=Recipe.objects.all().order_by('-_date_created'))
    found_recipes = text_search_form.qs.distinct()
    recipe_data = {recipe.title : {} for recipe in found_recipes}
    for recipe in found_recipes:
        recipe_data[recipe.title]['tags'] = [tag.name for tag in Tag.objects.filter(recipes=recipe)]
        recipe_data[recipe.title]['date_created'] = recipe._date_created.astimezone(timezone('US/Pacific')).strftime('%b %d, %Y')
        recipe_data[recipe.title]['clean_key'] = recipe.clean_key
        recipe_data[recipe.title]['duration_minutes'] = recipe.duration_minutes or 0
        recipe_data[recipe.title]['duration_string'] = convert_minutes_to_string(recipe.duration_minutes) if recipe.duration_minutes else ''
        cooked_count = CookedMeal.objects.filter(recipe=recipe).count()
        last_cooked_meal = CookedMeal.objects.filter(recipe=recipe).order_by('date_cooked').last()
        if cooked_count > 0:
            recipe_data[recipe.title]['times_cooked'] = str(cooked_count)
            recipe_data[recipe.title]['last_cooked'] = last_cooked_meal.date_cooked.astimezone(timezone('US/Pacific')).strftime('%b %d, %Y')
        else:
            recipe_data[recipe.title]['times_cooked'] = ''
            recipe_data[recipe.title]['last_cooked'] = ''
    
    # Separate out the list of tags from the form so we have more control over them in the HTML
    tags = [
        {
            'name': tag.name,
            'checked': tag.name in request.GET.getlist('tag'),
            'is_cooking_tag': tag.is_cooking_tag,
            'is_baking_tag': tag.is_baking_tag,
        }
        for tag 
        in text_search_form.filters['tag'].extra['queryset']
    ]

    context = {
        'text_search': text_search_form,
        'recipe_data': recipe_data,
        'tags': tags,
    }
    return render(request, 'search.html', context)


def edit_recipe(request, key):
    log_debug_message('edit_recipe() called', restart_timer=True)
    recipe_instance = get_object_or_404(Recipe, clean_key=key)

    # If this is a POST request then process the Form data similarly to an add_recipe request, 
    if request.method == 'POST':
        log_debug_message('is POST')
        # Create a form instance and populate it with data from the request (binding):
        extra_ingred_count = int(request.POST.get('extra_ingred_count'))
        total_ingred_count = extra_ingred_count + 1

        extra_step_count = int(request.POST.get('extra_step_count'))
        total_step_count = extra_step_count + 1
        create_recipe_form = CreateRecipeForm(request.POST, request.FILES, extra_ingreds=extra_ingred_count, extra_steps=extra_step_count)

        log_debug_message('is valid?')

        # Adding a new tag does not require the form to be valid
        if create_recipe_form.data.get('new_tag'):
            
            tag_instance = Tag(name=create_recipe_form.data['new_tag'])
            tag_instance.save()

            # Refresh the page
            return HttpResponseRedirect(reverse('add_recipe'))

        # Check if the form is valid:
        elif create_recipe_form.is_valid():
            log_debug_message('is valid.')
            
            # Parse servings field into the two model fields
            (servings_min, servings_max) = create_recipe_form.cleaned_data['servings']
            create_recipe_form.cleaned_data.pop('servings')
            create_recipe_form.cleaned_data['servings_min'] = servings_min
            create_recipe_form.cleaned_data['servings_max'] = servings_max

            # Update the recipe instance with the new data
            clean_key=sanitize_string(create_recipe_form.cleaned_data['title'])
            capital_title = capitalize_title(create_recipe_form.cleaned_data['title'])

            recipe_instance.clean_key=clean_key
            recipe_instance.title=capital_title
            recipe_instance.url=create_recipe_form.cleaned_data.get('url')
            recipe_instance.recipe_book_page=create_recipe_form.cleaned_data.get('recipe_book_page')
            recipe_instance.duration_minutes=create_recipe_form.cleaned_data['duration_minutes']
            recipe_instance.calories_per_recipe=create_recipe_form.cleaned_data.get('calories_per_recipe')
            recipe_instance.notes=create_recipe_form.cleaned_data.get('notes')
            recipe_instance.is_baking_recipe=create_recipe_form.cleaned_data.get('is_baking_recipe', False)

            log_debug_message('made recipe instance')

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

            log_debug_message('saved book')

            # Remove any existing tags from the recipe
            # Using a for loop instead of bulk_update because it can't update many-to-many relationship fields
            existing_tags = Tag.objects.filter(recipes=recipe_instance)
            for tag in existing_tags:
                tag.recipes.remove(recipe_instance)
                tag.save()
            
            log_debug_message('removed tags')
            
            # Extract tags from form data and create new relationships from tag -> recipe
            tags = get_only_relevant_tags(recipe_instance, request.POST.getlist('tag'))
            
            if tags:
                # Using a for loop instead of bulk_update because it can't update many-to-many relationship fields
                for tag_instance in tags:
                    tag_instance.recipes.add(recipe_instance)
                    tag_instance.save()
            
            log_debug_message('saved tags')

            # Only adding images here, not deleting any
            # Using a for loop instead of bulk_create to ensure RecipeImage.save() is triggered
            recipe_images = request.FILES.getlist('images')
            recipe_image_instances = []
            if recipe_images:
                for recipe_image in recipe_images:
                    recipe_image_instance = RecipeImage(
                        recipe=recipe_instance,
                        image=recipe_image,
                    )
                    recipe_image_instance.save()

            log_debug_message('saved pics')

            # Remove any existing ingredients from the recipe
            existing_ingreds = Ingredient.objects.filter(recipe=recipe_instance).delete()
            existing_ingred_categories = IngredientCategory.objects.filter(recipe=recipe_instance)
            # Before deleting the ingredient categories, preserve their orders
            existing_ingred_category_orders = {cat.name: cat.order_number for cat in existing_ingred_categories}
            # Now we can delete them
            existing_ingred_categories.delete()

            log_debug_message('removed ingreds and categories')

            # Establish ingredient categories and assign their order values
            ingredient_ids = {re.search(r'ingred_(\d+)', input_name).group() for input_name in create_recipe_form.cleaned_data.keys() if input_name.startswith('ingred_')}  # Creates a distinct set of ingredient ID prefixes, e.g. {ingred_0, ingred_1}
            new_ingredient_categories = remove_dupes_preserve_order([create_recipe_form.cleaned_data[f'{ingred_id_prefix}_ingredient_category'] or '' for ingred_id_prefix in sorted(ingredient_ids)])

            # Map categories to a new order number. New categories will be added alphabetically at the end of the list.
            ingred_category_orders = {}
            for i, category in enumerate(new_ingredient_categories):
                if category in existing_ingred_category_orders:
                    ingred_category_orders[category] = existing_ingred_category_orders[category]
                else:
                    ingred_category_orders[category] = len(existing_ingred_category_orders) + i

            log_debug_message('mapped ingred category numbers')

            ingredient_instances = []

            # For each ingredient in the form
            for ingred_id_prefix in sorted(ingredient_ids):
                    
                log_debug_message(f'start ingredient {ingred_id_prefix}')

                # Gather ingredients fields together
                ingred = {field: create_recipe_form.cleaned_data[f'{ingred_id_prefix}_{field}'] for field in ['food', 'unit_of_measurement', 'quantity', 'ingredient_category', 'notes']}

                # Check if food specified in ingredient already exists. If not, create it.
                existing_foods = [food.clean_key for food in Food.objects.all()]
                selected_food = sanitize_string(ingred['food'])
                if 'salt' in selected_food and 'pepper' in selected_food:
                    selected_food = 'salt-and-pepper'
                if selected_food not in existing_foods:
                    new_food = Food(
                        name=ingred['food'],
                        clean_key=selected_food,
                    )
                    new_food.save()
                
                # Same for unit of measurement
                existing_units = [unit.clean_key for unit in UnitOfMeasurement.objects.all()]
                raw_unit = ingred['unit_of_measurement']
                if raw_unit.endswith('s'):
                    raw_unit = raw_unit[:-1]
                selected_unit = sanitize_string(raw_unit)
                if selected_unit not in existing_units:
                    new_unit = UnitOfMeasurement(
                        name=raw_unit,
                        clean_key=selected_unit,
                    )
                    new_unit.save()
                
                # Same for ingredient category
                existing_categories = [cat.name for cat in IngredientCategory.objects.filter(recipe=recipe_instance)]
                category_name = ingred['ingredient_category']
                if category_name not in existing_categories:
                    ingredient_category_instance = IngredientCategory(
                        recipe=recipe_instance,
                        name=category_name,
                        order_number=ingred_category_orders[category_name],
                    )
                    ingredient_category_instance.save()
                else:
                    ingredient_category_instance = IngredientCategory.objects.get(recipe=recipe_instance, name=category_name)
                
                # Create ingredient instance
                ingredient_instance = Ingredient(
                    food=Food.objects.get(clean_key=selected_food),
                    recipe=recipe_instance,
                    unit_of_measurement=UnitOfMeasurement.objects.get(clean_key=selected_unit),
                    quantity=ingred['quantity'],
                    ingredient_category=ingredient_category_instance,
                    notes=ingred.get('notes', ''),
                )
                ingredient_instances.append(ingredient_instance)
            
            if len(ingredient_instances) > 0:
                # Save all ingredients in a single transaction
                Ingredient.objects.bulk_create(ingredient_instances)
                log_debug_message('bulk-saved ingredients')

            # Remove any existing steps from the recipe
            existing_steps = RecipeStep.objects.filter(recipe=recipe_instance)
            existing_steps.delete()

            # Now, for each step in the form
            step_ids = {re.search(r'step_(\d+)', input_name).group() for input_name in create_recipe_form.cleaned_data.keys() if input_name.startswith('step_')}  # Creates a distinct set of step ID prefixes, e.g. {step_0, step_1}
            step_instances = []
            for i, step_id_prefix in enumerate(sorted(step_ids)):
                step_description = create_recipe_form.cleaned_data[f'{step_id_prefix}_description']
                step_instance = RecipeStep(
                    recipe=recipe_instance,
                    order_number=i,
                    description=step_description,
                )
                step_instances.append(step_instance)

            if len(step_instances) > 0:
                # Save all steps in a single transaction
                RecipeStep.objects.bulk_create(step_instances)

            log_debug_message(f'finished steps')

            # if cloud sync is enabled, sync now
            if S3_SYNC_ENABLED:
                s3 = S3Sync()
                s3.upload_recipe(recipe_instance)
                log_debug_message(f'uploaded to S3')

            # redirect to a new URL:
            return redirect('recipe_detail', key=clean_key)

        else:
            return HttpResponseBadRequest(create_recipe_form.errors)

    # If this is a GET (or any other method), populate the form with the recipe's existing info.
    else:
        related_tags = [tag.name for tag in Tag.objects.filter(recipes=recipe_instance)]
        related_images = [{'url':recipe_image.image.url,'file_name':recipe_image._file_name} for recipe_image in RecipeImage.objects.filter(recipe=recipe_instance)]
        related_ingredients = Ingredient.objects.filter(recipe=recipe_instance).order_by('ingredient_category__order_number')
        related_steps = RecipeStep.objects.filter(recipe=recipe_instance).order_by('order_number')

        existing_foods = [food.name for food in Food.objects.all()]
        existing_units = [unit.name for unit in UnitOfMeasurement.objects.all()]
        existing_books = [book.name for book in RecipeBook.objects.all()]
        existing_tags = [tag for tag in Tag.objects.all().order_by('name')]
        
        create_recipe_form = CreateRecipeForm(
            initial=recipe_instance.__dict__,
            extra_ingreds=len(related_ingredients) - 1,
            extra_steps=len(related_steps) - 1,
        )
        create_recipe_form.fields['tags'].initial = [tag.name for tag in Tag.objects.filter(recipes=recipe_instance)]  # doesn't really do anything because the tags that get checked are set in context via related_tags
        create_recipe_form.fields['is_baking_recipe'].initial = recipe_instance.is_baking_recipe
        if recipe_instance.servings_min:
            create_recipe_form.fields['servings'].initial = str(recipe_instance.servings_min)
            if recipe_instance.servings_max:
                create_recipe_form.fields['servings'].initial+= " - " + str(recipe_instance.servings_max)
        else:
            create_recipe_form.fields['servings'].initial = ''
        
        if recipe_instance.recipe_book:
            create_recipe_form.fields['recipe_book'].initial = recipe_instance.recipe_book.name

        # Prepping ingredients and steps as dictionaries to be passed to the template, rather than setting inital fields,
        # because the template cannot dyanmically access dictionary keys (i.e. cannot do this: create_recipe_form['ingred_' + number + '_food'].value)
        ingredient_list = []
        ingredient_fields = ['food', 'unit_of_measurement', 'quantity', 'notes']
        for i, ingredient in enumerate(related_ingredients):
            ingredient_data = {}
            for field in ingredient_fields:
                # create_recipe_form.fields[f'ingred_{i}_{field}'].initial = getattr(ingredient, field)  # what you would set if using initial values
                ingredient_data[field] = getattr(ingredient, field)
            try:
                ingredient_data['ingredient_category'] = ingredient.ingredient_category.name
            except AttributeError:
                ingredient_data['ingredient_category'] = ''
            ingredient_list.append(ingredient_data)
        
        # If the recipe is from a recipe book, it may have no ingredients. Populate a blank one for the form.
        if len(ingredient_list) == 0:
            ingredient_list = [{key: '' for key in ingredient_fields}]

        step_list = []
        step_fields = ['description']
        for step in related_steps:
            step_data = {}
            for field in step_fields:
                # create_recipe_form.fields[f'step_{i}_{field}'].initial = getattr(step, field)
                step_data[field] = getattr(step, field)
            step_list.append(step_data)
        
        # If the recipe is from a recipe book, it may have no steps. Populate a blank one for the form.
        if len(step_list) == 0:
            step_list = [{key: '' for key in step_fields}]

    context = {
        'mode': 'edit',
        'create_recipe_form': create_recipe_form,
        'checked_tags': related_tags,
        'existing_images': related_images,
        'ingredient_list': ingredient_list,
        'step_list': step_list,
        'food_list': existing_foods,
        'unit_list': existing_units,
        'book_list': existing_books,
        'tag_list': existing_tags,
    }

    return render(request, 'add_edit_recipe.html', context)


def manage_food(request):
    food_search_form = FoodTextFilter(request.GET, queryset=Food.objects.all().order_by('name'))
    found_foods = food_search_form.qs.distinct()
    food_category_search_form = FoodCategoryTextFilter(request.GET, queryset=FoodCategory.objects.all().order_by('name'))
    found_categories = food_category_search_form.qs.distinct()
    foods = [
        {
            'name': food.name,
            'category': food.food_category.name if food.food_category else '',
            'recipes': [{'title': recipe.title, 'clean_key': recipe.clean_key} for recipe in Recipe.objects.filter(ingredient__food__clean_key=food.clean_key).distinct().order_by('title')],
        }
        for food in found_foods
    ]
    categories = [
        {
            'name': cat.name,
            'foods': [food.name for food in Food.objects.filter(food_category__name=cat.name).order_by('name')],
        }
        for cat in found_categories
    ]
    all_categories = [cat.name for cat in FoodCategory.objects.all().order_by('name')]
    context = {
        'foods': foods,
        'categories': categories,
        'all_categories': all_categories,
        'food_search': food_search_form,
        'category_search': food_category_search_form,
    }
    return render(request, 'manage_food.html', context)


@csrf_exempt
def add_tag(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        tag_instance = Tag(name=data['tag_name'])
        tag_instance.save()

        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])

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

@csrf_exempt
def delete_recipe_image(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recipe_image_instance = RecipeImage.objects.get(_file_name=data['file_name'])
        recipe_image_instance.delete()

        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])

@csrf_exempt
def get_ingredient_category_order_number(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recipe = Recipe.objects.get(clean_key=data['recipe_key'])
        ingredient_category = IngredientCategory.objects.get(recipe=recipe, name=data['ingredient_category'])

        print(f'get_ingredient_category_order_number: {ingredient_category.name} = {ingredient_category.order_number}')
        return HttpResponse(str(ingredient_category.order_number))
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])

@csrf_exempt
def swap_ingredient_category_order_numbers(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recipe = Recipe.objects.get(clean_key=data['recipe_key'])
        ingredient_category_1 = IngredientCategory.objects.get(recipe=recipe, name=data['ingredient_category_1'])
        new_number_1 = data['order_number_1']
        ingredient_category_2 = IngredientCategory.objects.get(recipe=recipe, name=data['ingredient_category_2'])
        new_number_2 = data['order_number_2']
        # This atomic function does not work with SQLite, but leaving in case I change database engines in the future
        with transaction.atomic():
            ingredient_category_1.order_number = new_number_1
            ingredient_category_2.order_number = new_number_2
            try:
                ingredient_category_1.save()
                ingredient_category_2.save()
            except IntegrityError:
                return HttpResponse(status=418)

        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])

@csrf_exempt
def merge_food_categories(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        category_to_merge = FoodCategory.objects.get(name=data['category_to_merge'])
        category_to_keep = FoodCategory.objects.get(name=data['category_to_keep'])
        foods_to_update = Food.objects.filter(food_category__name=category_to_merge.name)
        for food in foods_to_update:
            assert food.food_category == category_to_merge
            food.food_category = category_to_keep
            food.save()
        
        category_to_merge.delete()
        
        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])

@csrf_exempt
def merge_foods(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        food_to_merge = Food.objects.get(name=data['food_to_merge'])
        food_to_keep = Food.objects.get(name=data['food_to_keep'])
        ingreds_to_update = Ingredient.objects.filter(food__name=food_to_merge.name)
        for ingred in ingreds_to_update:
            assert ingred.food == food_to_merge
            ingred.food = food_to_keep
            ingred.save()
        
        food_to_merge.delete()
        
        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])
    
@csrf_exempt
def delete_food_category(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cat = FoodCategory.objects.get(name=data['category_name'])
        cat.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])
    
@csrf_exempt
def delete_food(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        food = Food.objects.get(name=data['food_name'])
        food.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])
    
@csrf_exempt
def edit_food_category(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cat = FoodCategory.objects.get(name=data['original_category_name'])
        cat.name = data['new_category_name']
        try:
            cat.save()
            return HttpResponse(status=200)
        except IntegrityError:
            return HttpResponse(status=406)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])
    
@csrf_exempt
def edit_food(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        food = Food.objects.get(name=data['original_food_name'])
        food.name = data['new_food_name']
        category_name = data['category_name']
        if category_name != '':
            category = FoodCategory.objects.get(name=category_name)
            food.food_category = category
        else:
            food.food_category = None
        try:
            food.save()
            return HttpResponse(status=200)
        except IntegrityError:
            return HttpResponse(status=406)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])