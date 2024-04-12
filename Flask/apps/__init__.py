# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os  # Importe o módulo os para usar funcionalidades relacionadas ao sistema operacional
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module

db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ("authentication", "home"):
        module = import_module("apps.{}.routes".format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):
    app.config["db_initialized"] = False

    @app.before_request
    def initialize_database():
        if not app.config["db_initialized"]:
            try:
                db.create_all()
                app.config["db_initialized"] = True
            except Exception as e:
                print("> Error: DBMS Exception: " + str(e))
                # fallback to SQLite
                basedir = os.path.abspath(os.path.dirname(__file__))
                app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
                    basedir, "db.sqlite3"
                )
                print("> Fallback to SQLite ")
                db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app
