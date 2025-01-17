from itsdangerous import URLSafeTimedSerializer
from django.conf import settings

def generate_reset_password_token(user):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps({"user_id": user.id}, salt="password-reset")
