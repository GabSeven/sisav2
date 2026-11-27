"""Cálculo puro de médias e situação final.

Todos os valores numéricos são inteiros em centésimos (7,5 -> 750).
A API converte para float; o banco guarda centésimos.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from sisav.academico.models import SituacaoAluno

CENTESIMOS_POR_UNIDADE = 100
LIMITE_APROVACAO = 600
LIMITE_EXAME = 500


@dataclass(frozen=True, slots=True)
class FolhaNota:
    """Nota de uma avaliação folha, com o peso já copiado para a turma."""

    valor: int
    peso: int


@dataclass(frozen=True, slots=True)
class CriterioNotas:
    """Critério pai e suas folhas."""

    peso: int
    folhas: Sequence[FolhaNota]


@dataclass(frozen=True, slots=True)
class ResultadoFinal:
    media_final: int
    situacao: SituacaoAluno


def para_centesimos(valor: float) -> int:
    """Converte o valor da API (float) para inteiro em centésimos."""
    return int(
        (Decimal(str(valor)) * CENTESIMOS_POR_UNIDADE).to_integral_value(
            rounding=ROUND_HALF_UP
        )
    )


def de_centesimos(valor: int) -> float:
    """Converte centésimos para o valor exposto pela API."""
    return valor / CENTESIMOS_POR_UNIDADE


def arredondar_uma_casa(valor: int) -> int:
    """Arredonda centésimos para uma casa decimal, com 0,5 para cima."""
    return ((valor + 5) // 10) * 10


def divisao_arredondada(numerador: int, denominador: int) -> int:
    """Divisão inteira com arredondamento de metade para cima."""
    if denominador <= 0:
        raise ValueError("Denominador deve ser positivo.")
    return (2 * numerador + denominador) // (2 * denominador)


def media_ponderada(itens: Sequence[FolhaNota]) -> int:
    """Média de (valor, peso), todos em centésimos."""
    if not itens:
        raise ValueError("Não há notas para calcular a média.")
    if any(item.peso <= 0 for item in itens):
        raise ValueError("Pesos devem ser positivos.")
    soma = sum(item.valor * item.peso for item in itens)
    total_pesos = sum(item.peso for item in itens)
    return divisao_arredondada(soma, total_pesos)


def media_folhas(folhas: Sequence[FolhaNota]) -> int:
    """media_folhas(c) da especificação."""
    return media_ponderada(folhas)


def media_pre_exame(criterios: Sequence[CriterioNotas]) -> int:
    """Média ponderada das contribuições dos critérios."""
    if not criterios:
        raise ValueError("Não há critérios para calcular a média.")
    if any(criterio.peso <= 0 for criterio in criterios):
        raise ValueError("Pesos devem ser positivos.")
    soma = sum(criterio.peso * media_folhas(criterio.folhas) for criterio in criterios)
    total_pesos = sum(criterio.peso for criterio in criterios)
    return divisao_arredondada(soma, total_pesos)


def calcular_situacao(
    media_pre: int,
    *,
    excedeu_limite: bool,
    nota_exame: int | None = None,
) -> ResultadoFinal:
    """Aplica a precedência: falta, aprovação direta, exame, exame final."""
    if excedeu_limite:
        return ResultadoFinal(media_pre, SituacaoAluno.REP_POR_FALTA)
    if arredondar_uma_casa(media_pre) >= LIMITE_APROVACAO:
        return ResultadoFinal(media_pre, SituacaoAluno.APROVADO)
    if nota_exame is None:
        return ResultadoFinal(media_pre, SituacaoAluno.EXAME_FINAL)

    media_final = divisao_arredondada(media_pre + nota_exame, 2)
    situacao = (
        SituacaoAluno.APROVADO
        if arredondar_uma_casa(media_final) >= LIMITE_EXAME
        else SituacaoAluno.REPROVADO
    )
    return ResultadoFinal(media_final, situacao)
