from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

_bearer = HTTPBearer(auto_error=False)


def require_token(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> None:
    if creds is None or creds.credentials != settings.retrieve_token:
        raise HTTPException(status_code=401, detail="invalid retrieve token")
