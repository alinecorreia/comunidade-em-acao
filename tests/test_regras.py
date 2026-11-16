"""Testes unitários das regras de negócio."""

from app import regras


def test_demanda_valida_nao_gera_erros(demanda_valida):
    limpos, erros = regras.validar_demanda(demanda_valida)
    assert erros == {}
    assert limpos["titulo"] == "Lixeira quebrada na praça"


def test_titulo_obrigatorio(demanda_valida):
    demanda_valida["titulo"] = "   "
    _, erros = regras.validar_demanda(demanda_valida)
    assert erros["titulo"].startswith("O título é obrigatório")


def test_campos_obrigatorios_vazios():
    _, erros = regras.validar_demanda({})
    assert set(erros) == {"titulo", "descricao", "categoria", "prioridade"}


def test_responsavel_e_opcional(demanda_valida):
    demanda_valida["responsavel"] = ""
    _, erros = regras.validar_demanda(demanda_valida)
    assert erros == {}


def test_descricao_acima_do_limite(demanda_valida):
    demanda_valida["descricao"] = "a" * (regras.TAMANHO_MAX_DESCRICAO + 1)
    _, erros = regras.validar_demanda(demanda_valida)
    assert "descricao" in erros


def test_valores_fora_das_listas_sao_recusados(demanda_valida):
    demanda_valida.update(categoria="Outra", prioridade="Urgente", responsavel="Desconhecido")
    _, erros = regras.validar_demanda(demanda_valida)
    assert {"categoria", "prioridade", "responsavel"} <= set(erros)


def test_espacos_sao_removidos(demanda_valida):
    demanda_valida["titulo"] = "  Poste caído  "
    limpos, _ = regras.validar_demanda(demanda_valida)
    assert limpos["titulo"] == "Poste caído"


def test_status_valido():
    assert regras.status_valido("Em andamento")
    assert not regras.status_valido("Arquivada")
    assert not regras.status_valido("")


def test_resumo_preenche_status_sem_demandas():
    assert regras.resumo_por_status({"Pendente": 2}) == {
        "Pendente": 2,
        "Em andamento": 0,
        "Concluída": 0,
    }


def test_numero_formatado():
    assert regras.numero_formatado(18) == "0018"
