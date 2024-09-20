from ..models import Ingredient, Food, Recipe, RecipeBook, UnitOfMeasurement, Tag
from ..views import sanitize_string

def create_base_data(cls):
    # Set up data for all test cases
    cls.book = RecipeBook.objects.create(name='book')
    cls.recipe = Recipe.objects.create(
        title = 'My recipe',
        clean_key = sanitize_string('My recipe'),
        recipe_book = cls.book,
        recipe_book_page = 22,
    )
    cls.unit = UnitOfMeasurement.objects.create(name = 'cup')
    cls.food = Food.objects.create(name='banana')
    Tag.objects.create(name='Pasta')