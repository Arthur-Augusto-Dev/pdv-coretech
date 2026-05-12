from core.database import conectar


def cadastrar_cliente(nome, cpf, telefone, email, endereco):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO clientes (nome, cpf, telefone, email, endereco)
            VALUES (?, ?, ?, ?, ?)
        """,
            (nome, cpf, telefone, email, endereco),
        )
        conn.commit()
        return True, "Cliente cadastrado com sucesso!"
    except Exception as e:
        return False, f"Erro ao cadastrar cliente: {str(e)}"
    finally:
        conn.close()


def buscar_cliente_por_cpf(cpf):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE cpf = ? AND ativo = 1", (cpf,))
    cliente = cursor.fetchone()
    conn.close()
    return cliente


def buscar_cliente_por_nome(nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM clientes WHERE nome LIKE ? AND ativo = 1", (f"%{nome}%",)
    )
    clientes = cursor.fetchall()
    conn.close()
    return clientes


def listar_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE ativo = 1 ORDER BY nome")
    clientes = cursor.fetchall()
    conn.close()
    return clientes


def atualizar_cliente(cliente_id, nome, cpf, telefone, email, endereco):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE clientes
            SET nome = ?, cpf = ?, telefone = ?, email = ?, endereco = ?
            WHERE id = ?
        """,
            (nome, cpf, telefone, email, endereco, cliente_id),
        )
        conn.commit()
        return True, "Cliente atualizado com sucesso!"
    except Exception as e:
        return False, f"Erro ao atualizar cliente: {str(e)}"
    finally:
        conn.close()


def desativar_cliente(cliente_id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE clientes SET ativo = 0 WHERE id = ?", (cliente_id,))
        conn.commit()
        return True, "Cliente removido com sucesso!"
    except Exception as e:
        return False, f"Erro ao remover cliente: {str(e)}"
    finally:
        conn.close()


def historico_compras_cliente(cliente_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT v.id, v.total, v.forma_pagamento, v.data_hora
        FROM vendas v
        WHERE v.cliente_id = ?
        ORDER BY v.data_hora DESC
    """,
        (cliente_id,),
    )
    historico = cursor.fetchall()
    conn.close()
    return historico
