
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_backends

from .forms import (
    SignupForm, SetPasswordForm, LoginForm, 
    ForgotPasswordForm, ProfileUpdateForm
)
from .models import User, OTP
from .utils import send_otp_email, send_otp_phone
from places.models import Place
from reviews.models import Review

class LoginRedirectView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('places:home')
        return redirect('welcome')


class WelcomeView(View):
    def get(self, request):
        return render(request, 'users/getting_started.html')


class LoginView(View):
    def get(self, request):
        return render(request, 'users/login.html', {'form': LoginForm()})
    
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            login_info = form.cleaned_data['login']
            password = form.cleaned_data['password']

            user_q = User.objects.filter(
                Q(username__iexact=login_info) |
                Q(email__iexact=login_info) |
                Q(phone_number=login_info)
            ).first()

            if user_q:
                user = authenticate(request, username=user_q.username, password=password)
                if user:
                    login(request, user)
                    return redirect('places:home')

            messages.error(request, "Invalid credentials. Please try again.")
        return render(request, 'users/login.html', {'form': form})


class SignupView(View):
    def get(self, request):
        return render(request, 'users/signup.html', {'form': SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            signup_data = form.cleaned_data
            request.session['signup_data'] = signup_data

            contact_info = signup_data['contact_info']
            otp_type = 'email' if '@' in contact_info else 'phone'

            OTP.objects.filter(contact_info=contact_info, purpose='signup').delete()
            otp = OTP.objects.create(
                contact_info=contact_info, 
                type=otp_type, 
                purpose='signup'
            )

            if otp_type == 'email':
                send_otp_email(otp)
            else:
                send_otp_phone(otp)

            request.session['signup_otp_id'] = otp.id
            request.session['verification_purpose'] = 'signup'
            messages.info(request, f"A verification code has been sent to {contact_info}.")
            return redirect('users:verify_otp')

        return render(request, 'users/signup.html', {'form': form})


class VerifyOTPView(View):
    def get(self, request):
        purpose = request.session.get('verification_purpose')
        if purpose == 'signup':
            otp_id = request.session.get('signup_otp_id')
        elif purpose == 'reset':
            otp_id = request.session.get('reset_otp_id')
        elif purpose == 'profile_update':
            otp_id = request.session.get('update_otp_id')
        else:
            otp_id = None
            
        if not purpose or not otp_id:
            messages.error(request, 'Invalid session. Please start over.')
            return redirect('welcome')

        try:
            otp = OTP.objects.get(id=otp_id, purpose=purpose) 
            return render(request, 'users/verify_otp.html', {'contact_info': otp.contact_info})
        except OTP.DoesNotExist:
            messages.error(request, 'Invalid session. Please start over.')
            return redirect('welcome')

    def post(self, request):
        otp_code = request.POST.get('otp_code')
        purpose = request.session.get('verification_purpose')

        if purpose == 'signup':
            otp_id = request.session.get('signup_otp_id')
        elif purpose == 'reset':
            otp_id = request.session.get('reset_otp_id')
        elif purpose == 'profile_update':
            otp_id = request.session.get('update_otp_id')
        else:
            otp_id = None

        if not all([otp_code, purpose, otp_id]):
            messages.error(request, 'Session expired. Please start over.')
            return redirect('welcome')

        try:
            otp = OTP.objects.get(id=otp_id, code=otp_code, purpose=purpose)
            
            if otp.is_valid():
                if purpose == 'signup':
                    return redirect('users:set_password')
                elif purpose == 'reset':
                    request.session['reset_user_id'] = otp.user_id
                    return redirect('users:reset_password')
                elif purpose == 'profile_update':
                    return redirect('users:verify_profile_update')
            else:
                messages.error(request, 'OTP expired. Please try again.')
        except OTP.DoesNotExist:
            messages.error(request, 'Invalid OTP code.')

        return render(request, 'users/verify_otp.html', {'contact_info': 'your contact'})


class SetPasswordView(View):
    template_name = 'users/set_password.html'

    def get(self, request):
        if not request.session.get('signup_data'):
            messages.error(request, 'Invalid session. Please sign up first.')
            return redirect('users:signup')
        return render(request, self.template_name, {'form': SetPasswordForm(user=None)})

    def post(self, request):
        signup_data = request.session.get('signup_data')
        otp_id = request.session.get('signup_otp_id')
        if not signup_data or not otp_id:
            messages.error(request, 'Session expired. Please start over.')
            return redirect('users:signup')

        form = SetPasswordForm(user=None, data=request.POST)
        if form.is_valid():
            otp = OTP.objects.filter(id=otp_id, purpose='signup').first()
            if not otp:
                messages.error(request, 'Session expired. Please start over.')
                return redirect('users:signup')

            contact_info = signup_data.get('contact_info')
            email, phone_number, email_verified = None, None, False

            if '@' in contact_info:
                email, email_verified = contact_info, True
            else:
                phone_number = contact_info

            age = form.cleaned_data.get('age')
            preferred_city = form.cleaned_data.get('preferred_city') or "Coimbatore"
            taste_tags = form.cleaned_data.get('taste_tags', '')

            user = User.objects.create_user(
                username=signup_data['username'],
                email=email,
                phone_number=phone_number,
                age=age,
                preferred_city=preferred_city,
                taste_tags=taste_tags,
                is_active=True,
                is_verified=True,
                email_verified=email_verified,
            )

            user.set_password(form.cleaned_data['new_password1'])
            user.save()

            otp.user = user
            otp.save()

            for key in ['signup_data', 'signup_otp_id', 'verification_purpose']:
                request.session.pop(key, None)

            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

            login(request, user, backend=user.backend)
            messages.success(request, 'Welcome to CityMate! Your account is all set.')
            return redirect('places:home')

        return render(request, self.template_name, {'form': form})


class ProfileView(LoginRequiredMixin, View):
    
    def get(self, request):
        user_reviews = Review.objects.filter(user=request.user).order_by('-created_at')
        added_places = Place.objects.filter(added_by=request.user).order_by('-name')
        form = ProfileUpdateForm(instance=request.user)
        
        return render(request, 'users/profile.html', {
            'user_reviews': user_reviews,
            'added_places': added_places,
            'form': form
        })

    def post(self, request):
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('users:profile')
        
        user_reviews = Review.objects.filter(user=request.user).order_by('-created_at')
        added_places = Place.objects.filter(added_by=request.user).order_by('-name')
        return render(request, 'users/profile.html', {
            'user_reviews': user_reviews,
            'added_places': added_places,
            'form': form
        })


class VerifyProfileUpdateView(LoginRequiredMixin, View):
    
    def get(self, request):
        if not request.session.get('update_otp_verified'):
            messages.error(request, "Please verify your OTP first.")
            return redirect('users:verify_otp')
        
        pending_data = request.session.get('pending_profile_update')
        if not pending_data:
            messages.error(request, "No pending update found. Please try again.")
            return redirect('users:profile')
            
        user = request.user
        
        
        temp_path = pending_data.get('profile_photo')
        if temp_path and temp_path != 'CLEAR':
            if default_storage.exists(temp_path):
                file_content = default_storage.open(temp_path)
                if user.profile_photo:
                    user.profile_photo.delete(save=False)
                user.profile_photo.save(os.path.basename(temp_path), file_content)
                default_storage.delete(temp_path)
        elif temp_path == 'CLEAR':
            if user.profile_photo:
                user.profile_photo.delete(save=False)
        
        user.username = pending_data.get('username', user.username)
        user.email = pending_data.get('email', user.email)
        user.phone_number = pending_data.get('phone_number', user.phone_number)
        user.age = pending_data.get('age', user.age)
        user.preferred_city = pending_data.get('preferred_city', user.preferred_city)
        user.preferred_area = pending_data.get('preferred_area', user.preferred_area)
        user.preferred_price = pending_data.get('preferred_price', user.preferred_price)
        user.taste_tags = pending_data.get('taste_tags', user.taste_tags)
        
        if user.email == pending_data.get('email'):
            user.email_verified = True
        
        user.save()
        
        for key in ['pending_profile_update', 'update_otp_id', 'update_otp_verified', 'verification_purpose']:
            if key in request.session:
                del request.session[key]
        
        messages.success(request, "Your profile has been updated successfully!")
        return redirect('users:profile')


class ForgotPasswordView(View):
    def get(self, request):
        return render(request, 'users/forgot_password.html', {'form': ForgotPasswordForm()})

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            contact_info = form.cleaned_data['contact_info']
            user = User.objects.filter(
                Q(email=contact_info) | Q(phone_number=contact_info),
                is_active=True
            ).first()

            if user:
                otp_type = 'email' if '@' in contact_info else 'phone'
                contact_to_send = user.email if otp_type == 'email' else user.phone_number
                
                OTP.objects.filter(user=user, purpose='reset').delete()
                otp = OTP.objects.create(
                    user=user, 
                    contact_info=contact_to_send, 
                    type=otp_type, 
                    purpose='reset'
                )

                if otp_type == 'email':
                    send_otp_email(otp)
                else:
                    send_otp_phone(otp)

                request.session['reset_otp_id'] = otp.id
                request.session['verification_purpose'] = 'reset'
                messages.info(request, f"A verification code has been sent to {contact_to_send}.")
                return redirect('users:verify_otp')

            messages.error(request, "No active user found with that email or phone number.")
        return render(request, 'users/forgot_password.html', {'form': form})


class ResetPasswordView(View):
    template_name = 'users/set_password.html'

    def get(self, request):
        user_id = request.session.get('reset_user_id')
        if not user_id or request.session.get('verification_purpose') != 'reset':
            messages.error(request, 'Invalid session. Please start again.')
            return redirect('users:forgot_password')

        try:
            user = User.objects.get(id=user_id)
            form = SetPasswordForm(user)
            return render(request, self.template_name, {'form': form, 'resetting': True})
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('users:forgot_password')

    def post(self, request):
        user_id = request.session.get('reset_user_id')
        if not user_id or request.session.get('verification_purpose') != 'reset':
            messages.error(request, 'Session expired.')
            return redirect('users:forgot_password')

        user = User.objects.get(id=user_id)
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            for key in ['reset_user_id', 'verification_purpose', 'reset_otp_id']:
                request.session.pop(key, None)
            messages.success(request, 'Password has been reset. Please log in.')
            return redirect('users:login')
        return render(request, self.template_name, {'form': form, 'resetting': True})


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect('welcome')