import re
import sys

from collections import defaultdict, OrderedDict
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import CookedMeal, Recipe



class BaseChart(APIView):
    def __init__(cls):
        assert cls.title
        assert cls.x_labels
        assert cls.y_data
        assert cls.type in ('bar', 'line')
        assert len(cls.x_labels) == len(cls.y_data), f"Chart {cls.title} has a mismatched number of x_labels and y_data"

    def get_data(cls):
        data = {
            'title': cls.title,
            'element_id': re.sub(r'[^a-z0-9-_]', '_', cls.title.lower()),
            'x_labels': cls.x_labels, 
            'y_data': cls.y_data,
            'type': cls.type,
            'step_size': 1
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
    
    def get(cls, request, format = None):
        return Response(cls._get_data())

class Top5Recipes(BaseChart):
    title = 'Top 5 Most Cooked Recipes'
    type = 'bar'
    y_axis_min = 0

    cooked_counts = defaultdict(int)
    for meal in CookedMeal.objects.all():
        cooked_counts[meal.recipe.title] += 1
    
    # sort by times cooked, descending
    cooked_counts = OrderedDict(sorted(cooked_counts.items(), key=lambda item: item[1], reverse=True))
    
    x_labels = list(cooked_counts.keys())[:5]
    y_data = list(cooked_counts.values())[:5]

class AllCharts(APIView):
    def __init__(self):
        # Get all chart classes from this module
        current_module = sys.modules[__name__]
        self.charts = {}
        for name, obj in current_module.__dict__.items():
            # Only instantiate classes that are not AllCharts or BaseChart and are defined in this file
            if isinstance(obj, type) and name not in ('AllCharts', 'BaseChart') and obj.__module__ == __name__:
                try:
                    chart_class = obj()
                    chart_data = chart_class.get_data()
                    self.charts[chart_data['element_id']] = chart_data
                except Exception:
                    # If instantiation fails (e.g., abstract base), skip
                    pass

    def get(self, request, format = None):
        return Response(self.charts)