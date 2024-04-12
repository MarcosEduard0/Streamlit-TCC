# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
import pandas as pd

D_PERIODO = pd.read_csv("../marcos/data/refined/d_periodo.csv")
D_ALUNO = pd.read_csv("../marcos/data/refined/d_aluno.csv")
F_DESEMPENHO_ACADEMICO = pd.read_csv(
    "../marcos/data/refined/f_desempenho_academico.csv"
)
F_MATRICULA_ALUNO = pd.read_csv("../marcos/data/refined/f_matricula_aluno.csv")

cra_periodo = pd.merge(
    D_PERIODO, F_DESEMPENHO_ACADEMICO, on="sk_d_periodo", how="inner"
)


def prepare_data_genero(situacao="Ativa"):
    df_genero = pd.merge(D_ALUNO, F_MATRICULA_ALUNO, on="sk_d_aluno", how="inner")
    df_genero = df_genero[
        (df_genero["situacao_matricula"] == situacao)
        & (df_genero["periodo"] == "2022/1")
    ]
    df_genero = df_genero.groupby(["sexo"]).size().reset_index(name="quantidade")
    df_genero.loc[len(df_genero)] = ["Ambos", df_genero["quantidade"].sum()]
    return df_genero.set_index("sexo")["quantidade"].to_dict()


def prepare_data_cr():
    cra_periodo_filtrado = (
        cra_periodo[
            (cra_periodo["periodo"].str.contains("/1"))
            | (cra_periodo["periodo"].str.contains("/2"))
        ]
        .groupby(["periodo"])["cr_acumulado"]
        .mean()
        .reset_index(name="cr_acumulado")
    )
    return {
        "periodos": cra_periodo_filtrado["periodo"].tolist(),
        "cr_acumulado": cra_periodo_filtrado["cr_acumulado"].tolist(),
        "media_cra": round(cra_periodo_filtrado["cr_acumulado"].mean(), 2),
    }


@blueprint.route("/index")
# @login_required
def index():

    # return render_template("home/index.html", segment="index")

    return render_template(
        "home/index.html",
        segment="index",
        metricas_cr=prepare_data_cr(),
        quant_genero=prepare_data_genero(),
        quant_genero_abandono=prepare_data_genero("Cancelada"),
    )


@blueprint.route("/<template>")
# @login_required
def route_template(template):

    try:

        if not template.endswith(".html"):
            template += ".html"

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template("home/page-404.html"), 404

    except:
        return render_template("home/page-500.html"), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split("/")[-1]

        if segment == "":
            segment = "index"

        return segment

    except:
        return None
