from app.models.categoria import Categoria
from app.models.produto import Produto


def test_produto_ativo_por_padrao(db_session_test):
    produto = Produto(nome="Caderno", preco=12.5, estoque_atual=10)
    db_session_test.add(produto)
    db_session_test.commit()

    assert produto.ativo is True


def test_produto_associado_a_categoria(db_session_test):
    categoria = Categoria(nome="Uniformes")
    db_session_test.add(categoria)
    db_session_test.flush()
    produto = Produto(nome="Camiseta", preco=40.0, estoque_atual=20, categoria_id=categoria.id)
    db_session_test.add(produto)
    db_session_test.commit()

    produto_salvo = db_session_test.query(Produto).filter_by(nome="Camiseta").one()
    assert produto_salvo.categoria.nome == "Uniformes"
