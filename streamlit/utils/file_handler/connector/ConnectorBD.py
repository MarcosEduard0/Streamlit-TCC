from pyrfc import Connection, CommunicationError, LogonError


class ConnectorDB:
    """
    A classe ConnectorSap é responsável por criar uma conexão SAP usando a biblioteca pyrfc.

    Args:
        sap_user (str): O nome de usuário SAP.
        sap_pwd (str): A senha do usuário SAP.
        sap_system (str): O nome do sistema SAP.
        sap_host (str): O endereço do servidor SAP.
        sap_sys (str): O número do sistema SAP.
        sap_client (str): O código de cliente SAP.

    Methods:
        conn(): Cria e retorna uma conexão SAP.

    Raises:
        CommunicationError: Se houver um erro de comunicação ao conectar-se ao servidor SAP.
        LogonError: Se houver um erro de logon ao autenticar-se no sistema SAP.
        Exception: Se ocorrer qualquer outro erro durante a criação da conexão.

    Example:
        sap_connector = ConnectorSap(sap_user="usuário", sap_pwd="senha", sap_system="systema", sap_host="hostname", sap_sys="04", sap_client="400")
        sap_connection = sap_connector.conn()
    """

    def __init__(self, sap_user, sap_pwd, sap_system, sap_host, sap_sys, sap_client):
        self.sap_user = sap_user
        self.sap_pwd = sap_pwd
        self.sap_system = sap_system
        self.sap_host = sap_host
        self.sap_sys = sap_sys
        self.sap_client = sap_client

    def conn(self):
        try:
            connection = Connection(
                user=self.sap_user,
                passwd=self.sap_pwd,
                name=self.sap_system,
                ashost=self.sap_host,
                sysnr=self.sap_sys,
                client=self.sap_client,
            )
            return connection
        except CommunicationError as e:
            print(f"Could not connect to server: {e}")
        except LogonError as e:
            print(f"Could not log in. Please check your ID/PW: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
