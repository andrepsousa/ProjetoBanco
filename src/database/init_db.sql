\c meu_banco

CREATE TABLE contas (
    numero INTEGER PRIMARY KEY,
    titular VARCHAR(100) NOT NULL,
    saldo NUMERIC NOT NULL
);


CREATE TABLE chaves_pix (
    id SERIAL PRIMARY KEY,
    conta_numero INTEGER REFERENCES contas(numero),
    tipo_chave VARCHAR(50),
    chave VARCHAR(50)
);

CREATE TABLE transacoes (
    id SERIAL PRIMARY KEY,
    conta_numero INTEGER NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    valor NUMERIC NOT NULL,
    saldo NUMERIC NOT NULL,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conta_numero) REFERENCES contas (numero)
);