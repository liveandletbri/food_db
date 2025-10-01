import re
import sys

from collections import defaultdict, OrderedDict
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import CookedMeal, Recipe

class BaseChart():
    def __init__(cls):
        assert cls.title
        assert cls.x_labels
        assert isinstance(cls.y_data, dict), "y_data must be a dictionary, where the keys are titles of datasets and the values are lists of values for the y axis"
        assert isinstance(list(cls.y_data.values())[0], list), "y_data must be a dictionary, where the keys are titles of datasets and the values are lists of values for the y axis"
        assert cls.type in ('bar', 'line')
        for label, y_dataset in cls.y_data.items():
            assert len(cls.x_labels) == len(y_dataset), f"Chart {cls.title} has a mismatched number of x_labels and data points for Y dataset {label}"

    def get_data(cls):
        data = {
            'title': cls.title,
            'element_id': re.sub(r'[^a-z0-9-_]', '_', cls.title.lower()),
            'x_labels': cls.x_labels, 
            'y_data': cls.y_data,
            'type': cls.type,
            'step_size': 1  # default value
        }
        optional_attributes = [
            'step_size',
            'y_axis_min',
            'y_axis_max',
        ]
        for attr in optional_attributes:
            if hasattr(cls, attr):
                data[attr] = cls.__getattribute__(attr)
        
        return data

class Top5CookedRecipes(BaseChart):
    title = 'Top 5 Most Cooked Recipes'
    type = 'bar'
    y_axis_min = 0

    cooked_counts = defaultdict(int)
    for meal in CookedMeal.objects.all():
        if meal.recipe.is_baking_recipe == False and meal.recipe.is_component_recipe == False:
            cooked_counts[meal.recipe.title] += 1
    
    # sort by times cooked, descending
    cooked_counts = OrderedDict(sorted(cooked_counts.items(), key=lambda item: item[1], reverse=True))
    
    x_labels = list(cooked_counts.keys())[:5]
    y_data = {title: list(cooked_counts.values())[:5]}

class Top5BakedRecipes(BaseChart):
    title = 'Top 5 Most Baked Recipes'
    type = 'bar'
    y_axis_min = 0

    baked_counts = defaultdict(int)
    for meal in CookedMeal.objects.all():
        if meal.recipe.is_baking_recipe == True and meal.recipe.is_component_recipe == False:
            baked_counts[meal.recipe.title] += 1
    
    # sort by times baked, descending
    baked_counts = OrderedDict(sorted(baked_counts.items(), key=lambda item: item[1], reverse=True))
    
    x_labels = list(baked_counts.keys())[:5]
    y_data = {title: list(baked_counts.values())[:5]}

class AllCharts(APIView):
    def __init__(self):
        # Get all chart classes from this module
        current_module = sys.modules[__name__]
        self.charts = {}
        for name, obj in current_module.__dict__.items():
            # Only instantiate classes that are not AllCharts or BaseChart and are defined in this file
            if isinstance(obj, type) and name not in ('AllCharts', 'BaseChart') and obj.__module__ == __name__:
                chart_class = obj()
                chart_data = chart_class.get_data()
                self.charts[chart_data['element_id']] = chart_data

        assert len(self.charts) > 0, "Failed to correctly gather chart classes. Check configs of each chart."

    def get(self, request, format = None):
        print('Retrieving charts: ' + ', '.join(list(self.charts.keys())))
        return Response(self.charts)