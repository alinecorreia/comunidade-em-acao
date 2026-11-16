"""Acesso ao banco SQLite."""

import sqlite3
from datetime import date, timedelta

import click
from flask import current_app, g

from .regras import STATUS_INICIAL

ESQUEMA = """
CREATE TABLE IF NOT EXISTS demanda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL,
    prioridade TEXT NOT NULL,
    responsavel TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL,
    criada_em TEXT NOT NULL
);
"""

# Dados fictícios para demonstração. Nenhum corresponde a pessoas ou locais reais.
EXEMPLOS = [
    ("Vazamento de água na calçada", "Água escorrendo na calçada em frente à quadra.",
     "Infraestrutura", "Alta", "", "Pendente"),
    ("Falta de sinalização", "Cruzamento sem placa de pare.",
     "Trânsito", "Baixa", "João Pereira", "Concluída"),
    ("Poda de árvore", "Galhos encostando na fiação da rua.",
     "Meio ambiente", "Média", "Ana Souza", "Em andamento"),
    ("Buraco na rua principal", "Buraco grande perto do ponto de ônibus.",
     "Infraestrutura", "Alta", "Marina Costa", "Concluída"),
    ("Coleta de lixo irregular", "O caminhão não passou nas duas últimas semanas.",
     "Limpeza urbana", "Média", "João Pereira", "Em andamento"),
    ("Lâmpada apagada na praça", "Poste ao lado do parquinho está sem luz.",
     "Iluminação pública", "Alta", "Ana Souza", "Pendente"),
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def fechar_db(_erro=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def criar_tabelas():
    get_db().executescript(ESQUEMA)


def inserir_demanda(dados, criada_em=None, status=STATUS_INICIAL):
    """Grava uma demanda já validada e devolve o número gerado."""
    db = get_db()
    cursor = db.execute(
        "INSERT INTO demanda (titulo, descricao, categoria, prioridade, responsavel,"
        " status, criada_em) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            dados["titulo"],
            dados["descricao"],
            dados["categoria"],
            dados["prioridade"],
            dados.get("responsavel", ""),
            status,
            criada_em or date.today().isoformat(),
        ),
    )
    db.commit()
    return cursor.lastrowid


def buscar_demanda(identificador):
    return get_db().execute(
        "SELECT * FROM demanda WHERE id = ?", (identificador,)
    ).fetchone()


def listar_demandas(filtros=None, limite=None):
    """Lista demandas da mais recente para a mais antiga, aplicando os filtros."""
    filtros = filtros or {}
    condicoes, valores = [], []

    busca = (filtros.get("busca") or "").strip()
    if busca:
        if busca.isdigit():
            condicoes.append("(id = ? OR titulo LIKE ?)")
            valores += [int(busca), f"%{busca}%"]
        else:
            condicoes.append("titulo LIKE ?")
            valores.append(f"%{busca}%")

    for campo in ("categoria", "prioridade", "status"):
        if filtros.get(campo):
            condicoes.append(f"{campo} = ?")
            valores.append(filtros[campo])

    responsavel = filtros.get("responsavel")
    if responsavel == "Não atribuído":
        condicoes.append("responsavel = ''")
    elif responsavel:
        condicoes.append("responsavel = ?")
        valores.append(responsavel)

    sql = "SELECT * FROM demanda"
    if condicoes:
        sql += " WHERE " + " AND ".join(condicoes)
    sql += " ORDER BY id DESC"
    if limite:
        sql += " LIMIT ?"
        valores.append(limite)
    return get_db().execute(sql, valores).fetchall()


def contar_por_status():
    linhas = get_db().execute(
        "SELECT status, COUNT(*) AS total FROM demanda GROUP BY status"
    ).fetchall()
    return {linha["status"]: linha["total"] for linha in linhas}


def atualizar_status(identificador, novo_status):
    """Altera o status e devolve True quando a demanda existe."""
    db = get_db()
    cursor = db.execute(
        "UPDATE demanda SET status = ? WHERE id = ?", (novo_status, identificador)
    )
    db.commit()
    return cursor.rowcount == 1


def inserir_exemplos():
    """Insere as demandas fictícias e devolve quantas foram gravadas."""
    hoje = date.today()
    for posicao, (titulo, descricao, categoria, prioridade, responsavel, status) in enumerate(
        EXEMPLOS
    ):
        inserir_demanda(
            {
                "titulo": titulo,
                "descricao": descricao,
                "categoria": categoria,
                "prioridade": prioridade,
                "responsavel": responsavel,
            },
            criada_em=(hoje - timedelta(days=len(EXEMPLOS) - 1 - posicao)).isoformat(),
            status=status,
        )
    return len(EXEMPLOS)


def banco_vazio():
    return get_db().execute("SELECT COUNT(*) FROM demanda").fetchone()[0] == 0


@click.command("dados-exemplo")
def comando_dados_exemplo():
    """Insere demandas fictícias para demonstração."""
    click.echo(f"{inserir_exemplos()} demandas fictícias inseridas.")


def registrar(app):
    app.teardown_appcontext(fechar_db)
    app.cli.add_command(comando_dados_exemplo)
    with app.app_context():
        criar_tabelas()
        # No ambiente de demonstração, o banco começa com os exemplos fictícios.
        if app.config.get("DADOS_EXEMPLO") and banco_vazio():
            inserir_exemplos()
