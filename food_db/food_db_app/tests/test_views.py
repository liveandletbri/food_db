import functools
import json
import logging
import types
from copy import deepcopy
from django.test import Client, TestCase
from django.urls import reverse
from functools import partial
from rest_framework import status
from ..models import Food, Ingredient, Recipe, RecipeBook, RecipeStep, UnitOfMeasurement, Tag
from ..urls import urlpatterns
from ..views import sanitize_string
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

        # For those with params, the attribute can be a function. So self.page_name(param_value), e.g. self.recipe_detail('my-recipe')

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
                return reverse('recipe_detail', kwargs={'key': param_value})
        cls.recipe_detail = recipe_detail
        
        def edit_recipe(self, param_value):
                return reverse('edit_recipe', kwargs={'key': param_value})
        cls.edit_recipe = edit_recipe
        

    @classmethod
    def setUpTestData(cls):
        create_base_data(cls)
    
    def test_index_GET(self):
        response = self.client.get(self.index)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'index.html')
    
    def test_recipe_detail_GET(self):
        response = self.client.get(self.recipe_detail('my-recipe'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'recipe_detail.html')
    
    def test_recipe_detail_bad_recipe_GET(self):
        response = self.client.get(self.recipe_detail('my-nonexistent-recipe'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_recipe_POST(self):
        post_data = {
            'title': 'The recipe\'s fancy name goes here',
            'duration_minutes': 60,
            'servings': '4-6',
            'calories_per_serving': 200,
            'tag': ['Pasta'],
            'extra_ingred_count': 0,
            'ingred_0_quantity': 1,
            'ingred_0_unit_of_measurement': 'pound',
            'ingred_0_food': 'garlic',
            'extra_step_count': 0,
            'step_0_description': 'Eat the garlic',
        }

        # First, post and verify response code
        post_response = self.client.post(
            self.add_recipe,
            data=post_data,
        )
        status_code_msg = 'Did not get 302 redirect code from recipe creation POST. A 400 likely indicates an invalid form.'
        self.assertEqual(post_response.status_code, status.HTTP_302_FOUND, msg=status_code_msg)

        # Confirm redirect URL
        recipe_page_redirect_url = post_response.url
        recipe_detail_url = self.recipe_detail(sanitize_string(post_data['title']))
        self.assertEqual(recipe_page_redirect_url, recipe_detail_url)

        # Confirm recipe detail page works
        get_response = self.client.get(recipe_detail_url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

        # Confirm all new objects were created
        self.assertEqual(Recipe.objects.all().count(), 2)
        self.assertEqual(Food.objects.all().count(), 2)
        self.assertEqual(UnitOfMeasurement.objects.all().count(), 2)

        # Confirm all attributes match
        (serv_min, serv_max) = post_data['servings'].split('-')

        new_recipe_instance = Recipe.objects.get(title=post_data['title'])
        self.assertEqual(new_recipe_instance.duration_minutes, post_data['duration_minutes'])
        self.assertEqual(new_recipe_instance.servings_min, int(serv_min))
        self.assertEqual(new_recipe_instance.servings_max, int(serv_max))
        self.assertEqual(new_recipe_instance.calories_per_serving, post_data['calories_per_serving'])

        # Confirm all model relations are established
        self.assertEqual(Ingredient.objects.filter(recipe=new_recipe_instance).count(), 1)
        self.assertEqual(RecipeStep.objects.filter(recipe=new_recipe_instance).count(), 1)
        self.assertEqual(Tag.objects.filter(recipes=new_recipe_instance).count(), 1)

    def test_edit_recipe_POST(self):
        title = 'My recipe'
        clean_key = sanitize_string(title)
        recipe_instance = Recipe.objects.get(clean_key=clean_key)
        
        self.assertEqual(Recipe.objects.all().count(), 1)
        self.assertEqual(Food.objects.all().count(), 1)
        self.assertEqual(UnitOfMeasurement.objects.all().count(), 1)
        self.assertEqual(Ingredient.objects.filter(recipe=recipe_instance).count(), 0)
        self.assertEqual(RecipeStep.objects.filter(recipe=recipe_instance).count(), 0)

        # this removes the link between recipe book and the recipe, and adds ingredients, steps, foods, and units
        post_data = {
            'title': title,
            'duration_minutes': 300,
            'servings': '4-6',
            'calories_per_serving': 200,
            'extra_ingred_count': 1,
            'ingred_0_quantity': 2,
            'ingred_0_unit_of_measurement': 'pound',
            'ingred_0_food': 'raw garlic',
            'ingred_1_quantity': 5,
            'ingred_1_unit_of_measurement': 'bulb',
            'ingred_1_food': 'roasted garlic',
            'ingred_1_notes': 'Yum!',
            'extra_step_count': 1,
            'step_0_description': 'Eat the garlic',
            'step_0_description': 'Eat the roasted garlic',
        }
        response = self.client.post(
            self.edit_recipe(clean_key),
            data=post_data,
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        recipe_page_redirect_url = response.url
        recipe_detail_url = self.recipe_detail(clean_key)
        self.assertEqual(recipe_page_redirect_url, recipe_detail_url)
        
        self.assertEqual(Food.objects.all().count(), 3)
        self.assertEqual(UnitOfMeasurement.objects.all().count(), 3)
        self.assertEqual(Ingredient.objects.filter(recipe=recipe_instance).count(), 2)
        self.assertEqual(RecipeStep.objects.filter(recipe=recipe_instance).count(), 2)

    def test_edit_recipe_add_tag_POST(self):
        title = 'My recipe'
        clean_key = sanitize_string(title)
        recipe_instance = Recipe.objects.get(title=title)
        
        # add tags
        Tag.objects.create(name='winter')
        Tag.objects.create(name='autumn')

        self.assertEqual(Tag.objects.filter(recipes=recipe_instance).count(), 0)

        # this removes the link between recipe book and the recipe, and adds ingredients, steps, foods, and units
        post_data = {
            'title': title,
            'tag': ['winter'],
            'servings': '',  # servings is required here because it gets passed into the cleaning function of the form
            'extra_ingred_count': 0,
            'extra_step_count': 0,
        }
        response = self.client.post(
            self.edit_recipe(clean_key),
            data=post_data,
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Tag.objects.filter(recipes=recipe_instance).count(), 1)
        self.assertEqual(Tag.objects.get(recipes=recipe_instance).name, 'winter')

    def test_add_recipe_new_tag_POST(self):
        starting_tag_count = Tag.objects.all().count()
        post_data = {
            'new_tag': 'winter',
            'extra_ingred_count': 0,
            'extra_step_count': 0,
        }
        response = self.client.post(
            self.add_recipe,
            data=post_data,
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, self.add_recipe)
        self.assertEqual(Tag.objects.all().count(), starting_tag_count + 1)

    def test_add_recipe_sanitize_units_and_foods_POST(self):
        Food.objects.create(name='garlic', clean_key='garlic')
        UnitOfMeasurement.objects.create(name='kilogram', clean_key='kilogram')

        number_existing_foods_before = Food.objects.all().count()
        number_existing_units_before = UnitOfMeasurement.objects.all().count()

        clean_key = 'clever-recipe-name'

        post_data = {
            'clean_key': clean_key,
            'title': 'Clever Recipe Name!',
            'servings': '',
            'extra_ingred_count': 0,
            'ingred_0_quantity': 1,
            'ingred_0_unit_of_measurement': 'KiloGrams',  # extra capital letters, ends in S
            'ingred_0_food': 'gArLiC',  # extra capital letters
            'extra_step_count': 0,
            'step_0_description': 'Eat the garlic',
        }
        self.client.post(
            self.add_recipe,
            data=post_data,
        )

        number_existing_foods_after = Food.objects.all().count()
        number_existing_units_after = UnitOfMeasurement.objects.all().count()

        self.assertEqual(number_existing_foods_before, number_existing_foods_after)
        self.assertEqual(number_existing_units_before, number_existing_units_after)

        new_recipe = Recipe.objects.get(clean_key=clean_key)
        ingred = Ingredient.objects.get(recipe=new_recipe)

        self.assertEqual(ingred.food.name, 'garlic')
        self.assertEqual(ingred.unit_of_measurement.name, 'kilogram')