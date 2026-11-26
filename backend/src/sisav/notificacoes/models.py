from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from sisav.core.db import Base


class TipoNotificacao(StrEnum):
    PRAZO = "PRAZO"
    INSTITUCIONAL = "INSTITUCIONAL"
    AVISO_PROFESSOR = "AVISO_PROFESSOR"
    LIMITE_FALTAS = "LIMITE_FALTAS"
    MENSAGEM = "MENSAGEM"


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[TipoNotificacao] = mapped_column(
        Enum(TipoNotificacao, name="tipo_notificacao"),
        nullable=False,
        default=TipoNotificacao.INSTITUCIONAL,
    )
    lida: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
