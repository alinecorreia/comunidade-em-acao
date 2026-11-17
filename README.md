# Comunidade em Ação

MVP de gestão de demandas comunitárias. Uma associação de moradores registra os pedidos da comunidade (iluminação, limpeza, infraestrutura), acompanha o status de cada um e consulta o histórico em um só lugar, no lugar de cadernos e mensagens espalhadas.

Projeto acadêmico relacionado ao ODS 11 (Cidades e Comunidades Sustentáveis).

## Funcionalidades

- **Painel:** total de demandas pendentes, em andamento e concluídas, e lista das mais recentes.
- **Cadastro de demanda:** título, descrição, categoria, prioridade e responsável opcional. Toda demanda nova entra como "Pendente".
- **Consulta e acompanhamento:** busca por título ou número, filtros por categoria, prioridade, status e responsável, e atualização de status com mensagem de confirmação.
- **Acessibilidade:** status e prioridade sempre com símbolo e texto, nunca só com cor. Rótulos em todos os campos, mensagens de erro ao lado do campo e navegação por teclado.

Fora do escopo desta versão: login de usuários, relatórios e envio de comunicados.

## Tecnologias

Python 3.12, Flask, SQLite, pytest e GitHub Actions.

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app app dados-exemplo    # opcional: insere demandas fictícias
flask --app app run
```

Acesse http://127.0.0.1:5000. O banco é criado automaticamente em `instance/comunidade.sqlite`.

## Publicação

O arquivo `render.yaml` publica a aplicação no [Render](https://render.com) com gunicorn. No ambiente publicado, a variável `DADOS_EXEMPLO=1` carrega as demandas fictícias e exibe um aviso de demonstração.

O plano gratuito não tem disco persistente: o banco SQLite é recriado a cada reinício do serviço. Serve para demonstração, não para uso real da associação.

A rota `/saude` responde se a aplicação e o banco estão funcionando e é usada pelo monitoramento.

## Testes

```bash
pytest                                        # roda os testes
pytest --cov=app --cov-report=term-missing    # roda os testes e mostra a cobertura
```

- `tests/test_regras.py`: testes unitários das regras de validação.
- `tests/test_rotas.py`: testes de integração das telas com o banco.

Os testes rodam automaticamente a cada push e Pull Request pela Integração Contínua (`.github/workflows/ci.yml`).

## Estrutura

```
app/
  __init__.py     criação da aplicação
  regras.py       validações e listas (categorias, prioridades, status)
  db.py           acesso ao SQLite
  rotas.py        telas e ações
  templates/      páginas HTML
  static/         folha de estilo
tests/            testes unitários e de integração
```

## Versionamento

Os commits seguem o padrão [Conventional Commits](https://www.conventionalcommits.org/pt-br/) (`feat`, `fix`, `test`, `docs`, `ci`, `chore`). Mudanças entram na `main` por Pull Request, com revisão antes do merge.

## Dados

Todos os nomes e demandas de exemplo são fictícios. O sistema não coleta documentos, telefones ou endereços de moradores.
