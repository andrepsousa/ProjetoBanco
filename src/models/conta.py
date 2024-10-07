import re
from decimal import Decimal
import psycopg2  # noqa: F401
from src.database import conectar_banco, criar_conta_db, registrar_transacao_db
from typing import Optional


class Conta:
    """Classe que representa uma conta bancária."""

    taxa = 0.50  # Taxa mensal para o plano
    plano_mensal = Decimal('10.00')  # Valor do plano mensal
    contas = {}  # Dicionário para armazenar contas
    chaves_pix = {}  # Dicionário para armazenar chaves Pix

    def __init__(self, numero: int, titular: str,
                 saldo: Decimal = Decimal('0.00')):
        """Inicializa uma nova conta.

        Args:
            numero (int): Número da conta.
            titular (str): Nome do titular da conta.
            saldo (Decimal): Saldo inicial da conta (default é 0).
        """
        self._numero = numero
        self.titular = titular
        self.__saldo = saldo
        if not self.__conta_existe():
            conn = conectar_banco()
            if conn:
                criar_conta_db(conn, self._numero, self.titular, self.__saldo)
                conn.close()
        Conta.contas[self._numero] = self
        self.__historico = []  # Histórico de transações
        self.__plano_assinado = False  # Indica se o plano foi assinado

        self.mensalidade()  # Solicita assinatura do plano

    def __conta_existe(self) -> bool:
        """Verifica se a conta já existe no banco de dados.

        Returns:
            bool: Verdadeiro se a conta existe, falso caso contrário.
        """
        conn = conectar_banco()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT 1 FROM contas WHERE numero = %s",
                        (self._numero,))
                    existe = cursor.fetchone() is not None
                return existe
            except Exception as banco:
                print(f'Erro ao verificar conta: {banco}')
                return False
        return False

    def get_titular(self) -> str:
        """Retorna o titular da conta.

        Returns:
            str: Nome do titular da conta.
        """
        return self.titular

    def set_titular(self, titular: str) -> None:
        """Define o titular da conta.

        Args:
            titular (str): Nome do titular.
        """
        self.titular = titular

    def get_saldo(self) -> Decimal:
        """Retorna o saldo da conta.

        Returns:
            Decimal: Saldo atual da conta.
        """
        return self.__saldo

    def set_saldo(self, valor: Decimal) -> None:
        """Define o saldo da conta.

        Args:
            valor (Decimal): Novo saldo da conta.
        """
        self.__saldo = valor

    def mensalidade(self) -> None:
        """Solicita ao usuário se deseja assinar o plano de benefícios."""
        if not self.__plano_assinado:
            print('Deseja assinar nosso plano de benefícios '
                  'por apenas R$10,00 por mês?')
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
                print('Opção inválida. Por favor, escolha 1 para Sim '
                      'ou 2 para Não.')
                self.mensalidade()

    def saldo(self) -> None:
        """Exibe o saldo atual da conta."""
        print(f'Saldo: R${self.__saldo:.2f}')  # Formatação do saldo

    def transacao(self, tipo: str, valor: Decimal) -> None:
        """Registra uma transação no banco de dados e no histórico.

        Args:
            tipo (str): Tipo de transação (Depósito, Saque,
            Transferência, etc.).
            valor (Decimal): Valor da transação.
        """
        saldo_atual = self.get_saldo()
        try:
            conn = conectar_banco()
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO transacoes (conta_numero, tipo, "
                        "valor, saldo) "
                        "VALUES (%s, %s, %s, %s)",
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
        """Exibe o extrato de transações da conta."""
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
                print(f'Tipo: {tipo} | Valor: R${
                      valor:.2f} | Saldo: R${saldo:.2f}')

    def depositar(self, valor: Decimal) -> None:
        """Realiza um depósito na conta.

        Args:
            valor (Decimal): Valor a ser depositado.
        """
        if valor > 0:
            valor_decimal = Decimal(str(valor))
            self.set_saldo(self.get_saldo() + valor_decimal)
            print('Depósito realizado com sucesso!')
            self.transacao('Depósito', valor_decimal)
        else:
            print('O valor do depósito deve ser positivo.')

    def transferir(self, valor: Decimal, conta_destino_numero: int) -> None:
        """Realiza uma transferência para outra conta.

        Args:
            valor (Decimal): Valor a ser transferido.
            conta_destino_numero (int): Número da conta de destino.
        """
        # Verifica se a conta de destino é a própria conta
        if conta_destino_numero == self._numero:
            print("Você não pode realizar transferências "
                  "para sua própria conta.")
            return

        conta_destino = self.buscar_conta_por_numero(conta_destino_numero)

        if not conta_destino:
            print("Conta destino não encontrada.")
            return

        valor = Decimal(str(valor))
        saldo_atual = self.get_saldo()

        # Verifica se o plano está assinado
        if not self.__plano_assinado:
            print("Deseja assinar nosso plano de benefícios?")
            print("1 - Sim")
            print("2 - Não")

            escolha_mensal = input('Digite o número da opção desejada: ')
            if escolha_mensal == '1':
                print('Você escolheu assinar o plano.')
                self.set_saldo(saldo_atual - Conta.plano_mensal)
                self.__plano_assinado = True
            elif escolha_mensal == '2':
                print('Você escolheu não assinar o plano.')
                return  # Retorna, pois o plano não foi assinado
            else:
                print('Opção inválida. Por favor, escolha 1 para Sim '
                      'ou 2 para Não.')
                return  # Retorna, pois a opção foi inválida

        # Verifica se há saldo suficiente para a transferência
        if saldo_atual >= valor:
            saldo_atual -= valor
            self.set_saldo(saldo_atual)

            self.transacao('Transferência', valor)

            conta_destino.depositar(valor)

            print(f'Transferência realizada com sucesso. '
                  f'Saldo atual: R${self.get_saldo():.2f}')
        else:
            print('Saldo insuficiente para realizar a transferência.')

    @staticmethod
    def buscar_conta_por_numero(numero: int) -> Optional['Conta']:
        """Busca uma conta pelo número.

        Args:
            numero (int): Número da conta a ser buscada.

        Returns:
            Optional[Conta]: Objeto da conta se encontrada,
            None caso contrário.
        """
        conn = None
        try:
            conn = conectar_banco()
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM contas WHERE numero = %s", (numero,))
                    resultado = cursor.fetchone()
                    if resultado:
                        print(f'Conta encontrada: {resultado}')
                        return Conta(
                            numero=resultado[0],
                            titular=resultado[1],
                            saldo=Decimal(resultado[2])
                        )
                    else:
                        print('Conta não encontrada.')
        except Exception as banco:
            print(f"Erro ao buscar conta: {banco}")
        finally:
            if conn:
                conn.close()
        return None

    def sacar(self, valor: Decimal) -> None:
        """Realiza um saque da conta.

        Args:
            valor (Decimal): Valor a ser sacado.
        """
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

        valor = Decimal(str(valor))

        saldo_atual = self.get_saldo()

        if saldo_atual >= valor:

            saldo_atual -= valor

            self.set_saldo(saldo_atual)

            self.transacao('PIX', valor)

            if isinstance(conta_destino, Conta):

                conta_destino.depositar(valor)

                print('PIX realizado com sucesso!')

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
