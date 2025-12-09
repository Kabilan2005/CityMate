from django.urls import path, include
from .views import (
    WelcomeView, 
    LoginView,     
    SignupView,
    VerifyOTPView,
    SetPasswordView,
    LogoutView,
    ForgotPasswordView,
    ResetPasswordView,
    ProfileView,
    LoginRedirectView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),

    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    
    path('set-password/', SetPasswordView.as_view(), name='set_password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),

    path('check-profile/', LoginRedirectView.as_view(), name='profile_completion_redirect'),
]