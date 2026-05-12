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
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QFormLayout,
    QDialog,
)
from PyQt6.QtCore import Qt

import sys, os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from core.produtos import (
    cadastrar_produto,
    listar_produtos,
    buscar_produto_por_nome,
    atualizar_produto,
    desativar_produto,
    produtos_estoque_baixo,
)

ESTILO_INPUT = """
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        background-color: #1e1e2e;
        border: 1px solid #2a2a3a;
        border-radius: 8px;
        padding: 8px;
        color: #e8e8f0;
        font-size: 14px;
    }
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
        border: 1px solid #6c63ff;
    }
    QComboBox QAbstractItemView {
        background-color: #1e1e2e;
        color: #e8e8f0;
        selection-background-color: #6c63ff;
    }
"""


class DialogProduto(QDialog):
    def __init__(self, parent=None, produto=None):
        super().__init__(parent)
        self.produto = produto
        self.setWindowTitle("Cadastrar Produto" if not produto else "Editar Produto")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #111118;
            }
            QLabel {
                color: #7070a0;
                font-size: 13px;
            }
        """ + ESTILO_INPUT)
        self.construir_interface()

    def construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        titulo = QLabel("Cadastrar Produto" if not self.produto else "Editar Produto")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #6c63ff;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)

        self.input_codigo = QLineEdit()
        self.input_nome = QLineEdit()
        self.input_preco = QDoubleSpinBox()
        self.input_estoque = QSpinBox()
        self.input_minimo = QSpinBox()
        self.input_categoria = QLineEdit()

        self.input_preco.setMinimum(0.01)
        self.input_preco.setMaximum(99999.99)
        self.input_preco.setDecimals(2)
        self.input_preco.setValue(0.01)

        self.input_estoque.setMinimum(0)
        self.input_estoque.setMaximum(99999)

        self.input_minimo.setMinimum(0)
        self.input_minimo.setMaximum(9999)
        self.input_minimo.setValue(5)

        self.input_codigo.setPlaceholderText("Ex: 7891234567890")
        self.input_nome.setPlaceholderText("Nome do produto")
        self.input_categoria.setPlaceholderText("Ex: Bebidas, Laticínios...")

        # Preenche se for edição
        if self.produto:
            self.input_codigo.setText(self.produto[1])
            self.input_nome.setText(self.produto[2])
            self.input_preco.setValue(self.produto[3])
            self.input_estoque.setValue(self.produto[4])
            self.input_minimo.setValue(self.produto[5])
            self.input_categoria.setText(self.produto[6] or "")

        form.addRow("Código:", self.input_codigo)
        form.addRow("Nome:", self.input_nome)
        form.addRow("Preço (R$):", self.input_preco)
        form.addRow("Estoque:", self.input_estoque)
        form.addRow("Estoque Mínimo:", self.input_minimo)
        form.addRow("Categoria:", self.input_categoria)
        layout.addLayout(form)

        # Botões
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
        codigo = self.input_codigo.text().strip()
        nome = self.input_nome.text().strip()
        preco = self.input_preco.value()
        estoque = self.input_estoque.value()
        minimo = self.input_minimo.value()
        categoria = self.input_categoria.text().strip()

        if not codigo or not nome:
            QMessageBox.warning(self, "Atenção", "Código e nome são obrigatórios!")
            return

        if self.produto:
            sucesso, msg = atualizar_produto(
                self.produto[0], codigo, nome, preco, minimo, categoria
            )
        else:
            sucesso, msg = cadastrar_produto(
                codigo, nome, preco, estoque, minimo, categoria
            )

        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", msg)


class TelaProdutos(QWidget):
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
        titulo = QLabel("📦 Produtos")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #6c63ff;")

        btn_novo = QPushButton("➕ Novo Produto")
        btn_novo.clicked.connect(self.abrir_dialog_novo)
        btn_novo.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.tema['cor_primaria']};
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {self.tema['cor_secundaria']}; color: black; }}
        """)

        btn_estoque_baixo = QPushButton("⚠️ Estoque Baixo")
        btn_estoque_baixo.clicked.connect(self.mostrar_estoque_baixo)
        btn_estoque_baixo.setStyleSheet("""
            QPushButton {
                background-color: #ffbd2e;
                color: black;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #e6a800; }
        """)

        layout_cabecalho.addWidget(titulo)
        layout_cabecalho.addStretch()
        layout_cabecalho.addWidget(btn_estoque_baixo)
        layout_cabecalho.addWidget(btn_novo)
        layout.addLayout(layout_cabecalho)

        # Busca
        layout_busca = QHBoxLayout()
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Buscar produto por nome...")
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
        self.input_busca.textChanged.connect(self.filtrar_produtos)

        layout_busca.addWidget(self.input_busca)
        layout.addLayout(layout_busca)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Código", "Nome", "Preço", "Estoque", "Mín.", "Categoria"]
        )
        self.tabela.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
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
        btn_editar = QPushButton("✏️ Editar")
        btn_editar.clicked.connect(self.editar_produto)
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
        btn_remover.clicked.connect(self.remover_produto)
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

        layout_acoes.addStretch()
        layout_acoes.addWidget(btn_editar)
        layout_acoes.addWidget(btn_remover)
        layout.addLayout(layout_acoes)

        self.carregar_produtos()

    def carregar_produtos(self):
        produtos = listar_produtos()
        self.preencher_tabela(produtos)

    def preencher_tabela(self, produtos):
        self.tabela.setRowCount(len(produtos))
        for row, p in enumerate(produtos):
            self.tabela.setItem(row, 0, QTableWidgetItem(str(p[0])))
            self.tabela.setItem(row, 1, QTableWidgetItem(p[1]))
            self.tabela.setItem(row, 2, QTableWidgetItem(p[2]))
            self.tabela.setItem(row, 3, QTableWidgetItem(f"R$ {p[3]:.2f}"))
            self.tabela.setItem(row, 4, QTableWidgetItem(str(p[4])))
            self.tabela.setItem(row, 5, QTableWidgetItem(str(p[5])))
            self.tabela.setItem(row, 6, QTableWidgetItem(p[6] or ""))

            # Destaca estoque baixo
            if p[4] <= p[5]:
                for col in range(7):
                    item = self.tabela.item(row, col)
                    if item:
                        item.setForeground(
                            __import__("PyQt6.QtGui", fromlist=["QColor"]).QColor(
                                "#ffbd2e"
                            )
                        )

    def filtrar_produtos(self):
        termo = self.input_busca.text().strip()
        if termo:
            produtos = buscar_produto_por_nome(termo)
        else:
            produtos = listar_produtos()
        self.preencher_tabela(produtos)

    def abrir_dialog_novo(self):
        dialog = DialogProduto(self)
        if dialog.exec():
            self.carregar_produtos()

    def editar_produto(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um produto para editar!")
            return
        produto_id = int(self.tabela.item(row, 0).text())
        produtos = listar_produtos()
        produto = next((p for p in produtos if p[0] == produto_id), None)
        if produto:
            dialog = DialogProduto(self, produto)
            if dialog.exec():
                self.carregar_produtos()

    def remover_produto(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um produto para remover!")
            return
        nome = self.tabela.item(row, 2).text()
        resposta = QMessageBox.question(
            self,
            "Remover Produto",
            f"Tem certeza que deseja remover '{nome}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            produto_id = int(self.tabela.item(row, 0).text())
            sucesso, msg = desativar_produto(produto_id)
            if sucesso:
                self.carregar_produtos()
            else:
                QMessageBox.critical(self, "Erro", msg)

    def mostrar_estoque_baixo(self):
        produtos = produtos_estoque_baixo()
        if not produtos:
            QMessageBox.information(
                self, "Estoque", "Todos os produtos estão com estoque OK!"
            )
            return
        self.preencher_tabela(produtos)
