-- ============================================
-- CONSULTAS SQL - SISTEMA DE GESTAO COMERCIAL
-- %s = parametro enviado pelo Flask (consulta parametrizada)
-- ============================================

-- 1. Listar produtos (rota /) - SELECT, FROM, ORDER BY
SELECT id, nome, descricao, preco, estoque
FROM produtos
ORDER BY nome;

-- 2. Cadastrar produto (rota /novo) - INSERT INTO, VALUES
INSERT INTO produtos (nome, descricao, preco, estoque)
VALUES (%s, %s, %s, %s);

-- 3. Atualizar produto (rota /editar/<id>, POST) - UPDATE, WHERE
UPDATE produtos
SET nome = %s,
    descricao = %s,
    preco = %s,
    estoque = %s
WHERE id = %s;

-- 4. Buscar produto pelo ID (rota /editar/<id>, GET) - SELECT, WHERE
SELECT id, nome, descricao, preco, estoque
FROM produtos
WHERE id = %s;

-- 5. Excluir produto (rota /excluir/<id>) - DELETE, WHERE
DELETE FROM produtos
WHERE id = %s;

-- 6. Dashboard (rota /dashboard) - COUNT, SUM, subconsultas
SELECT
    (SELECT COUNT(*) FROM pedidos)  AS total_pedidos,
    (SELECT COUNT(*) FROM clientes) AS total_clientes,
    (SELECT COUNT(*) FROM produtos) AS total_produtos,
    (SELECT COALESCE(SUM(quantidade * preco_unitario), 0)
       FROM itens_pedido)            AS faturamento,
    ROUND(
        (SELECT COALESCE(SUM(quantidade * preco_unitario), 0)
           FROM itens_pedido)
        / NULLIF((SELECT COUNT(*) FROM pedidos), 0)
    , 2)                             AS ticket_medio;

-- 7. Relatorio de clientes (rota /relatorio/clientes) - JOIN, GROUP BY
SELECT c.nome                               AS cliente,
       c.cidade                             AS cidade,
       COUNT(DISTINCT p.id)                 AS quantidade_pedidos,
       SUM(i.quantidade * i.preco_unitario) AS total_comprado
FROM clientes c
JOIN pedidos p      ON p.id_cliente = c.id
JOIN itens_pedido i ON i.id_pedido  = p.id
GROUP BY c.id, c.nome, c.cidade
ORDER BY total_comprado DESC;

-- 8. Produtos mais vendidos (rota /relatorio/produtos-vendidos) - JOIN, SUM, ORDER BY DESC
SELECT pr.nome                              AS produto,
       cat.nome                             AS categoria,
       SUM(i.quantidade)                    AS quantidade_vendida,
       SUM(i.quantidade * i.preco_unitario) AS faturamento
FROM produtos pr
JOIN itens_pedido i      ON i.id_produto = pr.id
JOIN pedidos pe          ON pe.id = i.id_pedido
LEFT JOIN categorias cat ON cat.id = pr.id_categoria
GROUP BY pr.id, pr.nome, cat.nome
ORDER BY quantidade_vendida DESC;

-- 9. Clientes sem pedidos (rota /relatorio/clientes-sem-pedidos) - NOT EXISTS
SELECT c.id, c.nome, c.email, c.cidade
FROM clientes c
WHERE NOT EXISTS (
    SELECT 1
    FROM pedidos p
    WHERE p.id_cliente = c.id
)
ORDER BY c.nome;

-- 10. Vendas por periodo (rota /relatorio/vendas-periodo) - BETWEEN, GROUP BY
SELECT pe.id                                AS id,
       c.nome                               AS cliente,
       pe.data_pedido                       AS data_pedido,
       SUM(i.quantidade * i.preco_unitario) AS faturamento
FROM pedidos pe
JOIN clientes c     ON c.id = pe.id_cliente
JOIN itens_pedido i ON i.id_pedido = pe.id
WHERE pe.data_pedido BETWEEN %s AND %s
GROUP BY pe.id, c.nome, pe.data_pedido
ORDER BY pe.data_pedido;

-- 11. Estoque abaixo da media (rota /relatorio/estoque-baixo) - subconsulta com AVG
SELECT id, nome, preco, estoque
FROM produtos
WHERE estoque < (SELECT AVG(estoque) FROM produtos)
ORDER BY estoque;

-- 12. Faturamento por categoria (rota /relatorio/categorias) - GROUP BY, HAVING
SELECT cat.nome                             AS categoria,
       SUM(i.quantidade)                    AS quantidade_vendida,
       SUM(i.quantidade * i.preco_unitario) AS faturamento
FROM categorias cat
JOIN produtos pr    ON pr.id_categoria = cat.id
JOIN itens_pedido i ON i.id_produto = pr.id
JOIN pedidos pe     ON pe.id = i.id_pedido
GROUP BY cat.id, cat.nome
HAVING SUM(i.quantidade * i.preco_unitario) > 5000
ORDER BY faturamento DESC;

-- 13. Classificacao de clientes (rota /relatorio/classificacao-clientes) - CASE WHEN
SELECT c.nome AS cliente,
       COALESCE(SUM(i.quantidade * i.preco_unitario), 0) AS total_comprado,
       CASE
           WHEN COALESCE(SUM(i.quantidade * i.preco_unitario), 0) > 10000
               THEN 'Ouro'
           WHEN COALESCE(SUM(i.quantidade * i.preco_unitario), 0) >= 5000
               THEN 'Prata'
           ELSE 'Bronze'
       END AS classificacao
FROM clientes c
LEFT JOIN pedidos p      ON p.id_cliente = c.id
LEFT JOIN itens_pedido i ON i.id_pedido  = p.id
GROUP BY c.id, c.nome
ORDER BY total_comprado DESC;
