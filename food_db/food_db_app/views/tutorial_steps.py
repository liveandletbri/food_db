"""
Tutorial steps configuration for Food DB interactive walkthrough.

TUTORIAL_STEPS is an OrderedDict where keys are section titles and values are lists of TutorialStep objects.
Steps are displayed in the order they appear in the OrderedDict (order numbers are assigned automatically).
The section attribute is automatically set for each step based on its key in the OrderedDict.

When adding a new step:
1. Add a TutorialStep instance to the appropriate section list in TUTORIAL_STEPS
2. Use a unique 'step_id' (lowercase with underscores, e.g., 'welcome', 'add_recipe_basic')
3. 'page_url' must match a Django URL name from urls.py
4. 'page_kwargs' should be None for simple pages, or a dict for pages requiring URL parameters
   (e.g., {'key': 'recipe-key'} for recipe_detail)
5. 'scroll_target' is a CSS selector (e.g., '#recipe_title', '.navbar', 'h1')
"""

import sys
from collections import OrderedDict
from django.urls import reverse


class TutorialStep:
    """Represents a single step in the tutorial walkthrough."""
    
    def __init__(self, step_id, page_url, scroll_target, tooltip_content, page_kwargs=None, order=None, section=None, skip_css_target_validation=False, highlight_scroll_target=False, js_function=None):
        """
        Initialize a tutorial step.
        
        Args:
            step_id (str): Unique identifier for the step
            page_url (str): Django URL name (e.g., 'index', 'recipe_detail')
            scroll_target (str): CSS selector for the element to scroll to
            tooltip_content (str): Text/HTML content for the tooltip
            page_kwargs (dict, optional): URL parameters if needed (e.g., {'key': 'recipe-key'})
            order (int, optional): Order number (automatically assigned if None)
            section (str, optional): Section the step is under (automatically set from TUTORIAL_STEPS if None)
            skip_css_target_validation (bool, optional): If True, skip CSS target validation for this step
            highlight_scroll_target (bool, optional): If True, highlight the scroll target element
            js_function (str, optional): Name of JavaScript function to execute when this step is shown
        """
        self.step_id = step_id
        self.page_url = page_url
        self.page_kwargs = page_kwargs
        self.scroll_target = scroll_target
        self.tooltip_content = tooltip_content
        self.order = order
        self.section = section
        self.skip_css_target_validation = skip_css_target_validation
        self.highlight_scroll_target = highlight_scroll_target
        self.js_function = js_function
    
    def to_dict_with_url(self):
        """Convert TutorialStep object to a dictionary with resolved URL.
        
        Returns:
            dict: Dictionary with step data including resolved URL.
                Includes: step_id, page_url, page_kwargs, scroll_target, 
                tooltip_content, order, url, is_last_step, highlight_scroll_target, js_function
        """
        url = None
        try:
            if self.page_kwargs:
                url = reverse(self.page_url, kwargs=self.page_kwargs)
            else:
                url = reverse(self.page_url)
        except:
            url = None
        
        # Calculate total number of steps across all sections
        total_steps = sum(len(steps) for steps in TUTORIAL_STEPS.values())
        is_last_step = self.order == total_steps
        
        return {
            'step_id': self.step_id,
            'section': self.section,
            'page_url': self.page_url,
            'page_kwargs': self.page_kwargs,
            'scroll_target': self.scroll_target,
            'tooltip_content': self.tooltip_content, 
            'order': self.order,
            'url': url,
            'is_last_step': is_last_step,
            'highlight_scroll_target': self.highlight_scroll_target,
            'js_function': self.js_function,
        }


TUTORIAL_STEPS = OrderedDict([
    ('Getting Familiar', [
        TutorialStep(
            step_id='welcome',
            page_url='index',
            page_kwargs=None,
            scroll_target='#logo_title',
            tooltip_content='''Welcome to Food DB! This is your personal recipe management system. Let's take a quick tour of the features. This tutorial will show you around. You can exit any time with the red button at the bottom of your screen, and revisit any part of the tutorial from the Help page.''',
        ),
        TutorialStep(
            step_id='charts',
            page_url='index',
            page_kwargs=None,
            scroll_target='h1',
            tooltip_content='''If you record your cooked meals, this section will show dashboards with charts and statistics about your cooking patterns. The best way to get interesting data here is to record every cooked meal and to use lots of tags on your recipes!''',
        ),
        TutorialStep(
            step_id='add_recipe_page',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='h1',
            tooltip_content='''This is where you add new recipes. We'll come back here to explore all the features later in the tutorial.''',
        ),
        TutorialStep(
            step_id='cooking_baking_add',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#baking_switch_label',
            tooltip_content='''You have two sides to your Food DB: Cooking and Baking. Use this toggle to determine which side each recipe is stored in.''',
            highlight_scroll_target=True,
        ),
        TutorialStep(
            step_id='search_recipes_page',
            page_url='search',
            page_kwargs=None,
            scroll_target='h1',
            tooltip_content='''Search and filter your recipes. Use tags, text search, and other filters to find exactly what you're looking for.''',
        ),
        TutorialStep(
            step_id='cooking_baking_search',
            page_url='search',
            page_kwargs=None,
            scroll_target='#baking_switch_label',
            tooltip_content='''Like on the add recipe page, this toggle sets you into Cooking or Baking "mode". On this page, it determines which side of your database you are searching in.''',
            highlight_scroll_target=True,
        ),
        TutorialStep(
            step_id='food_manager_page',
            page_url='manage_food',
            page_kwargs=None,
            scroll_target='h1',
            tooltip_content='''This is where you manage the list of all the foods you use as ingredients. You can edit foods, categorize them, and merge them with each other. You only need to use this page if you really like having an organized grocery list 😛''',
        ),
        TutorialStep(
            step_id='bulk_prep_page',
            page_url='bulk_prep',
            page_kwargs=None,
            scroll_target='h1',
            tooltip_content='''This is where you can plan a feast! You can add recipes to your cart and see how they compare to each other. You can also create view configurations to customize the columns you see in the table.''',
        ),
        TutorialStep(
            step_id='help_page',
            page_url='help',
            page_kwargs=None,
            scroll_target='h1',
            tooltip_content='''The help page lets you revisit any step in this tutorial and includes detailed guides about specific features of Food DB.''',
        ),
    ]),
    ('Adding Recipes', [
        TutorialStep(
            step_id='add_recipe_start',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='h1',
            tooltip_content='''Alright, let's dig into how to add a recipe. There is a lot here!''',
        ),
        TutorialStep(
            step_id='cooking_baking_recipe',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#baking_switch_label',
            tooltip_content='''The first choice you make is: is this a Cooking or a Baking recipe? Press this toggle when adding/editing a recipe to change where it is stored in the database. Changing to Cooking or Baking also exposes the tags you've deemed relevant to either Cooking or Baking, and Baking recipes also have additional attributes available to them.''',
            highlight_scroll_target=True,
        ),
        TutorialStep(
            step_id='basic_recipe_info',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='.recipe_summary_label',
            tooltip_content='''Most of the fields here are pretty self-explanatory. They're almost all optional, except the title, obviously.''',
        ),
        TutorialStep(
            step_id='is_component',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#is_component_recipe_row', 
            tooltip_content='''This "reusable component" attribute is for when you've got recipes for, well, components. Sauces, doughs, icings, etc. The only functional thing this attribute does is that it allows you to filter components out (or filter to <i>only</i> components) when searching.''',
            highlight_scroll_target=True,
        ),
        TutorialStep(
            step_id='recipe_url',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#recipe_url_row',
            tooltip_content='''I like to include the URL of the source of the recipe, in case I make a mistake in transcribing it. It's always nice to have the original to look back at! This otherwise doesn't do anything for you - it's just for reference.''',
            highlight_scroll_target=True,
        ),
        TutorialStep(
            step_id='tags_chooser_add_recipe',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#id_tags-label', 
            tooltip_content='''Tagging your recipes is one of the most powerful capabilities of the Food DB! I highly recommend you take the time to come up with a large handful of tags. Recipes can have multiple tags, and the search capabilties on the Recipes page allow you to include and/or exclude tags from your search. The more tags you create and use, the more accurately you can find the <i>exact</i> meal you're craving!''',
        ),
        TutorialStep(
            step_id='create_tag',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#add_tag_button_div',
            tooltip_content='''This is where you can create a new tag. In addition to the tag name, you can customize the appearance of the tag. A distinct appearance might help you spot a tag quickly when your eyes scan the Recipes search results.''',
            highlight_scroll_target=True,
        ),
        TutorialStep(
            step_id='linked_recipes',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#linked_recipes_header', 
            tooltip_content='''You can link recipes to each other to form two types of relationships. An example Full/Component relationship is cake: the cake is the Full recipe, and the icing and the sponge are Component recipes. An example Base/Variant relationship would be pizza: the Base recipe makes a cheese pizza, and each Variant is a pizza with some combination of toppings. Variant recipes include all the ingredients/steps of their Base recipes; similarly Full recipes include everything from their Components.''',
        ),
        TutorialStep(
            step_id='linked_recipes_help',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#linked_recipes_help_icon', 
            tooltip_content='''You can hover over this help icon any time to learn more about Linked Recipes.''',
            highlight_scroll_target=True,
        ),
        TutorialStep(
            step_id='ingreds_intro',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#ingreds_header', 
            tooltip_content='''Here's where you'll add the ingredients for your recipe. Note that recipes don't require ingredients - sometimes a recipe is just a book name and page number.''',
        ),
        TutorialStep(
            step_id='ingreds_table_intro',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='.ingred_body_quantity', 
            tooltip_content='''You can add your ingredients one by one in this table. Every field is optional except Food.''',
        ),
        TutorialStep(
            step_id='ingred_category',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='.ingred_body_ingredient_category', 
            tooltip_content='''Ingredient categories can be used to group ingredients together when you view the recipe later.''',
        ),
        TutorialStep(
            step_id='ingred_category_keyboard_shortcut',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='.ingred_body_ingredient_category',
            tooltip_content='''When your typing cursor is in any of the text boxes for an ingredient, you can press Ctrl+Alt+C to copy the Category of that ingredient's row to the row below it.''',
        ),
        TutorialStep(
            step_id='delete_ingred',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='.delete_ingred_button', 
            tooltip_content='''You can delete any ingredient by pressing the red X in its row.''',
            highlight_scroll_target=True,
        ),
        TutorialStep(
            step_id='ingred_parse',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#show_ingred_parse_button',
            tooltip_content='''There is a faster way to add ingredients! Click this "Parse ingredients from text" button to reveal a large text box.''',
            highlight_scroll_target=True,
        ),
        TutorialStep(
            step_id='ingred_parse_box',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#ingred-parser-textbox',
            tooltip_content='''You can enter ingredients in this text box in plain English, one ingredient per line, and then click the Parse Ingredients button below. This will switch you back to the table view and populate the table's fields for you.''',
            js_function='showIngredientParserOnClick'
        ),
        TutorialStep(
            step_id='recipe_steps_header',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#recipe_steps_header',
            tooltip_content='''This is where you enter the steps you must follow for your recipe. There are several neat features here!''',
            js_function='hideIngredientParserOnClick'
        ),
        TutorialStep(
            step_id='recipe_step_box',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#id_step_0_description',
            tooltip_content='''You enter each step in a box like this, and you can use the buttons below to add and remove boxes for more steps. You can use <a href="https://www.markdownguide.org/cheat-sheet/">Markdown syntax</a> inside these boxes to add some formatting to your steps.''',
            skip_css_target_validation=True,
        ),
        TutorialStep(
            step_id='recipe_step_parse_button',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='.parse_step_button',
            tooltip_content='''You can write or paste multiple steps in this one box. Separate steps with line breaks (you can include numbers at the front of each step or not, doesn't matter) and then press this ellipses button. The text you entered will be magically split into multiple step boxes.''',
            highlight_scroll_target=True,
        ),
        TutorialStep(
            step_id='steps_help_icon',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#markdown_help_icon',
            tooltip_content='''You can hover over this help icon any time to learn more about the syntax used to write recipe steps. In addition to Markdown, there are special rules for linking ingredients to steps. This has several benefits which you can read about on the Help page.''',
            highlight_scroll_target=True,
        ),
        TutorialStep(
            step_id='recipe_timing_attributes',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#timing_header',
            tooltip_content='''Many recipes, especially in baking, have stages where you wait a long time. This might be proving, baking, simmering, etc. These attributes record the times of these stages and display them at the top of the recipe. In addition to being a helpful quick reference, these times are very handy on the Bulk Prep page, where you can plan how you will cook/bake a feast with many different recipes.''',
        ),
        TutorialStep(
            step_id='submit_recipe',
            page_url='add_recipe',
            page_kwargs=None,
            scroll_target='#submit_recipe_button',
            tooltip_content='''All done! Save your recipe by clicking here!''',
        ),
    ]),
])

# Set section attribute and assign order numbers based on position across all sections
order = 1
for section_title, steps in TUTORIAL_STEPS.items():
    for step in steps:
        step.section = section_title
        step.order = order
        order += 1


def get_tutorial_steps():
    """
    Returns the list of tutorial steps, sorted by order.
    
    Returns:
        list: List of TutorialStep objects, sorted by 'order' field
    """
    all_steps = []
    for steps in TUTORIAL_STEPS.values():
        all_steps.extend(steps)
    return sorted(all_steps, key=lambda x: x.order)


def get_step_by_id(step_id):
    """
    Get a tutorial step by its step_id.
    
    Args:
        step_id (str): The unique identifier for the step
        
    Returns:
        TutorialStep: The step object, or None if not found
    """
    for steps in TUTORIAL_STEPS.values():
        for step in steps:
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
    for steps in TUTORIAL_STEPS.values():
        for step in steps:
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

