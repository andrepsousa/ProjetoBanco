import re
import psycopg2  # noqa: F401
from psycopg2 import sql  # noqa: F401
from src.database import (
    conectar_banco,
    criar_conta_db,
    registrar_transacao_db
)


class Conta:

    taxa = 0.50
    plano_mensal = 10
    contas = {}
    chaves_pix = {}

    def __init__(self, numero, titular, saldo=0):
        self._numero = numero
        self.titular = titular
        self.__saldo = saldo
        if not self.__conta_existe():
            criar_conta_db(self._numero, self.titular, self.__saldo)
        Conta.contas[self._numero] = self
        self.__historico = []
        self.__plano_assinado = False

        self.mensalidade()

    def __conta_existe(self):
        conn = conectar_banco()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM contas WHERE numero = %s", (self._numero))
                existe = cursor.fetchone() is not None
                cursor.close()
                conn.close()
                return existe
            except Exception as banco:
                print(f'Erro ao verificar conta: {banco}')
                return False
        return False

    def get_titular(self):
        return self.titular

    def set_titular(self, titular):
        self.titular = titular

    def get_saldo(self):
        return self.__saldo

    def set_saldo(self, valor):
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

    def transacao(self, tipo_transacao, valor):
        saldo_atual = self.get_saldo()
        self.__historico.append((tipo_transacao, valor, saldo_atual))
        (registrar_transacao_db(self._numero, tipo_transacao, valor,
                                saldo_atual))

    def extrato(self):
        if not self.__plano_assinado:
            saldo_atual = self.get_saldo() - Conta.taxa
            self.set_saldo(saldo_atual)
            self.transacao('Taxa', Conta.taxa)
        else:
            saldo_atual = self.get_saldo()
        for transacao in self.__historico:
            if isinstance(transacao, tuple) and len(transacao) == 3:
                tipo_transacao, valor, saldo = transacao
                print(f'Tipo: {tipo_transacao} | '
                      f'Valor: R${valor:.2f} | Saldo: R${saldo:.2f}')

    def depositar(self, valor):
        if valor > 0:
            self.set_saldo(self.get_saldo() + valor)
            print('Depósito realizado com sucesso!')
            self.transacao('Depósito', valor)
        else:
            print('O valor do depósito deve ser positivo.')

    def transferir(self, valor, numero):
        if numero in Conta.contas:
            conta_destino = Conta.contas[numero]
            if self.get_saldo() >= valor:
                self.set_saldo(self.get_saldo() - valor)
                conta_destino.set_saldo(conta_destino.get_saldo() + valor)
                print(f'Transferência realizada com sucesso. Saldo atual: '
                      f'R${self.get_saldo()}')
                self.transacao('Transferência', valor)
            else:
                print('Saldo insuficiente para realizar a transferência.')
        else:
            print('Conta de destino não encontrada.')

    def sacar(self, valor):
        if valor > 0 and valor <= self.get_saldo():
            self.set_saldo(self.get_saldo() - valor)
            print('Saque realizado com sucesso!')
            self.transacao('Saque', valor)
        else:
            print('Saldo insuficiente ou valor inválido para saque.')

    def pix(self, valor, chave):
        if valor > 0 and valor <= self.get_saldo():
            self.set_saldo(self.get_saldo() - valor)
            self.chave = chave
            print('Transferência realizada com sucesso!')
            self.transacao('Pix', valor)
        else:
            print('Saldo insuficiente ou valor inválido para transferência.')

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
            for indice, (tipo, chave) in enumerate(self.chaves_pix.items(),
                                                   start=1):
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
