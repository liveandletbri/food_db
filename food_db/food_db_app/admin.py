import inspect
from django.contrib import admin
from django.db.models import Model
from . import models

# Register your models here.

my_admin_site = admin.site
model_list = inspect.getmembers(models, inspect.isclass)
for model_class in model_list:
    # only register Model classes, not other created or imported classes
    class_parents = model_class[1].__bases__
    if Model not in class_parents:
        continue
    try:
        my_admin_site.register(model_class[1])
    except Exception as e:
        print(model_class)
        raise e