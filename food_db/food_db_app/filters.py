import django_filters as filters
from django import forms
from .models import Recipe, Tag

class RecipeTextFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')  # https://docs.djangoproject.com/en/5.1/ref/models/querysets/#field-lookups
    ingredient = filters.CharFilter(label='Ingredient contains', field_name='ingredient__food__name', lookup_expr='icontains')
    tag = filters.MultipleChoiceFilter(
        label='Tagged with',
        field_name='tags__name',
        choices=[(tag.name, tag.name) for tag in Tag.objects.all()],
        widget=forms.CheckboxSelectMultiple(),
        conjoined=True,
    )

    class Meta:
        model = Recipe
        fields = ['title']