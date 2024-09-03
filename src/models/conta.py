import re
from decimal import Decimal
import psycopg2  # noqa: F401
from src.database import conectar_banco, criar_conta_db, registrar_transacao_db
from typing import Optional


class Conta:

    taxa = 0.50
    plano_mensal = Decimal('10.00')
    contas = {}
    chaves_pix = {}

    def __init__(
            self, numero: int, titular: str, saldo: Decimal = Decimal('0.00')):
        self._numero = numero
        self.titular = titular
        self.__saldo = saldo
        if not self.__conta_existe():
            conn = conectar_banco()
            if conn:
                criar_conta_db(conn, self._numero, self.titular, self.__saldo)
                conn.close()
        Conta.contas[self._numero] = self
        self.__historico = []
        self.__plano_assinado = False

        self.mensalidade()

    def __conta_existe(self):
        conn = conectar_banco()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT 1 FROM contas WHERE numero = %s",
                        (self._numero,))
                    existe = cursor.fetchone() is not None
                cursor.close()
                return existe
            except Exception as banco:
                print(f'Erro ao verificar conta: {banco}')
                return False
        return False

    def get_titular(self):
        return self.titular

    def set_titular(self, titular):
        self.titular = titular

    def get_saldo(self) -> Decimal:
        return self.__saldo

    def set_saldo(self, valor: Decimal) -> None:
        self.__saldo = valor

    def mensalidade(self):
        if not self.__plano_assinado:
            print('Deseja assinar nosso plano de benefícios por apenas '
                  'R$10,00 por mês?')
            print('1 - Sim')
            print('2 - Não')

            escolha_mensal = input('Digite o número da opção desejada: ')
            if escolha_mensal == '1':
                print('Você escolheu assinar o plano.')
                self.set_saldo(self.get_saldo() - Conta.plano_mensal)
                self.__plano_assinado = True
            elif escolha_mensal == '2':
                print('Você escolheu não assinar o plano.')
            else:
                print('Opção inválida. Por favor, '
                      'escolha 1 para Sim ou 2 para Não.')
                self.mensalidade()

    def saldo(self):
        print(f'Saldo: R${self.__saldo}')

    def transacao(self, tipo: str, valor: Decimal) -> None:
        saldo_atual = self.get_saldo()
        try:
            conn = conectar_banco()
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO transacoes (conta_numero, tipo, "
                        "valor, saldo) VALUES (%s, %s, %s, %s)",
                        (self._numero, tipo, valor, saldo_atual)
                    )
                    conn.commit()
        except Exception as banco:
            print(f"Erro ao registrar transação: {banco}")
        finally:
            if conn:
                conn.close()

        self.__historico.append(
            (tipo, Decimal(str(valor)), saldo_atual)
        )

        registrar_transacao_db(
            self._numero, tipo, valor, saldo_atual)

    def extrato(self) -> None:
        if not self.__plano_assinado:
            saldo_atual = self.get_saldo() - Decimal(Conta.taxa)
            self.set_saldo(saldo_atual)
            self.transacao('Taxa', Decimal(Conta.taxa))
        else:
            saldo_atual = self.get_saldo()
        for transacao in self.__historico:
            if isinstance(transacao, tuple) and len(transacao) == 3:
                tipo, valor, saldo = transacao
                valor = Decimal(str(valor))
                saldo = Decimal(str(saldo))
                print(f'Tipo: {tipo} | '
                      f'Valor: R${valor:.2f} | Saldo: R${saldo:.2f}')

    def depositar(self, valor: Decimal) -> None:
        if valor > 0:
            valor_decimal = Decimal(str(valor))
            self.set_saldo(self.get_saldo() + valor_decimal)
            print('Depósito realizado com sucesso!')
            self.transacao('Depósito', valor_decimal)
        else:
            print('O valor do depósito deve ser positivo.')

    def transferir(self, valor: Decimal, conta_destino_numero: int) -> None:
        conta_destino = self.buscar_conta_por_numero(conta_destino_numero)

        if not conta_destino:
            print("Conta destino não encontrada.")
            return

        valor = Decimal(str(valor))
        saldo_atual = self.get_saldo()

        if saldo_atual >= valor:
            saldo_atual -= valor
            self.set_saldo(saldo_atual)

            self.transacao('Transferência', valor)

            conta_destino.depositar(valor)

            print(f'Transferência realizada com sucesso. '
                  f'Saldo atual: R${self.get_saldo()}')
        else:
            print('Saldo insuficiente para realizar a transferência.')

    @staticmethod
    def buscar_conta_por_numero(numero: int) -> Optional['Conta']:
        conn = None
        try:
            conn = conectar_banco()
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM contas WHERE numero = %s", (numero,))
                    resultado = cursor.fetchone()
                    if resultado:
                        return Conta(
                            numero=resultado[0],
                            titular=resultado[1],
                            saldo=Decimal(resultado[2])
                        )
        except Exception as banco:
            print(f"Erro ao buscar conta: {banco}")
        finally:
            if conn:
                conn.close()
        return None

    def sacar(self, valor: Decimal) -> None:
        valor = Decimal(str(valor))
        saldo_atual = self.get_saldo()
        if saldo_atual >= valor:
            saldo_atual -= valor
            self.set_saldo(saldo_atual)
            self.transacao('Saque', valor)
            print("Saque realizado com sucesso!")
        else:
            print('Saldo insuficiente ou valor inválido para saque.')

    def pix(self, valor: Decimal, conta_destino: 'Conta') -> None:
        if not isinstance(conta_destino, Conta):
            print("Erro: conta_destino deve ser uma instância da "
                  "classe Conta.")
            return
        valor = Decimal(str(valor))
        saldo_atual = self.get_saldo()
        if saldo_atual >= valor:
            saldo_atual -= valor
            self.set_saldo(saldo_atual)
            self.transacao('PIX', valor)
            conta_destino.depositar(valor)
            print("PIX realizado com sucesso!")
        else:
            print("Saldo insuficiente.")

    def cadastrar_chave_pix(self, chave):
        tipo_chave = self.tipo_chave(chave)
        if tipo_chave == 'Tipo desconhecido':
            print('Chave Pix inválida! Não foi possível cadastrar.')
        else:
            self.chaves_pix[tipo_chave] = chave
            print(f'Chave Pix do tipo "{tipo_chave}" cadastrada com sucesso!')

    def listar_chaves_pix(self, exibir_indice=True):
        if self.chaves_pix:
            print('Chaves Pix cadastradas: ')
            for indice, (tipo, chave) in enumerate(
                    self.chaves_pix.items(), start=1):
                if exibir_indice:
                    print(f'{indice}. Tipo: {tipo}, Chave: {chave}')
        else:
            print('Nenhuma chave Pix cadastrada!')

    def tipo_chave(self, chave):
        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', chave):
            return 'E-mail'
        elif (re.match(r'^\d{11}$', chave) and
              not re.match(r'^(\d{2})?9\d{8}$', chave)):
            return 'CPF'
        elif re.match(r'^\d{14}$', chave):
            return 'CNPJ'
        elif (re.match(r'^\d{10,11}$', chave) and
              re.match(r'^(\d{2})?9\d{8}$', chave)):
            return 'Telefone'
        elif len(chave) == 32 and re.match(r'^[a-zA-Z0-9]+$', chave):
            return 'Chave Aleatória'
        else:
            return 'Tipo desconhecido'

    def remover_chave_pix(self, indice):
        try:
            indice = int(indice) - 1
            chave_remover = list(self.chaves_pix.keys())[indice]
            self.chaves_pix.pop(chave_remover)
            print(f'Chave Pix "{chave_remover}" removida com sucesso!')
        except (IndexError, ValueError):
            print('Índice inválido. Tente novamente.')
