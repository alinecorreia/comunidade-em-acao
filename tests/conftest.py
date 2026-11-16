import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "teste.sqlite")})


@pytest.fixture
def cliente(app):
    return app.test_client()


@pytest.fixture
def demanda_valida():
    return {
        "titulo": "Lixeira quebrada na praça",
        "descricao": "A lixeira ao lado do parquinho está quebrada.",
        "categoria": "Limpeza urbana",
        "prioridade": "Média",
        "responsavel": "Ana Souza",
    }
