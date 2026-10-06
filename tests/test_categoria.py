from app.models.categoria import Categoria


def test_listar_categorias_retorna_200(cliente):
    response = cliente.get("/categorias/")
    assert response.status_code == 200


def test_criar_categoria_redireciona_e_salva_no_banco(cliente, db_session_test):
    response = cliente.post(
        "/categorias/nova",
        data={"nome": "Material escolar"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["location"] == "/categorias?criado=ok"
    assert db_session_test.query(Categoria).filter_by(nome="Material escolar").first() is not None


def test_busca_categoria_filtra_resultado(db_session_test, cliente):
    db_session_test.add_all([
        Categoria(nome="Lanches"),
        Categoria(nome="Uniformes"),
    ])
    db_session_test.commit()

    response = cliente.get("/categorias/", params={"busca": "Lanches"})

    assert response.status_code == 200
    assert "Lanches" in response.text
    assert "Uniformes" not in response.text
