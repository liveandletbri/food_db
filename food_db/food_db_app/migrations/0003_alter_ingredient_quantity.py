# Generated by Django 5.1 on 2024-09-13 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_db_app', '0002_remove_ingredient_unique_recipe_food_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]
