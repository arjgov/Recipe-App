from celery import shared_task
from django.core.mail import send_mail
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import Recipe, RecipeLike

@shared_task
def send_daily_like_notifications():
    yesterday = timezone.now() - timedelta(days=1)
    
    # Get recipes that received likes in the last 24 hours
    liked_recipes = Recipe.objects.filter(
        recipelike__created__gte=yesterday
    ).annotate(
        like_count=Count('recipelike')
    ).filter(like_count__gt=0)

    for recipe in liked_recipes:
        subject = f"Daily Like Update for '{recipe.title}'"
        message = f"Your recipe '{recipe.title}' received {recipe.like_count} new like(s) in the last 24 hours."
        send_mail(
            subject,
            message,
            'noreply@recipeapp.com',
            [recipe.author.email],
            fail_silently=False,
        )

    return f"Sent notifications for {liked_recipes.count()} recipes"
