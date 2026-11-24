"""
Cria as tabelas (schema.sql) e carrega os dados (carga_banco.txt)
no MySQL do Aiven.

Uso (com a .venv ativada):
    python carregar_banco.py HOST PORTA
A senha é pedida no terminal e não aparece na tela.
"""
import sys
import getpass
import pymysql

USUARIO = "avnadmin"


def comandos(arquivo):
    texto = open(arquivo, encoding="utf-8").read()
    linhas = [l for l in texto.splitlines() if not l.strip().startswith("--")]
    return [c.strip() for c in "\n".join(linhas).split(";") if c.strip()]


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    host, porta = sys.argv[1], int(sys.argv[2])
    senha = getpass.getpass(f"Senha do usuário {USUARIO}: ")

    conexao = pymysql.connect(host=host, port=porta, user=USUARIO, password=senha,
                              ssl={"verify_mode": "none"}, connect_timeout=15,
                              autocommit=True)
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SHOW DATABASES LIKE 'gestao_comercial'")
            if cursor.fetchone():
                cursor.execute("USE gestao_comercial")
                cursor.execute("SHOW TABLES LIKE 'produtos'")
                if cursor.fetchone():
                    print("O banco gestao_comercial já existe com as tabelas. Nada foi alterado.")
                    return

            for arquivo in ("schema.sql", "carga_banco.txt"):
                for sql in comandos(arquivo):
                    cursor.execute(sql)
                print(f"OK: {arquivo}")

            for tabela in ("categorias", "clientes", "produtos", "pedidos", "itens_pedido"):
                cursor.execute(f"SELECT COUNT(*) AS n FROM {tabela}")
                print(f"  {tabela}: {cursor.fetchone()[0]} registros")
    finally:
        conexao.close()

    print("Banco pronto!")


if __name__ == "__main__":
    main()
