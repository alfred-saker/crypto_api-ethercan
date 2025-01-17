from django.contrib import admin
from django.urls import path
from users.views import test_logging, transactions, prices, RegisterView, RefreshTokenView, LoginView, LogoutView, RoleView, WalletListView, ValidateEmailView, ResendEmailView, WalletEvolutionView, ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', test_logging),
    path('api/v1/transactions', transactions, name='transactions'),
    path('api/v1/prices', prices, name='prices'),
    path('api/v1/auth/register', RegisterView.as_view(), name='register'),
    path('api/v1/auth/login', LoginView.as_view(), name='login'),
    path('api/v1/auth/logout', LogoutView.as_view(), name='logout'),
    path('api/v1/role', RoleView.as_view(), name='role'),
    path('api/v1/auth/refresh', RefreshTokenView.as_view(), name='token_refresh'),
    path('api/v1/profile/wallets', WalletListView.as_view(), name='wallets'),
    path('api/v1/auth/validate/email', ValidateEmailView.as_view(), name='validate_email'),
    path('api/v1/auth/resend/email', ResendEmailView.as_view(), name='resend_email'),
    path('api/v1/profile/wallets/evolution', WalletEvolutionView.as_view(), name='wallets_evolution'),

    path('api/v1/auth/forgot/password', ForgotPasswordView.as_view(), name='forgot_password'),
    path('api/v1/auth/reset/password', ResetPasswordView.as_view(), name='reset_password'),

    
    


]
