"""
This module handles signal-based notifications and permission assignments
for the Django News Publishing application. It includes:

- Assigning appropriate permissions to the Editor group.
- Sending email notifications and optional social media updates
  when an article is approved.
"""

import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

from .models import Article, CustomUser


def assign_editor_permissions():
    """
    Assigns view, change, and delete permissions for both Article and Newsletter
    models to the 'Editor' group. Creates the group if it doesn't exist.
    """
    editor_group, created = Group.objects.get_or_create(name='Editor')

    Article = apps.get_model('newsapp', 'Article')
    Newsletter = apps.get_model('newsapp', 'Newsletter')

    article_ct = ContentType.objects.get_for_model(Article)
    newsletter_ct = ContentType.objects.get_for_model(Newsletter)

    # Permissions for Article
    article_perms = Permission.objects.filter(
        content_type=article_ct,
        codename__in=['view_article', 'change_article', 'delete_article']
    )
    # Permissions for Newsletter
    newsletter_perms = Permission.objects.filter(
        content_type=newsletter_ct,
        codename__in=['view_newsletter', 'change_newsletter', 'delete_newsletter']
    )

    # Add all permissions to the group
    for perm in list(article_perms) + list(newsletter_perms):
        editor_group.permissions.add(perm)


@receiver(post_save, sender=Article)
def article_approved_signal(sender, instance, created, **kwargs):
    """
    Signal handler that sends email notifications to subscribers and posts
    to X (formerly Twitter) when an article is approved.

    This function:
    - Finds all Readers subscribed to the article's publisher.
    - Finds all Journalists subscribed to the article's author.
    - Sends email notifications to all subscriber emails.
    - Posts to X if TWITTER_BEARER_TOKEN is configured.
    """
    if instance.approved and not created:
        # Get all subscribers (Readers subscribed to publisher + Journalists)
        reader_subs = CustomUser.objects.filter(
            role='Reader',
            subscribed_publishers=instance.publisher
        )
        journalist_subs = CustomUser.objects.filter(
            role='Journalist',
            subscribed_journalists=instance.author
        )
        subscribers = reader_subs.union(journalist_subs).distinct()

        recipient_list = [user.email for user in subscribers if user.email]

        if recipient_list:
            subject = f"New Article Published: {instance.title}"
            message = f"{instance.title}\n\n{instance.content}"
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "news@example.com")

            send_mail(subject, message, from_email, recipient_list)

        # Optional: Post to X (Twitter)
        try:
            x_post = {
                "text": f"New article published: {instance.title} by {instance.author.username}"
            }
            bearer_token = getattr(settings, "TWITTER_BEARER_TOKEN", None)

            if bearer_token:
                response = requests.post(
                    "https://api.twitter.com/2/tweets",
                    json=x_post,
                    headers={"Authorization": f"Bearer {bearer_token}"}
                )
                response.raise_for_status()
        except Exception as e:
            print(f"[X] Failed to post: {e}")
