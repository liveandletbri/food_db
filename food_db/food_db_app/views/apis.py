import json
import re
import requests

from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from food_db_app.forms import CreateRecipeForm
from food_db_app.models import *

from .utils import get_cart, sanitize_string
from .validate_ingredients import validate_ingredient_name

@csrf_exempt
def add_tag(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        tag_instance = Tag(
            name=data['tag_name'],
            is_cooking_tag=data['is_cooking_tag'],
            is_baking_tag=data['is_baking_tag'],
            fill_color=data['fill_color'],
            text_color=data['text_color'],
            border_color=data['border_color'],
            has_border=data['has_border'],
        )
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
        child_recipes = recipe_instance.child_recipes
        for rec in child_recipes + [recipe_instance]:
            cooked_meal_instance = CookedMeal(recipe=rec)
            cooked_meal_instance.save()

        total_cooked_meal_counts = recipe_instance.times_cooked

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
def delete_recipe(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recipe = Recipe.objects.get(clean_key=data['recipe_key'])
        recipe.delete()
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

@csrf_exempt
def edit_baking_switch_cookie(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request.session['is_baking_mode'] = bool(data['is_baking_mode'])
        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])

@csrf_exempt
def edit_view_config_key(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        view_config_key = data.get('view_config_key', '')
        # Store empty string as None to match the pattern used elsewhere
        request.session['view_config_key'] = view_config_key if view_config_key else None
        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])

@csrf_exempt
def add_recipe_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        recipe_key = data['recipe_key']
        
        # Get cart or initialize as empty list
        cart = request.session.get('cart', [])
        print(f"Current cart: {cart}")
        
        # If cart is None or contains None, reset it
        if cart is None or (isinstance(cart, list) and None in cart):
            cart = []
            print("Reset cart due to None values")
        
        # Add recipe if not already in cart
        if recipe_key not in cart:
            cart.append(recipe_key)
            request.session['cart'] = cart
            print(f"Added {recipe_key} to cart")
        else:
            print(f"{recipe_key} already in cart")
            
        print(f"Final cart: {request.session['cart']}")
        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])

@csrf_exempt
def remove_recipe_from_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recipe_key = data['recipe_key']
        
        # Get cart or initialize as empty list
        cart = request.session.get('cart', [])
        
        # If cart is None or contains None, reset it
        if cart is None or (isinstance(cart, list) and None in cart):
            cart = []
        
        # Remove recipe from cart
        try:
            cart.remove(recipe_key)
            request.session['cart'] = cart
        except ValueError:
            pass  # Recipe not in cart, which is fine
            
        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])

@csrf_exempt
def empty_cart(request):
    if request.method == 'POST':
        # Clear the cart by setting it to an empty list
        request.session['cart'] = []
        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])

@csrf_exempt
def get_cart_size(request):
    if request.method == 'GET':
        cart = get_cart(request)
        return HttpResponse(str(len(cart)))
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET'])

@csrf_exempt
def recipe_validation(request):
    """Validate recipe ingredients and store form data in session for later processing."""
    if request.method == 'POST':
        # Create form instance to validate structure
        extra_ingred_count = int(request.POST.get('extra_ingred_count', 0))
        extra_step_count = int(request.POST.get('extra_step_count', 0))
        extra_timing_count = int(request.POST.get('extra_timing_count', 0))
        
        create_recipe_form = CreateRecipeForm(request.POST, request.FILES, extra_ingreds=extra_ingred_count, extra_steps=extra_step_count, extra_timings=extra_timing_count)
        
        if not create_recipe_form.is_valid():
            return HttpResponseBadRequest(create_recipe_form.errors)
        
        # Store all POST data in session as JSON-serializable dict
        post_data_dict = {}
        for key in request.POST:
            values = request.POST.getlist(key)
            if len(values) == 1:
                post_data_dict[key] = values[0]
            else:
                post_data_dict[key] = values
        
        # Save images as RecipeImageTemp (recipe doesn't exist yet, so we use clean_key string)
        recipe_images = request.FILES.getlist('images')
        if recipe_images:
            # Generate recipe clean_key from title (same logic as in add_recipe)
            recipe_title = create_recipe_form.cleaned_data['title']
            recipe_clean_key = sanitize_string(recipe_title)
            
            # Delete any existing RecipeImageTemp for this recipe (in case user resubmitted)
            RecipeImageTemp.objects.filter(recipe_clean_key=recipe_clean_key).delete()
            
            # Save new images as RecipeImageTemp
            for recipe_image in recipe_images:
                recipe_image_temp = RecipeImageTemp(
                    recipe_clean_key=recipe_clean_key,
                    image=recipe_image,
                )
                recipe_image_temp.save()
        
        # Validate ingredients
        validation_issues = []
        if create_recipe_form.cleaned_data.get('ingred_0_food', '') != '':
            existing_foods = [food.name for food in Food.objects.all()]
            
            # Get all ingredient IDs
            ingredient_ids = {re.search(r'ingred_(\d+)', input_name).group() for input_name in create_recipe_form.cleaned_data.keys() if input_name.startswith('ingred_')}
            
            for ingred_id_prefix in sorted(ingredient_ids):
                ingred = {field: create_recipe_form.cleaned_data.get(f'{ingred_id_prefix}_{field}', '') for field in ['food', 'unit_of_measurement', 'quantity', 'ingredient_category', 'notes']}
                ingredient_name = ingred['food']
                
                if ingredient_name:  # Only validate if ingredient name is provided
                    is_valid, validation_message, suggested_corrections = validate_ingredient_name(ingredient_name, existing_foods)
                    
                    if not is_valid:
                        validation_issues.append({
                            'ingredient_id': ingred_id_prefix,
                            'ingredient_name': ingredient_name,
                            'message': validation_message,
                            'suggested_corrections': suggested_corrections,
                        })
        
        # Store data in session
        request.session['pending_recipe_data'] = {
            'post_data': post_data_dict,
            'validation_issues': validation_issues,
        }
        
        # If validation issues found, return validation page
        if validation_issues:
            context = {
                'validation_issues': validation_issues,
                'form_data': create_recipe_form.cleaned_data,
            }
            return render(request, 'validate_ingredients.html', context)
        else:
            # No validation issues, redirect to add_recipe with auto_confirm flag
            # This will trigger automatic processing
            return redirect(reverse('add_recipe') + '?auto_confirm=true')
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])