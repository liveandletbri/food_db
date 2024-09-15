from ..models import Ingredient, Food, Recipe, RecipeBook, UnitOfMeasurement

def create_base_data(cls):
    # Set up data for all test cases
    cls.book = RecipeBook.objects.create(name='book')
    cls.recipe = Recipe.objects.create(
        title = 'My recipe',
        recipe_book = cls.book,
        recipe_book_page = 22,
    )
    cls.unit = UnitOfMeasurement.objects.create(name = 'cup')
    cls.food = Food.objects.create(name='banana')