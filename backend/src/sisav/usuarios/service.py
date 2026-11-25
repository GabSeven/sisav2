from sisav.core.config import get_settings

settings = get_settings()

def email_institucional(login: str) -> str:
    return f"{login}@{settings.dominio_institucional}"