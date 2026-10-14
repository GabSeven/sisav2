import math

LIMITE_PERCENTUAL_FALTAS = 0.25


def limite_de_faltas(carga_horaria: int) -> int:
    return math.floor(carga_horaria * LIMITE_PERCENTUAL_FALTAS)


def percentual_de_faltas(total_faltas: int, carga_horaria: int) -> float:
    if carga_horaria <= 0:
        return 0.0
    return round(total_faltas / carga_horaria * 100, 2)


def excedeu_limite(total_faltas: int, carga_horaria: int) -> bool:
    return total_faltas > limite_de_faltas(carga_horaria)