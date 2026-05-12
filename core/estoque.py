from core.database import conectar
from datetime import datetime


def atualizar_estoque(produto_id, quantidade, tipo, motivo=""):
    """
    tipo: 'entrada' ou 'saida'
    """
    conn = conectar()
    cursor = conn.cursor()
    try:
        # Busca estoque atual
        cursor.execute("SELECT estoque FROM produtos WHERE id = ?", (produto_id,))
        produto = cursor.fetchone()

        if not produto:
            return False, "Produto não encontrado!"

        estoque_atual = produto[0]

        if tipo == "saida":
            if estoque_atual < quantidade:
                return False, "Estoque insuficiente!"
            novo_estoque = estoque_atual - quantidade
        else:
            novo_estoque = estoque_atual + quantidade

        # Atualiza o estoque
        cursor.execute(
            """
            UPDATE produtos SET estoque = ? WHERE id = ?
        """,
            (novo_estoque, produto_id),
        )

        # Registra a movimentação
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO movimentacao_estoque
            (produto_id, tipo, quantidade, motivo, data_hora)
            VALUES (?, ?, ?, ?, ?)
        """,
            (produto_id, tipo, quantidade, motivo, data_hora),
        )

        conn.commit()
        return True, f"Estoque atualizado! Novo estoque: {novo_estoque}"
    except Exception as e:
        return False, f"Erro ao atualizar estoque: {str(e)}"
    finally:
        conn.close()


def consultar_estoque(produto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, codigo, nome, estoque, estoque_minimo
        FROM produtos WHERE id = ? AND ativo = 1
    """,
        (produto_id,),
    )
    produto = cursor.fetchone()
    conn.close()
    return produto


def historico_movimentacao(produto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT tipo, quantidade, motivo, data_hora
        FROM movimentacao_estoque
        WHERE produto_id = ?
        ORDER BY data_hora DESC
    """,
        (produto_id,),
    )
    historico = cursor.fetchall()
    conn.close()
    return historico


def produtos_estoque_baixo():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, codigo, nome, estoque, estoque_minimo
        FROM produtos
        WHERE estoque <= estoque_minimo AND ativo = 1
        ORDER BY estoque ASC
    """)
    produtos = cursor.fetchall()
    conn.close()
    return produtos


def inventario_completo():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, codigo, nome, categoria, estoque, estoque_minimo, preco,
               (estoque * preco) as valor_total
        FROM produtos
        WHERE ativo = 1
        ORDER BY categoria, nome
    """)
    inventario = cursor.fetchall()
    conn.close()
    return inventario
