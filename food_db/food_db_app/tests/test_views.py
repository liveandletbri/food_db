import functools
import json
import logging
import types
from copy import deepcopy
from django.test import Client, TestCase
from django.urls import reverse
from functools import partial
from rest_framework import status
from ..models import Food, Ingredient, Recipe, RecipeBook, RecipeStep, UnitOfMeasurement
from ..urls import urlpatterns
from .config import create_base_data

logger = logging.getLogger(__name__)

def copy_func(f, name=None):
    g = types.FunctionType(f.__code__, f.__globals__, name=name or f.__name__,
                           argdefs=f.__defaults__,
                           closure=f.__closure__)
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = deepcopy(f.__kwdefaults__)
    # in case f was given attrs (note this dict is a shallow copy):
    g.__dict__.update(deepcopy(f.__dict__)) 
    return g

class ViewTests(TestCase):
    @classmethod
    def setUp(cls):
        cls.client = Client()
        
        patterns_without_params = [pattern for pattern in urlpatterns if ':' not in str(pattern.pattern)]
        patterns_with_params = [pattern for pattern in urlpatterns if pattern not in patterns_without_params]
        # Set cls.index = reverse('index'), for example. This first loop is for the URLs that don't need params
        for pattern in patterns_without_params:
            page_name = pattern.name
            setattr(cls, page_name, reverse(page_name)) 

        # For those with params, the attribute can be a function. So self.page_name(param_value), e.g. self.recipe_detail('My recipe')

        # This is the template of the function:
        # def url_func(self, param_value):
        #         return reverse(page_name, kwargs={param_name: param_value})
        
        # for pattern in patterns_with_params:
        #     page_name = pattern.name
        #     url_pattern = str(pattern.pattern)
        #     # Assuming just one param in the URL. If more, need to update this
        #     param_start = url_pattern.find('<')
        #     param_end = url_pattern.find('>')
        #     param_contents = url_pattern[param_start+1 : param_end]
        #     param_name = param_contents.split(':')[1]
        #     setattr(cls, page_name, copy_func(url_func, page_name))

        # I had this dynamic method of doing this ^ but my functions were being equated to the same thing (shallow copies overwriting each other somehow) so screw it, here's the manual way
        
        def recipe_detail(self, param_value):
                return reverse('recipe_detail', kwargs={'title': param_value})
        cls.recipe_detail = recipe_detail
        
        def edit_recipe(self, param_value):
                return reverse('edit_recipe', kwargs={'title': param_value})
        cls.edit_recipe = edit_recipe
        

    @classmethod
    def setUpTestData(cls):
        create_base_data(cls)
    
    def test_index_GET(self):
        response = self.client.get(self.index)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'index.html')
    
    def test_recipe_detail_GET(self):
        response = self.client.get(self.recipe_detail('My recipe'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'recipe_detail.html')
    
    def test_recipe_detail_bad_recipe_GET(self):
        response = self.client.get(self.recipe_detail('My nonexistent recipe'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_recipe_POST(self):
        post_data = {
            'title': 'The recipe\'s fancy name goes here',
            'duration_minutes': 60,
            'servings': '4-6',
            'calories_per_serving': 200,
            'extra_ingred_count': 0,
            'ingred_0_quantity': 1,
            'ingred_0_unit_of_measurement': 'pound',
            'ingred_0_food': 'garlic',
            'extra_step_count': 0,
            'step_0_description': 'Eat the garlic',
        }

        post_response = self.client.post(
            self.add_recipe,
            data=post_data,
        )
        recipe_page_redirect_url = post_response.url
        self.assertEqual(post_response.status_code, status.HTTP_302_FOUND)

        recipe_detail_url = self.recipe_detail(post_data['title'])
        self.assertEqual(recipe_page_redirect_url, recipe_detail_url)

        get_response = self.client.get(recipe_detail_url)

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

        self.assertEqual(Recipe.objects.all().count(), 2)
        self.assertEqual(Food.objects.all().count(), 2)
        self.assertEqual(UnitOfMeasurement.objects.all().count(), 2)

        new_recipe_instance = Recipe.objects.get(title=post_data['title'])
        self.assertEqual(Ingredient.objects.filter(recipe=new_recipe_instance).count(), 1)
        self.assertEqual(RecipeStep.objects.filter(recipe=new_recipe_instance).count(), 1)


