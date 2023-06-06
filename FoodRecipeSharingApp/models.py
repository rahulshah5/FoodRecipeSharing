from django.db import models

from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)


class Ingredient(models.Model):
    name = models.CharField(max_length=100)


class Recipe(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField('Ingredient')
    instructions = models.ManyToManyField('RecipeStep')
    cooking_time = models.PositiveIntegerField()
    difficulty_level = models.CharField(max_length=100)
    tags = models.ManyToManyField('Tag')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.PositiveIntegerField(default=0)




class RecipeStep(models.Model):
    recipe_name = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    step_number = models.IntegerField()
    description = models.TextField()
    time_in_minutes = models.PositiveIntegerField()



class Tag(models.Model):
    name = models.CharField(max_length=100)



class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=2)


class Review(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()



class Favourite(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='recipe_images/')


