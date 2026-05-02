from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from django.core.mail import EmailMessage
from .forms import RegisterForm
from .tokens import account_activation_token
from django.contrib.auth import get_user_model,authenticate, login,logout
from django.http import HttpResponse
from django.contrib import messages


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Activate your account'

            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            email = EmailMessage(
                mail_subject,
                message,
                to=[user.email]
            )
            email.send()

            return render(request, 'accounts/check_email.html')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


User = get_user_model()

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Invalid user
    if user is None:
        messages.error(request, "Invalid activation link.")
        return redirect('register')

    # Already activated
    if user.is_active:
        messages.info(request, "Account already activated. Please login.")
        return redirect('login')

    # Valid activation
    if account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated successfully. Please login.")
        return redirect('login')

    # Expired/invalid token
    messages.error(request, "Activation link expired or invalid. Please register again.")
    return redirect('register')

User = get_user_model()

def resend_activation_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        user = User.objects.filter(email=email).first()

        # Security: don't reveal if email exists or not
        if user:
            if user.is_active:
                messages.info(request, "Account already activated. Please login.")
                return redirect('login')

            # Send activation email again
            current_site = get_current_site(request)

            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            email_message = EmailMessage(
                "Activate your account",
                message,
                to=[user.email]
            )
            email_message.send()

        # Always show same message (prevents email enumeration)
        messages.success(request, "If your account exists, we sent you an activation email.")
        return redirect('login')

    return render(request, 'accounts/resend_activation.html')

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')  # email or phone
        password = request.POST.get('password')

        user = User.objects.filter(email=identifier).first()
        if not user:
            user = User.objects.filter(phone=identifier).first()

        if user:
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                if not user.is_active:
                    messages.error(request, "Account not activated. Check your email.")
                    return redirect('login')

                login(request, user)
                return redirect('home')  # change to your page

        messages.error(request, "Invalid email/phone or password.")
        return redirect('login')

    return render(request, 'accounts/login.html')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            current_site = get_current_site(request)
            message = render_to_string('accounts/password_reset_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            email_message = EmailMessage(
                "Reset your password",
                message,
                to=[user.email]
            )
            email_message.send()

        messages.success(request, "If your email exists, a reset link has been sent.")
        return redirect('login')

    return render(request, 'accounts/forgot_password.html')

def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is None or not account_activation_token.check_token(user, token):
        messages.error(request, "Invalid or expired link.")
        return redirect('login')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect(request.path)

        user.set_password(password)
        user.save()
        messages.success(request, "Password reset successful. You can login.")
        return redirect('login')

    return render(request, 'accounts/reset_password.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')