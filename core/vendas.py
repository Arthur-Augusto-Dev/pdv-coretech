from core.database import conectar
from datetime import datetime


def registrar_venda(itens, forma_pagamento, cliente_id=None, desconto=0.0):
    conn = conectar()
    cursor = conn.cursor()
    try:
        total = sum(item["quantidade"] * item["preco_unitario"] for item in itens)
        total_com_desconto = round(total - desconto, 2)
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Registra a venda
        cursor.execute(
            """
            INSERT INTO vendas (cliente_id, total, desconto, forma_pagamento, data_hora)
            VALUES (?, ?, ?, ?, ?)
        """,
            (cliente_id, total_com_desconto, desconto, forma_pagamento, data_hora),
        )

        venda_id = cursor.lastrowid

        # Registra itens e atualiza estoque na mesma conexão
        for item in itens:
            subtotal = round(item["quantidade"] * item["preco_unitario"], 2)

            cursor.execute(
                """
                INSERT INTO itens_venda
                (venda_id, produto_id, nome_produto, quantidade, preco_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    venda_id,
                    item["produto_id"],
                    item["nome_produto"],
                    item["quantidade"],
                    item["preco_unitario"],
                    subtotal,
                ),
            )

            # Verifica estoque
            cursor.execute(
                "SELECT estoque FROM produtos WHERE id = ?", (item["produto_id"],)
            )
            produto = cursor.fetchone()

            if not produto:
                raise Exception(f"Produto {item['nome_produto']} não encontrado!")

            estoque_atual = produto[0]
            if estoque_atual < item["quantidade"]:
                raise Exception(f"Estoque insuficiente para {item['nome_produto']}!")

            novo_estoque = estoque_atual - item["quantidade"]

            # Atualiza estoque
            cursor.execute(
                """
                UPDATE produtos SET estoque = ? WHERE id = ?
            """,
                (novo_estoque, item["produto_id"]),
            )

            # Registra movimentação
            cursor.execute(
                """
                INSERT INTO movimentacao_estoque
                (produto_id, tipo, quantidade, motivo, data_hora)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    item["produto_id"],
                    "saida",
                    item["quantidade"],
                    f"Venda #{venda_id}",
                    data_hora,
                ),
            )

        conn.commit()
        return True, venda_id, total_com_desconto, data_hora

    except Exception as e:
        conn.rollback()
        return False, None, None, f"Erro: {str(e)}"
    finally:
        conn.close()


def buscar_venda(venda_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT v.id, v.total, v.desconto, v.forma_pagamento, v.status, v.data_hora,
               c.nome as cliente
        FROM vendas v
        LEFT JOIN clientes c ON v.cliente_id = c.id
        WHERE v.id = ?
    """,
        (venda_id,),
    )
    venda = cursor.fetchone()
    conn.close()
    return venda


def buscar_itens_venda(venda_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT nome_produto, quantidade, preco_unitario, subtotal
        FROM itens_venda
        WHERE venda_id = ?
    """,
        (venda_id,),
    )
    itens = cursor.fetchall()
    conn.close()
    return itens


def cancelar_venda(venda_id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT produto_id, quantidade FROM itens_venda WHERE venda_id = ?
        """,
            (venda_id,),
        )
        itens = cursor.fetchall()

        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        for item in itens:
            cursor.execute("SELECT estoque FROM produtos WHERE id = ?", (item[0],))
            produto = cursor.fetchone()
            if produto:
                novo_estoque = produto[0] + item[1]
                cursor.execute(
                    "UPDATE produtos SET estoque = ? WHERE id = ?",
                    (novo_estoque, item[0]),
                )
                cursor.execute(
                    """
                    INSERT INTO movimentacao_estoque
                    (produto_id, tipo, quantidade, motivo, data_hora)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        item[0],
                        "entrada",
                        item[1],
                        f"Cancelamento venda #{venda_id}",
                        data_hora,
                    ),
                )

        cursor.execute(
            """
            UPDATE vendas SET status = 'cancelada' WHERE id = ?
        """,
            (venda_id,),
        )

        conn.commit()
        return True, "Venda cancelada com sucesso!"
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao cancelar venda: {str(e)}"
    finally:
        conn.close()


def vendas_do_dia():
    conn = conectar()
    cursor = conn.cursor()
    hoje = datetime.now().strftime("%d/%m/%Y")
    cursor.execute(
        """
        SELECT v.id, v.total, v.desconto, v.forma_pagamento, v.status, v.data_hora,
               c.nome as cliente
        FROM vendas v
        LEFT JOIN clientes c ON v.cliente_id = c.id
        WHERE v.data_hora LIKE ? AND v.status = 'concluida'
        ORDER BY v.data_hora DESC
    """,
        (f"{hoje}%",),
    )
    vendas = cursor.fetchall()
    conn.close()
    return vendas


def total_vendas_do_dia():
    conn = conectar()
    cursor = conn.cursor()
    hoje = datetime.now().strftime("%d/%m/%Y")
    cursor.execute(
        """
        SELECT COALESCE(SUM(total), 0)
        FROM vendas
        WHERE data_hora LIKE ? AND status = 'concluida'
    """,
        (f"{hoje}%",),
    )
    total = cursor.fetchone()[0]
    conn.close()
    return total


def vendas_por_periodo(data_inicio, data_fim):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT v.id, v.total, v.desconto, v.forma_pagamento, v.status, v.data_hora,
               c.nome as cliente
        FROM vendas v
        LEFT JOIN clientes c ON v.cliente_id = c.id
        WHERE v.data_hora BETWEEN ? AND ?
        AND v.status = 'concluida'
        ORDER BY v.data_hora DESC
    """,
        (data_inicio, data_fim),
    )
    vendas = cursor.fetchall()
    conn.close()
    return vendas
