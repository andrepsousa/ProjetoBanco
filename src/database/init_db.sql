CREATE DATABASE banco;

\c banco

CREATE TABLE contas (
    numero SERIAL PRIMARY KEY,
    titular VARCHAR(100),
    saldo DECIMAL(10,2)
);

CREATE TABLE transacoes (
    id SERIAL PRIMARY KEY,
    conta_numero INTEGER REFERENCES contas(numero),
    tipo_transacao VARCHAR(50),
    valor DECIMAL(10,2),
    saldo DECIMAL(10,2),
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chaves_pix (
    id SERIAL PRIMARY KEY,
    conta_numero INTEGER REFERENCES contas(numero),
    tipo_chave VARCHAR(50),
    chave VARCHAR(50)
);
