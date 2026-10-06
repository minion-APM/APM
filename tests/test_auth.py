from app.auth import hash_senha, verificar_senha


def test_hash_senha_nao_retorna_senha_em_texto():
    senha = "senha-de-teste-123"
    assert hash_senha(senha) != senha


def test_verificar_senha_aceita_senha_correta():
    senha = "senha-de-teste-123"
    assert verificar_senha(senha, hash_senha(senha)) is True


def test_verificar_senha_rejeita_senha_incorreta():
    senha_hash = hash_senha("senha-correta")
    assert verificar_senha("senha-errada", senha_hash) is False
