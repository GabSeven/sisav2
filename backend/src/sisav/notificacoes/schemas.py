from datetime import datetime

from pydantic import BaseModel, ConfigDict

from sisav.notificacoes.models import TipoNotificacao


class NotificacaoResponse(BaseModel):
    id: int
    titulo: str
    mensagem: str
    tipo: TipoNotificacao
    lida: bool
    criada_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ListaNotificacoesResponse(BaseModel):
    nao_lidas: int
    notificacoes: list[NotificacaoResponse]


class MarcarLidasRequest(BaseModel):
    notificacao_ids: list[int] | None = None


class MarcarLidasResponse(BaseModel):
    atualizadas: int
