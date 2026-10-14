import bcrypt

from sisav.core.config import get_settings


def gerar_hash(senha: str) -> str:
    senha_bytes = senha.encode("utf-8")

    if len(senha_bytes) > 72:
        raise ValueError("A senha deve ter no máximo 72 bytes em UTF-8.")

    salt = bcrypt.gensalt(rounds=get_settings().bcrypt_rounds)
    return bcrypt.hashpw(senha_bytes, salt).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    senha_bytes = senha.encode("utf-8")

    if len(senha_bytes) > 72:
        return False

    try:
        return bcrypt.checkpw(
            senha_bytes,
            senha_hash.encode("utf-8"),
        )
    except ValueError:
        return False
