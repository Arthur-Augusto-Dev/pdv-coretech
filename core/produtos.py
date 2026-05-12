from core.database import conectar
from datetime import datetime


def cadastrar_produto(codigo, nome, preco, estoque, estoque_minimo, categoria):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO produtos (codigo, nome, preco, estoque, estoque_minimo, categoria)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (codigo, nome, preco, estoque, estoque_minimo, categoria),
        )
        conn.commit()
        return True, "Produto cadastrado com sucesso!"
    except Exception as e:
        return False, f"Erro ao cadastrar produto: {str(e)}"
    finally:
        conn.close()


def buscar_produto_por_codigo(codigo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE codigo = ? AND ativo = 1", (codigo,))
    produto = cursor.fetchone()
    conn.close()
    return produto


def buscar_produto_por_nome(nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM produtos WHERE nome LIKE ? AND ativo = 1", (f"%{nome}%",)
    )
    produtos = cursor.fetchall()
    conn.close()
    return produtos


def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE ativo = 1 ORDER BY nome")
    produtos = cursor.fetchall()
    conn.close()
    return produtos


def atualizar_produto(produto_id, codigo, nome, preco, estoque_minimo, categoria):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE produtos
            SET codigo = ?, nome = ?, preco = ?, estoque_minimo = ?, categoria = ?
            WHERE id = ?
        """,
            (codigo, nome, preco, estoque_minimo, categoria, produto_id),
        )
        conn.commit()
        return True, "Produto atualizado com sucesso!"
    except Exception as e:
        return False, f"Erro ao atualizar produto: {str(e)}"
    finally:
        conn.close()


def desativar_produto(produto_id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE produtos SET ativo = 0 WHERE id = ?", (produto_id,))
        conn.commit()
        return True, "Produto removido com sucesso!"
    except Exception as e:
        return False, f"Erro ao remover produto: {str(e)}"
    finally:
        conn.close()


def produtos_estoque_baixo():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM produtos
        WHERE estoque <= estoque_minimo AND ativo = 1
        ORDER BY estoque ASC
    """)
    produtos = cursor.fetchall()
    conn.close()
    return produtos
