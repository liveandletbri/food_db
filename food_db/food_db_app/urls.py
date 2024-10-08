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
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_recipe, name='add_recipe'),
    path('cook/', views.cook_meal, name='cook_meal'),
    path('ingred_parse', views.ingredient_parse_api, name='ingred_parse'),
    path('recipe/<str:key>', views.recipe_detail, name='recipe_detail'),
    path('recipe/<str:key>/edit', views.edit_recipe, name='edit_recipe'),
    path('search/', views.search, name='search'),
    path('favicon.ico', RedirectView.as_view(url='/static/img/favicon.png')),
]
