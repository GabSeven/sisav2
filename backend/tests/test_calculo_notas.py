import pytest

from sisav.academico.models import SituacaoAluno
from sisav.academico.services.calculo import (
    CriterioNotas,
    FolhaNota,
    arredondar_uma_casa,
    calcular_situacao,
    de_centesimos,
    media_folhas,
    media_pre_exame,
    para_centesimos,
)


def test_arredondamento_para_uma_casa_meio_para_cima():
    assert arredondar_uma_casa(594) == 590
    assert arredondar_uma_casa(595) == 600
    assert arredondar_uma_casa(604) == 600
    assert arredondar_uma_casa(605) == 610
    assert arredondar_uma_casa(750) == 750


def test_conversao_entre_api_e_centesimos():
    assert para_centesimos(7.5) == 750
    assert para_centesimos(0.6) == 60
    assert para_centesimos(10.0) == 1000
    assert para_centesimos(5.955) == 596
    assert de_centesimos(750) == 7.5
    assert de_centesimos(60) == 0.6


def test_media_folhas_e_ponderada_pelo_peso_da_folha():
    folhas = [FolhaNota(valor=800, peso=60), FolhaNota(valor=600, peso=40)]
    assert media_folhas(folhas) == 720


def test_media_pre_exame_com_criterios_e_subcriterios():
    criterios = [
        CriterioNotas(peso=100, folhas=[FolhaNota(800, 100), FolhaNota(600, 100)]),
        CriterioNotas(peso=100, folhas=[FolhaNota(400, 100)]),
    ]
    assert media_pre_exame(criterios) == 550


def test_criterio_sem_subdivisao_usa_a_propria_folha():
    criterios = [CriterioNotas(peso=100, folhas=[FolhaNota(750, 100)])]
    assert media_pre_exame(criterios) == 750


def test_medias_rejeitam_pesos_invalidos_e_listas_vazias():
    with pytest.raises(ValueError, match="Não há notas"):
        media_folhas([])
    with pytest.raises(ValueError, match="Pesos devem ser positivos"):
        media_folhas([FolhaNota(valor=800, peso=0)])
    with pytest.raises(ValueError, match="Não há critérios"):
        media_pre_exame([])
    with pytest.raises(ValueError, match="Pesos devem ser positivos"):
        media_pre_exame([CriterioNotas(peso=0, folhas=[FolhaNota(800, 100)])])


def test_falta_excedida_precede_qualquer_nota():
    resultado = calcular_situacao(900, excedeu_limite=True, nota_exame=800)
    assert resultado.situacao is SituacaoAluno.REP_POR_FALTA
    assert resultado.media_final == 900


def test_arredondamento_para_uma_casa_pode_aprovar_direto():
    resultado = calcular_situacao(595, excedeu_limite=False)
    assert resultado.situacao is SituacaoAluno.APROVADO
    assert resultado.media_final == 595


def test_sem_nota_de_exame_fica_em_exame_final():
    resultado = calcular_situacao(594, excedeu_limite=False)
    assert resultado.situacao is SituacaoAluno.EXAME_FINAL
    assert resultado.media_final == 594


def test_media_com_exame_usa_media_crua_e_aprova():
    resultado = calcular_situacao(594, excedeu_limite=False, nota_exame=500)
    assert resultado.media_final == 547
    assert resultado.situacao is SituacaoAluno.APROVADO


def test_media_com_exame_reprova_abaixo_de_cinco():
    resultado = calcular_situacao(400, excedeu_limite=False, nota_exame=500)
    assert resultado.media_final == 450
    assert resultado.situacao is SituacaoAluno.REPROVADO


def test_exame_no_limite_arredonda_meio_para_cima():
    resultado = calcular_situacao(500, excedeu_limite=False, nota_exame=499)
    assert resultado.media_final == 500
    assert resultado.situacao is SituacaoAluno.APROVADO
