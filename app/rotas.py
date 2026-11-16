"""Telas do sistema: painel, cadastro, consulta e acompanhamento."""

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from . import db, regras

bp = Blueprint("demandas", __name__)


@bp.app_context_processor
def listas_para_templates():
    return {
        "CATEGORIAS": regras.CATEGORIAS,
        "PRIORIDADES": regras.PRIORIDADES,
        "STATUS": regras.STATUS,
        "RESPONSAVEIS": regras.RESPONSAVEIS,
        "TAMANHO_MAX_TITULO": regras.TAMANHO_MAX_TITULO,
        "TAMANHO_MAX_DESCRICAO": regras.TAMANHO_MAX_DESCRICAO,
    }


@bp.get("/")
def painel():
    resumo = regras.resumo_por_status(db.contar_por_status())
    recentes = db.listar_demandas(limite=5)
    return render_template("painel.html", resumo=resumo, demandas=recentes)


@bp.route("/demandas/nova", methods=["GET", "POST"])
def nova_demanda():
    dados, erros = {}, {}
    if request.method == "POST":
        dados, erros = regras.validar_demanda(request.form)
        if not erros:
            numero = db.inserir_demanda(dados)
            flash(
                f"Demanda {regras.numero_formatado(numero)} cadastrada com sucesso "
                f'com o status "{regras.STATUS_INICIAL}".'
            )
            return redirect(url_for("demandas.consulta"))
    codigo = 400 if erros else 200
    return render_template("nova_demanda.html", dados=dados, erros=erros), codigo


@bp.get("/demandas")
def consulta():
    filtros = {
        campo: request.args.get(campo, "").strip()
        for campo in ("busca", "categoria", "prioridade", "status", "responsavel")
    }
    demandas = db.listar_demandas(filtros)
    return render_template(
        "demandas.html",
        demandas=demandas,
        filtros=filtros,
        destaque=request.args.get("destaque", type=int),
    )


@bp.get("/demandas/<int:identificador>")
def detalhe(identificador):
    demanda = db.buscar_demanda(identificador)
    if demanda is None:
        abort(404)
    return render_template("detalhe.html", demanda=demanda)


@bp.post("/demandas/<int:identificador>/status")
def atualizar_status(identificador):
    demanda = db.buscar_demanda(identificador)
    if demanda is None:
        abort(404)

    novo_status = request.form.get("status", "")
    if not regras.status_valido(novo_status):
        abort(400)

    numero = regras.numero_formatado(identificador)
    if novo_status == demanda["status"]:
        flash(f'A demanda {numero} já está com o status "{novo_status}".')
    else:
        db.atualizar_status(identificador, novo_status)
        flash(
            f"Status atualizado com sucesso. A demanda {numero} passou de "
            f'"{demanda["status"]}" para "{novo_status}".'
        )
    if request.form.get("origem") == "detalhe":
        return redirect(url_for("demandas.detalhe", identificador=identificador))
    return redirect(url_for("demandas.consulta", destaque=identificador))
