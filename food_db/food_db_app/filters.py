import django_filters as filters
from django import forms
from .models import Recipe, Tag

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