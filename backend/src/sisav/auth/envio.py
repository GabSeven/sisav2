from typing import Protocol

from sisav.core.config import get_settings


class EnviadorLink(Protocol):
    async def __call__(self, usuario_id: int, token: str, destinos: list[str]) -> None: ...

async def enviador_link_dev(usuario_id: int, token: str, destinos: list[str]) -> None:
    if get_settings().mostrar_link_recuperacao:
        url = get_settings().password_reset_url.format(token=token)
        print(f"[DEV] recuperação {destinos}: {url}")

def get_enviador_link() -> EnviadorLink:
    return enviador_link_dev