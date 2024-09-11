import re

from django import forms

from django.conf.urls.static import static
from django.core.exceptions import ValidationError
from django.urls import reverse

from .admin import my_admin_site
from .models import Food, Recipe, RecipeBook, Ingredient, Tag, UnitOfMeasurement
from .widgets import CustomRelatedFieldWidgetWrapper, ListTextWidget

# Getting objects! You can run these queries directly by doing python manage.py shell
# Recipe.objects.all() - gets all recipes objects
# Recipe.objects.get(title='value') - gets a single object based on the matched title
# Recipe.objects.filter(attribute='value') - gets all objects that match the attribute
# Recipe.objects.filter(attribute__startswith='value') - gets all objects that match the attribute
#                                __contains='value')
#                                __icontains='value')
#                                __gt='value')
#                                __gte='value')
#                                __lt='value')
#                                __lte='value')
# Recipe.objects.exclude(attribute='value') - gets all objects excluding those that match the attribute
# Recipe.objects.filter(attribute='value').order_by('value') - orders the result set
# Recipe.objects.filter(attribute='value').order_by('-value') - orders the result set in reverse by adding the -

# Recipe.objects.create(attribute='value') - creates an instance of the model
# item = Recipe.objects.get(attribute='value')
# item.attribute = 'new value'
# item.save() - saves the modified instance to the database

# item = Recipe.objects.first()
# or
# item = Recipe.objects.last()
# item.delete() - deletes an instance

# my_recipe = Recipe.objects.get(title='Blah recipe')
# associated_tags = my_recipe.tags.all() - traverse the many to many relationship
# associated_steps = my_recipe.steps_set.all() - traverse the one to many relationship. Note the _set added to the column name

class CreateRecipeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        extra_ingred_fields = kwargs.pop('extra_ingreds', 0)
        extra_step_fields = kwargs.pop('extra_steps', 0)
        super(CreateRecipeForm,self).__init__(*args, **kwargs)

        # Ingredient fields
        food_list = [food.name for food in Food.objects.all()]
        unit_list = [unit.name for unit in UnitOfMeasurement.objects.all()]
        book_list = [book.name for book in RecipeBook.objects.all()]

        self.fields['ingred_0_food'].widget = ListTextWidget(data_list=food_list, name='food-list')
        self.fields['ingred_0_unit_of_measurement'].widget = ListTextWidget(data_list=unit_list, name='unit-list')
        self.fields['recipe_book'].widget = ListTextWidget(data_list=book_list, name='book-list')

        self.fields['extra_ingred_count'].initial = extra_ingred_fields
        for index in range(1, int(extra_ingred_fields)+1):
            # generate extra fields in the number specified via extra_ingred_fields
            self.fields[f'ingred_{index}_quantity'] = forms.DecimalField(required=False)
            self.fields[f'ingred_{index}_unit_of_measurement'] = forms.CharField(required=False)
            self.fields[f'ingred_{index}_food'] = forms.CharField(required=False)
            self.fields[f'ingred_{index}_ingredient_category'] = forms.CharField(required=False)
            self.fields[f'ingred_{index}_notes'] = forms.CharField(required=False)

            self.fields[f'ingred_{index}_food'].widget = ListTextWidget(data_list=food_list, name='food-list')
            self.fields[f'ingred_{index}_unit_of_measurement'].widget = ListTextWidget(data_list=unit_list, name='unit-list')
        
        # Recipe step fields
        self.fields['extra_step_count'].initial = extra_step_fields
        for index in range(1, int(extra_step_fields)+1):
            self.fields[f'step_{index}_description'] = forms.CharField(required=False)

    class Meta:
        model = Recipe  
    
    title = forms.CharField(required=True)
    url = forms.URLField(required=False)
    recipe_book = forms.CharField(required=False)
    recipe_book_page = forms.IntegerField(required=False)
    duration_minutes = forms.IntegerField(required=False)
    servings = forms.CharField(required=False)
    calories_per_serving = forms.IntegerField(required=False)
    notes = forms.CharField(required=False)
    tags = forms.ModelMultipleChoiceField(required=False, queryset=Tag.objects.all().order_by('name'), widget=forms.CheckboxSelectMultiple())
    
    # Tag fields
    new_tag = forms.CharField(required=False)

    # Ingredient fields
    ingred_0_quantity = forms.DecimalField(required=False)
    ingred_0_unit_of_measurement = forms.CharField(required=False)
    ingred_0_food = forms.CharField(required=False)
    ingred_0_ingredient_category = forms.CharField(required=False)
    ingred_0_notes = forms.CharField(required=False)

    extra_ingred_count = forms.CharField(widget=forms.HiddenInput())

    # Recipe step fields
    step_0_description = forms.CharField(required=False)
    extra_step_count = forms.CharField(widget=forms.HiddenInput())

    def clean_servings(self):
        raw_servings_str = self.cleaned_data['servings']

        if raw_servings_str != '':
            cleaned_str = re.sub(r"\s", "", raw_servings_str, flags = re.MULTILINE)
            try:
                assert re.match(r"^[0-9]+-[0-9]+$", cleaned_str)
            except AssertionError:
                raise ValidationError("Servings must be in the format '##-##'.")

            (servings_min, servings_max) = cleaned_str.split('-')

            return (servings_min, servings_max)
        else:
            return (None, None)