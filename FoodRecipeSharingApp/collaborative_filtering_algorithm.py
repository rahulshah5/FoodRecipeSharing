from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from FoodRecipeSharingApp.models import Rating,Recipe
def get_recipe_ratings():
    # Fetch all recipes and ratings from the database
    recipes = Recipe.objects.all()
    ratings = Rating.objects.all()

    # Create a matrix to store ratings
    num_recipes = Recipe.objects.count()  # Get the count of recipes
    num_users = Rating.objects.values_list('user_id', flat=True).distinct().count()  # Get the count of distinct users

    # Initialize the matrix with -1 indicating missing ratings
    ratings_matrix = np.full((num_users, num_recipes), -1)

    # Create a dictionary to map recipe IDs to matrix indices
    recipe_id_map = {recipe.id: index for index, recipe in enumerate(recipes)}

    # Fill the matrix with ratings
    for rating in ratings:
        user_index = rating.user_id - 1  # Assuming user_id starts from 1
        recipe_index = recipe_id_map.get(rating.recipe_id)
        if recipe_index is not None and user_index < num_users:
            ratings_matrix[user_index, recipe_index] = rating.rating

    return ratings_matrix


ratings_matrix = get_recipe_ratings()
user_similarity = cosine_similarity(ratings_matrix)

def recommend_recipes(user_id, num_recommendations=5):
    user_ratings = ratings_matrix[user_id - 1]  # Assuming user_id starts from 1
    similar_users = np.argsort(user_similarity[user_id - 1])[::-1][1:]

    unrated_recipes = [i for i, rating in enumerate(user_ratings) if rating == 0]

    recommendations = []
    for recipe_id in unrated_recipes:
        similar_ratings = [ratings_matrix[similar_user][recipe_id] for similar_user in similar_users]
        avg_rating = np.mean(similar_ratings)
        recommendations.append((recipe_id, avg_rating))

    recommendations.sort(key=lambda x: x[1], reverse=True)
    return recommendations[:num_recommendations]
