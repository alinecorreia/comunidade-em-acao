"""Testes de integração da atualização de status."""

from html import unescape


def cadastrar(cliente, dados):
    return cliente.post("/demandas/nova", data=dados, follow_redirects=True)


def test_atualizar_status_mostra_confirmacao(cliente, demanda_valida):
    cadastrar(cliente, demanda_valida)
    resposta = cliente.post(
        "/demandas/1/status", data={"status": "Em andamento"}, follow_redirects=True
    )
    texto = unescape(resposta.text)
    assert "Status atualizado com sucesso" in texto
    assert 'de "Pendente" para "Em andamento"' in texto
    assert 'class="destaque"' in texto


def test_mesmo_status_nao_gera_mensagem_de_sucesso(cliente, demanda_valida):
    cadastrar(cliente, demanda_valida)
    resposta = cliente.post(
        "/demandas/1/status", data={"status": "Pendente"}, follow_redirects=True
    )
    texto = unescape(resposta.text)
    assert "Status atualizado com sucesso" not in texto
    assert 'já está com o status "Pendente"' in texto


def test_status_invalido_e_recusado(cliente, demanda_valida):
    cadastrar(cliente, demanda_valida)
    resposta = cliente.post("/demandas/1/status", data={"status": "Arquivada"})
    assert resposta.status_code == 400
    assert "Pendente" in cliente.get("/demandas/1").text


def test_demanda_inexistente_retorna_404(cliente):
    resposta = cliente.post("/demandas/99/status", data={"status": "Concluída"})
    assert resposta.status_code == 404


def test_painel_e_filtro_refletem_o_novo_status(cliente, demanda_valida):
    cadastrar(cliente, demanda_valida)
    cadastrar(cliente, {**demanda_valida, "titulo": "Buraco na rua principal"})
    cliente.post("/demandas/2/status", data={"status": "Concluída"})

    painel = cliente.get("/").text
    assert painel.count("<strong>1</strong>") == 2  # uma pendente e uma concluída

    concluidas = cliente.get("/demandas?status=Concluída").text
    assert "Buraco na rua principal" in concluidas
    assert "Lixeira quebrada" not in concluidas


def test_atualizar_pela_tela_de_detalhes_volta_para_ela(cliente, demanda_valida):
    cadastrar(cliente, demanda_valida)
    resposta = cliente.post(
        "/demandas/1/status", data={"status": "Concluída", "origem": "detalhe"}
    )
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/demandas/1")


def test_confirmar_sem_escolher_status_pede_a_escolha(cliente, demanda_valida):
    cadastrar(cliente, demanda_valida)
    resposta = cliente.post("/demandas/1/status", data={"status": ""}, follow_redirects=True)
    texto = unescape(resposta.text)
    assert "Escolha o novo status da demanda 0001 antes de confirmar" in texto
    assert "Status atualizado com sucesso" not in texto
    assert "Pendente" in cliente.get("/demandas/1").text


def test_seletor_nao_oferece_o_status_atual(cliente, demanda_valida):
    cadastrar(cliente, demanda_valida)
    texto = cliente.get("/demandas").text
    seletor = texto[texto.index('id="status-1"'):]
    seletor = seletor[: seletor.index("</select>")]
    assert "Escolha o novo status" in seletor
    assert "<option>Pendente</option>" not in seletor
    assert "<option>Em andamento</option>" in seletor
