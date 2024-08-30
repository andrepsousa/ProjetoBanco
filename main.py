from src.models.conta import Conta
from decimal import Decimal
from src.interfaces.interface_usuario import InterfaceUsuario
from src.database.__init__ import (
    criar_conta_db,
    buscar_contas,
    conectar_banco
)


def main():
    conn = conectar_banco()

    if conn is None:
        print('Não foi possível conectar ao banco de dados.')
        return

    conta_data = buscar_contas(conn, numero=123)

    if conta_data:
        saldo = Decimal(str(conta_data['saldo']))
        conta = Conta(conta_data['numero'], conta_data['titular'], saldo)
    else:
        saldo = Decimal('500.00')
        criar_conta_db(conn, 123, 'Balde', saldo)
        conta = Conta(123, 'Balde', saldo)

    menu = InterfaceUsuario(conta)
    menu.exibir_menu()

    conn.close()


if __name__ == '__main__':
    main()
