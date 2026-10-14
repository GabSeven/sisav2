from sisav.academico.frequencia import (
    excedeu_limite,
    limite_de_faltas,
    percentual_de_faltas,
)


def test_limite_e_25_por_cento_da_carga_horaria():
    assert limite_de_faltas(60) == 15
    assert limite_de_faltas(90) == 22  # 22,5 arredonda para baixo


def test_percentual_de_faltas():
    assert percentual_de_faltas(15, 60) == 25.0
    assert percentual_de_faltas(0, 60) == 0.0
    assert percentual_de_faltas(7, 90) == 7.78


def test_carga_horaria_zero_nao_divide_por_zero():
    assert percentual_de_faltas(3, 0) == 0.0


def test_excedeu_limite_so_acima_do_limite():
    assert not excedeu_limite(15, 60)
    assert excedeu_limite(16, 60)