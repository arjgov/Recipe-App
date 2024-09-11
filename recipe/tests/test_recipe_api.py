import os
import shutil
import pytest
import tempfile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from recipe.models import Recipe, RecipeCategory
from users.models import CustomUser
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return CustomUser.objects.create_user(username='testuser', password='testpass', email='testuser@example.com')

@pytest.fixture
def recipe_category():
    return RecipeCategory.objects.create(name='Test Category')

@pytest.fixture(autouse=True)
def cleanup_images():
    yield  # Run the test
    # Clean up code after the test
    if os.path.exists('uploads'):
        shutil.rmtree('uploads')

@pytest.fixture
def recipe(user, recipe_category):
    return Recipe.objects.create(
        author=user,
        category=recipe_category,
        picture='path/to/image.jpg',  # Mock or placeholder image path
        title='Test Recipe',
        desc='Short description of the recipe',
        cook_time='01:00:00',
        ingredients='Ingredient 1, Ingredient 2',
        procedure='Step 1, Step 2'
    )

# Test for listing recipes
@pytest.mark.django_db
def test_list_recipes(api_client, recipe, user):
    api_client.force_authenticate(user=user)
    url = reverse('recipe:recipe-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0  # Ensure at least one recipe is returned

# Test for creating a recipe
@pytest.mark.django_db
def test_create_recipe(api_client, user, recipe_category):
    api_client.force_authenticate(user=user)
    url = reverse('recipe:recipe-create')

    # Create a valid image file in memory
    image = Image.new('RGB', (100, 100), color='red')  # Create a simple red image
    image_file = BytesIO()
    image.save(image_file, format='JPEG')  # Save the image to the BytesIO object
    image_file.seek(0)  # Move to the beginning of the BytesIO object

    # Create a SimpleUploadedFile using the valid image
    picture = SimpleUploadedFile("test_image.jpg", image_file.read(), content_type="image/jpeg")


    data = {
        'author': user.id,
        'category.name':"Test Category",  # Use the category ID directly
        'picture': picture,  # Use the uploaded file
        'title': 'New Recipe',
        'desc': 'Description of new recipe',
        'cook_time': '00:30:00',
        'ingredients': 'Ingredient A, Ingredient B',
        'procedure': 'Step A, Step B'
    }
    
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_create_recipe_unauthenticated(api_client, recipe_category):
    url = reverse('recipe:recipe-create')
    data = {
        'category.name':"Test Category",
        'title': 'New Recipe',
        'desc': 'Description of new recipe',
        'cook_time': '00:30:00',
        'ingredients': 'Ingredient A, Ingredient B',
        'procedure': 'Step A, Step B'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Test for retrieving a specific recipe
@pytest.mark.django_db
def test_retrieve_recipe(api_client, recipe, user):
    api_client.force_authenticate(user=user)
    url = reverse('recipe:recipe-detail', kwargs={'pk': recipe.pk})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == recipe.title

@pytest.mark.django_db
def test_retrieve_nonexistent_recipe(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse('recipe:recipe-detail', kwargs={'pk': 999})  # Assuming 999 does not exist
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test for updating a recipe
@pytest.mark.django_db
def test_update_recipe(api_client, recipe, user):
    api_client.force_authenticate(user=user)
    url = reverse('recipe:recipe-detail', kwargs={'pk': recipe.pk})

    # Create a valid image file in memory for the update
    image = Image.new('RGB', (100, 100), color='red')  # Create a simple red image
    image_file = BytesIO()
    image.save(image_file, format='JPEG')  # Save the image to the BytesIO object
    image_file.seek(0)  # Move to the beginning of the BytesIO object

    # Create a SimpleUploadedFile using the valid image
    picture = SimpleUploadedFile("updated_image.jpg", image_file.read(), content_type="image/jpeg")

    data = {
        'category.name':"Test Category" ,
        'title': 'Updated Recipe Title',
        'picture':picture,
        'desc': 'Updated description',
        'cook_time': '01:00:00',
        'ingredients': 'Updated Ingredient 1, Updated Ingredient 2',
        'procedure': 'Updated Step 1, Step 2',
        'picture': picture  # Include the picture field
    }
    
    response = api_client.put(url, data)
    assert response.status_code == status.HTTP_200_OK
    recipe.refresh_from_db()
    assert recipe.title == 'Updated Recipe Title'

@pytest.mark.django_db
def test_update_nonexistent_recipe(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse('recipe:recipe-detail', kwargs={'pk': 999})  # Assuming 999 does not exist
    data = {
        'title': 'Updated Recipe Title',
        'desc': 'Updated description',
        'cook_time': '01:00:00',
        'ingredients': 'Updated Ingredient 1, Updated Ingredient 2',
        'procedure': 'Updated Step 1, Updated Step 2'
    }
    response = api_client.put(url, data)
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test for deleting a recipe
@pytest.mark.django_db
def test_delete_recipe(api_client, recipe, user):
    api_client.force_authenticate(user=user)
    url = reverse('recipe:recipe-detail', kwargs={'pk': recipe.pk})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Recipe.objects.count() == 0  # Ensure the recipe is deleted

@pytest.mark.django_db
def test_delete_nonexistent_recipe(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse('recipe:recipe-detail', kwargs={'pk': 999})  # Assuming 999 does not exist
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test for liking a recipe
@pytest.mark.django_db
def test_like_recipe(api_client, recipe, user):
    api_client.force_authenticate(user=user)
    url = reverse('recipe:recipe-like', kwargs={'pk': recipe.pk})
    response = api_client.post(url)
    assert response.status_code == status.HTTP_201_CREATED
    assert recipe.get_total_number_of_likes() == 1  # Assuming the like is counted

@pytest.mark.django_db
def test_like_nonexistent_recipe(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse('recipe:recipe-like', kwargs={'pk': 999})  # Assuming 999 does not exist
    response = api_client.post(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

