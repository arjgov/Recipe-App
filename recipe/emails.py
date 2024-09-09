from django.core.mail import send_mail
from django.conf import settings

def send_like_notification(user_email, like_info):
    subject = "Daily Recipe Like Update"
    message = "Here's a summary of likes on your recipes in the last 24 hours:\n\n"
    for recipe_title, like_count in like_info.items():
        message += f"- '{recipe_title}': {like_count} new like(s)\n"
    message += "\nKeep up the great work!"
    
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    
    send_mail(subject, message, from_email, recipient_list)
