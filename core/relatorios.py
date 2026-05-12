from core.database import conectar
from datetime import datetime


def relatorio_vendas_dia():
    conn = conectar()
    cursor = conn.cursor()
    hoje = datetime.now().strftime("%d/%m/%Y")
    cursor.execute(
        """
        SELECT
            COUNT(*) as total_vendas,
            COALESCE(SUM(total), 0) as faturamento,
            COALESCE(AVG(total), 0) as ticket_medio,
            forma_pagamento
        FROM vendas
        WHERE data_hora LIKE ? AND status = 'concluida'
        GROUP BY forma_pagamento
    """,
        (f"{hoje}%",),
    )
    resultado = cursor.fetchall()
    conn.close()
    return resultado


def relatorio_vendas_periodo(data_inicio, data_fim):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            COUNT(*) as total_vendas,
            COALESCE(SUM(total), 0) as faturamento,
            COALESCE(AVG(total), 0) as ticket_medio,
            forma_pagamento
        FROM vendas
        WHERE data_hora BETWEEN ? AND ?
        AND status = 'concluida'
        GROUP BY forma_pagamento
    """,
        (data_inicio, data_fim),
    )
    resultado = cursor.fetchall()
    conn.close()
    return resultado


def produtos_mais_vendidos(limite=10):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            iv.nome_produto,
            SUM(iv.quantidade) as total_vendido,
            SUM(iv.subtotal) as faturamento
        FROM itens_venda iv
        JOIN vendas v ON iv.venda_id = v.id
        WHERE v.status = 'concluida'
        GROUP BY iv.nome_produto
        ORDER BY total_vendido DESC
        LIMIT ?
    """,
        (limite,),
    )
    produtos = cursor.fetchall()
    conn.close()
    return produtos


def faturamento_por_categoria():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            p.categoria,
            SUM(iv.quantidade) as total_vendido,
            SUM(iv.subtotal) as faturamento
        FROM itens_venda iv
        JOIN vendas v ON iv.venda_id = v.id
        JOIN produtos p ON iv.produto_id = p.id
        WHERE v.status = 'concluida'
        GROUP BY p.categoria
        ORDER BY faturamento DESC
    """)
    resultado = cursor.fetchall()
    conn.close()
    return resultado


def resumo_estoque():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) as total_produtos,
            SUM(estoque) as total_itens,
            SUM(estoque * preco) as valor_total_estoque,
            COUNT(CASE WHEN estoque <= estoque_minimo THEN 1 END) as produtos_criticos
        FROM produtos
        WHERE ativo = 1
    """)
    resultado = cursor.fetchone()
    conn.close()
    return resultado


def clientes_mais_ativos(limite=10):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            c.nome,
            COUNT(v.id) as total_compras,
            COALESCE(SUM(v.total), 0) as total_gasto
        FROM clientes c
        LEFT JOIN vendas v ON c.id = v.cliente_id
        WHERE v.status = 'concluida'
        GROUP BY c.id, c.nome
        ORDER BY total_gasto DESC
        LIMIT ?
    """,
        (limite,),
    )
    clientes = cursor.fetchall()
    conn.close()
    return clientes


def faturamento_mensal():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            substr(data_hora, 4, 7) as mes,
            COUNT(*) as total_vendas,
            COALESCE(SUM(total), 0) as faturamento
        FROM vendas
        WHERE status = 'concluida'
        GROUP BY mes
        ORDER BY mes DESC
        LIMIT 12
    """)
    resultado = cursor.fetchall()
    conn.close()
    return resultado
