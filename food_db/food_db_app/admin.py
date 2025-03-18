import inspect
from django.contrib import admin
from . import models

# Register your models here.

my_admin_site = admin.site
model_list = inspect.getmembers(models, inspect.isclass)
for model_class in model_list:
    if model_class[0] == 'PathAndRename':  # this class is not a model, but effectively a helper function
        continue
    try:
        my_admin_site.register(model_class[1])
    except Exception as e:
        print(model_class)
        raise e