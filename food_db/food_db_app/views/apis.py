import json
import requests

from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

from food_db_app.models import *

from .utils import get_cart

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