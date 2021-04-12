from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from django_rest_resetpassword.signals import reset_password_token_created


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    print("-----------------SENT EMAIL-----------------")
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)
    }

    email_html = render_to_string('../templates/email/reset_password.html', context)
    email_plaintext = render_to_string('../templates/email/reset_password.txt', context)

    msg = EmailMultiAlternatives(
        "Password Reset for {title}".format(title="Wasteless"),
        email_plaintext,
        "wasteless.mail@gmail.com",
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html, "text/html")
    msg.send()
