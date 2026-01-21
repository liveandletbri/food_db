"""
Tutorial steps configuration for Food DB interactive walkthrough.

TUTORIAL_STEPS is a list of TutorialStep objects (or objects that inherit from TutorialStep).
Steps are displayed in the order they appear in the list (order numbers are assigned automatically).
The section attribute is automatically set for each step based on its class.

When adding a new step:
1. Add an instance of the appropriate section-specific class to TUTORIAL_STEPS
2. Use a unique 'step_id' (lowercase with underscores, e.g., 'welcome', 'add_recipe_basic')
3. 'page_url' must match a Django URL name from urls.py (or use the default from the section class)
4. 'page_kwargs' should be None for simple pages, or a dict for pages requiring URL parameters
   (e.g., {'key': 'recipe-key'} for recipe_detail)
5. 'scroll_target' is a CSS selector (e.g., '#recipe_title', '.navbar', 'h1')
"""

import hashlib
from django.urls import reverse


class TutorialStep:
    """Represents a single step in the tutorial walkthrough."""
    
    def __init__(self,
        page_url,
        scroll_target,
        tooltip_content,
        page_kwargs=None,
        section=None,
        subsection=None,
        skip_css_target_validation=False,
        highlight_scroll_target=False,
        js_function=None,
        test_db=False,
    ):
        """
        Initialize a tutorial step.
        
        Args:
            page_url (str): Django URL name (e.g., 'index', 'recipe_detail')
            scroll_target (str): CSS selector for the element to scroll to
            tooltip_content (str): Text/HTML content for the tooltip
            page_kwargs (dict, optional): URL parameters if needed (e.g., {'key': 'recipe-key'})
            section (str, optional): Section the step is under (automatically set from class if None)
            subsection (str, optional): Subsection the step is under (None if no subsection)
            skip_css_target_validation (bool, optional): If True, skip CSS target validation for this step
            highlight_scroll_target (bool, optional): If True, highlight the scroll target element
            js_function (str, optional): Name of JavaScript function to execute when this step is shown
            test_db (bool, optional): If True, open the page with query parameter test_db=true, which uses the test database instead of primary database
        """
        
        step_hash_input = f'{page_url}|{scroll_target}|{tooltip_content}'
        self.step_id = hashlib.sha256(step_hash_input.encode('utf-8')).hexdigest()
        self.page_url = page_url
        self.page_kwargs = page_kwargs
        self.scroll_target = scroll_target
        self.tooltip_content = tooltip_content
        self.section = section
        self.subsection = subsection
        self.skip_css_target_validation = skip_css_target_validation
        self.highlight_scroll_target = highlight_scroll_target
        self.js_function = js_function
        self.test_db = test_db

    @property
    def name(self):
        return f'{self.__class__.__name__}_{self.scroll_target}_{self.order}'
    
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

            if self.test_db:
                url += '?test_db=true'
        except:
            url = None
        
        # Calculate total number of steps
        total_steps = len(TUTORIAL_STEPS)
        is_last_step = self.order == total_steps
        
        return {
            'step_id': self.step_id,
            'section': self.section,
            'subsection': self.subsection,
            'page_url': self.page_url,
            'page_kwargs': self.page_kwargs,
            'scroll_target': self.scroll_target,
            'tooltip_content': self.tooltip_content, 
            'order': self.order,
            'url': url,
            'is_last_step': is_last_step,
            'highlight_scroll_target': self.highlight_scroll_target,
            'js_function': self.js_function,
            'test_db': self.test_db
        }


class GettingFamiliarStep(TutorialStep):
    def __init__(self, scroll_target, tooltip_content, page_url=None, **kwargs):
        super().__init__(
            page_url=page_url,
            scroll_target=scroll_target,
            tooltip_content=tooltip_content,
            section='Getting Familiar',
            **kwargs
        )


class AddingRecipesBasicsStep(TutorialStep):
    def __init__(self, scroll_target, tooltip_content, page_url='add_recipe', **kwargs):
        super().__init__(
            page_url=page_url,
            scroll_target=scroll_target,
            tooltip_content=tooltip_content,
            section='Adding Recipes',
            subsection='Basics',
            **kwargs
        )


class AddingRecipesTagsAndLinkedRecipesStep(TutorialStep):
    def __init__(self, scroll_target, tooltip_content, page_url='add_recipe', **kwargs):
        super().__init__(
            page_url=page_url,
            scroll_target=scroll_target,
            tooltip_content=tooltip_content,
            section='Adding Recipes',
            subsection='Tags and Linked Recipes',
            **kwargs
        )


class AddingRecipesIngredientsStep(TutorialStep):
    def __init__(self, scroll_target, tooltip_content, page_url='add_recipe', **kwargs):
        super().__init__(
            page_url=page_url,
            scroll_target=scroll_target,
            tooltip_content=tooltip_content,
            section='Adding Recipes',
            subsection='Ingredients',
            **kwargs
        )


class AddingRecipesStepsAndTimingAttributesStep(TutorialStep):
    def __init__(self, scroll_target, tooltip_content, page_url='add_recipe', **kwargs):
        super().__init__(
            page_url=page_url,
            scroll_target=scroll_target,
            tooltip_content=tooltip_content,
            section='Adding Recipes',
            subsection='Steps and Timing Attributes',
            **kwargs
        )


class RecipePageStep(TutorialStep):
    def __init__(self, scroll_target, tooltip_content, page_url='recipe_detail', test_db=True, page_kwargs={'key': 'pesto-sauce'}, **kwargs):
        super().__init__(
            page_url=page_url,
            scroll_target=scroll_target,
            tooltip_content=tooltip_content,
            section='Recipe Page',
            test_db=test_db,
            page_kwargs=page_kwargs,
            **kwargs
        )


class SearchStep(TutorialStep):
    def __init__(self, scroll_target, tooltip_content, page_url='search', **kwargs):
        super().__init__(
            page_url=page_url,
            scroll_target=scroll_target,
            tooltip_content=tooltip_content,
            section='Searching Your Recipes',
            **kwargs
        )


class FoodManagerStep(TutorialStep):
    def __init__(self, scroll_target, tooltip_content, page_url='manage_food', **kwargs):
        super().__init__(
            page_url=page_url,
            scroll_target=scroll_target,
            tooltip_content=tooltip_content,
            section='Food Manager',
            **kwargs
        )


TUTORIAL_STEPS = [
    # Getting Familiar section
    GettingFamiliarStep(
        page_url='index',
        scroll_target='#logo_title',
        tooltip_content='''Welcome to Food DB! This is your personal recipe management system. Let's take a quick tour of the features. This tutorial will show you around. You can exit any time with the red button at the bottom of your screen, and revisit any part of the tutorial from the Help page.''',
    ),
    GettingFamiliarStep(
        page_url='index',
        scroll_target='h1',
        tooltip_content='''If you record your cooked meals, this section will show dashboards with charts and statistics about your cooking patterns. The best way to get interesting data here is to record every cooked meal and to use lots of tags on your recipes!''',
    ),
    GettingFamiliarStep(
        page_url='add_recipe',
        scroll_target='h1',
        tooltip_content='''This is where you add new recipes. We'll come back here to explore all the features later in the tutorial.''',
    ),
    GettingFamiliarStep(
        page_url='add_recipe',
        scroll_target='#baking_switch_label',
        tooltip_content='''You have two sides to your Food DB: Cooking and Baking. Use this toggle to determine which side each recipe is stored in.''',
        highlight_scroll_target=True,
    ),
    GettingFamiliarStep(
        page_url='search',
        scroll_target='h1',
        tooltip_content='''Search and filter your recipes. Use tags, text search, and other filters to find exactly what you're looking for.''',
    ),
    GettingFamiliarStep(
        page_url='search',
        scroll_target='#baking_switch_label',
        tooltip_content='''Like on the add recipe page, this toggle sets you into Cooking or Baking "mode". On this page, it determines which side of your database you are searching in.''',
        highlight_scroll_target=True,
    ),
    GettingFamiliarStep(
        page_url='manage_food',
        scroll_target='h1',
        tooltip_content='''This is where you manage the list of all the foods you use as ingredients. You can edit foods, categorize them, and merge them with each other. You only need to use this page if you really like having an organized grocery list 😛''',
    ),
    GettingFamiliarStep(
        page_url='bulk_prep',
        scroll_target='h1',
        tooltip_content='''This is where you can plan a feast! You can add recipes to your cart and see how they compare to each other. You can also create view configurations to customize the columns you see in the table.''',
    ),
    GettingFamiliarStep(
        page_url='help',
        scroll_target='h1',
        tooltip_content='''The help page lets you revisit any step in this tutorial and includes detailed guides about specific features of Food DB.''',
    ),
    # Adding Recipes: Basics section
    AddingRecipesBasicsStep(
        scroll_target='h1',
        tooltip_content='''Alright, let's dig into how to add a recipe. There is a lot here!''',
    ),
    AddingRecipesBasicsStep(
        scroll_target='#baking_switch_label',
        tooltip_content='''The first choice you make is: is this a Cooking or a Baking recipe? Press this toggle when adding/editing a recipe to change where it is stored in the database. Changing to Cooking or Baking also exposes the tags you've deemed relevant to either Cooking or Baking, and Baking recipes also have additional attributes available to them.''',
        highlight_scroll_target=True,
    ),
    AddingRecipesBasicsStep(
        scroll_target='.recipe_summary_label',
        tooltip_content='''Most of the fields here are pretty self-explanatory. They're almost all optional, except the title, obviously.''',
    ),
    AddingRecipesBasicsStep(
        scroll_target='#is_component_recipe_row', 
        tooltip_content='''This "reusable component" attribute is for when you've got recipes for, well, components. Sauces, doughs, icings, etc. The only functional thing this attribute does is that it allows you to filter components out (or filter to <i>only</i> components) when searching.''',
        highlight_scroll_target=True,
    ),
    AddingRecipesBasicsStep(
        scroll_target='#recipe_url_row',
        tooltip_content='''I like to include the URL of the source of the recipe, in case I make a mistake in transcribing it. It's always nice to have the original to look back at! This otherwise doesn't do anything for you - it's just for reference.''',
        highlight_scroll_target=True,
    ),
    # Adding Recipes: Tags and Linked Recipes section
    AddingRecipesTagsAndLinkedRecipesStep(
        scroll_target='#id_tags-label', 
        tooltip_content='''Tagging your recipes is one of the most powerful capabilities of the Food DB! I highly recommend you take the time to come up with a large handful of tags. Recipes can have multiple tags, and the search capabilties on the Recipes page allow you to include and/or exclude tags from your search. The more tags you create and use, the more accurately you can find the <i>exact</i> meal you're craving!''',
    ),
    AddingRecipesTagsAndLinkedRecipesStep(
        scroll_target='#add_tag_button_div',
        tooltip_content='''This is where you can create a new tag. In addition to the tag name, you can customize the appearance of the tag. A distinct appearance might help you spot a tag quickly when your eyes scan the Recipes search results.''',
        highlight_scroll_target=True,
    ),
    AddingRecipesTagsAndLinkedRecipesStep(
        scroll_target='#linked_recipes_header', 
        tooltip_content='''You can link recipes to each other to form two types of relationships. An example Full/Component relationship is cake: the cake is the Full recipe, and the icing and the sponge are Component recipes. An example Base/Variant relationship would be pizza: the Base recipe makes a cheese pizza, and each Variant is a pizza with some combination of toppings. Variant recipes include all the ingredients/steps of their Base recipes; similarly Full recipes include everything from their Components.''',
    ),
    AddingRecipesTagsAndLinkedRecipesStep(
        scroll_target='#linked_recipes_help_icon', 
        tooltip_content='''You can hover over this help icon any time to learn more about Linked Recipes.''',
        highlight_scroll_target=True,
    ),
    # Adding Recipes: Ingredients section
    AddingRecipesIngredientsStep(
        scroll_target='#ingreds_header', 
        tooltip_content='''Here's where you'll add the ingredients for your recipe. Note that recipes don't require ingredients - sometimes a recipe is just a book name and page number.''',
    ),
    AddingRecipesIngredientsStep(
        scroll_target='.ingred_body_quantity', 
        tooltip_content='''You can add your ingredients one by one in this table. Every field is optional except Food.''',
    ),
    AddingRecipesIngredientsStep(
        scroll_target='.ingred_body_ingredient_category', 
        tooltip_content='''Ingredient categories can be used to group ingredients together when you view the recipe later.''',
    ),
    AddingRecipesIngredientsStep(
        scroll_target='.ingred_body_ingredient_category',
        tooltip_content='''When your typing cursor is in any of the text boxes for an ingredient, you can press Ctrl+Alt+C to copy the Category of that ingredient's row to the row below it.''',
    ),
    AddingRecipesIngredientsStep(
        scroll_target='.delete_ingred_button', 
        tooltip_content='''You can delete any ingredient by pressing the red X in its row.''',
        highlight_scroll_target=True,
    ),
    AddingRecipesIngredientsStep(
        scroll_target='#show_ingred_parse_button',
        tooltip_content='''There is a faster way to add ingredients! Click this "Parse ingredients from text" button to reveal a large text box.''',
        highlight_scroll_target=True,
    ),
    AddingRecipesIngredientsStep(
        scroll_target='#ingred-parser-textbox',
        tooltip_content='''You can enter ingredients in this text box in plain English, one ingredient per line, and then click the Parse Ingredients button below. This will switch you back to the table view and populate the table's fields for you.''',
        js_function='showIngredientParserOnClick'
    ),
    # Adding Recipes: Steps and Timing Attributes section
    AddingRecipesStepsAndTimingAttributesStep(
        scroll_target='#recipe_steps_header',
        tooltip_content='''This is where you enter the steps you must follow for your recipe. There are several neat features here!''',
        js_function='hideIngredientParserOnClick'
    ),
    AddingRecipesStepsAndTimingAttributesStep(
        scroll_target='#id_step_0_description',
        tooltip_content='''You enter each step in a box like this, and you can use the buttons below to add and remove boxes for more steps. You can use <a href="https://www.markdownguide.org/cheat-sheet/">Markdown syntax</a> inside these boxes to add some formatting to your steps.''',
        skip_css_target_validation=True,
    ),
    AddingRecipesStepsAndTimingAttributesStep(
        scroll_target='.parse_step_button',
        tooltip_content='''You can write or paste multiple steps in this one box. Separate steps with line breaks (you can include numbers at the front of each step or not, doesn't matter) and then press this ellipses button. The text you entered will be magically split into multiple step boxes.''',
        highlight_scroll_target=True,
    ),
    AddingRecipesStepsAndTimingAttributesStep(
        scroll_target='#markdown_help_icon',
        tooltip_content='''You can hover over this help icon any time to learn more about the syntax used to write recipe steps. In addition to Markdown, there are special rules for linking ingredients to steps. This has several benefits which you can read about on the Help page.''',
        highlight_scroll_target=True,
    ),
    AddingRecipesStepsAndTimingAttributesStep(
        scroll_target='#timing_header',
        tooltip_content='''Many recipes, especially in baking, have stages where you wait a long time. This might be proving, baking, simmering, etc. These attributes record the times of these stages and display them at the top of the recipe. In addition to being a helpful quick reference, these times are very handy on the Bulk Prep page, where you can plan how you will cook/bake a feast with many different recipes.''',
    ),
    AddingRecipesStepsAndTimingAttributesStep(
        scroll_target='#submit_recipe_button',
        tooltip_content='''All done! Save your recipe by clicking here!''',
    ),
    # Recipe Page section
    RecipePageStep(
        scroll_target='h1',
        tooltip_content='''This is the page you'll see when viewing a recipe. I've pulled up a fake recipe for us to walk through.''',
    ),
    RecipePageStep(
        scroll_target='#edit_recipe_button',
        tooltip_content='''Clicking this button will open up the recipe add/edit form, pre-populated with all the values from this recipe.''',
        highlight_scroll_target=True,
    ),
    RecipePageStep(
        scroll_target='#share_button_link',
        tooltip_content='''If you have cloud backups enabled, this share button is a link to your publicly accessible backup of this recipe. The publicly accessible versions of recipes are stripped down significnatly in terms of how flashy the page is, but you can share them with your friends and view them from anywhere!<br><br>If you don't have cloud backups enabled, this is just a link to the page we are currently on.''',
        highlight_scroll_target=True,
    ),
    RecipePageStep(
        scroll_target='#recipe_detail_add_to_cart_icon',
        tooltip_content='''Use this button to add this recipe to your cart. The cart is used to populate the Bulk Prep page. You can read more about the Bulk Prep page on the Help page.''',
        highlight_scroll_target=True,
    ),
    RecipePageStep(
        scroll_target='#delete_recipe_button',
        tooltip_content='''You can delete recipes with this button. Careful, once they're gone, they're gone!''',
        highlight_scroll_target=True,
    ),
    RecipePageStep(
        scroll_target='#create_variant_button_link',
        tooltip_content='''Create a Variant of this recipe with this button. This will take you to the Add Recipe page for a blank recipe, except that a link to this recipe as the Base will already be set. You can read more about Bases and Variants on the Help page.''',
        highlight_scroll_target=True,
    ),
    RecipePageStep(
        scroll_target='#upvote_button_div',
        tooltip_content='''Click this button when you cook a meal. It'll record that you cooked the recipe on today's date, which then is shown on the Recipes search page and the graphs on the Home page.''',
        highlight_scroll_target=True,
    ),
    RecipePageStep(
        scroll_target='#ingredient_multiplier',
        tooltip_content='''Need to double the recipe? Or 3.5x it? Enter a value (increments of 0.5) here and the quantities of ingredients (including in your grocery list) will update accordingly.''',
        highlight_scroll_target=True,
    ),
    RecipePageStep(
        page_kwargs={'key': 'penne-with-pesto-and-chicken'},
        scroll_target='summary',
        tooltip_content='''Now we've loaded up a different recipe. This recipe has a link established: the Pesto Sauce recipe is a Component and the Penne/Chicken recipe is the Full recipe. You can see here how the steps and ingredients for linked Component recipes are displayed alongside steps/ingredients that are unique to the Full recipe.''',
        highlight_scroll_target=True,
    ),
    RecipePageStep(
        page_kwargs={'key': 'penne-with-pesto-and-chicken'},
        scroll_target='.ingredient_link',
        tooltip_content='''See how this is underlined? Try hovering over it. You can link your steps back to your ingredients, which does two things (and you can read more about this on the Help page). The first thing is this hover ability - you can see the quantity and any notes associated with an ingredient at a glance while cooking without needing to scroll back up. The other benefit is, when you're in Cooking Mode, you can check this step off and it will check the linked ingredients off as well. What's Cooking Mode, you ask...?''',
        highlight_scroll_target=True,
        skip_css_target_validation=True,
    ),
    RecipePageStep(
        page_kwargs={'key': 'penne-with-pesto-and-chicken'},
        scroll_target='#cooking_mode_title',
        tooltip_content='''You can enter Cooking Mode by clicking this button at any time.''',
    ),
    RecipePageStep(
        page_kwargs={'key': 'penne-with-pesto-and-chicken'},
        scroll_target='#cooking_mode_title',
        tooltip_content='''Now we're in Cooking Mode. This same button will let you exit Cooking Mode. In Cooking Mode, you're not making any changes to your database or anything permanent like that - you just are given the ability to check off steps and ingredients as you cook to help you see what's done and what's left.''',
        js_function='enterCookingMode',
    ),
    SearchStep(
        scroll_target='h1',
        tooltip_content='''This page is (probably) the reason you got the Food DB! Here you can browse and search your recipe collection in a number of different ways.''',
    ),
    SearchStep(
        scroll_target='#search_form',
        tooltip_content='''These first few filters are pretty straightforward: you can search by recipe title or by the names of any ingredients (you can only search for a single ingredient name, so "all purpose flour" is fine but "flour sugar butter" won't work). Use the duration filter to remove results with long (or unspecified) duration.''',
    ),
    SearchStep(
        scroll_target='#id_is_component_recipe',
        tooltip_content='''Filter to only full recipes or only components here. Keep in mind this attribute is determined <i>not</i> by a Linked Recipe relationship, but by the checkbox at the top of the recipe add/edit form that asks if this recipe is a component.''',
        skip_css_target_validation=True,
    ),
    SearchStep(
        scroll_target='#search_tag_filter_table',
        tooltip_content='''Here you can include and exclude tags from your search. The <b>"tagged with" search is an AND search</b>. If you select two tags, you will <b>only see recipes that have both</b>.<br><br>The <b>"not tagged with" section is an OR search</b>. If you select two tags, <b>recipes that have either tag will be exlucded</b> from results.''',
    ),
    SearchStep(
        scroll_target='#search_results_table',
        tooltip_content='''Your search reults show up here. You can click any of the column titles to sort the results by that column. Click the title again to change between Ascending/Descending. You can also add any search result to your Bulk Prep cart by clicking the cart icon on the far right (read more about Bulk Prep on the Help page).''',
    ),
    FoodManagerStep(
        scroll_target='h1',
        tooltip_content='''This is where you can categorize and edit all the foods you've ever used, or might use, for ingredients. The only purpose of doing this is so you can generate a nice clean grocery list from your recipe (or, if doing Bulk Prep, your recipe<b>s</b>). If you automatic grocery list generation doesn't interest you, you can skip right on past this page!''',
    ),
]

# Assign order numbers based on position in list
for order, step in enumerate(TUTORIAL_STEPS, start=1):
    step.order = order


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

