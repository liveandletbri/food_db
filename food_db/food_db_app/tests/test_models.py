import logging
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from ..models import Ingredient, Food, Recipe, RecipeBook, UnitOfMeasurement

logger = logging.getLogger(__name__)

# tests for models, without needing to render a view

def populate_base_data():
    book = RecipeBook(name='book')
    book.save()
    recipe = Recipe(
        title = 'My recipe',
        recipe_book = book,
        recipe_book_page = 22,
    )
    recipe.save()
    unit = UnitOfMeasurement(name = 'cup')
    unit.save()
    food = Food(name='banana')
    food.save()

    return {
        'recipe': recipe,
        'unit': unit,
        'food': food,
        'book': book,
    }

class ModelTests(TestCase):    
    def test_create_recipe(self):
        recipe = Recipe.objects.create(title='Blah recipe')
        self.assertEqual(str(recipe), recipe.title)

    def test_create_ingredient_with_all_fields(self):
        data = populate_base_data()
        ingred = Ingredient(
            recipe = data['recipe'],
            food = data['food'],
            quantity = 1.5,
            unit_of_measurement = data['unit'],
            ingredient_category = 'Blah',
            notes = 'Yum',
        )
        ingred.save()
        found_ingred = Ingredient.objects.get(recipe=data['recipe'])
        self.assertEqual(ingred, found_ingred)

    def test_create_ingredient_with_only_food(self):
        """
        All attributes of an ingredient should be allowed to be blank except food and recipe
        """
        data = populate_base_data()
        ingred = Ingredient(
            recipe = data['recipe'],
            food = data['food'],
        )
        ingred.save()
        found_ingred = Ingredient.objects.get(recipe=data['recipe'])
        logging.info(ingred)
        self.assertEqual(ingred, found_ingred)

    def test_(self):
        data = populate_base_data()
        response = self.client.get('/cook_meal/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, '12')