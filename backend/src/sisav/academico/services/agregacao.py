"""Agregação de avaliações e notas compartilhada por boletim e fechamento."""

from collections import defaultdict
from collections.abc import Sequence

from sisav.academico.models import Avaliacao, Nota, TipoAvaliacao
from sisav.academico.services.calculo import CriterioNotas, FolhaNota

MapaNotas = dict[tuple[int, int], Nota]


def folhas_por_pai(avaliacoes: Sequence[Avaliacao]) -> dict[int, list[Avaliacao]]:
    agrupado: dict[int, list[Avaliacao]] = defaultdict(list)
    for avaliacao in avaliacoes:
        if (
            avaliacao.pai_id is not None
            and avaliacao.tipo == TipoAvaliacao.AVALIACAO.value
        ):
            agrupado[avaliacao.pai_id].append(avaliacao)
    return dict(agrupado)


def folhas_de_nota(avaliacoes: Sequence[Avaliacao]) -> list[Avaliacao]:
    return [
        avaliacao
        for avaliacao in avaliacoes
        if avaliacao.pai_id is not None
        and avaliacao.tipo == TipoAvaliacao.AVALIACAO.value
    ]


def exame_da_turma(avaliacoes: Sequence[Avaliacao]) -> Avaliacao | None:
    return next(
        (
            avaliacao
            for avaliacao in avaliacoes
            if avaliacao.tipo == TipoAvaliacao.EXAME.value
        ),
        None,
    )


def valor_da_nota(
    notas_por_chave: MapaNotas, matricula_id: int, avaliacao_id: int
) -> int | None:
    nota = notas_por_chave.get((matricula_id, avaliacao_id))
    return nota.valor if nota is not None else None


def criterios_da_matricula(
    avaliacoes: Sequence[Avaliacao],
    notas_por_chave: MapaNotas,
    matricula_id: int,
) -> list[CriterioNotas]:
    filhas = folhas_por_pai(avaliacoes)
    criterios: list[CriterioNotas] = []
    for avaliacao in avaliacoes:
        if avaliacao.tipo != TipoAvaliacao.CRITERIO.value:
            continue
        folhas: list[FolhaNota] = []
        for folha in filhas.get(avaliacao.id, []):
            valor = valor_da_nota(notas_por_chave, matricula_id, folha.id)
            if valor is not None:
                folhas.append(FolhaNota(valor=valor, peso=folha.peso))
        if folhas:
            criterios.append(CriterioNotas(peso=avaliacao.peso, folhas=folhas))
    return criterios
