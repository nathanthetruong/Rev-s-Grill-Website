from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import perform_login
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import perform_login
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.signals import pre_social_login
from allauth.utils import get_user_model
from django.conf import settings
from django.dispatch import receiver
from django.shortcuts import redirect


class MyLoginAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        """
        get the redirect login
        """
        if request.user.is_authenticated:
            return settings.LOGIN_REDIRECT_URL.format(id=request.user.id)
        else:
            return "/"


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        pass 


@receiver(pre_social_login)
def link_to_local_user(sender, request, sociallogin, **kwargs):
    email_address = sociallogin.account.extra_data.get("email") or sociallogin.account.extra_data.get("mail")

    User = get_user_model()
    if users := User.objects.filter(email=email_address):
        perform_login(request, users[0], email_verification="optional")
        raise ImmediateHttpResponse(
            redirect(settings.LOGIN_REDIRECT_URL.format(id=request.user.id))
        )
