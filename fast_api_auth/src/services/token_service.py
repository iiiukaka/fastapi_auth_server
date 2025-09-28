import jwt
from fastapi import HTTPException, status
from jwt import ExpiredSignatureError, InvalidAudienceError, InvalidTokenError

from src.core.config import project_settings
from src.db.redis_cache import RedisClientFactory


class TokenService:
    """Унифицированный сервис для работы с JWT токенами."""

    @staticmethod
    def encode_jwt(payload: dict[str, any]) -> str:
        """Кодирование данных в JWT токен."""
        try:
            return jwt.encode(
                payload,
                project_settings.secret,
                algorithm='HS256',
                audience='fastapi-users:auth'
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Token encoding error: {str(e)}'
            )

    @staticmethod
    def decode_jwt(token: str) -> dict[str, any]:
        """Декодирование JWT токена с обработкой ошибок."""
        try:
            return jwt.decode(
                token,
                project_settings.secret,
                algorithms=['HS256'],
                audience='fastapi-users:auth'
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token expired'
            )
        except InvalidAudienceError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token audience'
            )
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'Invalid token: {str(e)}'
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'Token decoding error: {str(e)}'
            )

    @staticmethod
    async def validate_refresh_token(token: str, user_id: str) -> bool:
        """Проверка refresh токена в Redis."""
        try:
            redis = await RedisClientFactory.create(project_settings.redis_dsn)
            stored_token = await redis.get(f'refresh_token:{user_id}')

            if not stored_token:
                return False

            return stored_token.decode('utf-8') == token
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Redis validation error: {str(e)}'
            )

    @staticmethod
    async def store_refresh_token(
        user_id: str, token: str, expire_seconds: int = 86400
    ) -> None:
        """Сохранение refresh токена в Redis."""
        try:
            redis = await RedisClientFactory.create(project_settings.redis_dsn)
            await redis.setex(
                f'refresh_token:{user_id}', expire_seconds, token
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Redis storage error: {str(e)}'
            )

    @staticmethod
    async def revoke_refresh_token(user_id: str) -> None:
        """Удаление refresh токена из Redis."""
        try:
            redis = await RedisClientFactory.create(project_settings.redis_dsn)
            await redis.delete(f'refresh_token:{user_id}')
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Redis deletion error: {str(e)}'
            )
