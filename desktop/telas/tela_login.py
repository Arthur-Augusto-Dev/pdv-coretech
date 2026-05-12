from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFrame,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

import sys, os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from core.usuarios import verificar_login


class TelaLogin(QWidget):
    login_sucesso = pyqtSignal(dict)  # emite os dados do usuário logado

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.loja = config["loja"]
        self.tema = config["tema"]
        self.setWindowTitle(f"Login — {self.loja['nome']}")
        self.setFixedSize(420, 500)
        self.construir_interface()

    def construir_interface(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.tema['cor_fundo']};
                color: {self.tema['cor_texto']};
                font-family: Arial;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        # Logo / Nome da loja
        label_logo = QLabel(self.loja["nome"])
        label_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_logo.setStyleSheet(f"""
            font-size: 26px;
            font-weight: bold;
            color: {self.tema['cor_primaria']};
            padding: 10px;
        """)
        layout.addWidget(label_logo)

        label_slogan = QLabel(self.loja.get("slogan", ""))
        label_slogan.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_slogan.setStyleSheet("font-size: 12px; color: #7070a0;")
        layout.addWidget(label_slogan)

        layout.addSpacing(20)

        # Card do formulário
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #111118;
                border-radius: 12px;
                border: 1px solid #2a2a3a;
            }
        """)
        layout_card = QVBoxLayout(card)
        layout_card.setContentsMargins(24, 24, 24, 24)
        layout_card.setSpacing(14)

        titulo = QLabel("Acesso ao Sistema")
        titulo.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #e8e8f0; border: none;"
        )
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_card.addWidget(titulo)

        # Login
        label_login = QLabel("Usuário:")
        label_login.setStyleSheet("color: #7070a0; font-size: 13px; border: none;")
        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("Digite seu usuário")
        self.input_login.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e2e;
                border: 1px solid #2a2a3a;
                border-radius: 8px;
                padding: 10px;
                color: #e8e8f0;
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #6c63ff; }
        """)
        self.input_login.returnPressed.connect(lambda: self.input_senha.setFocus())

        # Senha
        label_senha = QLabel("Senha:")
        label_senha.setStyleSheet("color: #7070a0; font-size: 13px; border: none;")
        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText("Digite sua senha")
        self.input_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_senha.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e2e;
                border: 1px solid #2a2a3a;
                border-radius: 8px;
                padding: 10px;
                color: #e8e8f0;
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #6c63ff; }
        """)
        self.input_senha.returnPressed.connect(self.fazer_login)

        # Botão entrar
        btn_entrar = QPushButton("🔓 Entrar")
        btn_entrar.setFixedHeight(45)
        btn_entrar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_entrar.clicked.connect(self.fazer_login)
        btn_entrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.tema['cor_primaria']};
                color: white;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.tema['cor_secundaria']};
                color: black;
            }}
        """)

        layout_card.addWidget(label_login)
        layout_card.addWidget(self.input_login)
        layout_card.addWidget(label_senha)
        layout_card.addWidget(self.input_senha)
        layout_card.addSpacing(8)
        layout_card.addWidget(btn_entrar)

        layout.addWidget(card)
        layout.addStretch()

        # Rodapé
        label_rodape = QLabel(f"Core Tech v{self.config['sistema']['versao']}")
        label_rodape.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_rodape.setStyleSheet("font-size: 11px; color: #3a3a5a;")
        layout.addWidget(label_rodape)

        # Tab order
        self.setTabOrder(self.input_login, self.input_senha)

    def fazer_login(self):
        login = self.input_login.text().strip()
        senha = self.input_senha.text().strip()

        if not login or not senha:
            QMessageBox.warning(self, "Atenção", "Preencha usuário e senha!")
            return

        usuario = verificar_login(login, senha)

        if usuario:
            self.login_sucesso.emit(usuario)
        else:
            QMessageBox.critical(self, "Acesso negado", "Usuário ou senha incorretos!")
            self.input_senha.clear()
            self.input_senha.setFocus()
