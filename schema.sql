-- ============================================
-- ESQUEMA DO BANCO - GESTÃO COMERCIAL
-- Rodar este arquivo primeiro e depois o carga_banco.txt
-- ============================================

CREATE DATABASE IF NOT EXISTS gestao_comercial
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE gestao_comercial;

CREATE TABLE categorias (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);

CREATE TABLE clientes (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    nome          VARCHAR(150) NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    cidade        VARCHAR(100),
    estado        CHAR(2),
    data_cadastro DATE
);

CREATE TABLE produtos (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    nome         VARCHAR(150) NOT NULL,
    descricao    VARCHAR(255),
    preco        DECIMAL(10,2) NOT NULL,
    estoque      INT NOT NULL DEFAULT 0,
    id_categoria INT NULL,
    CONSTRAINT fk_produto_categoria
        FOREIGN KEY (id_categoria) REFERENCES categorias(id)
);

CREATE TABLE pedidos (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente  INT NOT NULL,
    data_pedido DATE NOT NULL,
    status      VARCHAR(30) NOT NULL DEFAULT 'Concluído',
    CONSTRAINT fk_pedido_cliente
        FOREIGN KEY (id_cliente) REFERENCES clientes(id)
);

-- ON DELETE RESTRICT: impede excluir um produto que já está em algum pedido
CREATE TABLE itens_pedido (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido      INT NOT NULL,
    id_produto     INT NOT NULL,
    quantidade     INT NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_item_pedido
        FOREIGN KEY (id_pedido) REFERENCES pedidos(id),
    CONSTRAINT fk_item_produto
        FOREIGN KEY (id_produto) REFERENCES produtos(id) ON DELETE RESTRICT
);
