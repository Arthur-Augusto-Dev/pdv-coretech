from core.database import conectar
from datetime import datetime


def abrir_caixa(valor_inicial, usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id FROM caixa WHERE status = 'aberto'
        """)
        if cursor.fetchone():
            return False, "Já existe um caixa aberto!"

        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO caixa (usuario_id, valor_inicial, data_abertura, status)
            VALUES (?, ?, ?, 'aberto')
        """,
            (usuario_id, valor_inicial, data_hora),
        )

        caixa_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO movimentacao_caixa
            (caixa_id, tipo, valor, motivo, data_hora)
            VALUES (?, 'abertura', ?, 'Abertura de caixa', ?)
        """,
            (caixa_id, valor_inicial, data_hora),
        )

        conn.commit()
        return True, f"Caixa aberto com fundo de R$ {valor_inicial:.2f}!"
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao abrir caixa: {str(e)}"
    finally:
        conn.close()


def fechar_caixa(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id FROM caixa WHERE status = 'aberto'
        """)
        caixa = cursor.fetchone()
        if not caixa:
            return False, "Nenhum caixa aberto!"

        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute(
            """
            UPDATE caixa
            SET status = 'fechado', data_fechamento = ?
            WHERE id = ?
        """,
            (data_hora, caixa[0]),
        )

        conn.commit()
        return True, "Caixa fechado com sucesso!"
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao fechar caixa: {str(e)}"
    finally:
        conn.close()


def caixa_aberto():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, usuario_id, valor_inicial, data_abertura
        FROM caixa WHERE status = 'aberto'
    """)
    caixa = cursor.fetchone()
    conn.close()
    return caixa


def registrar_sangria(valor, usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id FROM caixa WHERE status = "aberto"')
        caixa = cursor.fetchone()
        if not caixa:
            return False, "Nenhum caixa aberto!"

        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO movimentacao_caixa
            (caixa_id, tipo, valor, motivo, data_hora)
            VALUES (?, 'sangria', ?, 'Sangria de caixa', ?)
        """,
            (caixa[0], valor, data_hora),
        )

        conn.commit()
        return True, f"Sangria de R$ {valor:.2f} registrada!"
    except Exception as e:
        conn.rollback()
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()


def registrar_suprimento(valor, usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id FROM caixa WHERE status = "aberto"')
        caixa = cursor.fetchone()
        if not caixa:
            return False, "Nenhum caixa aberto!"

        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO movimentacao_caixa
            (caixa_id, tipo, valor, motivo, data_hora)
            VALUES (?, 'suprimento', ?, 'Suprimento de caixa', ?)
        """,
            (caixa[0], valor, data_hora),
        )

        conn.commit()
        return True, f"Suprimento de R$ {valor:.2f} registrado!"
    except Exception as e:
        conn.rollback()
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()


def obter_movimentacoes_caixa(caixa_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT tipo, valor, motivo, data_hora
        FROM movimentacao_caixa
        WHERE caixa_id = ?
        ORDER BY data_hora ASC
    """,
        (caixa_id,),
    )
    movs = cursor.fetchall()
    conn.close()
    return movs
