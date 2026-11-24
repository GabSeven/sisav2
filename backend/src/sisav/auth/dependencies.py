from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sisav.auth.tokens import TokenInvalido, usuario_id_do_token
from sisav.core.config import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{get_settings().api_v1_prefix}/auth/token")

def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]) -> int:
    try:
        return usuario_id_do_token(token)
    except TokenInvalido as erro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from erro