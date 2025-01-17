from itsdangerous import URLSafeTimedSerializer
from django.conf import settings

def validate_reset_password_token(token):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        data = serializer.loads(token, salt="password-reset", max_age=3600)  # 1 heure
        return data["user_id"]
    except Exception:
        return None
