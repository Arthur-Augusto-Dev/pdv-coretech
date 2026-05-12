import sys, os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QMessageBox,
    QDoubleSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt6.QtCore import Qt
from datetime import datetime

from core.caixa import (
    abrir_caixa,
    fechar_caixa,
    caixa_aberto,
    registrar_sangria,
    registrar_suprimento,
    obter_movimentacoes_caixa,
)


class TelaCaixaOperacao(QWidget):
    def __init__(self, config, usuario):
        super().__init__()
        self.config = config
        self.usuario = usuario
        self.tema = config["tema"]
        self.construir_interface()

    def construir_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        titulo = QLabel("💰 Operação de Caixa")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #6c63ff;")
        layout.addWidget(titulo)

        # Status do caixa
        self.frame_status = QFrame()
        self.frame_status.setStyleSheet("""
            QFrame {
                background-color: #111118;
                border-radius: 12px;
                border: 1px solid #2a2a3a;
            }
        """)
        layout_status = QHBoxLayout(self.frame_status)
        layout_status.setContentsMargins(20, 16, 20, 16)

        self.label_status = QLabel("Verificando...")
        self.label_status.setStyleSheet(
            "font-size: 16px; font-weight: bold; border: none;"
        )

        self.label_abertura = QLabel("")
        self.label_abertura.setStyleSheet(
            "font-size: 13px; color: #7070a0; border: none;"
        )

        self.label_valor_inicial = QLabel("")
        self.label_valor_inicial.setStyleSheet(
            "font-size: 13px; color: #00d4aa; border: none;"
        )

        layout_status.addWidget(self.label_status)
        layout_status.addStretch()
        layout_status.addWidget(self.label_valor_inicial)
        layout_status.addWidget(self.label_abertura)
        layout.addWidget(self.frame_status)

        # Área principal
        layout_main = QHBoxLayout()
        layout_main.setSpacing(16)

        # Painel esquerdo — ações
        painel_esq = QFrame()
        painel_esq.setFixedWidth(300)
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

        # Abertura de caixa
        label_abertura = QLabel("Abertura de Caixa")
        label_abertura.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #e8e8f0; border: none;"
        )
        layout_esq.addWidget(label_abertura)

        label_fundo = QLabel("Valor do fundo de caixa (R$):")
        label_fundo.setStyleSheet("color: #7070a0; font-size: 13px; border: none;")
        self.input_fundo = QDoubleSpinBox()
        self.input_fundo.setMinimum(0.0)
        self.input_fundo.setMaximum(99999.99)
        self.input_fundo.setDecimals(2)
        self.input_fundo.setValue(0.0)
        self.input_fundo.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #1e1e2e;
                border: 1px solid #2a2a3a;
                border-radius: 8px;
                padding: 8px;
                color: #e8e8f0;
                font-size: 14px;
            }
        """)

        self.btn_abrir = QPushButton("🔓 Abrir Caixa")
        self.btn_abrir.setFixedHeight(42)
        self.btn_abrir.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_abrir.clicked.connect(self.abrir_caixa)
        self.btn_abrir.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.tema['cor_secundaria']};
                color: black;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{ background-color: #00b894; }}
        """)

        layout_esq.addWidget(label_fundo)
        layout_esq.addWidget(self.input_fundo)
        layout_esq.addWidget(self.btn_abrir)

        # Separador
        linha = QFrame()
        linha.setFrameShape(QFrame.Shape.HLine)
        linha.setStyleSheet("background-color: #2a2a3a; border: none; max-height: 1px;")
        layout_esq.addWidget(linha)

        # Sangria
        label_sangria = QLabel("Sangria")
        label_sangria.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #e8e8f0; border: none;"
        )
        layout_esq.addWidget(label_sangria)

        label_val_sangria = QLabel("Valor (R$):")
        label_val_sangria.setStyleSheet(
            "color: #7070a0; font-size: 13px; border: none;"
        )
        self.input_sangria = QDoubleSpinBox()
        self.input_sangria.setMinimum(0.01)
        self.input_sangria.setMaximum(99999.99)
        self.input_sangria.setDecimals(2)
        self.input_sangria.setValue(0.01)
        self.input_sangria.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #1e1e2e;
                border: 1px solid #2a2a3a;
                border-radius: 8px;
                padding: 8px;
                color: #e8e8f0;
                font-size: 14px;
            }
        """)

        self.btn_sangria = QPushButton("📤 Registrar Sangria")
        self.btn_sangria.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_sangria.clicked.connect(self.fazer_sangria)
        self.btn_sangria.setStyleSheet("""
            QPushButton {
                background-color: #ffbd2e;
                color: black;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #e6a800; }
        """)

        layout_esq.addWidget(label_val_sangria)
        layout_esq.addWidget(self.input_sangria)
        layout_esq.addWidget(self.btn_sangria)

        # Separador
        linha2 = QFrame()
        linha2.setFrameShape(QFrame.Shape.HLine)
        linha2.setStyleSheet(
            "background-color: #2a2a3a; border: none; max-height: 1px;"
        )
        layout_esq.addWidget(linha2)

        # Suprimento
        label_suprimento = QLabel("Suprimento")
        label_suprimento.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #e8e8f0; border: none;"
        )
        layout_esq.addWidget(label_suprimento)

        label_val_sup = QLabel("Valor (R$):")
        label_val_sup.setStyleSheet("color: #7070a0; font-size: 13px; border: none;")
        self.input_suprimento = QDoubleSpinBox()
        self.input_suprimento.setMinimum(0.01)
        self.input_suprimento.setMaximum(99999.99)
        self.input_suprimento.setDecimals(2)
        self.input_suprimento.setValue(0.01)
        self.input_suprimento.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #1e1e2e;
                border: 1px solid #2a2a3a;
                border-radius: 8px;
                padding: 8px;
                color: #e8e8f0;
                font-size: 14px;
            }
        """)

        self.btn_suprimento = QPushButton("📥 Registrar Suprimento")
        self.btn_suprimento.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_suprimento.clicked.connect(self.fazer_suprimento)
        self.btn_suprimento.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.tema['cor_primaria']};
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #5a52e0; }}
        """)

        layout_esq.addWidget(label_val_sup)
        layout_esq.addWidget(self.input_suprimento)
        layout_esq.addWidget(self.btn_suprimento)
        layout_esq.addStretch()

        # Botão fechar caixa
        self.btn_fechar = QPushButton("🔒 Fechar Caixa")
        self.btn_fechar.setFixedHeight(42)
        self.btn_fechar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_fechar.clicked.connect(self.fechar_caixa)
        self.btn_fechar.setStyleSheet("""
            QPushButton {
                background-color: #ff5f57;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #cc4a43; }
        """)
        layout_esq.addWidget(self.btn_fechar)

        # Painel direito — movimentações
        painel_dir = QFrame()
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

        label_mov = QLabel("📋 Movimentações do Caixa")
        label_mov.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #e8e8f0; border: none;"
        )
        layout_dir.addWidget(label_mov)

        self.tabela_mov = QTableWidget()
        self.tabela_mov.setColumnCount(4)
        self.tabela_mov.setHorizontalHeaderLabels(
            ["Tipo", "Valor", "Motivo", "Data/Hora"]
        )
        self.tabela_mov.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.tabela_mov.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela_mov.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela_mov.setStyleSheet("""
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
        layout_dir.addWidget(self.tabela_mov)

        self.label_resumo = QLabel("")
        self.label_resumo.setStyleSheet(
            "font-size: 13px; color: #00d4aa; border: none; padding: 8px;"
        )
        layout_dir.addWidget(self.label_resumo)

        layout_main.addWidget(painel_esq)
        layout_main.addWidget(painel_dir)
        layout.addLayout(layout_main)

        self.atualizar_status()

    def atualizar_status(self):
        caixa = caixa_aberto()
        if caixa:
            self.label_status.setText("🟢 Caixa ABERTO")
            self.label_status.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: #00d4aa; border: none;"
            )
            self.label_abertura.setText(f"Aberto em: {caixa[3]}")
            self.label_valor_inicial.setText(f"Fundo: R$ {caixa[2]:.2f}")
            self.btn_abrir.setEnabled(False)
            self.btn_fechar.setEnabled(True)
            self.btn_sangria.setEnabled(True)
            self.btn_suprimento.setEnabled(True)
            self.carregar_movimentacoes(caixa[0])
        else:
            self.label_status.setText("🔴 Caixa FECHADO")
            self.label_status.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: #ff5f57; border: none;"
            )
            self.label_abertura.setText("")
            self.label_valor_inicial.setText("")
            self.btn_abrir.setEnabled(True)
            self.btn_fechar.setEnabled(False)
            self.btn_sangria.setEnabled(False)
            self.btn_suprimento.setEnabled(False)
            self.tabela_mov.setRowCount(0)
            self.label_resumo.setText("")

    def carregar_movimentacoes(self, caixa_id):
        movs = obter_movimentacoes_caixa(caixa_id)
        self.tabela_mov.setRowCount(len(movs))
        total_entradas = 0
        total_saidas = 0
        for row, m in enumerate(movs):
            tipo = m[0]
            valor = m[1]
            motivo = m[2] or ""
            data = m[3]
            self.tabela_mov.setItem(row, 0, QTableWidgetItem(tipo.upper()))
            self.tabela_mov.setItem(row, 1, QTableWidgetItem(f"R$ {valor:.2f}"))
            self.tabela_mov.setItem(row, 2, QTableWidgetItem(motivo))
            self.tabela_mov.setItem(row, 3, QTableWidgetItem(data))
            if tipo in ("abertura", "suprimento"):
                total_entradas += valor
            else:
                total_saidas += valor
        saldo = total_entradas - total_saidas
        self.label_resumo.setText(
            f"Entradas: R$ {total_entradas:.2f}  |  "
            f"Saídas: R$ {total_saidas:.2f}  |  "
            f"Saldo: R$ {saldo:.2f}"
        )

    def abrir_caixa(self):
        fundo = self.input_fundo.value()
        sucesso, msg = abrir_caixa(fundo, self.usuario["id"])
        if sucesso:
            QMessageBox.information(self, "Caixa Aberto", msg)
            self.atualizar_status()
        else:
            QMessageBox.critical(self, "Erro", msg)

    def fechar_caixa(self):
        resposta = QMessageBox.question(
            self,
            "Fechar Caixa",
            "Tem certeza que deseja fechar o caixa?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            sucesso, msg = fechar_caixa(self.usuario["id"])
            if sucesso:
                QMessageBox.information(self, "Caixa Fechado", msg)
                self.atualizar_status()
            else:
                QMessageBox.critical(self, "Erro", msg)

    def fazer_sangria(self):
        valor = self.input_sangria.value()
        sucesso, msg = registrar_sangria(valor, self.usuario["id"])
        if sucesso:
            QMessageBox.information(self, "Sangria", msg)
            self.atualizar_status()
        else:
            QMessageBox.critical(self, "Erro", msg)

    def fazer_suprimento(self):
        valor = self.input_suprimento.value()
        sucesso, msg = registrar_suprimento(valor, self.usuario["id"])
        if sucesso:
            QMessageBox.information(self, "Suprimento", msg)
            self.atualizar_status()
        else:
            QMessageBox.critical(self, "Erro", msg)
