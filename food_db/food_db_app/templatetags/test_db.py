from django import template
from django.urls import reverse
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

register = template.Library()

@register.filter
def add_test_db(url, test_db):
    """
    Append ?test_db=true to a URL if test_db is True.
    If the URL already has query parameters, append to them.
    Usage: {{ url_string|add_test_db:test_db }}
    """
    if not test_db:
        return url
    
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    query_params['test_db'] = ['true']
    
    # Reconstruct the query string
    new_query = urlencode(query_params, doseq=True)
    
    # Reconstruct the URL
    new_parsed = parsed._replace(query=new_query)
    return urlunparse(new_parsed)

@register.simple_tag
def url_with_test_db(view_name, test_db=False, key=None):
    """
    Generate a URL using reverse() and append ?test_db=true if test_db is True.
    Usage: {% url_with_test_db 'view_name' test_db=test_db %}
    Or: {% url_with_test_db 'recipe_detail' test_db=test_db key=recipe.clean_key %}
    """
    if key:
        url = reverse(view_name, kwargs={'key': key})
    else:
        url = reverse(view_name)
    
    if test_db:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params['test_db'] = ['true']
        new_query = urlencode(query_params, doseq=True)
        new_parsed = parsed._replace(query=new_query)
        return urlunparse(new_parsed)
    
    return url

