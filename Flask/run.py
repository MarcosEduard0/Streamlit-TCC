# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - UFRJ
"""

import os
from flask_migrate import Migrate
from flask_minify import Minify
from sys import exit

from apps.config import config_dict
from apps import create_app, db

from flask_socketio import SocketIO

# AVISO: Não execute com o modo de debug ativado em produção!
DEBUG = os.getenv("DEBUG", "False") == "True"

# Configuração
get_config_mode = "Debug" if DEBUG else "Production"

try:

    # Carrega a configuração usando os valores padrão
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit("Erro: <config_mode> inválido. Valores esperados [Debug, Production]")

app = create_app(app_config)
socketio = SocketIO(app)
Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

if DEBUG:
    app.logger.info("DEBUG            = " + str(DEBUG))
    app.logger.info("Page Compression = " + "FALSE" if DEBUG else "TRUE")
    app.logger.info("DBMS             = " + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info("ASSETS_ROOT      = " + app_config.ASSETS_ROOT)

if __name__ == "__main__":
    # app.run()
    socketio.run(app, debug=True)
