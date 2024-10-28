from models.conta import Conta
from decimal import Decimal


class InterfaceUsuario:

    def __init__(self, conta):
        self.conta = conta

    def exibir_menu(self):

        while True:
            print('-' * 30)
            print('Escolha a operação:')
            print('1. Saldo')
            print('2. Depositar')
            print('3. Transferir')
            print('4. Sacar')
            print('5. Extrato')
            print('6. Pix')
            print('7. Detalhes da conta')
            print('8. Sair')
            print('-' * 30)

            operacao = input('Digite o número da operação desejada: ')

            if operacao == '8':
                print('Saindo...')
                break

            if operacao in ['1', '2', '3', '4', '5', '6', '7']:

                if operacao == '1':
                    print(f"Seu saldo é: R${self.conta.get_saldo():.2f}")
                elif operacao == '2':
                    valor_str = input('Digite o valor que deseja '
                                      'depositar: R$')
                    valor = Decimal(valor_str.replace(',', '.'))
                    self.conta.depositar(valor)
                    print(f'Saldo atual: R${self.conta.get_saldo():.2f}')
                elif operacao == '3':
                    valor = float(input('Digite o valor que deseja '
                                        'transferir: R$'))
                    numero = int(input('Digite o número da conta para a qual '
                                       'deseja transferir: '))
                    self.conta.transferir(valor, numero)
                elif operacao == '4':
                    valor = float(input('Digite o valor que deseja sacar: R$'))
                    self.conta.sacar(valor)
                    print(f'Saldo atual: R${self.conta.get_saldo():.2f}')
                elif operacao == '5':
                    print('----Extrato----')
                    print(f'Conta: {self.conta.get_titular()}')
                    self.conta.extrato()
                elif operacao == '6':
                    pix_menu_ativo = True
                    while pix_menu_ativo:
                        print('-' * 30)
                        print('Escolha a operação:')
                        print('1. Transferência via Pix')
                        print('2. Cadastrar Chave Pix')
                        print('3. Remover Chave Pix')
                        print('4. Listar Chaves pix')
                        print('5. Voltar')
                        print('-' * 30)

                        escolha_pix = input('Digite o número da operação '
                                            'desejada: ')

                        if escolha_pix == '1':
                            valor = float(input('Digite o valor que deseja '
                                                'transferir: R$'))
                            chave = input('Digite a chave pix do '
                                          'destinatário: ')
                            self.conta.pix(valor, chave)
                            print(f'Saldo atual: '
                                  f'R${self.conta.get_saldo():.2f}')
                            pass
                        elif escolha_pix == '2':
                            chave = input('Digite a chave Pix que deseja '
                                          'cadastrar: ')
                            self.conta.cadastrar_chave_pix(chave)
                        elif escolha_pix == '3':
                            print('Chaves cadastradas:')
                            (self.conta.listar_chaves_pix
                                (exibir_indice=True))
                            escolha_indice = input('Digite o número da chave '
                                                   'que deseja remover: ')
                            self.conta.remover_chave_pix(escolha_indice)
                        elif escolha_pix == '4':
                            self.conta.listar_chaves_pix()
                        elif escolha_pix == '5':
                            pix_menu_ativo = False
                        else:
                            print('Opção inválida! Tente novamente.')
                elif operacao == '7':
                    for numero, conta in Conta.contas.items():
                        print(f'Número da conta: {numero}, '
                              f'Titular: {conta.get_titular()}, '
                              f'Saldo: R${conta.get_saldo():.2f}')
                else:
                    print('Opção inválida! Tente novamente.')
