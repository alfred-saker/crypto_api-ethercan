from django.http import JsonResponse
import logging
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from users.wallets.generate_email_token import generate_email_token
from users.wallets.validate_email_token import validate_email_token
from users.wallets.calculate_wallet_evolution import calculate_wallet_evolution

from users.auth.generate_reset_password_token import generate_reset_password_token
from users.auth.validate_reset_password_token import validate_reset_password_token


from .models import User, Role, Wallet
from .serializers import UserSerializer, RoleSerializer, LoginSerializer,WalletSerializer
from .services import get_etherscan_transactions, get_crypto_prices
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import IsAuthenticated



logger = logging.getLogger('django')

def test_logging(request):
    logger.debug("Test log message")
    return JsonResponse({"message": "Logged"})


@api_view(['GET'])
def transactions(request):
    address = request.query_params.get('address')
    print(address)
    if not address:
        return Response({"error": "Address is required"}, status=400)
    data = get_etherscan_transactions(address)
    print(data)
    return Response(data)

@api_view(['GET'])
def prices(request):
    devise = request.query_params.get('devise')
    if not devise:
        return Response({"error": "Devise is required"}, status=400)
    data = get_crypto_prices(devise)
    return Response(data)


class RoleView(APIView):
    def post(self, request):
        data = request.data
        name = data.get("name")
        try:
            if not name:
                return Response({"error": "Name is equired."}, status=status.HTTP_400_BAD_REQUEST)
            role = Role.objects.create(
                name=name,
            )
            serializer = RoleSerializer(role)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RegisterView(APIView):
   def post(self, request):
        data = request.data
        password = data.get("password")
        username = data.get("username")
        email = data.get("email")
        
        try:
            if not password or not username or not email:
                return Response({"error": "Email, password and username are required."}, status=status.HTTP_400_BAD_REQUEST)
            
            if len(password) < 8:
                return Response({"error": "Password must be at least 8 characters long."}, status=status.HTTP_400_BAD_REQUEST)
            if not any(char.isdigit() for char in password):
                return Response({"error": "Password must contain at least one digit."}, status=status.HTTP_400_BAD_REQUEST)
            if not any(char.isupper() for char in password):
                return Response({"error": "Password must contain at least one uppercase letter."}, status=status.HTTP_400_BAD_REQUEST)

            role_id = data.get("role")
            if role_id:
                role = Role.objects.get(id=role_id)
            else:
                role = None
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password, 
                role=role
            )
            user.is_active = True
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Role.DoesNotExist:
            return Response({"error": "Role not found."}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class LoginView(APIView):
    def post(self, request):
        # serializer = LoginSerializer(data=request.data)
        data=request.data
        print(data)
        # if serializer.is_valid():
            # print(serializer.data) 
            # username = serializer.validated_data['username']
            # password = serializer.validated_data['password']
        if data:
            credentials = {
            "username" : data.get("username"),
            "password" : data.get("password")
            }
            print(f"{credentials}")

            user = authenticate(request, username=data.get("username"), password=data.get("password"))
            if user is None:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
            # login(request, user)
            print(f"User {user.username} logged in.")
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = Response({
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "username":user.username
             }, status=status.HTTP_200_OK)

            # Ajouter le refresh token dans les cookies sécurisés
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                #secure=not settings.DEBUG,  #OnlyInProd
                samesite="Strict",
            )
            return response
        
        
        return Response({"error": "RData not found"}, status=status.HTTP_400_BAD_REQUEST)
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response({"message": "Logout successful"}, status=200)
            response.delete_cookie('refresh_token')  # Supprimez le cookie
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class RefreshTokenView(TokenRefreshView):
    pass


class WalletListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallets = Wallet.objects.filter(user=request.user)
        serializer = WalletSerializer(wallets, many=True)
        return Response(serializer.data, status=200)

    def put(self, request):
        data = request.data.get("wallets")
        print(data)
        if not data:
            return Response({"error": "Wallet data is required"}, status=400)

        try:
            Wallet.objects.filter(user=request.user).delete()  # Supprimer les anciens wallets
            for wallet_data in data:
                Wallet.objects.create(user=request.user, address=wallet_data["address"])
            return Response({"message": "Wallets updated successfully"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class ValidateEmailView(APIView):
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=400)

        user_id = validate_email_token(token)
        if user_id is None:
            return Response({"error": "Invalid or expired token"}, status=400)

        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()
        return Response({"message": "Email validated successfully"}, status=200)


class ResendEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        token = generate_email_token(user)
        # Simuler l'envoi d'un email
        print(f"Validation link: http://127.0.0.1:8000/api/v1/auth/validate/email?token={token}")
        return Response({"message": "Validation email sent"}, status=200)


class WalletEvolutionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        devise = request.query_params.get("devise", "ETH")  # Par défaut, "ETH"
        wallets = Wallet.objects.filter(user=request.user)
        if not wallets.exists():
            return Response({"error": "No wallets found for user"}, status=404)

        all_evolution = []
        for wallet in wallets:
            evolution = calculate_wallet_evolution(wallet.address, devise)
            if isinstance(evolution, dict) and "error" in evolution:
                return Response({"error": evolution["error"]}, status=400)
            all_evolution.extend(evolution)

        # Fusionner les données par date
        merged_evolution = {}
        for entry in all_evolution:
            date = entry["date"]
            merged_evolution[date] = merged_evolution.get(date, 0) + entry["price"]

        # Tri des données
        sorted_evolution = [{"date": date, "price": price} for date, price in sorted(merged_evolution.items())]

        return Response({
            "wallets": [wallet.address for wallet in wallets],
            "evolution": sorted_evolution
        }, status=200)
    
    def put(self, request):
        print("Données reçues :", request.data)  # Log des données reçues
        data = request.data.get("wallets")
        if not data or not isinstance(data, list):
            return Response({"error": "Wallet data must be a list of wallets"}, status=400)

        try:
            for wallet_data in data:
                wallet = Wallet.objects.filter(user=request.user).first()
                if wallet:
                    wallet.address = wallet_data["address"]
                    wallet.save()
                else:
                    Wallet.objects.create(user=request.user, address=wallet_data["address"])

            return Response({"message": "Wallet updated successfully"}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


 

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        try:
            user = User.objects.get(email=email)
            token = generate_reset_password_token(user)

            print(f"Password reset link: http://127.0.0.1:8000/api/v1/auth/reset-password?token={token}")
            return Response({"message": "Password reset email sent"}, status=200)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=404)


class ResetPasswordView(APIView):
    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("password")

        if not token or not new_password:
            return Response({"error": "Token and password are required"}, status=400)

        user_id = validate_reset_password_token(token)
        if user_id is None:
            return Response({"error": "Invalid or expired token"}, status=400)

        user = User.objects.get(id=user_id)
        user.set_password(new_password)
        user.save()

        # TODO: blacklist all user's refresh token

        return Response({"message": "Password reset successfully"}, status=200)





