"""
Validation functions for tutorial steps configuration.

This module provides validation to ensure tutorial steps are correctly configured.
Validation runs on Django startup to catch configuration errors early.
"""

import re
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch, reverse

from .tutorial_steps import TUTORIAL_STEPS


def _get_template_path(page_url):
    """
    Map page_url to local HTML template file path.
    
    Args:
        page_url (str): Django URL name
        
    Returns:
        str: Template file path relative to templates directory
    """
    url_to_template = {
        'index': 'index.html',
        'search': 'search.html',
        'add_recipe': 'add_edit_recipe.html',
        'help': 'help.html',
        'bulk_prep': 'bulk_prep.html',
        'manage_food': 'manage_food.html',
        'recipe_detail': 'recipe_detail.html',
        'edit_recipe': 'add_edit_recipe.html',
        'recipe_validation': 'recipe_validation.html',
    }
    return url_to_template.get(page_url)


def _read_template_content(template_path):
    """
    Read template file content, including extended/included templates.
    
    Args:
        template_path (str): Path to template file relative to templates directory
        
    Returns:
        str: Combined HTML content from template and its includes
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    templates_dir = base_dir / 'food_db_app' / 'templates'
    
    content_parts = []
    read_files = set()
    
    def read_file_if_not_read(file_path):
        """Read a file if it hasn't been read yet."""
        file_path_str = str(file_path)
        if file_path_str in read_files:
            return
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                content_parts.append(content)
                read_files.add(file_path_str)
                return content
        return None
    
    # Read main template
    template_file = templates_dir / template_path
    template_content = read_file_if_not_read(template_file)
    
    if template_content:
        # Check if template extends main.html
        if '{% extends \'main.html\' %}' in template_content or "{% extends \"main.html\" %}" in template_content:
            main_file = templates_dir / 'main.html'
            main_content = read_file_if_not_read(main_file)
            
            # Check if main.html includes navbar.html
            if main_content and ('{% include \'navbar.html\' %}' in main_content or "{% include \"navbar.html\" %}" in main_content):
                navbar_file = templates_dir / 'navbar.html'
                read_file_if_not_read(navbar_file)
        
        # Check if template directly includes navbar.html
        if '{% include \'navbar.html\' %}' in template_content or "{% include \"navbar.html\" %}" in template_content:
            navbar_file = templates_dir / 'navbar.html'
            read_file_if_not_read(navbar_file)
    
    return '\n'.join(content_parts)


def _css_selector_exists_in_html(selector, html_content):
    """
    Check if a CSS selector exists in HTML content. This is a naive search 
    that does not render the HTML templates or accept CSS parent/child/sibling
    logic.
    
    Handles:
    - ID selectors (#id): checks for id="id" or id='id'
    - Class selectors (.class): checks for class containing the class name
    - Tag selectors (h1, div, etc.): checks for the tag
    
    Args:
        selector (str): CSS selector (e.g., '#logo_title', '.left_side_of_page', 'h1')
        html_content (str): HTML content to search
        
    Returns:
        bool: True if selector exists in HTML, False otherwise
    """
    if selector.startswith('#'):
        # ID selector
        id_name = selector[1:]
        # Look for id="id_name" or id='id_name'
        pattern = rf'\bid=["\']{re.escape(id_name)}["\']'
        return bool(re.search(pattern, html_content))
    elif selector.startswith('.'):
        # Class selector
        class_name = selector[1:]
        # Look for class="...class_name..." or class='...class_name...'
        # Class names can be space-separated, so we need to match word boundaries
        # Match class="class_name", class="... class_name", class="class_name ...", or class="... class_name ..."
        pattern = rf'\bclass=["\']([^"\']*\s+)?{re.escape(class_name)}(\s+[^"\']*)?["\']'
        return bool(re.search(pattern, html_content))
    else:
        # Tag selector
        # Look for <tag or <tag> or <tag 
        pattern = rf'<{re.escape(selector)}\b'
        return bool(re.search(pattern, html_content, re.IGNORECASE))


def validate_tutorial_steps():
    """
    Validate all tutorial steps configuration.
    
    Checks:
    - All steps have required fields (step_id, page_url, scroll_target, tooltip_content)
    - All steps are in sequential order (no gaps, starts at 1)
    - All page_url values are valid Django URL names
    - All step_id values are unique
    - All scroll_target CSS selectors exist in their corresponding HTML templates
    
    Raises:
        ImproperlyConfigured: If any validation check fails
    """
    print('Validating tutorial steps...')
    if not TUTORIAL_STEPS:
        raise ImproperlyConfigured('TUTORIAL_STEPS list is empty. At least one tutorial step is required.')
    
    step_ids = set()
    orders = []
    all_steps = TUTORIAL_STEPS
    
    for index, step in enumerate(all_steps, start=1):
        print(f'Validating step {index}: {step.step_id}')
        # Check required fields
        if not step.step_id:
            raise ImproperlyConfigured(f'Tutorial step at index {index} is missing step_id.')
        
        if not step.page_url:
            raise ImproperlyConfigured(f'Tutorial step "{step.name}" is missing page_url.')
        
        if not step.scroll_target:
            raise ImproperlyConfigured(f'Tutorial step "{step.name}" is missing scroll_target.')
        
        if not step.tooltip_content:
            raise ImproperlyConfigured(f'Tutorial step "{step.name}" is missing tooltip_content.')
        
        # Check for unique step_id
        if step.step_id in step_ids:
            raise ImproperlyConfigured(f'Duplicate step_id found: "{step.name}". All step_id values must be unique.')
        step_ids.add(step.step_id)
        
        # Collect order numbers
        if step.order is not None:
            orders.append(step.order)
        
        # Validate page_url is a valid Django URL name
        try:
            if step.page_kwargs:
                reverse(step.page_url, kwargs=step.page_kwargs)
            else:
                reverse(step.page_url)
        except NoReverseMatch as e:
            raise ImproperlyConfigured(
                f'Tutorial step "{step.name}" has invalid page_url "{step.page_url}". '
                f'URL name not found in URL configuration. Error: {str(e)}'
            )
    
    # Validate sequential order (no gaps, starts at 1)
    if orders:
        expected_order = list(range(1, len(all_steps) + 1))
        orders_sorted = sorted(orders)
        if orders_sorted != expected_order:
            raise ImproperlyConfigured(
                f'Tutorial steps have non-sequential order numbers. Expected: {expected_order}, Found: {orders_sorted}. '
                f'Order numbers must be sequential starting from 1 with no gaps.'
            )
    
    # Validate scroll_target exists in HTML templates
    for step in all_steps:
        # Skip validation if skip_css_target_validation is True
        if step.skip_css_target_validation:
            continue
        
        template_path = _get_template_path(step.page_url)
        if not template_path:
            # Skip validation if we don't have a mapping for this page_url
            continue
        
        html_content = _read_template_content(template_path)
        if not _css_selector_exists_in_html(step.scroll_target, html_content):
            raise ImproperlyConfigured(
                f'Tutorial step "{step.name}" has scroll_target "{step.scroll_target}" that does not exist '
                f'in the HTML template "{template_path}".'
            )

    print('Tutorial steps validated successfully.')