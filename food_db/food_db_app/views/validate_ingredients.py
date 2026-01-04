import nltk
import os

def damerau_levenshtein_distance(s1, s2):
    """
    Calculate Damerau-Levenshtein distance between two strings.
    This includes insertions, deletions, substitutions, and transpositions of adjacent characters.
    """
    len1, len2 = len(s1), len(s2)
    
    # Create a matrix to store distances
    d = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    
    # Initialize first row and column
    for i in range(len1 + 1):
        d[i][0] = i
    for j in range(len2 + 1):
        d[0][j] = j
    
    # Fill the matrix
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if s1[i-1] == s2[j-1]:
                cost = 0
            else:
                cost = 1
            
            d[i][j] = min(
                d[i-1][j] + 1,      # deletion
                d[i][j-1] + 1,      # insertion
                d[i-1][j-1] + cost  # substitution
            )
            
            # Check for transposition (Damerau extension)
            if i > 1 and j > 1 and s1[i-1] == s2[j-2] and s1[i-2] == s2[j-1]:
                d[i][j] = min(d[i][j], d[i-2][j-2] + 1)
    
    return d[len1][len2]

def ngram_similarity(s1, s2, n=2):
    """
    Calculate n-gram similarity between two strings using Jaccard coefficient.
    
    Args:
        s1: First string
        s2: Second string
        n: Size of n-grams (default: 2 for bigrams)
    
    Returns:
        Similarity score between 0 and 1 (1 = identical, 0 = no overlap)
    """
    def get_ngrams(text, n):
        """Generate n-grams from a string."""
        return set(text[i:i+n] for i in range(len(text) - n + 1))
    
    ngrams1 = get_ngrams(s1, n)
    ngrams2 = get_ngrams(s2, n)
    
    if not ngrams1 and not ngrams2:
        return 1.0  # Both empty strings
    if not ngrams1 or not ngrams2:
        return 0.0  # One is empty, other is not
    
    intersection = len(ngrams1 & ngrams2)
    union = len(ngrams1 | ngrams2)
    
    return intersection / union if union > 0 else 0.0

def is_substring_match(s1, s2, min_substring_length=4):
    """
    Check if one string is a substring of another, or if they share a significant word.
    Useful for cases like "all purpose flour" vs "flour" or "kosher salt" vs "salt".
    
    Args:
        s1: First string
        s2: Second string
        min_substring_length: Minimum length of substring to consider (default: 4)
    
    Returns:
        True if one string contains the other as a significant substring
    """
    # Normalize: replace common separators with spaces and split
    def normalize(text):
        return ' '.join(text.replace('&', ' and ').replace(',', ' ').split())
    
    s1_norm = normalize(s1)
    s2_norm = normalize(s2)
    
    # Find the shorter and longer string
    shorter = s1_norm if len(s1_norm) <= len(s2_norm) else s2_norm
    longer = s2_norm if len(s1_norm) <= len(s2_norm) else s1_norm
    
    # Only check substring if shorter string is at least min_substring_length
    if len(shorter) < min_substring_length:
        return False
    
    # Check if shorter string is a substring of longer string
    if shorter in longer:
        return True
    
    # Check if they share significant words (at least min_substring_length characters)
    # But require the shared word to be a substantial part of the shorter string
    words_shorter = [w for w in shorter.split() if len(w) >= min_substring_length]
    words_longer = set(w for w in longer.split() if len(w) >= min_substring_length)
    
    # Only match if:
    # 1. They share at least one significant word
    # 2. The shared word is at least 50% of the shorter string's length (to avoid matching "a" in "salt")
    # 3. One string is at least 4 characters longer (to catch modifier cases)
    shared_words = [w for w in words_shorter if w in words_longer]
    if shared_words:
        longest_shared = max(shared_words, key=len)
        len_diff = len(longer) - len(shorter)
        # Shared word should be substantial part of shorter string, and there should be a meaningful length difference
        if len(longest_shared) >= len(shorter) * 0.5 and len_diff >= 4:
            return True
    
    return False

def find_similar_foods(ingredient_name, existing_foods):
    """
    Find foods that are reasonably similar to the ingredient name using Levenshtein distance.
    Excludes exact matches.
    
    Args:
        ingredient_name: The name to search for
        existing_foods: List of existing food names
    
    Returns:
        List of similar food names
    """
    ingredient_name = ingredient_name.strip().lower()
    similar_foods = []

    # By default, skip this behavior. Users must opt in.
    if os.getenv('SUGGEST_FOOD_NAME_MATCHES', 'false').lower() == 'true':
        max_levenshtein_distance = 3
        max_hamming_distance = 2
        max_damerau_levenshtein_distance = 3
        min_ngram_similarity = 0.6
        
        for food in existing_foods:
            food_lower = food.strip().lower()
            # Skip exact matches
            if food_lower == ingredient_name:
                continue
            
            # Calculate Levenshtein distance
            # Only match if distance is small relative to string length
            lev_distance = nltk.edit_distance(ingredient_name, food_lower)
            max_len = max(len(ingredient_name), len(food_lower))
            if lev_distance <= max_levenshtein_distance and lev_distance <= max_len * 0.4:
                similar_foods.append(food)
            
            # Calculate Hamming distance (only for strings of equal length)
            if len(ingredient_name) == len(food_lower):
                ham_distance = sum(c1 != c2 for c1, c2 in zip(ingredient_name, food_lower))
                if ham_distance <= max_hamming_distance:
                    similar_foods.append(food)
            
            # Calculate Damerau-Levenshtein distance
            # Only match if distance is small relative to string length
            dam_lev_distance = damerau_levenshtein_distance(ingredient_name, food_lower)
            if dam_lev_distance <= max_damerau_levenshtein_distance and dam_lev_distance <= max_len * 0.4:
                similar_foods.append(food)
            
            # Calculate n-gram similarity
            ngram_sim = ngram_similarity(ingredient_name, food_lower)
            if ngram_sim >= min_ngram_similarity:
                similar_foods.append(food)
            
            # Check for substring matches (e.g., "all purpose flour" vs "flour")
            if is_substring_match(ingredient_name, food_lower):
                similar_foods.append(food)
    
    return list(set(similar_foods))

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
