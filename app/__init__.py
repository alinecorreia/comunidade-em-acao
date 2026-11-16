"""Comunidade em Ação: gestão de demandas comunitárias (MVP)."""

import os
from datetime import date

from flask import Flask

from . import db, regras


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # Em produção, defina SECRET_KEY no ambiente. O valor padrão serve só para desenvolvimento.
        SECRET_KEY=os.environ.get("SECRET_KEY", "chave-apenas-para-desenvolvimento"),
        DATABASE=os.path.join(app.instance_path, "comunidade.sqlite"),
    )
    if config:
        app.config.update(config)

    os.makedirs(app.instance_path, exist_ok=True)

    @app.template_filter("numero")
    def filtro_numero(identificador):
        return regras.numero_formatado(identificador)

    @app.template_filter("data_br")
    def filtro_data_br(texto_iso):
        return date.fromisoformat(texto_iso).strftime("%d/%m/%Y")

    db.registrar(app)

    from .rotas import bp

    app.register_blueprint(bp)
    return app
