from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QFrame,
    QMessageBox,
    QHeaderView,
    QFormLayout,
    QDialog,
)
from PyQt6.QtCore import Qt

import sys, os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from core.clientes import (
    cadastrar_cliente,
    listar_clientes,
    buscar_cliente_por_nome,
    atualizar_cliente,
    desativar_cliente,
    historico_compras_cliente,
)

ESTILO_INPUT = """
    QLineEdit {
        background-color: #1e1e2e;
        border: 1px solid #2a2a3a;
        border-radius: 8px;
        padding: 8px;
        color: #e8e8f0;
        font-size: 14px;
    }
    QLineEdit:focus { border: 1px solid #6c63ff; }
"""


class DialogCliente(QDialog):
    def __init__(self, parent=None, cliente=None):
        super().__init__(parent)
        self.cliente = cliente
        self.setWindowTitle("Cadastrar Cliente" if not cliente else "Editar Cliente")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog { background-color: #111118; }
            QLabel { color: #7070a0; font-size: 13px; }
        """ + ESTILO_INPUT)
        self.construir_interface()

    def construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        titulo = QLabel("Cadastrar Cliente" if not self.cliente else "Editar Cliente")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #6c63ff;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)

        self.input_nome = QLineEdit()
        self.input_cpf = QLineEdit()
        self.input_telefone = QLineEdit()
        self.input_email = QLineEdit()
        self.input_endereco = QLineEdit()

        self.input_nome.setPlaceholderText("Nome completo")
        self.input_cpf.setPlaceholderText("000.000.000-00")
        self.input_telefone.setPlaceholderText("(84) 99999-9999")
        self.input_email.setPlaceholderText("email@exemplo.com")
        self.input_endereco.setPlaceholderText("Rua, número, bairro")

        if self.cliente:
            self.input_nome.setText(self.cliente[1])
            self.input_cpf.setText(self.cliente[2] or "")
            self.input_telefone.setText(self.cliente[3] or "")
            self.input_email.setText(self.cliente[4] or "")
            self.input_endereco.setText(self.cliente[5] or "")

        form.addRow("Nome:", self.input_nome)
        form.addRow("CPF:", self.input_cpf)
        form.addRow("Telefone:", self.input_telefone)
        form.addRow("Email:", self.input_email)
        form.addRow("Endereço:", self.input_endereco)
        layout.addLayout(form)

        layout_btns = QHBoxLayout()
        btn_salvar = QPushButton("💾 Salvar")
        btn_cancelar = QPushButton("Cancelar")

        btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #6c63ff;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #5a52e0; }
        """)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #7070a0;
                border: 1px solid #2a2a3a;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover { color: white; border-color: white; }
        """)

        btn_salvar.clicked.connect(self.salvar)
        btn_cancelar.clicked.connect(self.reject)
        layout_btns.addWidget(btn_cancelar)
        layout_btns.addWidget(btn_salvar)
        layout.addLayout(layout_btns)

    def salvar(self):
        nome = self.input_nome.text().strip()
        cpf = self.input_cpf.text().strip()
        telefone = self.input_telefone.text().strip()
        email = self.input_email.text().strip()
        endereco = self.input_endereco.text().strip()

        if not nome:
            QMessageBox.warning(self, "Atenção", "O nome é obrigatório!")
            return

        if self.cliente:
            sucesso, msg = atualizar_cliente(
                self.cliente[0], nome, cpf, telefone, email, endereco
            )
        else:
            sucesso, msg = cadastrar_cliente(nome, cpf, telefone, email, endereco)

        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", msg)


class TelaClientes(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.tema = config["tema"]
        self.construir_interface()

    def construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Cabeçalho
        layout_cabecalho = QHBoxLayout()
        titulo = QLabel("👥 Clientes")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #6c63ff;")

        btn_novo = QPushButton("➕ Novo Cliente")
        btn_novo.clicked.connect(self.abrir_dialog_novo)
        btn_novo.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.tema['cor_primaria']};
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.tema['cor_secundaria']};
                color: black;
            }}
        """)

        layout_cabecalho.addWidget(titulo)
        layout_cabecalho.addStretch()
        layout_cabecalho.addWidget(btn_novo)
        layout.addLayout(layout_cabecalho)

        # Busca
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Buscar cliente por nome...")
        self.input_busca.setStyleSheet("""
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
        self.input_busca.textChanged.connect(self.filtrar_clientes)
        layout.addWidget(self.input_busca)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Nome", "CPF", "Telefone", "Email", "Endereço"]
        )
        self.tabela.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e2e;
                border: 1px solid #2a2a3a;
                border-radius: 8px;
                color: #e8e8f0;
                gridline-color: #2a2a3a;
            }
            QHeaderView::section {
                background-color: #16161f;
                color: #6c63ff;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #6c63ff;
                color: white;
            }
        """)
        layout.addWidget(self.tabela)

        # Botões de ação
        layout_acoes = QHBoxLayout()

        btn_historico = QPushButton("📋 Histórico de Compras")
        btn_historico.clicked.connect(self.ver_historico)
        btn_historico.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.tema['cor_primaria']};
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.tema['cor_secundaria']};
                color: black;
            }}
        """)

        btn_editar = QPushButton("✏️ Editar")
        btn_editar.clicked.connect(self.editar_cliente)
        btn_editar.setStyleSheet("""
            QPushButton {
                background-color: #ffbd2e;
                color: black;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #e6a800; }
        """)

        btn_remover = QPushButton("🗑 Remover")
        btn_remover.clicked.connect(self.remover_cliente)
        btn_remover.setStyleSheet("""
            QPushButton {
                background-color: #ff5f57;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #cc4a43; }
        """)

        layout_acoes.addWidget(btn_historico)
        layout_acoes.addStretch()
        layout_acoes.addWidget(btn_editar)
        layout_acoes.addWidget(btn_remover)
        layout.addLayout(layout_acoes)

        self.carregar_clientes()

    def carregar_clientes(self):
        clientes = listar_clientes()
        self.preencher_tabela(clientes)

    def preencher_tabela(self, clientes):
        self.tabela.setRowCount(len(clientes))
        for row, c in enumerate(clientes):
            self.tabela.setItem(row, 0, QTableWidgetItem(str(c[0])))
            self.tabela.setItem(row, 1, QTableWidgetItem(c[1]))
            self.tabela.setItem(row, 2, QTableWidgetItem(c[2] or ""))
            self.tabela.setItem(row, 3, QTableWidgetItem(c[3] or ""))
            self.tabela.setItem(row, 4, QTableWidgetItem(c[4] or ""))
            self.tabela.setItem(row, 5, QTableWidgetItem(c[5] or ""))

    def filtrar_clientes(self):
        termo = self.input_busca.text().strip()
        if termo:
            clientes = buscar_cliente_por_nome(termo)
        else:
            clientes = listar_clientes()
        self.preencher_tabela(clientes)

    def abrir_dialog_novo(self):
        dialog = DialogCliente(self)
        if dialog.exec():
            self.carregar_clientes()

    def editar_cliente(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um cliente para editar!")
            return
        cliente_id = int(self.tabela.item(row, 0).text())
        clientes = listar_clientes()
        cliente = next((c for c in clientes if c[0] == cliente_id), None)
        if cliente:
            dialog = DialogCliente(self, cliente)
            if dialog.exec():
                self.carregar_clientes()

    def remover_cliente(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um cliente para remover!")
            return
        nome = self.tabela.item(row, 1).text()
        resposta = QMessageBox.question(
            self,
            "Remover Cliente",
            f"Tem certeza que deseja remover '{nome}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            cliente_id = int(self.tabela.item(row, 0).text())
            sucesso, msg = desativar_cliente(cliente_id)
            if sucesso:
                self.carregar_clientes()
            else:
                QMessageBox.critical(self, "Erro", msg)

    def ver_historico(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um cliente!")
            return
        cliente_id = int(self.tabela.item(row, 0).text())
        nome = self.tabela.item(row, 1).text()
        historico = historico_compras_cliente(cliente_id)
        if not historico:
            QMessageBox.information(
                self, "Histórico", f"{nome} ainda não realizou compras."
            )
            return
        texto = f"Histórico de compras — {nome}\n\n"
        total_gasto = 0
        for h in historico:
            texto += f"Venda #{h[0]} | R$ {h[1]:.2f} | {h[2]} | {h[3]}\n"
            total_gasto += h[1]
        texto += f"\nTotal gasto: R$ {total_gasto:.2f}"
        QMessageBox.information(self, "Histórico de Compras", texto)
