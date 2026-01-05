"""
Tutorial steps configuration for Food DB interactive walkthrough.

Each step in TUTORIAL_STEPS represents a single step in the tutorial walkthrough.
Steps are displayed in the order they appear in the TUTORIAL_STEPS list (order numbers are assigned automatically).

When adding a new step:
1. Add a TutorialStep instance to TUTORIAL_STEPS list
2. Use a unique 'step_id' (lowercase with underscores, e.g., 'welcome', 'add_recipe_basic')
3. 'page_url' must match a Django URL name from urls.py
4. 'page_kwargs' should be None for simple pages, or a dict for pages requiring URL parameters
   (e.g., {'key': 'recipe-key'} for recipe_detail)
5. 'scroll_target' is a CSS selector (e.g., '#recipe_title', '.navbar', 'h1')
"""

import sys
from django.urls import reverse


class TutorialStep:
    """Represents a single step in the tutorial walkthrough."""
    
    def __init__(self, step_id, title, page_url, scroll_target, tooltip_content, page_kwargs=None, order=None):
        """
        Initialize a tutorial step.
        
        Args:
            step_id (str): Unique identifier for the step
            title (str): Display name for the step
            page_url (str): Django URL name (e.g., 'index', 'recipe_detail')
            scroll_target (str): CSS selector for the element to scroll to
            tooltip_content (str): Text/HTML content for the tooltip
            page_kwargs (dict, optional): URL parameters if needed (e.g., {'key': 'recipe-key'})
            order (int, optional): Order number (automatically assigned if None)
        """
        self.step_id = step_id
        self.title = title
        self.page_url = page_url
        self.page_kwargs = page_kwargs
        self.scroll_target = scroll_target
        self.tooltip_content = tooltip_content
        self.order = order
    
    def to_dict_with_url(self):
        """Convert TutorialStep object to a dictionary with resolved URL.
        
        Returns:
            dict: Dictionary with step data including resolved URL.
                Includes: step_id, title, page_url, page_kwargs, scroll_target, 
                tooltip_content, order, url, is_last_step
        """
        url = None
        try:
            if self.page_kwargs:
                url = reverse(self.page_url, kwargs=self.page_kwargs)
            else:
                url = reverse(self.page_url)
        except:
            url = None
        
        is_last_step = self.order == len(TUTORIAL_STEPS)
        
        return {
            'step_id': self.step_id,
            'title': self.title,
            'page_url': self.page_url,
            'page_kwargs': self.page_kwargs,
            'scroll_target': self.scroll_target,
            'tooltip_content': self.tooltip_content,
            'order': self.order,
            'url': url,
            'is_last_step': is_last_step,
        }


TUTORIAL_STEPS = [
    TutorialStep(
        step_id='welcome',
        title='Welcome to Food DB',
        page_url='index',
        page_kwargs=None,
        scroll_target='#logo_title',
        tooltip_content='Welcome to Food DB! This is your personal recipe management system. Let\'s take a quick tour of the features.',
    ),
    TutorialStep(
        step_id='cooking_baking_switch',
        title='Cooking vs Baking Mode',
        page_url='index',
        page_kwargs=None,
        scroll_target='#baking_switch_label',
        tooltip_content='Switch between Cooking and Baking modes. This changes the color scheme and filters recipes based on your selection.',
    ),
    TutorialStep(
        step_id='navigation_bar',
        title='Navigation',
        page_url='index',
        page_kwargs=None,
        scroll_target='.left_side_of_page',
        tooltip_content='Use the navigation bar to access different sections: Home, Add Recipe, Recipes (search), Food Manager, and Bulk Prep.',
    ),
    TutorialStep(
        step_id='search_recipes',
        title='Search Recipes',
        page_url='search',
        page_kwargs=None,
        scroll_target='h1',
        tooltip_content='Search and filter your recipes. Use tags, text search, and other filters to find exactly what you\'re looking for.',
    ),
    TutorialStep(
        step_id='add_recipe',
        title='Add a New Recipe',
        page_url='add_recipe',
        page_kwargs=None,
        scroll_target='h1',
        tooltip_content='Create new recipes here. Add ingredients, steps, images, tags, and more to build your recipe collection.',
    ),
    # Add more steps here as features are developed
    # Example template:
    # TutorialStep(
    #     step_id='feature_name',
    #     title='Feature Title',
    #     page_url='url_name',
    #     page_kwargs=None,  # or {'key': 'value'} if URL needs parameters
    #     scroll_target='#element-id',
    #     tooltip_content='Explanation of the feature...',
    # ),
]

# Assign order numbers based on position in the list
for index, step in enumerate(TUTORIAL_STEPS, start=1):
    step.order = index


def get_tutorial_steps():
    """
    Returns the list of tutorial steps, sorted by order.
    
    Returns:
        list: List of TutorialStep objects, sorted by 'order' field
    """
    return sorted(TUTORIAL_STEPS, key=lambda x: x.order)


def get_step_by_id(step_id):
    """
    Get a tutorial step by its step_id.
    
    Args:
        step_id (str): The unique identifier for the step
        
    Returns:
        TutorialStep: The step object, or None if not found
    """
    for step in TUTORIAL_STEPS:
        if step.step_id == step_id:
            return step
    return None


def get_step_by_order(order):
    """
    Get a tutorial step by its order number.
    
    Args:
        order (int): The order number of the step
        
    Returns:
        TutorialStep: The step object, or None if not found
    """
    for step in TUTORIAL_STEPS:
        if step.order == order:
            return step
    return None


def get_next_step(current_step_id):
    """
    Get the next step in the tutorial sequence.
    
    Args:
        current_step_id (str): The step_id of the current step
        
    Returns:
        TutorialStep: The next step object, or None if current step is the last one
    """
    current_step = get_step_by_id(current_step_id)
    if current_step is None:
        return None
    
    return get_step_by_order(current_step.order + 1)


def get_previous_step(current_step_id):
    """
    Get the previous step in the tutorial sequence.
    
    Args:
        current_step_id (str): The step_id of the current step
        
    Returns:
        TutorialStep: The previous step object, or None if current step is the first one
    """
    current_step = get_step_by_id(current_step_id)
    if current_step is None:
        return None
    
    if current_step.order <= 1:
        return None
    
    return get_step_by_order(current_step.order - 1)

