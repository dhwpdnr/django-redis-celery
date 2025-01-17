from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_email_task(subject, body, recipient_email):
    """비동기로 이메일을 전송하는 Celery 태스크"""
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        return f"Email successfully sent to {recipient_email}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"
