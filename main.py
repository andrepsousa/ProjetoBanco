from src.models.conta import Conta
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
        conta = Conta(conta_data['numero'], conta_data['titular'],
                      conta_data['saldo'])
    else:
        criar_conta_db(conn, 123, 'Balde', 500)
        conta = Conta(123, 'Balde', 500)

    menu = InterfaceUsuario(conta)
    menu.exibir_menu()

    conn.close()


if __name__ == '__main__':
    main()
