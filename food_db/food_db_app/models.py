import os
import pytz
from colorfield.fields import ColorField
from django.db import models
from django.dispatch.dispatcher import receiver
from django.utils import timezone
from django.utils.deconstruct import deconstructible

from .cloud_sync.s3 import S3_SYNC_ENABLED, S3Sync

@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path='media/'):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        new_name = instance._file_name + '.' + ext
        # return the whole path to the file
        return os.path.join(self.path, new_name)
    
    def __eq__(self, other):
        return self.path == other

rename_image_recipe = PathAndRename("images/recipes/")

class ParentChildRecipe(models.Model):
    def __str__(self):
        return f'Parent: {self.parent_recipe.title} - Child: {self.child_recipe.title}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['parent_recipe', 'child_recipe'], name='unique_parent_child_recipe')
        ]
    parent_recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='child_relationship',
    )
    child_recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='parent_relationship',
    )
    order_number = models.PositiveSmallIntegerField(
        default=0,
        help_text="Order number for the child recipe when displayed on page for parent recipe. Lower numbers appear first.",
    )
    _date_created = models.DateTimeField(default=timezone.now)

class Recipe(models.Model):
    def __str__(self):
        return self.title
    clean_key = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    url = models.TextField(blank=True)
    recipe_book = models.ForeignKey(
        'RecipeBook', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    recipe_book_page = models.PositiveSmallIntegerField(null=True, blank=True)
    duration_minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    servings_min = models.PositiveSmallIntegerField(null=True, blank=True)
    servings_max = models.PositiveSmallIntegerField(null=True, blank=True)
    calories_per_recipe = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', related_name='recipes', blank=True)
    is_baking_recipe = models.BooleanField(default=False)  # Either Cooking or Baking recipe

    # foo = models.TextField(max_length=200)

    # def set_foo(self, x):
    #     self.foo = json.dumps(x)

    # def get_foo(self):
    #     return json.loads(self.foo)

    @property
    def has_ingredients(self):
        ingreds = Ingredient.objects.filter(recipe=self)

        if ingreds.count() == 0:
            return False
        elif ingreds.count() > 1:
            return True
        elif ingreds.count() == 1:
            ingredient = ingreds.first()
            if ingredient.food is None or ingredient.food.name == '':
                return False
            else:
                return True
        # If we somehow get here, return a confusing value
        return 'wut this should never happen'

    @property
    def has_steps(self):
        steps = RecipeStep.objects.filter(recipe=self).order_by('order_number')
        
        if steps.count() == 1 and steps[0].description == '':
            # If there is only one step and it is blank, then there aren't actually any steps. Not totally sure why this happens.
            return False
        elif steps.count() == 0:
            # This is what I'd expect to happen if there are no steps.
            return False
        else:
            return True

    @property
    def has_children(self):
        return self.child_relationship.count() > 0

    @property
    def children(self):
        return [relationship.child_recipe for relationship in ParentChildRecipe.objects.filter(parent_recipe=self).order_by('order_number')]

    def add_child(self, child_recipe):
        '''Adds a child recipe to this recipe.'''
        if not isinstance(child_recipe, Recipe):
            raise ValueError("child_recipe must be an instance of Recipe")
        existing_children = ParentChildRecipe.objects.filter(parent_recipe=self)
        if existing_children.count() > 0:
            order_number = ParentChildRecipe.objects.aggregate(max_order=models.Max('order_number'))['max_order'] + 1
        else:
            order_number = 0
        ParentChildRecipe.objects.create(
            parent_recipe=self,
            child_recipe=child_recipe,
            order_number=order_number,
        )
    
    def remove_all_children(self):
        ParentChildRecipe.objects.filter(parent_recipe=self).delete()

    _date_created = models.DateTimeField(default=timezone.now)
    _date_modified = models.DateTimeField(default=timezone.now)

@receiver(models.signals.pre_delete, sender=Recipe)
def recipe_delete(sender, instance, **kwargs):
    '''If a recipe is backed up in S3, delete it from S3 when the
    Recipe instance is deleted from the database'''
    if S3_SYNC_ENABLED:
        s3 = S3Sync()
        s3.delete_recipe(instance.title)
        print(f'Successfully deleted recipe "{instance.title}" from S3')

class RecipeStep(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'order_number'], name='unique_recipe_step_order_number')
        ]
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    order_number = models.PositiveSmallIntegerField()
    description = models.TextField()
    _date_created = models.DateTimeField(default=timezone.now)
    _date_modified = models.DateTimeField(default=timezone.now)

class Ingredient(models.Model):
    def __str__(self):
        return f'{self.recipe.title}: {self.ingredient_category.name + " - " if self.ingredient_category else ""}{self.food.name}'
    
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    food = models.ForeignKey(
        'Food',
        on_delete=models.PROTECT,
    )
    unit_of_measurement = models.ForeignKey(
        'UnitOfMeasurement',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    ingredient_category = models.ForeignKey(
        'IngredientCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    quantity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    _date_created = models.DateTimeField(default=timezone.now)
    _date_modified = models.DateTimeField(default=timezone.now)

class IngredientCategory(models.Model):
    def __str__(self):
        friendly_name = self.name if self.name != "" else "(Blank)"
        return f'{self.recipe.title}: {friendly_name}'
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'name'],
                name='unique_recipe_ingredient_category_name',
            ),
            models.CheckConstraint(
                condition=~models.Q(name__exact='Misc'),
                name='recipe_ingredient_category_name_not_misc',
            ),
        ]
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255, blank=True)
    order_number = models.PositiveSmallIntegerField()
    _date_created = models.DateTimeField(default=timezone.now)
    _date_modified = models.DateTimeField(default=timezone.now)

class Tag(models.Model):
    def __str__(self):
        return self.name
    # clean_key = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    fill_color = ColorField(default='#3cc382')
    border_color = ColorField(default='#000000')
    text_color = ColorField(default='#ffffff')
    has_border = models.BooleanField(default=False, help_text='Whether the tag has a border or not')

    # Unlike recipes, which are exclusively a cooking or baking recipe, tags can be used for both.
    is_cooking_tag = models.BooleanField(default=True)
    is_baking_tag = models.BooleanField(default=False)

    _date_created = models.DateTimeField(default=timezone.now)

class Food(models.Model):
    def __str__(self):
        return self.name
    clean_key = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    food_category = models.ForeignKey(
        'FoodCategory',
        on_delete=models.PROTECT,
        null=True,
    )
    _date_created = models.DateTimeField(default=timezone.now)

    def clean_name(self, raw_name):
        return raw_name.lower()
    
    def save(self, **kwargs):
        self.name = self.clean_name(self.name)
        self.clean_key = self.clean_name(self.clean_key)

        if (
            update_fields := kwargs.get("update_fields")
        ) is not None and "name" in update_fields:
            kwargs["update_fields"] = {"name"}.union(update_fields)

        if (
            update_fields := kwargs.get("update_fields")
        ) is not None and "clean_key" in update_fields:
            kwargs["update_fields"] = {"clean_key"}.union(update_fields)

        super().save(**kwargs)

class UnitOfMeasurement(models.Model):
    def __str__(self):
        return self.name
    clean_key = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    _date_created = models.DateTimeField(default=timezone.now)
    _date_modified = models.DateTimeField(default=timezone.now)

    def clean_name(self, raw_name):
        clean_name = raw_name.lower()
        if clean_name.endswith('s'):
            clean_name = clean_name[:-1]
        return clean_name
    
    def save(self, **kwargs):
        self.name = self.clean_name(self.name)
        self.clean_key = self.clean_name(self.clean_key)

        if (
            update_fields := kwargs.get("update_fields")
        ) is not None and "name" in update_fields:
            kwargs["update_fields"] = {"name"}.union(update_fields)

        if (
            update_fields := kwargs.get("update_fields")
        ) is not None and "clean_key" in update_fields:
            kwargs["update_fields"] = {"clean_key"}.union(update_fields)

        super().save(**kwargs)

class CookedMeal(models.Model):
    def __str__(self):
        return self.recipe.title + ' - ' + self.date_cooked.astimezone(pytz.timezone('US/Pacific')).strftime('%Y/%m/%d')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    date_cooked = models.DateTimeField(default=timezone.now)
    _date_created = models.DateTimeField(default=timezone.now)

class RecipeBook(models.Model):
    def __str__(self):
        return self.name
    clean_key = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    _date_created = models.DateTimeField(default=timezone.now)
    _date_modified = models.DateTimeField(default=timezone.now)

class RecipeImage(models.Model):
    def __str__(self):
        return self._file_name
    
    def save(self, **kwargs):
        self._file_name = self.recipe.clean_key + '__' + self._date_created.astimezone(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d-%H%M%S.%f')

        if (
            update_fields := kwargs.get("update_fields")
        ) is not None and "_file_name" in update_fields:
            kwargs["update_fields"] = {"_file_name"}.union(update_fields)

        super().save(**kwargs)
    
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    image = models.ImageField(upload_to=rename_image_recipe)
    _file_name = models.CharField(max_length=300, null=True, blank=True)
    _date_created = models.DateTimeField(default=timezone.now)

@receiver(models.signals.pre_delete, sender=RecipeImage)
def recipe_image_delete(sender, instance, **kwargs):
    '''Deletes the image file from the media folder when a
    RecipeImage instance is deleted from the database'''
    # Pass false so FileField doesn't save the model.
    instance.image.delete(False)

class FoodCategory(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=255, unique=True)
    _date_created = models.DateTimeField(default=timezone.now)
    _date_modified = models.DateTimeField(default=timezone.now)