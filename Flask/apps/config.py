# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - UFRJ
"""

import os, random, string


class Config(object):

    caminho_base = os.path.abspath(os.path.dirname(__file__))

    # Gerenciamento de Assets
    RAIZ_ASSETS = os.getenv("RAIZ_ASSETS", "/static/assets")

    # Configure o aplicativo SECRET_KEY
    SECRET_KEY = os.getenv("SECRET_KEY", None)
    if not SECRET_KEY:
        SECRET_KEY = "".join(random.choice(string.ascii_lowercase) for i in range(32))

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_ENGINE = os.getenv("DB_ENGINE", None)
    DB_USUARIO = os.getenv("DB_USUARIO", None)
    DB_SENHA = os.getenv("DB_SENHA", None)
    DB_HOST = os.getenv("DB_HOST", None)
    DB_PORTA = os.getenv("DB_PORTA", None)
    DB_NOME = os.getenv("DB_NOME", None)

    USE_SQLITE = True

    # Tentar configurar um SGBD Relacional
    if DB_ENGINE and DB_NOME and DB_USUARIO:

        try:

            # SGBD Relacional: PSQL, MySql
            SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}:{}/{}".format(
                DB_ENGINE, DB_USUARIO, DB_SENHA, DB_HOST, DB_PORTA, DB_NOME
            )

            USE_SQLITE = False

        except Exception as e:

            print("> Error: DBMS Exception: " + str(e))
            print("> Fallback to SQLite ")

    if USE_SQLITE:

        # Isso criará um arquivo na PASTA <app>
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
            caminho_base, "db.sqlite3"
        )


class ProductionConfig(Config):
    DEBUG = False

    # Seguranca
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURACAO = 3600


class DebugConfig(Config):
    DEBUG = True


# Carregue todas as configurações possíveis
config_dict = {"Production": ProductionConfig, "Debug": DebugConfig}
