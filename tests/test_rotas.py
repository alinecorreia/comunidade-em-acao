"""Testes de integração: rotas, banco e templates funcionando juntos."""


def cadastrar(cliente, dados):
    return cliente.post("/demandas/nova", data=dados, follow_redirects=True)


def test_painel_vazio(cliente):
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert "Nenhuma demanda cadastrada ainda" in resposta.text


def test_cadastro_grava_com_status_pendente(cliente, demanda_valida):
    resposta = cadastrar(cliente, demanda_valida)
    assert resposta.status_code == 200
    assert "Demanda 0001 cadastrada com sucesso" in resposta.text
    assert "Lixeira quebrada na praça" in resposta.text
    assert "Pendente" in resposta.text


def test_cadastro_sem_titulo_mostra_erro_e_nao_grava(cliente, demanda_valida):
    demanda_valida["titulo"] = ""
    resposta = cliente.post("/demandas/nova", data=demanda_valida)
    assert resposta.status_code == 400
    assert "O título é obrigatório" in resposta.text
    # Os outros campos preenchidos continuam na tela.
    assert "A lixeira ao lado do parquinho" in resposta.text
    assert "0 demandas encontradas" in cliente.get("/demandas").text


def test_painel_mostra_contagem_de_pendentes(cliente, demanda_valida):
    cadastrar(cliente, demanda_valida)
    cadastrar(cliente, demanda_valida)
    texto = cliente.get("/").text
    assert "<strong>2</strong>" in texto  # duas pendentes
    assert "<strong>0</strong>" in texto  # nenhuma em andamento ou concluída


def test_demanda_inexistente_retorna_404(cliente):
    assert cliente.get("/demandas/99").status_code == 404


def test_filtro_por_categoria_e_busca(cliente, demanda_valida):
    cadastrar(cliente, demanda_valida)
    cadastrar(cliente, {**demanda_valida, "titulo": "Buraco na rua principal",
                        "categoria": "Infraestrutura", "prioridade": "Alta"})

    infraestrutura = cliente.get("/demandas?categoria=Infraestrutura").text
    assert "Buraco na rua principal" in infraestrutura
    assert "Lixeira quebrada" not in infraestrutura

    busca = cliente.get("/demandas?busca=lixeira").text
    assert "Lixeira quebrada" in busca
    assert "Buraco na rua principal" not in busca

    assert "Nenhuma demanda encontrada" in cliente.get("/demandas?prioridade=Baixa").text


def test_detalhe_mostra_dados_da_demanda(cliente, demanda_valida):
    cadastrar(cliente, demanda_valida)
    texto = cliente.get("/demandas/1").text
    assert "Demanda 0001" in texto
    assert "Ana Souza" in texto


def test_conteudo_digitado_e_escapado(cliente, demanda_valida):
    demanda_valida["titulo"] = "<script>alert(1)</script>"
    cadastrar(cliente, demanda_valida)
    assert "<script>alert(1)</script>" not in cliente.get("/demandas").text


def test_formulario_tem_contador_de_caracteres(cliente):
    texto = cliente.get("/demandas/nova").text
    assert 'id="contador-descricao"' in texto
    assert "caracteres usados" in texto
