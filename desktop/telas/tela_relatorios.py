from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFrame,
    QHeaderView,
    QTabWidget,
    QDateEdit,
)
from PyQt6.QtCore import Qt, QDate

import sys, os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from core.relatorios import (
    relatorio_vendas_dia,
    produtos_mais_vendidos,
    faturamento_por_categoria,
    resumo_estoque,
    clientes_mais_ativos,
    faturamento_mensal,
)
from core.vendas import vendas_do_dia, total_vendas_do_dia


class TelaRelatorios(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.tema = config["tema"]
        self.construir_interface()

    def construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Título
        titulo = QLabel("📊 Relatórios")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #6c63ff;")
        layout.addWidget(titulo)

        # Cards de resumo do dia
        layout_cards = QHBoxLayout()
        layout_cards.setSpacing(12)

        self.card_faturamento = self.criar_card(
            "💰 Faturamento Hoje", "R$ 0,00", "#00d4aa"
        )
        self.card_vendas = self.criar_card("🛒 Vendas Hoje", "0", "#6c63ff")
        self.card_estoque = self.criar_card("📦 Produtos Ativos", "0", "#ffbd2e")
        self.card_criticos = self.criar_card("⚠️ Estoque Crítico", "0", "#ff5f57")

        layout_cards.addWidget(self.card_faturamento)
        layout_cards.addWidget(self.card_vendas)
        layout_cards.addWidget(self.card_estoque)
        layout_cards.addWidget(self.card_criticos)
        layout.addLayout(layout_cards)

        # Abas de relatórios
        self.abas = QTabWidget()
        self.abas.setStyleSheet("""
            QTabWidget::pane {
                background-color: #111118;
                border: 1px solid #2a2a3a;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #1e1e2e;
                color: #7070a0;
                padding: 10px 20px;
                border: none;
                margin-right: 4px;
                border-radius: 6px 6px 0 0;
            }
            QTabBar::tab:selected {
                background-color: #6c63ff;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #2a2a3a;
                color: white;
            }
        """)

        # Aba vendas do dia
        aba_dia = QWidget()
        layout_dia = QVBoxLayout(aba_dia)
        layout_dia.setContentsMargins(12, 12, 12, 12)
        self.tabela_dia = self.criar_tabela(
            ["ID", "Total", "Desconto", "Pagamento", "Status", "Data/Hora", "Cliente"]
        )
        layout_dia.addWidget(self.tabela_dia)
        self.abas.addTab(aba_dia, "🛒 Vendas do Dia")

        # Aba produtos mais vendidos
        aba_produtos = QWidget()
        layout_produtos = QVBoxLayout(aba_produtos)
        layout_produtos.setContentsMargins(12, 12, 12, 12)
        self.tabela_produtos = self.criar_tabela(
            ["Produto", "Qtd Vendida", "Faturamento"]
        )
        layout_produtos.addWidget(self.tabela_produtos)
        self.abas.addTab(aba_produtos, "🏆 Mais Vendidos")

        # Aba faturamento por categoria
        aba_categoria = QWidget()
        layout_categoria = QVBoxLayout(aba_categoria)
        layout_categoria.setContentsMargins(12, 12, 12, 12)
        self.tabela_categoria = self.criar_tabela(
            ["Categoria", "Qtd Vendida", "Faturamento"]
        )
        layout_categoria.addWidget(self.tabela_categoria)
        self.abas.addTab(aba_categoria, "📂 Por Categoria")

        # Aba clientes mais ativos
        aba_clientes = QWidget()
        layout_clientes = QVBoxLayout(aba_clientes)
        layout_clientes.setContentsMargins(12, 12, 12, 12)
        self.tabela_clientes = self.criar_tabela(
            ["Cliente", "Total Compras", "Total Gasto"]
        )
        layout_clientes.addWidget(self.tabela_clientes)
        self.abas.addTab(aba_clientes, "👥 Melhores Clientes")

        # Aba faturamento mensal
        aba_mensal = QWidget()
        layout_mensal = QVBoxLayout(aba_mensal)
        layout_mensal.setContentsMargins(12, 12, 12, 12)
        self.tabela_mensal = self.criar_tabela(["Mês", "Total Vendas", "Faturamento"])
        layout_mensal.addWidget(self.tabela_mensal)
        self.abas.addTab(aba_mensal, "📅 Mensal")

        layout.addWidget(self.abas)

        # Botão atualizar
        btn_atualizar = QPushButton("🔄 Atualizar Relatórios")
        btn_atualizar.clicked.connect(self.carregar_dados)
        btn_atualizar.setStyleSheet(f"""
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
        layout.addWidget(btn_atualizar)

        self.carregar_dados()

    def criar_card(self, titulo, valor, cor):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111118;
                border: 1px solid {cor};
                border-radius: 12px;
                padding: 8px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet(
            f"color: {cor}; font-size: 12px; font-weight: bold; border: none;"
        )

        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet(
            f"color: white; font-size: 24px; font-weight: bold; border: none;"
        )
        lbl_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)

        # Guarda referência ao label de valor
        frame.lbl_valor = lbl_valor
        return frame

    def criar_tabela(self, colunas):
        tabela = QTableWidget()
        tabela.setColumnCount(len(colunas))
        tabela.setHorizontalHeaderLabels(colunas)
        tabela.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabela.setStyleSheet("""
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
        return tabela

    def carregar_dados(self):
        # Cards
        total_dia = total_vendas_do_dia()
        vendas_dia = vendas_do_dia()
        resumo = resumo_estoque()

        self.card_faturamento.lbl_valor.setText(f"R$ {total_dia:.2f}")
        self.card_vendas.lbl_valor.setText(str(len(vendas_dia)))

        if resumo:
            self.card_estoque.lbl_valor.setText(str(resumo[0]))
            self.card_criticos.lbl_valor.setText(str(resumo[3]))

        # Tabela vendas do dia
        self.tabela_dia.setRowCount(len(vendas_dia))
        for row, v in enumerate(vendas_dia):
            for col, val in enumerate(v):
                self.tabela_dia.setItem(
                    row, col, QTableWidgetItem(str(val) if val else "—")
                )

        # Produtos mais vendidos
        mais_vendidos = produtos_mais_vendidos()
        self.tabela_produtos.setRowCount(len(mais_vendidos))
        for row, p in enumerate(mais_vendidos):
            self.tabela_produtos.setItem(row, 0, QTableWidgetItem(p[0]))
            self.tabela_produtos.setItem(row, 1, QTableWidgetItem(str(p[1])))
            self.tabela_produtos.setItem(row, 2, QTableWidgetItem(f"R$ {p[2]:.2f}"))

        # Por categoria
        categorias = faturamento_por_categoria()
        self.tabela_categoria.setRowCount(len(categorias))
        for row, c in enumerate(categorias):
            self.tabela_categoria.setItem(
                row, 0, QTableWidgetItem(c[0] or "Sem categoria")
            )
            self.tabela_categoria.setItem(row, 1, QTableWidgetItem(str(c[1])))
            self.tabela_categoria.setItem(row, 2, QTableWidgetItem(f"R$ {c[2]:.2f}"))

        # Melhores clientes
        clientes = clientes_mais_ativos()
        self.tabela_clientes.setRowCount(len(clientes))
        for row, c in enumerate(clientes):
            self.tabela_clientes.setItem(row, 0, QTableWidgetItem(c[0]))
            self.tabela_clientes.setItem(row, 1, QTableWidgetItem(str(c[1])))
            self.tabela_clientes.setItem(row, 2, QTableWidgetItem(f"R$ {c[2]:.2f}"))

        # Mensal
        mensal = faturamento_mensal()
        self.tabela_mensal.setRowCount(len(mensal))
        for row, m in enumerate(mensal):
            self.tabela_mensal.setItem(row, 0, QTableWidgetItem(m[0]))
            self.tabela_mensal.setItem(row, 1, QTableWidgetItem(str(m[1])))
            self.tabela_mensal.setItem(row, 2, QTableWidgetItem(f"R$ {m[2]:.2f}"))
