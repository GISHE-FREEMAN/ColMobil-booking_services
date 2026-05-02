from django.urls import path
from .views import register_view, activate_account,resend_activation_view,login_view,forgot_password_view,reset_password_view,logout_view

urlpatterns = [
    path('register/', register_view, name='register'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),
    path('resend-activation/', resend_activation_view, name='resend_activation'),
    # accounts/urls.py
    path('login/', login_view, name='login'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', reset_password_view, name='reset_password'),
    path('logout/', logout_view, name='logout'),
    ]