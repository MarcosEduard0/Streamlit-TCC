NOMES_PAYLOADS = {
    "Volumes": [
        "BogNGAvilVol",
        "ActualVolTotal",
        "LNGActVol",
        "InvForecast",
        "NGAvailVol",
        "TotalLNGSchedVol",
        "LNGAvailVol",
    ],
    "Prices": [
        "Forward",
        "Settle",
    ],
}


def conectar_ftp():
    ftp = FTP(FTP_HOST)
    ftp.login(user=FTP_USUARIO, passwd=FTP_SENHA)
    return ftp


def verificar_status_payload(ftp, nome_arquivo, diretorio):
    try:
        # Diretórios a serem verificados
        status_dirs = {
            "AGUARDANDO": diretorio,
            "COMPLETO": f"{diretorio}/Completed",
            "FALHA": f"{diretorio}/Failed",
        }

        # Verifica em cada diretório o status do arquivo
        for status, caminho in status_dirs.items():
            ftp.cwd("/")
            ftp.cwd(caminho)
            if nome_arquivo in ftp.nlst():
                return status

    except Exception:
        return "ERRO"

    return "AUSENTE"


def monitorar_arquivos():
    with conectar_ftp() as ftp:
        dia, mes, ano = obter_data_anterior()
        relatorio_status = {}

        for diretorio, nomes_payload in NOMES_PAYLOADS.items():
            for nome_payload in nomes_payload:
                nome_arquivo = f"{nome_payload}{ano}{mes}{dia}.xlsx"
                status = verificar_status_payload(
                    ftp, nome_arquivo, FTP_DIRETORIO + diretorio
                )
                relatorio_status[nome_payload] = status

        # Verifica se todos os Payloads estão completos
        status_incompleto = {
            k: v for k, v in relatorio_status.items() if v != "COMPLETO"
        }
        if status_incompleto:
            status_incompleto_str = "\n".join(
                [f"{k}: {v}" for k, v in status_incompleto.items()]
            )
            raise RuntimeError(
                f"Um ou mais payloads não estão completos:\n\n{status_incompleto_str}"
            )
