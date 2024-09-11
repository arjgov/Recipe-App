import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from recipe.models import Recipe, RecipeCategory
from users.models import CustomUser

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return CustomUser.objects.create_user(username='testuser', password='testpass', email='testuser@example.com')

@pytest.fixture
def recipe_category():
    return RecipeCategory.objects.create(name='Test Category')

@pytest.fixture
def recipe(user, recipe_category):
    return Recipe.objects.create(
        author=user,  # Ensure this is an instance of CustomUser
        category=recipe_category,  # Use the recipe_category fixture
        picture='path/to/image.jpg',  # Mock or placeholder image path
        title='Test Recipe',
        desc='Short description of the recipe',
        cook_time='01:00:00',  # Example cook time (1 hour)
        ingredients='Ingredient 1, Ingredient 2',
        procedure='Step 1, Step 2'
    )
# Test for user registration
@pytest.mark.django_db
def test_create_user(api_client):
    url = reverse('users:create-user')
    data = {
        'username': 'newuser',
        'password': 'newpassword',
        'email': 'newuser@example.com'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert CustomUser.objects.count() == 1
    assert CustomUser.objects.get().username == 'newuser'

@pytest.mark.django_db
def test_create_user_with_existing_username(api_client, user):
    url = reverse('users:create-user')
    data = {
        'username': 'testuser',  # Existing username
        'password': 'newpassword',
        'email': 'newuser@example.com'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in response.data

# Test for user login
@pytest.mark.django_db
def test_login_user(api_client, user):
    url = reverse('users:login-user')
    data = {
        'email': 'testuser@example.com',
        'password': 'testpass'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_login_user_with_invalid_credentials(api_client):
    url = reverse('users:login-user')
    data = {
        'email': 'invaliduser@example.com',
        'password': 'wrongpassword'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# Test for token refresh
@pytest.mark.django_db
def test_token_refresh(api_client, user):
    # First, log in to get the refresh token
    login_url = reverse('users:login-user')
    login_data = {
        'email': 'testuser@example.com',  # Use the email of the created user
        'password': 'testpass'             # Ensure this matches the created user's password
    }
    login_response = api_client.post(login_url, login_data)
    assert login_response.status_code == status.HTTP_200_OK

    # Extract the refresh token from the login response
    refresh_token = login_response.data['tokens']['refresh']  # Access the refresh token

    # Now test the token refresh
    url = reverse('users:token-refresh')
    response = api_client.post(url, {'refresh': refresh_token})
    assert response.status_code == status.HTTP_200_OK  # Expecting a successful refresh

# Test for user logout
@pytest.mark.django_db
def test_logout_user(api_client, user):
    # First, log in to get the refresh token
    login_url = reverse('users:login-user')
    login_data = {
        'email': 'testuser@example.com',  # Use the email of the created user
        'password': 'testpass'             # Ensure this matches the created user's password
    }
    login_response = api_client.post(login_url, login_data)
    assert login_response.status_code == status.HTTP_200_OK

    # Extract the refresh token from the login response
    refresh_token = login_response.data['tokens']['refresh']  # Access the refresh token
    access_token = login_response.data['tokens']['access'] 

    # Now test the logout
    url = reverse('users:logout-user')
    
    # Authenticate the user using the refresh token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)  # Set the authorization header

    response = api_client.post(url, {'refresh': refresh_token})  # Include the refresh token in the body
    assert response.status_code == status.HTTP_205_RESET_CONTENT

# Test for user info
@pytest.mark.django_db
def test_user_info(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse('users:user-info')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == user.username

# Test for user profile
@pytest.mark.django_db
def test_user_profile(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse('users:user-profile')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"bookmarks":[],"bio":""}

@pytest.mark.django_db
def test_user_profile_unauthenticated(api_client):
    url = reverse('users:user-profile')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Test for user avatar
@pytest.mark.django_db
def test_user_avatar(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse('users:user-avatar')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_user_avatar_unauthenticated(api_client):
    url = reverse('users:user-avatar')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Test for user bookmarks
@pytest.mark.django_db
def test_user_bookmarks(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse('users:user-bookmark', kwargs={'pk': user.pk})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_user_bookmarks_unauthenticated(api_client, user):
    url = reverse('users:user-bookmark', kwargs={'pk': user.pk})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_add_bookmark(api_client, user, recipe):
    api_client.force_authenticate(user=user)
    url = reverse('users:user-bookmark', kwargs={'pk': user.pk})
    response = api_client.post(url, {'id': recipe.id})
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_delete_bookmark(api_client, user, recipe):
    api_client.force_authenticate(user=user)
    url = reverse('users:user-bookmark', kwargs={'pk': user.pk})
    api_client.post(url, {'id': recipe.id})  # First, add the bookmark
    response = api_client.delete(url, {'id': recipe.id})  # Now delete it
    assert response.status_code == status.HTTP_200_OK


# Test for changing password
@pytest.mark.django_db
def test_change_password(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse('users:change-password')
    data = {
        'old_password': 'testpass',  # Current password
        'new_password': 'testpass123'  # New password
    }
    response = api_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_change_password_incorrect_old_password(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse('users:change-password')
    data = {
        'old_password': 'wrongpassword',  # Incorrect old password
        'new_password': 'testpass123'
    }
    response = api_client.patch(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST