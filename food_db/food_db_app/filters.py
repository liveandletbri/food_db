import django_filters as filters
from django import forms
from .models import Recipe, Tag, Food

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
    name = filters.CharFilter(
        label='Food name contains',
        lookup_expr='icontains',
        distinct = True
    )  # https://docs.djangoproject.com/en/5.1/ref/models/querysets/#field-lookups
    category = filters.CharFilter(
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

    def filter_no_category(self, queryset, name, value):
        if value:
            return queryset.filter(food_category=None)
        else:
            return queryset

    
    class Meta:
        model = Food
        fields = ['name', 'food_category']
        distinct = True