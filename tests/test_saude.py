"""Testes da verificação de saúde e do ambiente de demonstração."""

from app import create_app


def test_saude_responde_ok(cliente):
    resposta = cliente.get("/saude")
    assert resposta.status_code == 200
    assert resposta.get_json() == {"status": "ok", "banco": "ok", "demandas": 0}


def test_saude_retorna_503_quando_o_banco_falha(cliente, monkeypatch):
    def falhar():
        raise RuntimeError("banco fora do ar")

    monkeypatch.setattr("app.rotas.db.contar_por_status", falhar)
    resposta = cliente.get("/saude")
    assert resposta.status_code == 503
    assert resposta.get_json()["status"] == "erro"


def test_ambiente_de_demonstracao_comeca_com_exemplos_e_aviso(tmp_path):
    config = {"TESTING": True, "DATABASE": str(tmp_path / "demo.sqlite"), "DADOS_EXEMPLO": True}
    cliente = create_app(config).test_client()
    assert cliente.get("/saude").get_json()["demandas"] == 6
    assert "Ambiente de demonstração" in cliente.get("/").text

    # Reiniciar a aplicação não duplica os exemplos.
    assert create_app(config).test_client().get("/saude").get_json()["demandas"] == 6


def test_aviso_de_demonstracao_nao_aparece_fora_dela(cliente):
    assert "Ambiente de demonstração" not in cliente.get("/").text
