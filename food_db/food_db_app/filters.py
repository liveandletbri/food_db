import django_filters as filters
from django import forms
from django.db.models import Count
from .models import Recipe, Tag, Food, FoodCategory

class RecipeTextFilter(filters.FilterSet):
    title = filters.CharFilter(
        lookup_expr='icontains',
        distinct = True
    )  # https://docs.djangoproject.com/en/5.1/ref/models/querysets/#field-lookups
    ingredient = filters.CharFilter(
        label='Ingredient names contain',
        field_name='ingredient__food__name',
        lookup_expr='icontains',
        distinct = True,
    )
    duration_lt = filters.NumberFilter(
        label='Duration less than',
        field_name='duration_minutes',
        lookup_expr='lt',
    )
    tag = filters.ModelMultipleChoiceFilter(
        label='Tagged with',
        field_name='tags__name',
        to_field_name='name',
        queryset=Tag.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple(),
        conjoined=True,
        distinct = True,
    )
    tag_exclusion = filters.ModelMultipleChoiceFilter(
        label='Not tagged with',
        field_name='tags__name',
        to_field_name='name',
        queryset=Tag.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple(),
        conjoined=True,
        distinct = True,
        exclude = True,
    )

    class Meta:
        model = Recipe
        fields = ['title', 'ingredient', 'duration_minutes', 'tags']
        distinct = True

class FoodTextFilter(filters.FilterSet):
    food_name = filters.CharFilter(
        label='Food name contains',
        lookup_expr='icontains',
        field_name='name',
        distinct = True
    )  # https://docs.djangoproject.com/en/5.1/ref/models/querysets/#field-lookups
    food_category = filters.CharFilter(
        label='Category name contains',
        field_name='food_category__name',
        lookup_expr='icontains',
        distinct = True,
    )
    no_category = filters.BooleanFilter(
        method='filter_no_category',
        label='Foods without Categories',
        widget=forms.CheckboxInput,
        initial=False,
    )
    no_recipe = filters.BooleanFilter(
        method='filter_no_recipe',
        label='Foods not used in a Recipe',
        widget=forms.CheckboxInput,
        initial=False,
    )

    def filter_no_category(self, queryset, name, value):
        if value:
            return queryset.filter(food_category=None)
        else:
            return queryset

    def filter_no_recipe(self, queryset, name, value):
        if value:
            return queryset.annotate(recipe_count=Count('ingredient')).filter(recipe_count=0)
        else:
            return queryset

    
    class Meta:
        model = Food
        fields = ['name', 'food_category']
        distinct = True

class FoodCategoryTextFilter(filters.FilterSet):
    category_name = filters.CharFilter(
        label='Category name contains',
        lookup_expr='icontains',
        field_name='name',
        distinct = True
    )
    no_food = filters.BooleanFilter(
        method='filter_no_foods',
        label='Categories not assigned to a Food',
        widget=forms.CheckboxInput,
        initial=False,
    )

    def filter_no_foods(self, queryset, name, value):
        if value:
            return queryset.annotate(food_count=Count('food')).filter(food_count=0)
        else:
            return queryset

    
    class Meta:
        model = FoodCategory
        fields = ['name']
        distinct = True