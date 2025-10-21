"""
URL configuration for food_db project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from . import views
from . import charts

urlpatterns = [
    # pages
    path('', views.index, name='index'),
    path('add/', views.add_recipe, name='add_recipe'),
    path('bulk/', views.bulk_prep, name='bulk_prep'),
    path('food/', views.manage_food, name='manage_food'),
    path('recipe/<str:key>', views.recipe_detail, name='recipe_detail'),
    path('recipe/<str:key>/edit', views.edit_recipe, name='edit_recipe'),
    path('search/', views.search, name='search'),

    # apis
    path('add_recipe_to_cart/', views.add_recipe_to_cart, name='add_recipe_to_cart'),
    path('add_tag/', views.add_tag, name='add_tag'),
    path('cook/', views.cook_meal, name='cook_meal'),
    path('delete_recipe_image/', views.delete_recipe_image, name='delete_recipe_image'),
    path('delete_food_category/', views.delete_food_category, name='delete_food_category'),
    path('delete_food/', views.delete_food, name='delete_food'),
    path('edit_baking_switch_cookie/', views.edit_baking_switch_cookie, name='edit_baking_switch_cookie'),
    path('edit_food_category/', views.edit_food_category, name='edit_food_category'),
    path('edit_food/', views.edit_food, name='edit_food'),
    path('empty_cart/', views.empty_cart, name='empty_cart'),
    path('get_cart_size/', views.get_cart_size, name='get_cart_size'),
    path('get_ingredient_category_order_number/', views.get_ingredient_category_order_number, name='get_ingredient_category_order_number'),
    path('ingred_parse', views.ingredient_parse_api, name='ingred_parse'),
    path('merge_food_categories/', views.merge_food_categories, name='merge_food_categories'),
    path('merge_foods/', views.merge_foods, name='merge_foods'),
    path('remove_recipe_from_cart/', views.remove_recipe_from_cart, name='remove_recipe_from_cart'),
    path('swap_ingredient_category_order_numbers/', views.swap_ingredient_category_order_numbers, name='swap_ingredient_category_order_numbers'),

    # charts - this returns one JSON blob containing the data for every chart
    path('charts/', charts.AllCharts.as_view(), name='charts'),

    # and this stupid thing to stop the console from complaining when every page loads
    path('favicon.ico', RedirectView.as_view(url='/static/img/favicon.png')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
