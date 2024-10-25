import logging
from decimal import Decimal
import psycopg2
from psycopg2 import OperationalError, IntegrityError, ProgrammingError

# Configuração básica de logs
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def conectar_banco():
    try:
        conn = psycopg2.connect(
            dbname='meu_banco',
            user='postgres',
            password='andre159375',
            host='localhost',
            port='5432'
        )
        return conn
    except OperationalError as e:
        logging.error(f'Erro operacional ao conectar ao banco de dados: {e}')
    except Exception as e:
        logging.error(f'Erro inesperado ao conectar ao banco de dados: {e}')
    return None


def criar_conta_db(conn, numero, titular, saldo):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO contas (numero, titular, saldo)
                VALUES (%s, %s, %s)
            """, (numero, titular, saldo))
            conn.commit()
    except IntegrityError as e:
        logging.error(f'Erro de integridade ao criar conta: {e}')
    except ProgrammingError as e:
        logging.error(f'Erro de sintaxe ao criar conta: {e}')
    except Exception as e:
        logging.error(f'Erro inesperado ao criar conta: {e}')
        conn.rollback()  # Certifique-se de fazer rollback em caso de erro
    finally:
        if conn:
            conn.close()


def registrar_transacao_db(numero: int, tipo: str, valor: Decimal,
                           saldo: Decimal) -> None:
    conn = None
    try:
        conn = conectar_banco()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO transacoes (conta_numero, tipo, valor, "
                    "saldo) VALUES (%s, %s, %s, %s)",
                    (numero, tipo, valor, saldo)
                )
                conn.commit()
    except IntegrityError as e:
        logging.error(f'Erro de integridade ao registrar transação: {e}')
    except ProgrammingError as e:
        logging.error(f'Erro de sintaxe ao registrar transação: {e}')
    except Exception as e:
        logging.error(f"Erro inesperado ao registrar transação: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


def buscar_contas(conn, numero=None, titular=None):
    query = "SELECT * FROM contas"
    params = []

    if numero is not None:
        query += " WHERE numero = %s"
        params.append(numero)
    elif titular is not None:
        query += " WHERE titular = %s"
        params.append(titular)

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            contas = cursor.fetchall()
            if contas:
                conta = contas[0]
                return {
                    'numero': conta[0],
                    'titular': conta[1],
                    'saldo': conta[2]
                }
            return None
    except ProgrammingError as e:
        logging.error(f'Erro de sintaxe ao buscar conta: {e}')
    except Exception as e:
        logging.error(f'Erro inesperado ao buscar conta: {e}')
        return None
