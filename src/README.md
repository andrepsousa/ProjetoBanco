
# Projeto Banco

Uma aplicação de gerenciamento bancário desenvolvida em Python, com integração ao PostgreSQL. A aplicação oferece CRUD completo de contas bancárias e interface para interação do usuário.

## Funcionalidades

- **Gerenciamento de Contas**: Criação, leitura, atualização e exclusão de contas bancárias.
- **Persistência de Dados**: Integração com banco de dados PostgreSQL.
- **Interface de Usuário**: Baseada em API e uso de Django REST Framework.

## Tecnologias Utilizadas

- **Python** e **Django REST Framework**
- **PostgreSQL**
- **Psycopg2** para conexão ao banco de dados

## Estrutura do Projeto

- `src/`
  - `models/`: Classes e modelos de dados.
  - `views/`: Implementação das operações CRUD.
  - `api/`: Endpoints da API para comunicação REST.
- `main.py`: Arquivo principal da aplicação.

## Como Executar

### Configuração do Ambiente
1. Certifique-se de ter **Python 3.x** instalado.
2. Crie e ative o ambiente virtual:
   ```bash
   python -m venv env_banco
   source env_banco/bin/activate  # Linux/Mac
   .\env_banco\Scripts\activate  # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### Configuração do Banco de Dados
1. Inicie o **PostgreSQL**.
2. Crie o banco de dados:
   ```bash
   psql -U postgres -d meu_banco -f src/database/init_db.sql
   ```

### Executar a Aplicação
1. Execute as migrações:
   ```bash
   python manage.py migrate
   ```
2. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```

Acesse `http://127.0.0.1:8000/BaldePay/` para interagir com a API.

## Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

---

Para mais informações, entre em contato via [andre.pds07@gmail.com](mailto:andre.pds07@gmail.com).