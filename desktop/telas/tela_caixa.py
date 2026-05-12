from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QFrame,
    QMessageBox,
    QHeaderView,
    QSpinBox,
    QDoubleSpinBox,
    QCompleter,
)
from PyQt6.QtCore import Qt, QStringListModel, QTimer

import sys, os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from core.produtos import buscar_produto_por_codigo, buscar_produto_por_nome
from core.vendas import registrar_venda
from comprovante.comprovante import gerar_comprovante


class TelaCaixa(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.tema = config["tema"]
        self.itens = []
        self.produto_selecionado = None
        self._atualizando_tabela = False
        self.construir_interface()

    def construir_interface(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # PAINEL ESQUERDO
        painel_esq = QFrame()
        painel_esq.setStyleSheet("""
            QFrame {
                background-color: #111118;
                border-radius: 12px;
                border: 1px solid #2a2a3a;
            }
        """)
        layout_esq = QVBoxLayout(painel_esq)
        layout_esq.setContentsMargins(16, 16, 16, 16)
        layout_esq.setSpacing(12)

        titulo = QLabel("🛒 Caixa")
        titulo.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #6c63ff; border: none;"
        )
        layout_esq.addWidget(titulo)

        # Busca
        layout_busca = QHBoxLayout()
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Digite o código ou nome do produto...")
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

        # Autocomplete
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.input_busca.setCompleter(self.completer)
        self.input_busca.textChanged.connect(self.atualizar_autocomplete)
        self.input_busca.returnPressed.connect(self.buscar_produto)

        btn_buscar = QPushButton("Buscar")
        btn_buscar.setFixedWidth(100)
        btn_buscar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_buscar.clicked.connect(self.buscar_produto)
        btn_buscar.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.tema['cor_primaria']};
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.tema['cor_secundaria']};
                color: black;
            }}
        """)

        layout_busca.addWidget(self.input_busca)
        layout_busca.addWidget(btn_buscar)
        layout_esq.addLayout(layout_busca)

        # Label produto encontrado
        self.label_produto = QLabel("")
        self.label_produto.setStyleSheet("""
            color: #00d4aa;
            font-size: 13px;
            font-weight: bold;
            border: none;
            padding: 4px 0;
        """)
        layout_esq.addWidget(self.label_produto)

        # Quantidade e botão adicionar
        layout_qtd = QHBoxLayout()
        label_qtd = QLabel("Quantidade:")
        label_qtd.setStyleSheet("border: none; color: #7070a0;")

        self.input_qtd = QSpinBox()
        self.input_qtd.setMinimum(0)
        self.input_qtd.setMaximum(9999)
        self.input_qtd.setValue(0)
        self.input_qtd.setSpecialValueText("0")
        self.input_qtd.setStyleSheet("""
            QSpinBox {
                background-color: #1e1e2e;
                border: 1px solid #2a2a3a;
                border-radius: 8px;
                padding: 8px;
                color: #e8e8f0;
                font-size: 14px;
            }
        """)
        # Enter no campo quantidade adiciona o item
        self.input_qtd.lineEdit().returnPressed.connect(self.adicionar_item)

        self.btn_adicionar = QPushButton("➕ Adicionar")
        self.btn_adicionar.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.btn_adicionar.clicked.connect(self.adicionar_item)
        self.btn_adicionar.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.tema['cor_secundaria']};
                color: black;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #00b894; }}
            QPushButton:focus {{
                border: 2px solid white;
            }}
        """)

        layout_qtd.addWidget(label_qtd)
        layout_qtd.addWidget(self.input_qtd)
        layout_qtd.addWidget(self.btn_adicionar)
        layout_qtd.addStretch()
        layout_esq.addLayout(layout_qtd)

        # Define ordem do Tab: busca → quantidade → adicionar
        self.setTabOrder(self.input_busca, self.input_qtd)
        self.setTabOrder(self.input_qtd, self.btn_adicionar)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(
            ["Código", "Produto", "Qtd", "Preço Unit.", "Subtotal"]
        )
        self.tabela.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabela.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
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
        self.tabela.itemChanged.connect(self.on_tabela_changed)
        layout_esq.addWidget(self.tabela)

        btn_remover = QPushButton("🗑 Remover Item Selecionado")
        btn_remover.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_remover.clicked.connect(self.remover_item)
        btn_remover.setStyleSheet("""
            QPushButton {
                background-color: #ff5f57;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #cc4a43; }
        """)
        layout_esq.addWidget(btn_remover)

        # PAINEL DIREITO
        painel_dir = QFrame()
        painel_dir.setFixedWidth(280)
        painel_dir.setStyleSheet("""
            QFrame {
                background-color: #111118;
                border-radius: 12px;
                border: 1px solid #2a2a3a;
            }
        """)
        layout_dir = QVBoxLayout(painel_dir)
        layout_dir.setContentsMargins(16, 16, 16, 16)
        layout_dir.setSpacing(12)

        label_total_titulo = QLabel("Total da Venda")
        label_total_titulo.setStyleSheet(
            "font-size: 14px; color: #7070a0; border: none;"
        )
        label_total_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_total = QLabel("R$ 0,00")
        self.label_total.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #00d4aa;
            border: none;
        """)
        self.label_total.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_desconto = QLabel("Desconto (R$):")
        label_desconto.setStyleSheet("border: none; color: #7070a0;")
        self.input_desconto = QDoubleSpinBox()
        self.input_desconto.setMinimum(0.0)
        self.input_desconto.setMaximum(9999.99)
        self.input_desconto.setDecimals(2)
        self.input_desconto.setValue(0.0)
        self.input_desconto.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.input_desconto.valueChanged.connect(self.atualizar_total)
        self.input_desconto.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #1e1e2e;
                border: 1px solid #2a2a3a;
                border-radius: 8px;
                padding: 8px;
                color: #e8e8f0;
                font-size: 14px;
            }
        """)

        label_pagamento = QLabel("Forma de Pagamento:")
        label_pagamento.setStyleSheet("border: none; color: #7070a0;")
        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItems(
            ["Dinheiro", "Pix", "Cartão Débito", "Cartão Crédito"]
        )
        self.combo_pagamento.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.combo_pagamento.setStyleSheet("""
            QComboBox {
                background-color: #1e1e2e;
                border: 1px solid #2a2a3a;
                border-radius: 8px;
                padding: 8px;
                color: #e8e8f0;
                font-size: 14px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #1e1e2e;
                color: #e8e8f0;
                selection-background-color: #6c63ff;
            }
        """)

        btn_finalizar = QPushButton("✅ Finalizar Venda")
        btn_finalizar.setFixedHeight(50)
        btn_finalizar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_finalizar.clicked.connect(self.finalizar_venda)
        btn_finalizar.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.tema['cor_secundaria']};
                color: #000000;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #00b894; }}
        """)

        btn_cancelar = QPushButton("❌ Cancelar Venda")
        btn_cancelar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_cancelar.clicked.connect(self.cancelar_venda)
        btn_cancelar.setStyleSheet("""
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

        layout_dir.addWidget(label_total_titulo)
        layout_dir.addWidget(self.label_total)
        layout_dir.addWidget(label_desconto)
        layout_dir.addWidget(self.input_desconto)
        layout_dir.addWidget(label_pagamento)
        layout_dir.addWidget(self.combo_pagamento)
        layout_dir.addStretch()
        layout_dir.addWidget(btn_finalizar)
        layout_dir.addWidget(btn_cancelar)

        layout.addWidget(painel_esq)
        layout.addWidget(painel_dir)

    def atualizar_autocomplete(self):
        termo = self.input_busca.text().strip()
        if len(termo) >= 2:
            produtos = buscar_produto_por_nome(termo)
            nomes = [f"{p[1]} — {p[2]}" for p in produtos]
            model = QStringListModel(nomes)
            self.completer.setModel(model)
        self.produto_selecionado = None
        self.label_produto.setText("")

    def buscar_produto(self):
        termo = self.input_busca.text().strip()
        if not termo:
            return

        if " — " in termo:
            codigo = termo.split(" — ")[0].strip()
            produto = buscar_produto_por_codigo(codigo)
        else:
            produto = buscar_produto_por_codigo(termo)
            if not produto:
                produtos = buscar_produto_por_nome(termo)
                produto = produtos[0] if produtos else None

        if not produto:
            QMessageBox.warning(
                self,
                "Produto não encontrado",
                f"Nenhum produto encontrado para '{termo}'.",
            )
            self.label_produto.setText("")
            self.produto_selecionado = None
            return

        self.produto_selecionado = produto
        self.label_produto.setText(
            f"✔ {produto[2]} — R$ {produto[3]:.2f} — Estoque: {produto[4]}"
        )

        # Zera e foca na quantidade para digitar direto
        self.input_qtd.setValue(0)
        self.input_qtd.selectAll()
        self.input_qtd.setFocus()

    def adicionar_item(self):
        if not self.produto_selecionado:
            QMessageBox.warning(self, "Atenção", "Busque um produto primeiro!")
            return

        qtd = self.input_qtd.value()
        if qtd <= 0:
            QMessageBox.warning(self, "Atenção", "Informe uma quantidade válida!")
            self.input_qtd.setFocus()
            return

        produto = self.produto_selecionado
        produto_id = produto[0]
        codigo = produto[1]
        nome = produto[2]
        preco = produto[3]
        estoque = produto[4]

        if estoque < qtd:
            QMessageBox.warning(
                self, "Estoque insuficiente", f"Estoque disponível: {estoque} unidades."
            )
            return

        for item in self.itens:
            if item["produto_id"] == produto_id:
                item["quantidade"] += qtd
                self.atualizar_tabela()
                self.limpar_busca()
                return

        self.itens.append(
            {
                "produto_id": produto_id,
                "codigo": codigo,
                "nome_produto": nome,
                "quantidade": qtd,
                "preco_unitario": preco,
            }
        )

        self.atualizar_tabela()
        self.limpar_busca()

    def limpar_busca(self):
        self.input_busca.clear()
        self.input_qtd.setValue(0)
        self.label_produto.setText("")
        self.produto_selecionado = None
        self.input_busca.setFocus()

    def on_tabela_changed(self, item):
        if self._atualizando_tabela:
            return
        if item.column() == 2:
            try:
                nova_qtd = int(item.text())
                if nova_qtd <= 0:
                    nova_qtd = 1
                self.itens[item.row()]["quantidade"] = nova_qtd
                self.atualizar_tabela()
            except ValueError:
                self.atualizar_tabela()

    def atualizar_tabela(self):
        self._atualizando_tabela = True
        self.tabela.setRowCount(len(self.itens))
        for row, item in enumerate(self.itens):
            subtotal = item["quantidade"] * item["preco_unitario"]
            self.tabela.setItem(row, 0, QTableWidgetItem(item["codigo"]))
            self.tabela.setItem(row, 1, QTableWidgetItem(item["nome_produto"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(str(item["quantidade"])))
            self.tabela.setItem(
                row, 3, QTableWidgetItem(f"R$ {item['preco_unitario']:.2f}")
            )
            self.tabela.setItem(row, 4, QTableWidgetItem(f"R$ {subtotal:.2f}"))
        self._atualizando_tabela = False
        self.atualizar_total()

    def atualizar_total(self):
        total = sum(i["quantidade"] * i["preco_unitario"] for i in self.itens)
        desconto = self.input_desconto.value()
        total_final = max(0, total - desconto)
        self.label_total.setText(f"R$ {total_final:.2f}")

    def remover_item(self):
        row = self.tabela.currentRow()
        if row >= 0:
            self.itens.pop(row)
            self.atualizar_tabela()

    def finalizar_venda(self):
        self.input_desconto.clearFocus()
        self.combo_pagamento.clearFocus()
        self.setFocus()

        if not self.itens:
            QMessageBox.warning(self, "Atenção", "Adicione pelo menos um produto!")
            return

        desconto = self.input_desconto.value()
        forma = self.combo_pagamento.currentText()

        # Guarda os itens antes de limpar
        itens_venda = self.itens.copy()

        sucesso, venda_id, total, data_hora = registrar_venda(
            itens_venda, forma, desconto=desconto
        )

        if sucesso:
            # Limpa a tela imediatamente — sem delay
            self.itens = []
            self.atualizar_tabela()
            self.input_desconto.setValue(0.0)
            self.limpar_busca()

            # Gera e exibe o comprovante após limpar
            comprovante = gerar_comprovante(
                venda_id, data_hora, itens_venda, total, forma, self.config["loja"]
            )
            QMessageBox.information(
                self,
                "Venda Finalizada!",
                f"Venda #{venda_id} registrada!\n\n{comprovante}",
            )
        else:
            QMessageBox.critical(self, "Erro", f"Erro ao registrar venda:\n{data_hora}")

    def cancelar_venda(self):
        if not self.itens:
            return
        resposta = QMessageBox.question(
            self,
            "Cancelar Venda",
            "Tem certeza que deseja cancelar a venda atual?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            self.itens = []
            self.atualizar_tabela()
            self.input_desconto.setValue(0.0)
            self.limpar_busca()
