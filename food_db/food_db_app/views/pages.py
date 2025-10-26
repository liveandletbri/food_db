import json
import pytz
import re

from collections import Counter, defaultdict, OrderedDict
from copy import deepcopy
from decimal import Decimal
from django.core.serializers import serialize
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from food_db_app.charts import AllCharts
from food_db_app.filters import RecipeTextFilter, FoodTextFilter, FoodCategoryTextFilter
from food_db_app.forms import CreateRecipeForm
from food_db_app.models import *
from food_db_app.cloud_sync.s3 import S3_SYNC_ENABLED, S3Sync

from .utils import (
    RecipeIngredientData,
    GroceryList,
    convert_minutes_to_string,
    sanitize_string,
    capitalize_title,
    remove_dupes_preserve_order,
    log_debug_message,
    get_only_relevant_tags,
    get_derived_tags,
    get_is_baking_cookie,
    get_cart,
)

def index(request):
    all_charts = AllCharts()
    context = {
        'charts': list(all_charts.charts.keys()),
        'cart': get_cart(request),
    }
    return render(request, 'index.html', context)

def recipe_detail(request, key):
    # assert isinstance(multiplier, float) and multiplier > 0, "Multiplier must be a positive number"
    
    recipe = get_object_or_404(Recipe, clean_key=key)
    multiplier = float(request.GET.get('multiplier', 1))
    child_recipes = recipe.children
    
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

    ingred_data = RecipeIngredientData(recipe, multiplier)
    
    # If there are child recipes, gather their ingredient data too
    recipes = OrderedDict()  # use an ordered dict so that child recipes are displayed in the order they were added
    for rec in child_recipes + [recipe]:
        ingred_data = RecipeIngredientData(rec, multiplier)
        recipes[rec.title] = {
            'clean_key': rec.clean_key,
            'ingred_data': ingred_data,
            'ingreds_by_category': ingred_data.ingreds_by_category,
            'ingredients_have_categories': ingred_data.ingredients_have_categories,
            'steps': RecipeStep.objects.filter(recipe=rec).order_by('order_number')
        }
    
    # convert grocery list dictionary into string
    groceries = GroceryList([rec['ingred_data'] for rec in recipes.values()], multiplier)

    total_cooked_meal_counts = recipe.times_cooked

    last_cooked_meal = CookedMeal.objects.filter(recipe=recipe).order_by('date_cooked').last()
    if last_cooked_meal:
        last_cooked_date = last_cooked_meal.date_cooked.astimezone(pytz.timezone('America/Los_Angeles')).strftime('%b %d, %Y')
    else:
        last_cooked_date = ''

    context = {
        'recipe': recipe,
        'recipe_ingreds_and_steps': recipes,
        'calorie_string': calorie_string,
        'images': images,
        'grocery_list': groceries.grocery_list_str,
        'multiplier': multiplier,
        'total_cooked_meal_counts': total_cooked_meal_counts,
        'last_cooked_date': last_cooked_date,
        'has_steps': recipe.has_steps,
        'is_baking_recipe': str(recipe.is_baking_recipe),
        'has_children': recipe.has_children,
        'cloud_sync_enabled': S3_SYNC_ENABLED,
        'cloud_url': S3Sync().bucket_url,
        'cart': (cart := get_cart(request)),
        'in_cart': str(recipe.clean_key in cart).lower()
    }
    return render(request, 'recipe_detail.html', context)

def add_recipe(request):
    log_debug_message('add_recipe() called', restart_timer=True)
    existing_foods = [food.name for food in Food.objects.all()]
    existing_units = [unit.name for unit in UnitOfMeasurement.objects.all()]
    existing_books = [book.name for book in RecipeBook.objects.all()]
    existing_tags = [tag for tag in Tag.objects.all().order_by('name')]
    existing_recipes = {recipe.title: recipe.clean_key for recipe in Recipe.objects.all().order_by('title')}

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        log_debug_message('is POST')
        # Create a form instance and populate it with data from the request (binding):
        extra_ingred_count = int(request.POST.get('extra_ingred_count'))
        total_ingred_count = extra_ingred_count + 1

        extra_step_count = int(request.POST.get('extra_step_count'))
        total_step_count = extra_step_count + 1

        extra_timing_count = int(request.POST.get('extra_timing_count', 0))
        total_timing_count = extra_timing_count + 1
        create_recipe_form = CreateRecipeForm(request.POST, request.FILES, extra_ingreds=extra_ingred_count, extra_steps=extra_step_count, extra_timings=extra_timing_count)

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
                is_component_recipe=create_recipe_form.cleaned_data.get('is_component_recipe', False),
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
                    existing_food_keys = [food.clean_key for food in Food.objects.all()]
                    existing_food_names = [food.name for food in Food.objects.all()]
                    selected_food_name = ingred['food']
                    selected_food_key = sanitize_string(selected_food_name)
                    if 'salt' in selected_food_key and 'pepper' in selected_food_key:
                        selected_food_key = 'salt-and-pepper'
                    if selected_food_key not in existing_food_keys:
                        # Sometimes, when foods are merged, the clean_key no longer matches the name, so just checking keys
                        # may not be sufficient. Do a second check by name to ensure food name uniqueness.
                        if selected_food_name in existing_food_names:
                            selected_food_key = Food.objects.get(name=selected_food_name).clean_key
                        else:
                            new_food = Food(
                                name=selected_food_name,
                                clean_key=selected_food_key,
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
                        food=Food.objects.get(clean_key=selected_food_key),
                        recipe=recipe_instance,
                        unit_of_measurement=UnitOfMeasurement.objects.get(clean_key=selected_unit),
                        quantity=ingred['quantity'],
                        ingredient_category=ingredient_category_instance,
                        notes=ingred.get('notes', ''),
                    )
                    ingredient_instances.append(ingredient_instance)
                
                Ingredient.objects.bulk_create(ingredient_instances)
            
            # Gather food names and sort them by number of words (descending), then by total string length (descending). The sort order helps ensure that something like "rice vinegar" will match correctly before it matches to "rice".
            food_set = [ingred.food.name for ingred in ingredient_instances if Counter(ingredient_instances)[ingred] == 1]  # only returns foods that are not duplicated - any food mentioned more than once in the ingredient list will not be included at all
            sorted_food_list = sorted(
                food_set,
                key=lambda name: (len(name.split()), len(name)),
                reverse=True
            )
            food_name_regex = '(' + '|'.join(sorted_food_list) + ')'

            if create_recipe_form.cleaned_data['step_0_description'] != '':  # steps were entered for this recipe
                # Now, for each step
                step_ids = {re.search(r'step_(\d+)', input_name).group() for input_name in create_recipe_form.cleaned_data.keys() if input_name.startswith('step_')}  # Creates a distinct set of step ID prefixes, e.g. {step_0, step_1}
                for i, step_id_prefix in enumerate(sorted(step_ids)):
                    step_description = create_recipe_form.cleaned_data[f'{step_id_prefix}_description']
                    # Attempt to automatically find ingredient links. This involves searching the step description for ingredient names, then wrapping the names with [square brackets].
                    # This is only done when adding a recipe - not on edit - to prevent driving the user crazy with repeated attempts at the wrong ingredient links
                    def wrap_food_with_brackets(match):
                        return '[' + match.group(0) + ']'
                    step_description_with_links = re.sub(food_name_regex, wrap_food_with_brackets, step_description, flags=re.IGNORECASE)
                    step_instance = RecipeStep(
                        recipe=recipe_instance,
                        order_number=i + 1,
                        description=step_description_with_links,
                    )
                    step_instances.append(step_instance)
                
                RecipeStep.objects.bulk_create(step_instances)
            log_debug_message(f'finished steps')

            child_recipe_keys = request.POST.getlist('child_recipe')
            child_recipe_keys.remove('recipe_key')  # this is the example value and can be ignored
            if len(child_recipe_keys) > 0:
                for child_recipe_key in child_recipe_keys:
                    child_recipe = Recipe.objects.get(clean_key=child_recipe_key)
                    recipe_instance.add_child(child_recipe)

            log_debug_message('created child recipes')

            # Handle timing attributes
            timing_id_prefixes = {re.search(r'timing_(\d+)', input_name).group() for input_name in create_recipe_form.cleaned_data.keys() if input_name.startswith('timing_')}
            timing_ids = [int(id.replace('timing_','')) for id in timing_id_prefixes]  # pulls just the numbers from the timing ID prefix
            timing_instances = []
            
            for timing_id in sorted(timing_ids):
                timing_type = create_recipe_form.cleaned_data.get(f'timing_{timing_id}_type')
                timing_minutes = create_recipe_form.cleaned_data.get(f'timing_{timing_id}_minutes')
                
                if timing_type and timing_minutes:
                    timing_instance = RecipeTimingAttribute(
                        recipe=recipe_instance,
                        type=timing_type,
                        minutes=timing_minutes,
                    )
                    timing_instances.append(timing_instance)
            
            if timing_instances:
                RecipeTimingAttribute.objects.bulk_create(timing_instances)
            
            log_debug_message('saved timing attributes')

            # if cloud sync is enabled, sync now
            if S3_SYNC_ENABLED:
                s3 = S3Sync()
                s3.upload_recipe(recipe_instance)
                s3.upload_db_backup()
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
        'timing_list': [
            {'type': '', 'minutes': None},
        ],
        'food_list': existing_foods,
        'unit_list': existing_units,
        'book_list': existing_books,
        'tag_list': existing_tags,
        'recipe_list': existing_recipes,
        'current_is_baking_mode': get_is_baking_cookie(request),
        'cart': get_cart(request),
    }

    return render(request, 'add_edit_recipe.html', context)

def search(request):
    search_params = request.GET.copy()
    if 'is_baking_recipe' not in search_params:
        # The lack of this key means we should filter to cooking recipes only
        search_params['is_baking_recipe'] = get_is_baking_cookie(request).lower()

    text_search_form = RecipeTextFilter(search_params, queryset=Recipe.objects.all().order_by('-_date_created'))
    found_recipes = text_search_form.qs.distinct()
    cart = get_cart(request)
    recipe_data = {recipe.title : {} for recipe in found_recipes}
    for recipe in found_recipes:
        recipe_data[recipe.title]['tags'] = [t['fields'] for t in json.loads(serialize('json',recipe.associated_tags))]  # convert Tag to JSON, then dict, because Tag object cannot be implicitly serialized into JSON (which is done on the search template so the data is accessible in Javascript layer)
        recipe_data[recipe.title]['date_created'] = recipe._date_created.astimezone(pytz.timezone('America/Los_Angeles')).strftime('%b %d, %Y')
        recipe_data[recipe.title]['clean_key'] = recipe.clean_key
        recipe_data[recipe.title]['duration_minutes'] = recipe.duration_minutes or 0
        recipe_data[recipe.title]['duration_string'] = convert_minutes_to_string(recipe.duration_minutes) if recipe.duration_minutes else ''
        cooked_count = recipe.times_cooked
        last_cooked_meal = CookedMeal.objects.filter(recipe=recipe).order_by('date_cooked').last()
        if cooked_count > 0:
            recipe_data[recipe.title]['times_cooked'] = str(cooked_count)
            recipe_data[recipe.title]['last_cooked'] = last_cooked_meal.date_cooked.astimezone(pytz.timezone('America/Los_Angeles')).strftime('%b %d, %Y')
        else:
            recipe_data[recipe.title]['times_cooked'] = ''
            recipe_data[recipe.title]['last_cooked'] = ''
        recipe_data[recipe.title]['in_cart'] = str(recipe.clean_key in cart).lower()
    
    # Get count of recipes by tag, used to display metadata on search page
    tag_counts = defaultdict(int)
    for rec in recipe_data.values():
        for tag in rec['tags']:
            tag_counts[tag['name']] += 1
    
    # Separate out the list of tags from the form so we have more control over them in the HTML
    tag_data = [
        {
            'name': tag.name,
            'checked': tag.name in request.GET.getlist('tag'),
            'is_cooking_tag': tag.is_cooking_tag,
            'is_baking_tag': tag.is_baking_tag,
            'result_count': tag_counts[tag.name]
        }
        for tag 
        in text_search_form.filters['tag'].extra['queryset']
    ]

    context = {
        'text_search': text_search_form,
        'recipe_data': recipe_data,
        'tags': tag_data,
        'tag_counts': tag_counts,
        'is_baking_recipe': search_params['is_baking_recipe'],
        'current_is_baking_mode': get_is_baking_cookie(request),
        'cart': cart,
    }
    return render(request, 'search.html', context)


def edit_recipe(request, key):
    log_debug_message('edit_recipe() called', restart_timer=True)
    recipe_instance = get_object_or_404(Recipe, clean_key=key)
    existing_recipe_title = deepcopy(recipe_instance.title)  # Make a copy of the title so we can check if it was changed later
    existing_recipes = {recipe.title: recipe.clean_key for recipe in Recipe.objects.all().order_by('title')}

    # If this is a POST request then process the Form data similarly to an add_recipe request, 
    if request.method == 'POST':
        log_debug_message('is POST')
        # Create a form instance and populate it with data from the request (binding):
        extra_ingred_count = int(request.POST.get('extra_ingred_count'))
        total_ingred_count = extra_ingred_count + 1

        extra_step_count = int(request.POST.get('extra_step_count'))
        total_step_count = extra_step_count + 1

        extra_timing_count = int(request.POST.get('extra_timing_count', 0))
        total_timing_count = extra_timing_count + 1
        create_recipe_form = CreateRecipeForm(request.POST, request.FILES, extra_ingreds=extra_ingred_count, extra_steps=extra_step_count, extra_timings=extra_timing_count)

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

            clean_key=sanitize_string(create_recipe_form.cleaned_data['title'])

            recipe_instance.clean_key=clean_key
            recipe_instance.title=create_recipe_form.cleaned_data['title']  # not capitalizing title on editing a recipe - only on adding. This allows users to have full control if they don't like the capitals
            recipe_instance.url=create_recipe_form.cleaned_data.get('url')
            recipe_instance.recipe_book_page=create_recipe_form.cleaned_data.get('recipe_book_page')
            recipe_instance.duration_minutes=create_recipe_form.cleaned_data['duration_minutes']
            recipe_instance.calories_per_recipe=create_recipe_form.cleaned_data.get('calories_per_recipe')
            recipe_instance.notes=create_recipe_form.cleaned_data.get('notes')
            recipe_instance.is_baking_recipe=create_recipe_form.cleaned_data.get('is_baking_recipe', False)
            recipe_instance.is_component_recipe=create_recipe_form.cleaned_data.get('is_component_recipe', False)

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
                existing_food_keys = [food.clean_key for food in Food.objects.all()]
                existing_food_names = [food.name for food in Food.objects.all()]
                selected_food_name = ingred['food']
                selected_food_key = sanitize_string(selected_food_name)
                if 'salt' in selected_food_key and 'pepper' in selected_food_key:
                    selected_food_key = 'salt-and-pepper'
                if selected_food_key not in existing_food_keys:
                    # Sometimes, when foods are merged, the clean_key no longer matches the name, so just checking keys
                    # may not be sufficient. Do a second check by name to ensure food name uniqueness.
                    if selected_food_name in existing_food_names:
                        selected_food_key = Food.objects.get(name=selected_food_name).clean_key
                    else:
                        new_food = Food(
                            name=selected_food_name,
                            clean_key=selected_food_key,
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
                    food=Food.objects.get(clean_key=selected_food_key),
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
            step_id_prefixes = {re.search(r'step_(\d+)', input_name).group() for input_name in create_recipe_form.cleaned_data.keys() if input_name.startswith('step_')}  # Creates a distinct set of step ID prefixes, e.g. {step_0, step_1}
            step_ids = [int(id.replace('step_','')) for id in step_id_prefixes]  # pulls just the numbers from teh step ID prefix
            step_instances = []
            # in JavaScript, all step rows are updated on form submission to be sequential integers (start at 0, increment by 1), so we can assume a predictable set of step_ids
            for step_id in sorted(step_ids):
                step_description = create_recipe_form.cleaned_data[f'step_{step_id}_description']
                step_instance = RecipeStep(
                    recipe=recipe_instance,
                    order_number=step_id + 1,
                    description=step_description,
                )
                step_instances.append(step_instance)

            if len(step_instances) > 0:
                # Save all steps in a single transaction
                RecipeStep.objects.bulk_create(step_instances)

            log_debug_message(f'finished steps')

            # Remove any existing tags from the recipe
            # Using a for loop instead of bulk_update because it can't update many-to-many relationship fields
            existing_tags = recipe_instance.associated_tags
            for tag in existing_tags:
                tag.recipes.remove(recipe_instance)
                tag.save()
            
            log_debug_message('removed tags')
            
            # Narrow selected tags down to cooking/baking as appropriate
            form_tags = get_only_relevant_tags(recipe_instance, request.POST.getlist('tag'))
            
            log_debug_message('narrowed down cooking/baking tags')

            # Add any derived tags 
            derived_tags = get_derived_tags(recipe_instance)
            
            log_debug_message('got derived tags')

            all_tags = form_tags + derived_tags
            
            if all_tags:
                # Create tag relationship. Using a for loop instead of bulk_update because it can't update
                # many-to-many relationship fields
                for tag_instance in all_tags:
                    tag_instance.recipes.add(recipe_instance)
                    tag_instance.save()
            
            log_debug_message('saved tags')

            child_recipe_keys = request.POST.getlist('child_recipe')
            child_recipe_keys.remove('recipe_key')  # this is the example value and can be ignored
            # First remove existing child recipes
            recipe_instance.remove_all_children()
            if len(child_recipe_keys) > 0:
                # Add the ones declared here
                for child_recipe_key in child_recipe_keys:
                    child_recipe = Recipe.objects.get(clean_key=child_recipe_key)
                    recipe_instance.add_child(child_recipe)

            log_debug_message('created child recipes')

            # Handle timing attributes - remove existing ones first
            RecipeTimingAttribute.objects.filter(recipe=recipe_instance).delete()
            
            timing_id_prefixes = {re.search(r'timing_(\d+)', input_name).group() for input_name in create_recipe_form.cleaned_data.keys() if input_name.startswith('timing_')}
            timing_ids = [int(id.replace('timing_','')) for id in timing_id_prefixes]  # pulls just the numbers from the timing ID prefix
            timing_instances = []
            
            for timing_id in sorted(timing_ids):
                timing_type = create_recipe_form.cleaned_data.get(f'timing_{timing_id}_type')
                timing_minutes = create_recipe_form.cleaned_data.get(f'timing_{timing_id}_minutes')
                
                if timing_type and timing_minutes:
                    timing_instance = RecipeTimingAttribute(
                        recipe=recipe_instance,
                        type=timing_type,
                        minutes=timing_minutes,
                    )
                    timing_instances.append(timing_instance)
            
            if timing_instances:
                RecipeTimingAttribute.objects.bulk_create(timing_instances)
            
            log_debug_message('saved timing attributes')

            # if cloud sync is enabled, sync now
            if S3_SYNC_ENABLED:
                s3 = S3Sync()
                s3.upload_recipe(recipe_instance, existing_recipe_title)
                s3.upload_db_backup()
                log_debug_message(f'uploaded to S3')

            # redirect to a new URL:
            return redirect('recipe_detail', key=clean_key)

        else:
            return HttpResponseBadRequest(create_recipe_form.errors)

    # If this is a GET (or any other method), populate the form with the recipe's existing info.
    else:
        related_tags = [tag.name for tag in recipe_instance.associated_tags]
        related_images = [{'url':recipe_image.image.url,'file_name':recipe_image._file_name} for recipe_image in RecipeImage.objects.filter(recipe=recipe_instance)]
        related_ingredients = Ingredient.objects.filter(recipe=recipe_instance).order_by('ingredient_category__order_number')
        related_steps = RecipeStep.objects.filter(recipe=recipe_instance).order_by('order_number')
        related_timing_attributes = RecipeTimingAttribute.objects.filter(recipe=recipe_instance)
        child_recipes = recipe_instance.children

        existing_foods = [food.name for food in Food.objects.all()]
        existing_units = [unit.name for unit in UnitOfMeasurement.objects.all()]
        existing_books = [book.name for book in RecipeBook.objects.all()]
        existing_tags = [tag for tag in Tag.objects.all().order_by('name')]
        
        create_recipe_form = CreateRecipeForm(
            initial=recipe_instance.__dict__,
            extra_ingreds=len(related_ingredients) - 1,
            extra_steps=len(related_steps) - 1,
            extra_timings=len(related_timing_attributes) - 1 if len(related_timing_attributes) > 0 else 0,
        )
        create_recipe_form.fields['tags'].initial = [tag.name for tag in recipe_instance.associated_tags]  # doesn't really do anything because the tags that get checked are set in context via related_tags
        create_recipe_form.fields['is_baking_recipe'].initial = recipe_instance.is_baking_recipe
        create_recipe_form.fields['is_component_recipe'].initial = recipe_instance.is_component_recipe
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

        # Prepping timing attributes as dictionaries
        timing_list = []
        timing_fields = ['type', 'minutes']
        for timing in related_timing_attributes:
            timing_data = {}
            for field in timing_fields:
                timing_data[field] = getattr(timing, field)
            timing_list.append(timing_data)
        
        # If there are no timing attributes, populate a blank one for the form
        if len(timing_list) == 0:
            timing_list = [{key: '' for key in timing_fields}]

        # Change the cookie for is_baking_mode to match the recipe's is_baking_recipe value
        request.session['is_baking_mode'] = recipe_instance.is_baking_recipe

    context = {
        'mode': 'edit',
        'create_recipe_form': create_recipe_form,
        'checked_tags': related_tags,
        'existing_images': related_images,
        'ingredient_list': ingredient_list,
        'step_list': step_list,
        'timing_list': timing_list,
        'food_list': existing_foods,
        'unit_list': existing_units,
        'book_list': existing_books,
        'tag_list': existing_tags,
        'recipe_list': existing_recipes,
        'child_recipes': child_recipes,
        'current_is_baking_mode': get_is_baking_cookie(request),
        'cart': get_cart(request),
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
        'cart': get_cart(request),
    }
    return render(request, 'manage_food.html', context)


def bulk_prep(request):
    cart = get_cart(request)
    cart_recipes = [Recipe.objects.get(clean_key = key) for key in cart]

    all_recipes_with_children = [child for rec in cart_recipes for child in rec.children if rec.has_children] + cart_recipes
    groceries = GroceryList([RecipeIngredientData(rec, 1) for rec in all_recipes_with_children], 1)

    # Build a set of all tags that are associated with any cart recipe
    all_tags = defaultdict(int)
    for recipe in cart_recipes:
        for tag in recipe.associated_tags:
            all_tags[tag] += 1
    
    # sort by count descending, then by name
    all_tags_sorted = OrderedDict(
        sorted(
            dict(all_tags).items(),
            key=lambda item: (-item[1], item[0].name)
        )
    )

    # recipe_tag_matrix is a dict where the keys are recipe clean_keys and the values are dicts. Each inner dict has a key for every tag in all_tags, and a 1 or 0 indicating if the parent recipe is associated with a given tag.
    recipe_tag_matrix = {}
    for recipe in cart_recipes:
        tag_presence = {}
        for tag in all_tags.keys():
            tag_presence[tag.name] = 1 if tag in recipe.associated_tags else 0
        recipe_tag_matrix[recipe] = tag_presence

    context = {
        'cart': cart,
        'recipes': cart_recipes,
        'grocery_list': groceries.grocery_list_str,
        'recipe_tag_matrix': recipe_tag_matrix,
        'all_tags': all_tags_sorted,
    }
    return render(request, 'bulk_prep.html', context)
