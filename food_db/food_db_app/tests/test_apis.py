import json
import logging
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from ..models import Food, Recipe, RecipeBook, UnitOfMeasurement
from .config import create_base_data

logger = logging.getLogger(__name__)

class APITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_base_data(cls)
        
    def test_cook_meal(self):
        post_data = {
            'title': 'My recipe'
        }
        number_cooks = 4
        for i in range(1, number_cooks):
            response = self.client.post(
                reverse('cook_meal'),
                data=json.dumps(post_data),
                content_type='application/json',
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.content.decode('utf-8'), str(i))

    def test_cook_meal_fails_get(self):
        response = self.client.get(reverse('cook_meal'))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cook_meal_janky_recipe_title(self):
        disgusting_title = """
        \n\nThis recipe's ;janky-title: a F$#ckin! `${shart_show}`
        """
        Recipe.objects.create(title=disgusting_title)
        post_data = {
            'title': disgusting_title
        }
        response = self.client.post(
            reverse('cook_meal'),
            data=json.dumps(post_data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode('utf-8'), '1')

    def test_ingred_parse(self):
        ingredient_text = """
        basil
        3 cloves garlic
        1/2 tomato, sliced
        """
        expected_response = [
            {
                'food': 'basil',
                'quantity': '',
                'unit_of_measurement': '',
                'notes': '',
            },
            {
                'food': 'garlic',
                'quantity': 3.0,
                'unit_of_measurement': 'cloves',
                'notes': '',
            },
            {
                'food': 'tomato',
                'quantity': 0.5,
                'unit_of_measurement': '',
                'notes': 'sliced',
            },
        ]
        post_data = {
            'text': ingredient_text,
        }
        response = self.client.post(
            reverse('ingred_parse'),
            data=json.dumps(post_data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data_raw = json.loads(response.content)
        response_data = sorted(response_data_raw, key=lambda ingred: ingred['food'])
        self.assertEqual(response_data, expected_response)