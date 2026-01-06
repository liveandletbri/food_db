import os
import re
import shutil
import tempfile

from collections import Counter
from django.core.files import File
from django.http import HttpResponseBadRequest, QueryDict
from django.shortcuts import render, redirect

from food_db_app.forms import CreateRecipeForm
from food_db_app.models import *
from food_db_app.cloud_sync.s3 import S3_SYNC_ENABLED, S3Sync

from .utils import (
    sanitize_string,
    capitalize_title,
    remove_dupes_preserve_order,
    log_debug_message,
    get_only_relevant_tags,
    context,
)


def _restore_post_from_session(session_data, apply_corrections=None):
    """
    Restore POST data from session and optionally apply corrections.
    
    Args:
        session_data: Dictionary from request.session['pending_recipe_data']
        apply_corrections: Optional dict of corrections to apply (key: ingred_id, value: corrected_food_name)
    
    Returns:
        QueryDict: Restored POST data
    """
    post_dict = session_data['post_data'].copy()
    
    # Apply corrections if provided
    if apply_corrections:
        for ingred_id, corrected_name in apply_corrections.items():
            if corrected_name:
                post_dict[f'{ingred_id}_food'] = corrected_name
    
    # Convert back to QueryDict
    restored_post = QueryDict('', mutable=True)
    for key, value in post_dict.items():
        if isinstance(value, list):
            for v in value:
                restored_post.appendlist(key, v)
        else:
            restored_post[key] = value
    
    return restored_post


def _create_form_from_post_data(post_data, files=None):
    """Create CreateRecipeForm from POST data."""
    extra_ingred_count = int(post_data.get('extra_ingred_count', 0))
    extra_step_count = int(post_data.get('extra_step_count', 0))
    extra_timing_count = int(post_data.get('extra_timing_count', 0))
    
    return CreateRecipeForm(post_data, files or {}, extra_ingreds=extra_ingred_count, extra_steps=extra_step_count, extra_timings=extra_timing_count)


def _build_form_context(request, create_recipe_form, ingredient_list, step_list, timing_list, existing_data, child_relationships=None):
    """Build context dictionary for rendering the add/edit recipe form."""
    return context(
        request=request,
        mode='add',
        create_recipe_form=create_recipe_form,
        ingredient_list=ingredient_list,
        step_list=step_list,
        timing_list=timing_list,
        food_list=existing_data['existing_foods'],
        unit_list=existing_data['existing_units'],
        book_list=existing_data['existing_books'],
        tag_list=existing_data['existing_tags'],
        recipe_list=existing_data['existing_recipes'],
        child_relationships=child_relationships,
    )


def _process_recipe_creation(request, create_recipe_form):
    """
    Process recipe creation from a validated form.
    This is the shared logic for creating a recipe (used by confirmation POST and auto_confirm GET).
    """
    log_debug_message('is valid?')
    
    if not create_recipe_form.is_valid():
        return HttpResponseBadRequest(create_recipe_form.errors)
    
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
        oven_temp=create_recipe_form.cleaned_data.get('oven_temp'),
        is_baking_recipe=(is_baking := create_recipe_form.cleaned_data.get('is_baking_recipe', False)),
        is_component_recipe=create_recipe_form.cleaned_data.get('is_component_recipe', False),
        is_cookie_recipe=(is_cookie := create_recipe_form.cleaned_data.get('is_cookie_recipe', False) if is_baking else False),
        cookie_style=create_recipe_form.cleaned_data.get('cookie_style') if is_cookie else None,
        cookie_color=create_recipe_form.cleaned_data.get('cookie_color') if is_cookie else None,
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
    
    # Convert RecipeImageTemp to RecipeImage (images were saved during validation)
    recipe_image_temps = RecipeImageTemp.objects.filter(recipe_clean_key=clean_key)
    if recipe_image_temps.exists():
        for recipe_image_temp in recipe_image_temps:
            # Copy the image file to a new RecipeImage
            # We need to copy the file since deleting RecipeImageTemp will delete the original file
            temp_image_file = recipe_image_temp.image
            # Create a temporary copy of the file
            with temp_image_file.open('rb') as source:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(temp_image_file.name)[1]) as temp_file:
                    shutil.copyfileobj(source, temp_file)
                    temp_file_path = temp_file.name
                
                # Create RecipeImage with the copied file
                with open(temp_file_path, 'rb') as f:
                    recipe_image_instance = RecipeImage(
                        recipe=recipe_instance,
                        image=File(f, name=os.path.basename(temp_image_file.name)),
                    )
                    recipe_image_instance.save()
                
                # Clean up temporary file
                os.unlink(temp_file_path)
            
            # Delete the temp image (this will delete the original file via the signal)
            recipe_image_temp.delete()
    
    log_debug_message('saved pics')
    
    # Establish ingredient categories
    ingredient_ids = {re.search(r'ingred_(\d+)', input_name).group() for input_name in create_recipe_form.cleaned_data.keys() if input_name.startswith('ingred_')}
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
        step_ids = {re.search(r'step_(\d+)', input_name).group() for input_name in create_recipe_form.cleaned_data.keys() if input_name.startswith('step_')}
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
    
    number_of_child_recipes = request.POST.get('number_of_linked_recipes') or 0
    number_of_child_recipes = int(number_of_child_recipes)
    
    if number_of_child_recipes > 0:
        for child_index in range(number_of_child_recipes):
            child_recipe_key = request.POST.get(f'child_recipe_{child_index}')
            if not child_recipe_key or child_recipe_key == 'recipe_key':
                continue
            relationship_type = request.POST.get(f'relationship_type_{child_index}', '')
            relationship_type = relationship_type.strip() if relationship_type else None
            child_recipe = Recipe.objects.get(clean_key=child_recipe_key)
            if relationship_type in ('variant', 'full'):
                # in these cases, the current recipe is being made the child, not the parent
                inverse_relationship_type = 'base' if relationship_type == 'variant' else 'component'
                child_recipe.add_child(recipe_instance, inverse_relationship_type)
            else:
                # current recipe is the parent
                recipe_instance.add_child(child_recipe, relationship_type)
    
    log_debug_message('created child recipes')
    
    # Handle timing attributes
    timing_id_prefixes = {re.search(r'timing_(\d+)', input_name).group() for input_name in create_recipe_form.cleaned_data.keys() if input_name.startswith('timing_')}
    timing_ids = [int(id.replace('timing_','')) for id in timing_id_prefixes]
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


# Case 1: POST request after submitting from validate_ingredients.html
def _handle_confirmation_post(request):
    """Handle POST request from validate_ingredients.html confirmation form."""
    log_debug_message('is POST')
    
    # This should only be a confirmation POST (user confirmed ingredient validation in validate_ingredients.html)
    if request.POST.get('confirm_ingredient_validation') != 'true':
        return HttpResponseBadRequest("This endpoint only accepts confirmation POSTs. Submit recipe to /recipe_validation/ first.")
    
    # Restore form data from session and apply corrections
    session_data = request.session.get('pending_recipe_data', None)
    if not session_data:
        return HttpResponseBadRequest("No pending recipe data found. Please submit the form again.")
    
    # Extract corrections from the confirmation form
    corrections = {}
    for key, value in request.POST.items():
        if key.startswith('correction_'):
            ingred_id = key.replace('correction_', '')
            if value:  # User provided a correction
                corrections[ingred_id] = value
    
    # Restore POST data and apply corrections
    restored_post = _restore_post_from_session(session_data, apply_corrections=corrections)
    
    # Temporarily replace request.POST for form creation and the rest of the function
    request.POST = restored_post
    
    # Create form
    create_recipe_form = _create_form_from_post_data(restored_post, request.FILES)
    
    # Clear session data after restoring
    del request.session['pending_recipe_data']
    
    # Process recipe creation
    return _process_recipe_creation(request, create_recipe_form)


# Case 2: GET request with auto_confirm=true (redirected from recipe_validation when no validation issues)
def _handle_auto_confirm_get(request):
    """Handle GET request with auto_confirm flag (no validation issues, proceed directly)."""
    session_data = request.session.get('pending_recipe_data', None)
    if not session_data:
        return HttpResponseBadRequest("No pending recipe data found.")
    
    # Restore POST data from session (no corrections needed)
    restored_post = _restore_post_from_session(session_data)
    
    # Temporarily replace request.POST
    request.POST = restored_post
    
    # Create form
    create_recipe_form = _create_form_from_post_data(restored_post, request.FILES)
    
    # Clear session data
    del request.session['pending_recipe_data']
    
    # Process recipe creation
    return _process_recipe_creation(request, create_recipe_form)


# Case 3: GET request for initial form setup
def _handle_initial_get(request, existing_data):
    """Handle GET request for initial form setup (first time user clicks 'add new recipe')."""
    create_recipe_form = CreateRecipeForm()
    ingredient_list = [
        {'food': '', 'unit_of_measurement': '', 'quantity': None, 'ingredient_category': '', 'notes': ''},
    ]
    step_list = [
        {'description': ''},
    ]
    timing_list = [
        {'type': '', 'minutes': None},
    ]
    
    # Check for base_recipe_key (Create Variant button)
    base_recipe_key = request.GET.get('base_recipe_key')
    child_relationships = None
    if base_recipe_key:
        child_relationships = [{
            'recipe': Recipe.objects.get(clean_key=base_recipe_key),
            'relationship_type': 'base',
        }]
    
    context = _build_form_context(request, create_recipe_form, ingredient_list, step_list, timing_list, existing_data, child_relationships)
    return render(request, 'add_edit_recipe.html', context)


# Case 4: GET request with restore_from_session=true (go back button)
def _handle_restore_from_session_get(request, existing_data):
    """Handle GET request with restore_from_session flag (user clicked 'go back' from validation page)."""
    session_data = request.session.get('pending_recipe_data', None)
    
    if session_data:
        # Restore form data from session
        post_data_dict = session_data['post_data']
        
        # Delete any RecipeImageTemp objects for this recipe (user is going back to edit)
        recipe_title = post_data_dict['title']
        recipe_clean_key = sanitize_string(recipe_title)
        RecipeImageTemp.objects.filter(recipe_clean_key=recipe_clean_key).delete()
        
        # Create form with restored data
        restored_post = _restore_post_from_session(session_data)
        create_recipe_form = _create_form_from_post_data(restored_post)
        
        # Extract form lists for template
        ingredient_list = []
        step_list = []
        timing_list = []
        
        # Extract ingredient data
        ingred_ids = sorted([k.replace('ingred_', '').split('_')[0] for k in post_data_dict.keys() if k.startswith('ingred_') and '_food' in k])
        for ingred_id in ingred_ids:
            ingredient_list.append({
                'food': post_data_dict.get(f'ingred_{ingred_id}_food', ''),
                'unit_of_measurement': post_data_dict.get(f'ingred_{ingred_id}_unit_of_measurement', ''),
                'quantity': post_data_dict.get(f'ingred_{ingred_id}_quantity', None),
                'ingredient_category': post_data_dict.get(f'ingred_{ingred_id}_ingredient_category', ''),
                'notes': post_data_dict.get(f'ingred_{ingred_id}_notes', ''),
            })
        
        # Extract step data
        step_ids = sorted([k.replace('step_', '').split('_')[0] for k in post_data_dict.keys() if k.startswith('step_') and '_description' in k])
        for step_id in step_ids:
            step_list.append({
                'description': post_data_dict.get(f'step_{step_id}_description', ''),
            })
        
        # Extract timing data
        timing_ids = sorted([k.replace('timing_', '').split('_')[0] for k in post_data_dict.keys() if k.startswith('timing_') and '_type' in k])
        for timing_id in timing_ids:
            timing_list.append({
                'type': post_data_dict.get(f'timing_{timing_id}_type', ''),
                'minutes': post_data_dict.get(f'timing_{timing_id}_minutes', None),
            })
    else:
        # No session data, create empty form
        create_recipe_form = CreateRecipeForm()
        ingredient_list = [{'food': '', 'unit_of_measurement': '', 'quantity': None, 'ingredient_category': '', 'notes': ''}]
        step_list = [{'description': ''}]
        timing_list = [{'type': '', 'minutes': None}]
    
    # Check for base_recipe_key (Create Variant button)
    base_recipe_key = request.GET.get('base_recipe_key')
    child_relationships = None
    if base_recipe_key:
        child_relationships = [{
            'recipe': Recipe.objects.get(clean_key=base_recipe_key),
            'relationship_type': 'base',
        }]
    
    context = _build_form_context(request, create_recipe_form, ingredient_list, step_list, timing_list, existing_data, child_relationships)
    return render(request, 'add_edit_recipe.html', context)


# Main entry point
def add_recipe(request):
    """Main entry point for add_recipe view. Routes to appropriate handler based on request type."""
    log_debug_message('add_recipe() called', restart_timer=True)
    
    # Get existing data needed for recipe form (foods, units, books, tags, recipes)
    existing_data = {
        'existing_foods': [food.name for food in Food.objects.all()],
        'existing_units': [unit.name for unit in UnitOfMeasurement.objects.all()],
        'existing_books': [book.name for book in RecipeBook.objects.all()],
        'existing_tags': [tag for tag in Tag.objects.all().order_by('name')],
        'existing_recipes': {recipe.title: recipe.clean_key for recipe in Recipe.objects.all().order_by('title')},
    }
    
    # Case 1: POST request after submitting from validate_ingredients.html
    if request.method == 'POST':
        return _handle_confirmation_post(request)
    
    # Case 2: GET request with auto_confirm=true
    elif request.method == 'GET' and request.GET.get('auto_confirm') == 'true':
        return _handle_auto_confirm_get(request)
    
    # Case 4: GET request with restore_from_session=true
    elif request.method == 'GET' and request.GET.get('restore_from_session') == 'true':
        return _handle_restore_from_session_get(request, existing_data)
    
    # Case 3: GET request for initial form setup
    else:
        return _handle_initial_get(request, existing_data)
