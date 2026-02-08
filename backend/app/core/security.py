from datetime import UTC, datetime, timedelta
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class TokenPayloadError(ValueError):
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _create_token(subject: str, token_type: str, expires_delta: timedelta, role: str | None = None, jti: str | None = None) -> str:
    now = datetime.now(UTC)
    payload = {
        'sub': subject,
        'type': token_type,
        'exp': now + expires_delta,
        'iat': now,
        'jti': jti or str(uuid4()),
    }
    if role:
        payload['role'] = role
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, role: str) -> str:
    return _create_token(
        subject=subject,
        token_type='access',
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        role=role,
    )


def create_refresh_token(subject: str, jti: str | None = None) -> tuple[str, str]:
    token_id = jti or str(uuid4())
    token = _create_token(
        subject=subject,
        token_type='refresh',
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        jti=token_id,
    )
    return token, token_id


def decode_token(token: str, expected_type: str | None = None) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise TokenPayloadError('Invalid token') from exc

    token_type = payload.get('type')
    if expected_type and token_type != expected_type:
        raise TokenPayloadError('Unexpected token type')

    if 'sub' not in payload:
        raise TokenPayloadError('Invalid token payload')

    return payload
