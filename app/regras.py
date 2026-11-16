"""Regras de negócio das demandas, sem dependência de Flask ou do banco."""

STATUS = ["Pendente", "Em andamento", "Concluída"]
STATUS_INICIAL = "Pendente"
PRIORIDADES = ["Alta", "Média", "Baixa"]
CATEGORIAS = [
    "Iluminação pública",
    "Limpeza urbana",
    "Infraestrutura",
    "Meio ambiente",
    "Trânsito",
]
# Nomes fictícios, usados apenas para demonstração do MVP.
RESPONSAVEIS = ["Ana Souza", "João Pereira", "Marina Costa"]

TAMANHO_MAX_TITULO = 80
TAMANHO_MAX_DESCRICAO = 1000


def validar_demanda(dados):
    """Valida os campos do formulário de cadastro.

    Recebe um dicionário com os valores enviados e devolve uma tupla
    (limpos, erros). `erros` é um dicionário campo -> mensagem; vazio
    significa que a demanda pode ser gravada.
    """
    limpos = {
        "titulo": (dados.get("titulo") or "").strip(),
        "descricao": (dados.get("descricao") or "").strip(),
        "categoria": (dados.get("categoria") or "").strip(),
        "prioridade": (dados.get("prioridade") or "").strip(),
        "responsavel": (dados.get("responsavel") or "").strip(),
    }
    erros = {}

    if not limpos["titulo"]:
        erros["titulo"] = "O título é obrigatório. Informe um título para a demanda."
    elif len(limpos["titulo"]) > TAMANHO_MAX_TITULO:
        erros["titulo"] = f"O título deve ter no máximo {TAMANHO_MAX_TITULO} caracteres."

    if not limpos["descricao"]:
        erros["descricao"] = "A descrição é obrigatória. Descreva o problema e o local."
    elif len(limpos["descricao"]) > TAMANHO_MAX_DESCRICAO:
        erros["descricao"] = (
            f"A descrição deve ter no máximo {TAMANHO_MAX_DESCRICAO} caracteres."
        )

    if limpos["categoria"] not in CATEGORIAS:
        erros["categoria"] = "Selecione uma categoria da lista."

    if limpos["prioridade"] not in PRIORIDADES:
        erros["prioridade"] = "Selecione a prioridade da demanda."

    if limpos["responsavel"] and limpos["responsavel"] not in RESPONSAVEIS:
        erros["responsavel"] = "Selecione um responsável da lista ou deixe em branco."

    return limpos, erros


def status_valido(status):
    """Indica se o status informado é um dos três aceitos pelo sistema."""
    return status in STATUS


def resumo_por_status(contagens):
    """Completa as contagens com zero para os status sem demandas.

    `contagens` é um dicionário status -> quantidade vindo do banco.
    """
    return {status: int(contagens.get(status, 0)) for status in STATUS}


def numero_formatado(identificador):
    """Formata o número da demanda com quatro dígitos, como 0018."""
    return f"{int(identificador):04d}"
