from core.database import conectar
import hashlib


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def criar_usuario_admin():
    """
    Cria o usuário admin padrão se não existir nenhum usuário.
    Login: admin | Senha: admin123
    """
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total = cursor.fetchone()[0]

    if total == 0:
        cursor.execute(
            """
            INSERT INTO usuarios (nome, login, senha, perfil)
            VALUES (?, ?, ?, ?)
        """,
            ("Administrador", "admin", hash_senha("admin123"), "admin"),
        )
        conn.commit()
    conn.close()


def verificar_login(login, senha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, nome, login, perfil
        FROM usuarios
        WHERE login = ? AND senha = ? AND ativo = 1
    """,
        (login, hash_senha(senha)),
    )
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        return {
            "id": usuario[0],
            "nome": usuario[1],
            "login": usuario[2],
            "perfil": usuario[3],
        }
    return None


def listar_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, login, perfil, ativo FROM usuarios ORDER BY nome")
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios


def cadastrar_usuario(nome, login, senha, perfil="operador"):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO usuarios (nome, login, senha, perfil)
            VALUES (?, ?, ?, ?)
        """,
            (nome, login, hash_senha(senha), perfil),
        )
        conn.commit()
        return True, "Usuário cadastrado com sucesso!"
    except Exception as e:
        return False, f"Erro ao cadastrar usuário: {str(e)}"
    finally:
        conn.close()


def alterar_senha(usuario_id, senha_nova):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE usuarios SET senha = ? WHERE id = ?
        """,
            (hash_senha(senha_nova), usuario_id),
        )
        conn.commit()
        return True, "Senha alterada com sucesso!"
    except Exception as e:
        return False, f"Erro ao alterar senha: {str(e)}"
    finally:
        conn.close()


def desativar_usuario(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE usuarios SET ativo = 0 WHERE id = ?", (usuario_id,))
        conn.commit()
        return True, "Usuário desativado!"
    except Exception as e:
        return False, f"Erro: {str(e)}"
    finally:
        conn.close()
