from copy import deepcopy
import pytz
import re
import sys

from collections import defaultdict, OrderedDict
from datetime import datetime
from django.db.utils import OperationalError
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import CookedMeal, Recipe, Tag

# Any class name that starts with 'Base' is not treated as a chart. 'Base' classes are created for chart classes to inherit.
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

class BaseTopRecipes(BaseChart):
    type = 'bar'
    y_axis_min = 0

    cooked_counts = defaultdict(int)
    baked_counts = defaultdict(int)
    try:
        for meal in CookedMeal.objects.filter(recipe__is_component_recipe=False):
            if meal.recipe.is_baking_recipe:
                baked_counts[meal.recipe.title] += 1
            else:
                cooked_counts[meal.recipe.title] += 1
        
        # sort by times cooked, descending
        cooked_counts = OrderedDict(sorted(cooked_counts.items(), key=lambda item: item[1], reverse=True))
        baked_counts = OrderedDict(sorted(baked_counts.items(), key=lambda item: item[1], reverse=True))
    except OperationalError:
        # During migrations, database schema may not match models yet
        pass

class Top5CookedRecipes(BaseTopRecipes):
    title = 'Top 5 Most Cooked Recipes'
    
    cooked_counts = BaseTopRecipes.cooked_counts
    x_labels = list(cooked_counts.keys())[:5]
    y_data = {title: list(cooked_counts.values())[:5]}

class Top5BakedRecipes(BaseTopRecipes):
    title = 'Top 5 Most Baked Recipes'
    
    baked_counts = BaseTopRecipes.baked_counts
    x_labels = list(baked_counts.keys())[:5]
    y_data = {title: list(baked_counts.values())[:5]}

class BaseTopTags(BaseChart):
    type = 'bar'
    y_axis_min = 0

    cooked_cooking_tag_counts = defaultdict(int)
    cooked_baking_tag_counts = defaultdict(int)
    try:
        for meal in CookedMeal.objects.filter(recipe__is_component_recipe=False):
            for tag in meal.recipe.associated_tags:
                if meal.recipe.is_baking_recipe:
                    cooked_baking_tag_counts[tag.name] += 1
                else:
                    cooked_cooking_tag_counts[tag.name] += 1
        
        # sort by times cooked, descending
        cooked_cooking_tag_counts = OrderedDict(sorted(cooked_cooking_tag_counts.items(), key=lambda item: item[1], reverse=True))
        cooked_baking_tag_counts = OrderedDict(sorted(cooked_baking_tag_counts.items(), key=lambda item: item[1], reverse=True))
    except OperationalError:
        # During migrations, database schema may not match models yet
        pass

class Top10CookedTags(BaseTopTags):
    title = 'Top 10 Most Cooked Tags'
    
    cooked_counts = BaseTopTags.cooked_cooking_tag_counts
    x_labels = list(cooked_counts.keys())[:10]
    y_data = {title: list(cooked_counts.values())[:10]}

class Top10BakedTags(BaseTopTags):
    title = 'Top 10 Most Baked Tags'
    
    baked_counts = BaseTopTags.cooked_baking_tag_counts
    x_labels = list(baked_counts.keys())[:10]
    y_data = {title: list(baked_counts.values())[:10]}

class TagOverTime(BaseChart):
    type = 'line'
    y_axis_min = 0
    title = 'Tag Cooks Over Time'

    try:
        earliest_meal = CookedMeal.objects.filter(recipe__is_component_recipe=False).order_by('_date_created').first()  # ordering by date created instead of date cooked to avoid back-dated meals
        earliest_date = earliest_meal.date_cooked 

        # Create a dictionary where each key is the first of a month
        now = datetime.now(pytz.timezone('America/Los_Angeles'))
        month_iter = earliest_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        months_dict = OrderedDict()
        while month_iter <= last_month:
            key = month_iter.strftime('%Y-%m')
            # months_dict[key] = {tag: 0 for tag in all_tags}
            months_dict[key] = 0
            # Advance to next month
            if month_iter.month == 12:
                month_iter = month_iter.replace(year=month_iter.year+1, month=1)
            else:
                month_iter = month_iter.replace(month=month_iter.month+1)

        # dataset will be split/keyed by Tag
        tag_dict = {}
        for tag in Tag.objects.all():
            tag_dict[tag.name] = deepcopy(months_dict)  # doing this in a loop instead of a comprehension to ensure months_dict is always defined

        for meal in CookedMeal.objects.filter(recipe__is_component_recipe=False):
            cooked_date_month = meal.date_cooked.replace(day=1, hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m')
            for tag in meal.recipe.associated_tags:
                tag_dict[tag.name][cooked_date_month] += 1
        
        x_labels = list(months_dict.keys())
        y_data = {tag_name: list(monthly_data.values()) for tag_name, monthly_data in tag_dict.items() if tag_name in ['Healthy', 'Cookies', 'Soup', 'Asian', 'Mexican', 'Bread']}
    except OperationalError:
        # During migrations, database schema may not match models yet
        pass

class AllCharts(APIView):
    def __init__(self):
        # Get all chart classes from this module
        current_module = sys.modules[__name__]
        self.charts = {}
        self.chart_count = 0
        for name, obj in current_module.__dict__.items():
            # Only instantiate classes that are not AllCharts or BaseChart and are defined in this file
            if isinstance(obj, type) and name not in ('AllCharts') and not name.startswith('Base') and obj.__module__ == __name__:
                chart_class = obj()
                chart_data = chart_class.get_data()
                self.charts[chart_data['element_id']] = chart_data
                self.chart_count += 1

        assert len(self.charts) > 0, "Failed to correctly gather chart classes. Check configs of each chart."
        assert self.chart_count == len(self.charts.keys()), "Chart titles must be unique. Double-check chart titles."

    def get(self, request, format = None):
        print('Retrieving charts: ' + ', '.join(list(self.charts.keys())))
        return Response(self.charts)