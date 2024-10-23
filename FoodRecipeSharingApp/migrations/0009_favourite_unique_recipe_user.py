# Generated by Django 4.2.1 on 2023-11-28 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodRecipeSharingApp', '0008_alter_recipestep_step_number'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='favourite',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='unique_recipe_user'),
        ),
    ]