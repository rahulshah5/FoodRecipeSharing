import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .models import *

def get_user_ratings(user):
    return Rating.objects.filter(user=user).select_related('recipe')

def get_user_favorites(user):
    return Favourite.objects.filter(user=user).select_related('recipe')


def generate_ratings_matrix(users, recipes):
    num_users = len(users)
    num_recipes = len(recipes)
    ratings_matrix = np.full((num_users, num_recipes), -1)

    user_id_map = {user.id: index for index, user in enumerate(users)}
    recipe_id_map = {recipe.id: index for index, recipe in enumerate(recipes)}

    for user in users:
        user_ratings = get_user_ratings(user)
        user_favorites = get_user_favorites(user)

        for rating in user_ratings:
            recipe_index = recipe_id_map.get(rating.recipe.id)
            if recipe_index is not None:
                ratings_matrix[user_id_map[user.id], recipe_index] = rating.rating

        for favorite in user_favorites:
            recipe_index = recipe_id_map.get(favorite.recipe.id)
            if recipe_index is not None:
                ratings_matrix[user_id_map[user.id], recipe_index] = 1  

    return ratings_matrix

def recommend_recipes(user_id, users, recipes, num_recommendations=4):
    user_index = user_id - 1 
    ratings_matrix = generate_ratings_matrix(users, recipes)
    user_similarity = cosine_similarity(ratings_matrix)

    num_users = len(users)
    if user_index >= num_users:
        return []

    similar_users = np.argsort(user_similarity[user_index])[::-1][1:]
    num_similar_users = len(similar_users)
    if num_similar_users == 0:
        return []

    user_favorites = get_user_favorites(users[user_index])
    unrated_recipes = [recipe for recipe in recipes if recipe not in [fav.recipe for fav in user_favorites]]

    recipes_list = list(recipes)  
    recommendations = []
    for recipe in unrated_recipes:
        recipe_index = recipes_list.index(recipe)
        similar_ratings = [ratings_matrix[similar_user][recipe_index] for similar_user in similar_users if similar_user < num_users]
        rated_similar_ratings = [rating for rating in similar_ratings if rating != -1]
        if rated_similar_ratings:
            avg_rating = np.mean(rated_similar_ratings)
            recommendations.append((recipe, avg_rating))

    recommendations.sort(key=lambda x: x[1], reverse=True)
    return [recipe for recipe, _ in recommendations[:num_recommendations]]

def get_recommended_recipes(user_id):
    users = User.objects.all()
    recipes = Recipe.objects.all()
    recommended_recipes = recommend_recipes(user_id, users, recipes)
    for recipe in recommended_recipes:
        print(f"- {recipe.title}")

    return recommended_recipes