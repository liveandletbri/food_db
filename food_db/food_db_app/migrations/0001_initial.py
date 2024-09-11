# Generated by Django 5.1 on 2024-09-11 15:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('qfc_aisle', models.CharField(blank=True, max_length=255)),
                ('_date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('url', models.TextField(blank=True)),
                ('recipe_book_page', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('duration_minutes', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('servings_min', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('servings_max', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('calories_per_serving', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('_date_created', models.DateTimeField(auto_now_add=True)),
                ('_date_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='RecipeBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('author', models.CharField(blank=True, max_length=255)),
                ('_date_created', models.DateTimeField(auto_now_add=True)),
                ('_date_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('_date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UnitOfMeasurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('_date_created', models.DateTimeField(auto_now_add=True)),
                ('_date_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CookedMeal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_cooked', models.DateField(auto_now=True)),
                ('_date_created', models.DateField(auto_now_add=True)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='food_db_app.recipe')),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='recipe_book',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='food_db_app.recipebook'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='recipes', to='food_db_app.tag'),
        ),
        migrations.CreateModel(
            name='RecipeStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.PositiveSmallIntegerField()),
                ('description', models.TextField()),
                ('_date_created', models.DateTimeField(auto_now_add=True)),
                ('_date_modified', models.DateTimeField(auto_now=True)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='food_db_app.recipe')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('recipe', 'order_number'), name='unique_recipe_step_order_number')],
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField()),
                ('ingredient_category', models.CharField(blank=True, max_length=255)),
                ('notes', models.TextField(blank=True)),
                ('_date_created', models.DateTimeField(auto_now_add=True)),
                ('_date_modified', models.DateTimeField(auto_now=True)),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='food_db_app.food')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='food_db_app.recipe')),
                ('unit_of_measurement', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='food_db_app.unitofmeasurement')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('recipe', 'food', 'ingredient_category'), name='unique_recipe_food_category')],
            },
        ),
    ]
