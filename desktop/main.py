import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QFrame,
)
from PyQt6.QtCore import Qt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import criar_tabelas
from core.usuarios import criar_usuario_admin
from desktop.telas.tela_login import TelaLogin
from desktop.telas.tela_caixa import TelaCaixa
from desktop.telas.tela_produtos import TelaProdutos
from desktop.telas.tela_clientes import TelaClientes
from desktop.telas.tela_relatorios import TelaRelatorios
from desktop.telas.tela_caixa_operacao import TelaCaixaOperacao

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")


def carregar_config():
    if getattr(sys, "frozen", False):
        # Rodando como .exe
        base = sys._MEIPASS
    else:
        # Rodando como script Python
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config_path = os.path.join(base, "config", "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


class MainWindow(QMainWindow):
    def __init__(self, config, usuario):
        super().__init__()
        self.config = config
        self.usuario = usuario
        self.tema = config["tema"]
        self.loja = config["loja"]

        self.setWindowTitle(f"PDV — {self.loja['nome']}")
        self.setMinimumSize(1280, 720)
        self.showMaximized()

        self.aplicar_estilo()
        self.construir_interface()

    def aplicar_estilo(self):
        t = self.tema
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {t['cor_fundo']}; }}
            QWidget {{
                background-color: {t['cor_fundo']};
                color: {t['cor_texto']};
                font-family: Arial;
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {t['cor_primaria']};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {t['cor_secundaria']};
                color: #000000;
            }}
            QLabel {{ color: {t['cor_texto']}; }}
            QFrame#sidebar {{
                background-color: #111118;
                border-right: 1px solid #2a2a3a;
            }}
            QPushButton#btn_menu {{
                background-color: transparent;
                color: #7070a0;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                text-align: left;
            }}
            QPushButton#btn_menu:hover {{
                background-color: #1e1e2e;
                color: #ffffff;
            }}
            QPushButton#btn_menu_ativo {{
                background-color: {t['cor_primaria']};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                text-align: left;
            }}
        """)

    def construir_interface(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QHBoxLayout(widget_central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # SIDEBAR
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        layout_sidebar = QVBoxLayout(self.sidebar)
        layout_sidebar.setContentsMargins(12, 20, 12, 20)
        layout_sidebar.setSpacing(8)

        # Nome da loja
        label_logo = QLabel(self.loja["nome"])
        label_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_logo.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #6c63ff;
            padding: 10px;
            border-bottom: 1px solid #2a2a3a;
            margin-bottom: 10px;
        """)
        layout_sidebar.addWidget(label_logo)

        # Usuário logado
        label_usuario = QLabel(f"👤 {self.usuario['nome']}")
        label_usuario.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_usuario.setStyleSheet("""
            font-size: 12px;
            color: #00d4aa;
            padding: 4px;
            border: none;
            margin-bottom: 8px;
        """)
        layout_sidebar.addWidget(label_usuario)

        label_perfil = QLabel(f"🔑 {self.usuario['perfil'].upper()}")
        label_perfil.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_perfil.setStyleSheet("""
            font-size: 11px;
            color: #7070a0;
            border: none;
            margin-bottom: 12px;
        """)
        layout_sidebar.addWidget(label_perfil)

        # Menus
        self.botoes_menu = []
        menus = [
            ("🛒  Caixa", 0),
            ("💰  Op. Caixa", 1),
            ("📦  Produtos", 2),
            ("👥  Clientes", 3),
            ("📊  Relatórios", 4),
        ]

        for texto, indice in menus:
            btn = QPushButton(texto)
            btn.setObjectName("btn_menu")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=indice: self.mudar_tela(i))
            layout_sidebar.addWidget(btn)
            self.botoes_menu.append(btn)

        layout_sidebar.addStretch()

        # Botão sair
        btn_sair = QPushButton("🚪 Sair")
        btn_sair.setObjectName("btn_menu")
        btn_sair.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sair.clicked.connect(self.fazer_logout)
        btn_sair.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ff5f57;
                border: 1px solid #ff5f57;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5f57;
                color: white;
            }
        """)
        layout_sidebar.addWidget(btn_sair)

        # Versão
        label_versao = QLabel(f"Core Tech v{self.config['sistema']['versao']}")
        label_versao.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_versao.setStyleSheet("font-size: 11px; color: #3a3a5a; border: none;")
        layout_sidebar.addWidget(label_versao)

        # CONTEÚDO
        self.stack = QStackedWidget()
        self.tela_caixa = TelaCaixa(self.config)
        self.tela_produtos = TelaProdutos(self.config)
        self.tela_clientes = TelaClientes(self.config)
        self.tela_relatorios = TelaRelatorios(self.config)

        self.tela_caixa_op = TelaCaixaOperacao(self.config, self.usuario)
        self.stack.addWidget(self.tela_caixa)
        self.stack.addWidget(self.tela_caixa_op)
        self.stack.addWidget(self.tela_produtos)
        self.stack.addWidget(self.tela_clientes)
        self.stack.addWidget(self.tela_relatorios)

        layout_principal.addWidget(self.sidebar)
        layout_principal.addWidget(self.stack)

        self.mudar_tela(0)

    def mudar_tela(self, indice):
        self.stack.setCurrentIndex(indice)
        for i, btn in enumerate(self.botoes_menu):
            btn.setObjectName("btn_menu_ativo" if i == indice else "btn_menu")
            btn.setStyle(btn.style())

    def fazer_logout(self):
        from PyQt6.QtWidgets import QMessageBox

        resposta = QMessageBox.question(
            self,
            "Sair",
            "Tem certeza que deseja sair do sistema?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            self.close()
            iniciar_app()


def iniciar_app():
    config = carregar_config()

    login_window = TelaLogin(config)

    def ao_fazer_login(usuario):
        login_window.close()
        main = MainWindow(config, usuario)
        main.show()
        app._main_window = main

    login_window.login_sucesso.connect(ao_fazer_login)
    login_window.show()
    app._login_window = login_window


if __name__ == "__main__":
    criar_tabelas()
    criar_usuario_admin()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    iniciar_app()

    sys.exit(app.exec())
