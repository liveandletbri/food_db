"""
Validation functions for tutorial steps configuration.

This module provides validation to ensure tutorial steps are correctly configured.
Validation runs on Django startup to catch configuration errors early.
"""

from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch, reverse

from .tutorial_steps import TUTORIAL_STEPS


def validate_tutorial_steps():
    """
    Validate all tutorial steps configuration.
    
    Checks:
    - All steps have required fields (step_id, page_url, scroll_target, tooltip_content)
    - All steps are in sequential order (no gaps, starts at 1)
    - All page_url values are valid Django URL names
    - All step_id values are unique
    
    Raises:
        ImproperlyConfigured: If any validation check fails
    """
    if not TUTORIAL_STEPS:
        raise ImproperlyConfigured('TUTORIAL_STEPS list is empty. At least one tutorial step is required.')
    
    step_ids = set()
    orders = []
    
    for index, step in enumerate(TUTORIAL_STEPS, start=1):
        # Check required fields
        if not step.step_id:
            raise ImproperlyConfigured(f'Tutorial step at index {index} is missing step_id.')
        
        if not step.page_url:
            raise ImproperlyConfigured(f'Tutorial step "{step.step_id}" is missing page_url.')
        
        if not step.scroll_target:
            raise ImproperlyConfigured(f'Tutorial step "{step.step_id}" is missing scroll_target.')
        
        if not step.tooltip_content:
            raise ImproperlyConfigured(f'Tutorial step "{step.step_id}" is missing tooltip_content.')
        
        # Check for unique step_id
        if step.step_id in step_ids:
            raise ImproperlyConfigured(f'Duplicate step_id found: "{step.step_id}". All step_id values must be unique.')
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
                f'Tutorial step "{step.step_id}" has invalid page_url "{step.page_url}". '
                f'URL name not found in URL configuration. Error: {str(e)}'
            )
    
    # Validate sequential order (no gaps, starts at 1)
    if orders:
        expected_order = list(range(1, len(TUTORIAL_STEPS) + 1))
        orders_sorted = sorted(orders)
        if orders_sorted != expected_order:
            raise ImproperlyConfigured(
                f'Tutorial steps have non-sequential order numbers. Expected: {expected_order}, Found: {orders_sorted}. '
                f'Order numbers must be sequential starting from 1 with no gaps.'
            )

