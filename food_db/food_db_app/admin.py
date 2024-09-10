import inspect
from django.contrib import admin
from . import models

# Register your models here.

my_admin_site = admin.site
model_list = inspect.getmembers(models, inspect.isclass)
for model_class in model_list:
    try:
        my_admin_site.register(model_class[1])
    except Exception as e:
        print(model_class)
        raise e