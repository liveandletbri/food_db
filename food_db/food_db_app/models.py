import pytz
from django.db import models
from django.utils import timezone

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
    calories_per_serving = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', related_name='recipes', blank=True)

    # foo = models.TextField(max_length=200)

    # def set_foo(self, x):
    #     self.foo = json.dumps(x)

    # def get_foo(self):
    #     return json.loads(self.foo)

    _date_created = models.DateTimeField(default=timezone.now)
    _date_modified = models.DateTimeField(default=timezone.now)

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
        return f'{self.recipe.title}: {self.ingredient_category + " - " if self.ingredient_category else ""}{self.food.name}'
    
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
    quantity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ingredient_category = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    _date_created = models.DateTimeField(default=timezone.now)
    _date_modified = models.DateTimeField(default=timezone.now)

class Tag(models.Model):
    def __str__(self):
        return self.name
    # clean_key = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    _date_created = models.DateTimeField(default=timezone.now)

class Food(models.Model):
    def __str__(self):
        return self.name
    clean_key = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    qfc_aisle = models.CharField(max_length=255, blank=True)
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