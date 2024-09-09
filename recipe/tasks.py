import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.contrib.auth import get_user_model
from .models import Recipe, RecipeLike
from .emails import send_like_notification

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task
def process_email_queue(user_id, like_info):
    user = User.objects.get(id=user_id)
    send_like_notification(user.email, like_info)

@shared_task
def send_daily_like_notifications():
    logger.info("Starting send_daily_like_notifications task")
    last_24_hours = timezone.now() - timedelta(hours=24)
    
    liked_recipes = Recipe.objects.filter(
        recipelike__created__gte=last_24_hours
    ).values('author', 'title').annotate(like_count=Count('recipelike'))
    
    author_likes = {}
    for recipe in liked_recipes:
        author_id = recipe['author']
        if author_id not in author_likes:
            author_likes[author_id] = {}
        author_likes[author_id][recipe['title']] = recipe['like_count']
    
    for author_id, like_info in author_likes.items():
        user = User.objects.get(id=author_id)
        logger.info(f"Sending notification to {user.email}")
        send_like_notification(user.email, like_info)

    result = f"Sent notifications for {len(author_likes)} authors"
    logger.info(result)
    return result
