
from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave_sistema")


# =====================================
# CONEXÃO COM O BANCO DE DADOS
# =====================================

def conectar_banco():
    # Os dados de conexão vêm de variáveis de ambiente (configuradas no
    # Render / PythonAnywhere ou no terminal local), para a senha
    # nunca ficar salva no código nem no GitHub.
    ssl_config = None
    if os.environ.get("DB_SSL", "false").lower() in ("1", "true", "yes"):
        ca = os.environ.get("DB_SSL_CA")
        ssl_config = {"ca": ca} if ca else {"verify_mode": "none"}

    return pymysql.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "gestao_comercial"),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
        ssl=ssl_config
    )


# =====================================
# TRATAMENTO DE ERROS
# =====================================

def tratar_erro(e):
    print(f"Erro no sistema: {e}")
    flash("Ocorreu um erro ao acessar o banco de dados.", "danger")


# =====================================
# LISTAR PRODUTOS
# =====================================

@app.route("/")
def listar_produtos():

    produtos = []

    try:
        conexao = conectar_banco()

        try:
            with conexao.cursor() as cursor:

                # TODO 1: Selecionar todos os produtos.

                sql = """
                    SELECT id, nome, descricao, preco, estoque
                    FROM produtos
                    ORDER BY nome
                """

                cursor.execute(sql)
                produtos = cursor.fetchall()

        finally:
            conexao.close()

    except pymysql.MySQLError as e:
        tratar_erro(e)

    return render_template(
        "index.html",
        produtos=produtos
    )


# =====================================
# CADASTRAR PRODUTO
# =====================================

@app.route("/novo", methods=["GET", "POST"])
def novo_produto():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        preco = request.form.get("preco", "").strip()
        estoque = request.form.get("estoque", "").strip()

        if not nome or not preco or not estoque:
            flash("Preencha os campos obrigatórios.", "warning")
            return render_template("formulario.html")

        try:
            preco = float(preco)
            estoque = int(estoque)

            if preco < 0 or estoque < 0:
                raise ValueError

        except ValueError:
            flash("Informe preço e estoque válidos.", "warning")
            return render_template("formulario.html")

        try:
            conexao = conectar_banco()

            try:
                with conexao.cursor() as cursor:

                    # TODO 2: Inserir um novo produto.

                    sql = """
                        INSERT INTO produtos (nome, descricao, preco, estoque)
                        VALUES (%s, %s, %s, %s)
                    """

                    cursor.execute(sql, (
                        nome,
                        descricao,
                        preco,
                        estoque
                    ))

                conexao.commit()

                flash("Produto cadastrado com sucesso!", "success")

            finally:
                conexao.close()

        except pymysql.MySQLError as e:
            tratar_erro(e)

        return redirect(url_for("listar_produtos"))

    return render_template("formulario.html")


# =====================================
# EDITAR PRODUTO
# =====================================

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_produto(id):

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        preco = request.form.get("preco", "").strip()
        estoque = request.form.get("estoque", "").strip()

        if not nome or not preco or not estoque:
            flash("Preencha os campos obrigatórios.", "warning")
            return redirect(url_for("editar_produto", id=id))

        try:
            preco = float(preco)
            estoque = int(estoque)

            if preco < 0 or estoque < 0:
                raise ValueError

        except ValueError:
            flash("Informe preço e estoque válidos.", "warning")
            return redirect(url_for("editar_produto", id=id))

        try:
            conexao = conectar_banco()

            try:
                with conexao.cursor() as cursor:

                    # TODO 3: Atualizar produto pelo ID.

                    sql = """
                        UPDATE produtos
                        SET nome = %s,
                            descricao = %s,
                            preco = %s,
                            estoque = %s
                        WHERE id = %s
                    """

                    cursor.execute(sql, (
                        nome,
                        descricao,
                        preco,
                        estoque,
                        id
                    ))

                conexao.commit()

                flash("Produto atualizado com sucesso!", "success")

            finally:
                conexao.close()

        except pymysql.MySQLError as e:
            tratar_erro(e)

        return redirect(url_for("listar_produtos"))

    produto = None

    try:
        conexao = conectar_banco()

        try:
            with conexao.cursor() as cursor:

                # TODO 4: Buscar produto pelo ID.

                sql = """
                    SELECT id, nome, descricao, preco, estoque
                    FROM produtos
                    WHERE id = %s
                """

                cursor.execute(sql, (id,))
                produto = cursor.fetchone()

        finally:
            conexao.close()

    except pymysql.MySQLError as e:
        tratar_erro(e)
        return redirect(url_for("listar_produtos"))

    if produto is None:
        flash("Produto não encontrado.", "warning")
        return redirect(url_for("listar_produtos"))

    return render_template(
        "formulario.html",
        produto=produto
    )


# =====================================
# EXCLUIR PRODUTO
# =====================================

@app.route("/excluir/<int:id>", methods=["POST"])
def excluir_produto(id):

    try:
        conexao = conectar_banco()

        try:
            with conexao.cursor() as cursor:

                # TODO 5: Excluir produto pelo ID.

                sql = """
                    DELETE FROM produtos
                    WHERE id = %s
                """

                cursor.execute(sql, (id,))

            conexao.commit()

            if cursor.rowcount > 0:
                flash("Produto excluído com sucesso!", "success")
            else:
                flash("Produto não encontrado.", "warning")

        finally:
            conexao.close()

    except pymysql.err.IntegrityError:
        flash("Este produto não pode ser excluído porque está vinculado a pedidos.", "danger")

    except pymysql.MySQLError as e:
        tratar_erro(e)

    return redirect(url_for("listar_produtos"))


# =====================================
# DASHBOARD
# =====================================

@app.route("/dashboard")
def dashboard():

    indicadores = {
        "total_pedidos": 0,
        "total_clientes": 0,
        "total_produtos": 0,
        "faturamento": 0,
        "ticket_medio": 0
    }

    try:
        conexao = conectar_banco()

        try:
            with conexao.cursor() as cursor:

                # TODO 6: Utilizar COUNT, SUM e AVG.
                # Retornar:
                # total_pedidos
                # total_clientes
                # total_produtos
                # faturamento
                # ticket_medio

                sql = """
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
                        , 2)                             AS ticket_medio
                """

                cursor.execute(sql)
                resultado = cursor.fetchone()

                if resultado:
                    indicadores.update(resultado)

        finally:
            conexao.close()

    except pymysql.MySQLError as e:
        tratar_erro(e)

    return render_template(
        "dashboard.html",
        indicadores=indicadores
    )


# =====================================
# RELATÓRIO DE CLIENTES
# =====================================

@app.route("/relatorio/clientes")
def relatorio_clientes():

    dados = []

    try:
        conexao = conectar_banco()

        try:
            with conexao.cursor() as cursor:

                # TODO 7:
                # Relacionar clientes e pedidos.
                # Calcular quantidade de pedidos.
                # Calcular total comprado por cliente.
                # Agrupar por cliente.

                sql = """
                    SELECT c.nome                               AS cliente,
                           c.cidade                             AS cidade,
                           COUNT(DISTINCT p.id)                 AS quantidade_pedidos,
                           SUM(i.quantidade * i.preco_unitario) AS total_comprado
                    FROM clientes c
                    JOIN pedidos p      ON p.id_cliente = c.id
                    JOIN itens_pedido i ON i.id_pedido  = p.id
                    GROUP BY c.id, c.nome, c.cidade
                    ORDER BY total_comprado DESC
                """

                cursor.execute(sql)
                dados = cursor.fetchall()

        finally:
            conexao.close()

    except pymysql.MySQLError as e:
        tratar_erro(e)

    return render_template(
        "relatorio_tabela.html",
        titulo="Relatório de clientes",
        descricao="Total de pedidos e compras por cliente.",
        colunas=["Cliente", "Cidade", "Pedidos", "Total comprado"],
        dados=dados
    )


# =====================================
# PRODUTOS MAIS VENDIDOS
# =====================================

@app.route("/relatorio/produtos-vendidos")
def produtos_vendidos():

    dados = []

    try:
        conexao = conectar_banco()

        try:
            with conexao.cursor() as cursor:

                # TODO 8:
                # Relacionar produtos, itens_pedido e pedidos.
                # Somar quantidades vendidas.
                # Calcular faturamento.
                # Ordenar do mais vendido para o menos vendido.

                sql = """
                    SELECT pr.nome                              AS produto,
                           cat.nome                             AS categoria,
                           SUM(i.quantidade)                    AS quantidade_vendida,
                           SUM(i.quantidade * i.preco_unitario) AS faturamento
                    FROM produtos pr
                    JOIN itens_pedido i      ON i.id_produto = pr.id
                    JOIN pedidos pe          ON pe.id = i.id_pedido
                    LEFT JOIN categorias cat ON cat.id = pr.id_categoria
                    GROUP BY pr.id, pr.nome, cat.nome
                    ORDER BY quantidade_vendida DESC
                """

                cursor.execute(sql)
                dados = cursor.fetchall()

        finally:
            conexao.close()

    except pymysql.MySQLError as e:
        tratar_erro(e)

    return render_template(
        "relatorio_tabela.html",
        titulo="Produtos mais vendidos",
        descricao="Ranking de produtos por quantidade vendida.",
        colunas=["Produto", "Categoria", "Quantidade", "Faturamento"],
        dados=dados
    )


# =====================================
# CLIENTES SEM PEDIDOS
# =====================================

@app.route("/relatorio/clientes-sem-pedidos")
def clientes_sem_pedidos():

    dados = []

    try:
        conexao = conectar_banco()

        try:
            with conexao.cursor() as cursor:

                # TODO 9:
                # Localizar clientes sem pedidos.
                # Utilizar NOT EXISTS ou LEFT JOIN.

                sql = """
                    SELECT c.id, c.nome, c.email, c.cidade
                    FROM clientes c
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM pedidos p
                        WHERE p.id_cliente = c.id
                    )
                    ORDER BY c.nome
                """

                cursor.execute(sql)
                dados = cursor.fetchall()

        finally:
            conexao.close()

    except pymysql.MySQLError as e:
        tratar_erro(e)

    return render_template(
        "relatorio_tabela.html",
        titulo="Clientes sem pedidos",
        descricao="Clientes que nunca realizaram compras.",
        colunas=["ID", "Nome", "Email", "Cidade"],
        dados=dados
    )


# =====================================
# VENDAS POR PERÍODO
# =====================================

@app.route("/relatorio/vendas-periodo", methods=["GET", "POST"])
def vendas_periodo():

    dados = []
    data_inicio = ""
    data_fim = ""

    if request.method == "POST":

        data_inicio = request.form.get("data_inicio", "")
        data_fim = request.form.get("data_fim", "")

        try:
            inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            fim = datetime.strptime(data_fim, "%Y-%m-%d")

            if inicio > fim:
                flash("A data inicial não pode ser maior que a data final.", "warning")

                return render_template(
                    "vendas_periodo.html",
                    dados=dados,
                    data_inicio=data_inicio,
                    data_fim=data_fim
                )

        except ValueError:
            flash("Informe um período válido.", "warning")

            return render_template(
                "vendas_periodo.html",
                dados=dados,
                data_inicio=data_inicio,
                data_fim=data_fim
            )

        try:
            conexao = conectar_banco()

            try:
                with conexao.cursor() as cursor:

                    # TODO 10:
                    # Buscar pedidos entre duas datas.
                    # Relacionar pedidos, clientes e itens_pedido.
                    # Calcular faturamento por pedido.
                    # Ordenar pela data.

                    sql = """
                        SELECT pe.id                                AS id,
                               c.nome                               AS cliente,
                               pe.data_pedido                       AS data_pedido,
                               SUM(i.quantidade * i.preco_unitario) AS faturamento
                        FROM pedidos pe
                        JOIN clientes c     ON c.id = pe.id_cliente
                        JOIN itens_pedido i ON i.id_pedido = pe.id
                        WHERE pe.data_pedido BETWEEN %s AND %s
                        GROUP BY pe.id, c.nome, pe.data_pedido
                        ORDER BY pe.data_pedido
                    """

                    cursor.execute(sql, (
                        data_inicio,
                        data_fim
                    ))

                    dados = cursor.fetchall()

            finally:
                conexao.close()

        except pymysql.MySQLError as e:
            tratar_erro(e)

    return render_template(
        "vendas_periodo.html",
        dados=dados,
        data_inicio=data_inicio,
        data_fim=data_fim
    )


# =====================================
# ESTOQUE ABAIXO DA MÉDIA
# =====================================

@app.route("/relatorio/estoque-baixo")
def estoque_baixo():

    dados = []

    try:
        conexao = conectar_banco()

        try:
            with conexao.cursor() as cursor:

                # TODO 11:
                # Selecionar produtos cujo estoque
                # seja inferior à média geral.
                # Utilizar subconsulta com AVG().

                sql = """
                    SELECT id, nome, preco, estoque
                    FROM produtos
                    WHERE estoque < (SELECT AVG(estoque) FROM produtos)
                    ORDER BY estoque
                """

                cursor.execute(sql)
                dados = cursor.fetchall()

        finally:
            conexao.close()

    except pymysql.MySQLError as e:
        tratar_erro(e)

    return render_template(
        "relatorio_tabela.html",
        titulo="Estoque abaixo da média",
        descricao="Produtos com estoque inferior à média geral.",
        colunas=["ID", "Produto", "Preço", "Estoque"],
        dados=dados
    )


# =====================================
# FATURAMENTO POR CATEGORIA
# =====================================

@app.route("/relatorio/categorias")
def relatorio_categorias():

    dados = []

    try:
        conexao = conectar_banco()

        try:
            with conexao.cursor() as cursor:

                # TODO 12:
                # Relacionar categorias, produtos,
                # itens_pedido e pedidos.
                # Agrupar por categoria.
                # Filtrar faturamento acima de R$ 5.000.

                sql = """
                    SELECT cat.nome                             AS categoria,
                           SUM(i.quantidade)                    AS quantidade_vendida,
                           SUM(i.quantidade * i.preco_unitario) AS faturamento
                    FROM categorias cat
                    JOIN produtos pr    ON pr.id_categoria = cat.id
                    JOIN itens_pedido i ON i.id_produto = pr.id
                    JOIN pedidos pe     ON pe.id = i.id_pedido
                    GROUP BY cat.id, cat.nome
                    HAVING SUM(i.quantidade * i.preco_unitario) > 5000
                    ORDER BY faturamento DESC
                """

                cursor.execute(sql)
                dados = cursor.fetchall()

        finally:
            conexao.close()

    except pymysql.MySQLError as e:
        tratar_erro(e)

    return render_template(
        "relatorio_tabela.html",
        titulo="Faturamento por categoria",
        descricao="Categorias com faturamento acima de R$ 5.000.",
        colunas=["Categoria", "Quantidade vendida", "Faturamento"],
        dados=dados
    )


# =====================================
# CLASSIFICAÇÃO DE CLIENTES
# =====================================

@app.route("/relatorio/classificacao-clientes")
def classificacao_clientes():

    dados = []

    try:
        conexao = conectar_banco()

        try:
            with conexao.cursor() as cursor:

                # TODO 13:
                # Calcular total comprado por cliente.
                # Classificar utilizando CASE WHEN.
                #
                # Ouro: acima de R$ 10.000
                # Prata: de R$ 5.000 até R$ 10.000
                # Bronze: abaixo de R$ 5.000

                sql = """
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
                    ORDER BY total_comprado DESC
                """

                cursor.execute(sql)
                dados = cursor.fetchall()

        finally:
            conexao.close()

    except pymysql.MySQLError as e:
        tratar_erro(e)

    
    return render_template(
        "relatorio_tabela.html",
        titulo="Classificação dos clientes",
        descricao="Classificação Ouro, Prata e Bronze.",
        colunas=["Cliente", "Total comprado", "Classificação"],
        dados=dados
    )


# =====================================
# EXECUÇÃO DA APLICAÇÃO
# =====================================

if __name__ == "__main__":
    app.run(debug=True)
