import pytest

from sisav.auth.security import gerar_hash, verificar_senha


def test_hash_gerado_diferente_senha_original():
    senha = "senha-teste"
    assert gerar_hash(senha) != senha

def test_senha_correta_valida():
    senha = "senha-teste"
    assert verificar_senha(senha, gerar_hash(senha))

def test_senha_incorreta_nao_valida():
    senha = "senha-teste"
    assert not verificar_senha("outra-senha", gerar_hash(senha))

def test_senha_maior_que_limite_rejeita():
    senha = "s" * 73

    with pytest.raises(ValueError):
        gerar_hash(senha)

def test_hashes_diferentes_validam_mesma_senha():
    senha = "senha-teste"
    primeiro = gerar_hash(senha)
    segundo = gerar_hash(senha)

    assert primeiro != segundo
    assert verificar_senha(senha, primeiro)
    assert verificar_senha(senha, segundo)

def test_hash_invalido_nao_valida():
    assert not verificar_senha("senha-teste", "hash-invalido")