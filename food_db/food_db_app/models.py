import json
from django.db import models

class Recipe(models.Model):
    def __str__(self):
        return self.title
    title = models.CharField(max_length=255, unique=True)
    url = models.TextField(blank=True)
    duration_minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    servings_min = models.PositiveSmallIntegerField(null=True, blank=True)
    servings_max = models.PositiveSmallIntegerField(null=True, blank=True)
    calories_per_serving = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', related_name='recipes', blank=True)

    # foo = models.TextField(max_length=200)

    # def set_foo(self, x):
    #     self.foo = json.dumps(x)

    # def get_foo(self):
    #     return json.loads(self.foo)

    _date_created = models.DateTimeField(auto_now_add=True)
    _date_modified = models.DateTimeField(auto_now=True)

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
    _date_created = models.DateTimeField(auto_now_add=True)
    _date_modified = models.DateTimeField(auto_now=True)

class Ingredient(models.Model):
    def __str__(self):
        return f'{self.recipe.title}: {self.ingredient_category + " - " if self.ingredient_category else ""}{self.food.name}'
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'food', 'ingredient_category'], name='unique_recipe_food_category')
        ]
    
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
    )
    quantity = models.PositiveSmallIntegerField()
    ingredient_category = models.CharField(max_length=255, blank=True)
    _date_created = models.DateTimeField(auto_now_add=True)
    _date_modified = models.DateTimeField(auto_now=True)

class Tag(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=255, unique=True)
    _date_created = models.DateTimeField(auto_now_add=True)

class Food(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=255)
    qfc_aisle = models.CharField(max_length=255, blank=True)
    _date_created = models.DateTimeField(auto_now_add=True)

class UnitOfMeasurement(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=255)
    _date_created = models.DateTimeField(auto_now_add=True)
    _date_modified = models.DateTimeField(auto_now=True)

class CookedMeal(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    date_cooked = models.DateField(auto_now=True)
    _date_created = models.DateField(auto_now_add=True)