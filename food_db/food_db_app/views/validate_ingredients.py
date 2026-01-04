import nltk

def find_similar_foods(ingredient_name, existing_foods, max_distance=3):
    """
    Find foods that are reasonably similar to the ingredient name using Levenshtein distance.
    Excludes exact matches.
    
    Args:
        ingredient_name: The name to search for
        existing_foods: List of existing food names
        max_distance: Maximum edit distance to consider similar (default: 3)
    
    Returns:
        List of similar food names
    """
    ingredient_name = ingredient_name.strip().lower()
    similar_foods = []
    
    for food in existing_foods:
        food_lower = food.strip().lower()
        # Skip exact matches
        if food_lower == ingredient_name:
            continue
        
        # Calculate Levenshtein distance
        distance = nltk.edit_distance(ingredient_name, food_lower)
        
        # Consider foods with distance <= max_distance as similar
        if distance <= max_distance:
            similar_foods.append(food)
    
    return similar_foods

class IngredientValidationRule:
    def __init__(self, validation_func, validation_message, suggestion_func=None):
        self.validation_func = validation_func
        self.validation_message = validation_message
        self.suggestion_func = suggestion_func

    def validate(self, ingredient_name, **kwargs):
        is_valid = self.validation_func(ingredient_name, **kwargs)
        if not is_valid:
            validation_message = self.validation_message
            suggested_corrections = self.suggestion_func(ingredient_name, **kwargs) if self.suggestion_func else None
        else:
            validation_message = None
            suggested_corrections = None
        return is_valid, validation_message, suggested_corrections

INGREDIENT_VALIDATION_RULES = [
    IngredientValidationRule(
        validation_func=lambda x, **kwargs: len(x.strip()) >= 2,
        validation_message="Ingredient name is too short. Please provide a valid ingredient name."
    ),
    IngredientValidationRule(
        validation_func=lambda x, existing_foods: x.strip() in existing_foods,
        validation_message="Ingredient name does not currently exist in the database. Either confirm this new ingredient or select a similar existing ingredient.",
        suggestion_func=lambda x, existing_foods: find_similar_foods(x, existing_foods),
    ),
]

def validate_ingredient_name(ingredient_name, existing_foods):
    """
    Validate an ingredient name. This function can be customized to add validation logic.
    
    Args:
        ingredient_name: The name of the ingredient to validate
        existing_foods: List of existing food names in the database
    
    Returns:
        tuple: (is_valid: bool, validation_message: str or None, suggested_corrections: list or None)
        - is_valid: True if the ingredient name is valid, False otherwise
        - validation_message: Message to display to the user if validation fails
        - suggested_corrections: List of suggested corrections if validation fails
    """

    is_valid = True
    validation_message = None
    suggested_corrections = None

    for rule in INGREDIENT_VALIDATION_RULES:
        is_valid, validation_message, suggested_corrections = rule.validate(ingredient_name, existing_foods=existing_foods)
        if not is_valid:
            break

    return is_valid, validation_message, suggested_corrections
