import logging
from django.test import TestCase
from ..models import Ingredient, Food, Recipe, RecipeBook, UnitOfMeasurement
from .config import create_base_data

logger = logging.getLogger(__name__)

# tests for models, without needing to render a view

class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_base_data(cls)
        
    def test_create_recipe(self):
        recipe = Recipe.objects.create(title='Blah recipe')
        self.assertEqual(str(recipe), recipe.title)

    def test_create_ingredient_with_all_fields(self):
        ingred = Ingredient(
            recipe = self.recipe,
            food = self.food,
            quantity = 1.5,
            unit_of_measurement = self.unit,
            ingredient_category = 'Blah',
            notes = 'Yum',
        )
        ingred.save()
        found_ingred = Ingredient.objects.get(recipe=self.recipe)
        self.assertEqual(ingred, found_ingred)

    def test_create_ingredient_with_only_food(self):
        """
        All attributes of an ingredient should be allowed to be blank except food and recipe
        """
        ingred = Ingredient(
            recipe = self.recipe,
            food = self.food,
        )
        ingred.save()
        found_ingred = Ingredient.objects.get(recipe=self.recipe)
        logging.info('abcdefg')
        logging.info(ingred)
        self.assertEqual(ingred, found_ingred)

    def test_create_unit_with_plural_name(self):
        """
        UnitOfMeasurement should strip the s from the end of a name, as well as lowercase it
        """
        bad_name = 'Kilograms'
        good_name = 'kilogram'
        unit = UnitOfMeasurement(
            name = bad_name,
            clean_key = bad_name,
        )
        unit.save()
        
        found_units = UnitOfMeasurement.objects.filter(name=bad_name)
        self.assertEqual(len(found_units), 0)

        found_units = UnitOfMeasurement.objects.filter(name=good_name)
        self.assertEqual(len(found_units), 1)
