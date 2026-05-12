import streamlit as st
import sys, os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import criar_tabelas
from core.produtos import (
    cadastrar_produto,
    listar_produtos,
    buscar_produto_por_codigo,
    buscar_produto_por_nome,
    desativar_produto,
)
from core.vendas import registrar_venda, vendas_do_dia, total_vendas_do_dia
from core.clientes import cadastrar_cliente, listar_clientes
from core.relatorios import produtos_mais_vendidos, resumo_estoque, faturamento_mensal
from comprovante.comprovante import gerar_comprovante

# Carrega config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

loja = config["loja"]
tema = config["tema"]

# Inicializa banco
criar_tabelas()

# Configuração da página
st.set_page_config(
    page_title=f'PDV — {loja["nome"]}', layout="wide", initial_sidebar_state="expanded"
)

# Estilo global
st.markdown(
    f"""
<style>
    .main {{ background-color: {tema['cor_fundo']}; }}
    .stButton>button {{
        background-color: {tema['cor_primaria']};
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }}
    .stButton>button:hover {{
        background-color: {tema['cor_secundaria']};
        color: black;
    }}
    .metric-card {{
        background-color: #111118;
        border: 1px solid {tema['cor_primaria']};
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }}
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.title(f"🏪 {loja['nome']}")
st.sidebar.markdown("---")
menu = st.sidebar.selectbox(
    "Navegação", ["🛒 Caixa", "📦 Produtos", "👥 Clientes", "📊 Relatórios"]
)
st.sidebar.markdown("---")
st.sidebar.caption(f"Core Tech v{config['sistema']['versao']}")

# =====================
# CAIXA
# =====================
if menu == "🛒 Caixa":
    st.title("🛒 Caixa")

    if "itens" not in st.session_state:
        st.session_state.itens = []

    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form("adicionar_item", clear_on_submit=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            busca = c1.text_input("Código ou Nome do Produto")
            qtd = c2.number_input("Qtd", min_value=1, value=1)
            submit = st.form_submit_button("➕ Adicionar")

            if submit and busca:
                produto = buscar_produto_por_codigo(busca)
                if not produto:
                    resultados = buscar_produto_por_nome(busca)
                    produto = resultados[0] if resultados else None

                if produto:
                    if produto[4] < qtd:
                        st.error(f"Estoque insuficiente! Disponível: {produto[4]}")
                    else:
                        # Verifica se já está na lista
                        encontrado = False
                        for item in st.session_state.itens:
                            if item["produto_id"] == produto[0]:
                                item["quantidade"] += qtd
                                encontrado = True
                                break
                        if not encontrado:
                            st.session_state.itens.append(
                                {
                                    "produto_id": produto[0],
                                    "codigo": produto[1],
                                    "nome_produto": produto[2],
                                    "quantidade": qtd,
                                    "preco_unitario": produto[3],
                                }
                            )
                        st.rerun()
                else:
                    st.error("Produto não encontrado!")

        if st.session_state.itens:
            import pandas as pd

            df = pd.DataFrame(st.session_state.itens)
            df["subtotal"] = df["quantidade"] * df["preco_unitario"]
            df = df[["nome_produto", "quantidade", "preco_unitario", "subtotal"]]
            df.columns = ["Produto", "Qtd", "Preço Unit.", "Subtotal"]
            st.dataframe(df, use_container_width=True)

            if st.button("🗑 Limpar Lista"):
                st.session_state.itens = []
                st.rerun()

    with col2:
        total = sum(
            i["quantidade"] * i["preco_unitario"] for i in st.session_state.itens
        )
        desconto = st.number_input("Desconto (R$)", min_value=0.0, value=0.0)
        total_final = max(0, total - desconto)

        st.metric("Total", f"R$ {total_final:.2f}")

        forma = st.selectbox(
            "Pagamento", ["Dinheiro", "Pix", "Cartão Débito", "Cartão Crédito"]
        )

        if st.button("✅ Finalizar Venda", type="primary"):
            if st.session_state.itens:
                sucesso, venda_id, total_venda, data_hora = registrar_venda(
                    st.session_state.itens, forma, desconto=desconto
                )
                if sucesso:
                    comprovante = gerar_comprovante(
                        venda_id,
                        data_hora,
                        st.session_state.itens,
                        total_venda,
                        forma,
                        loja,
                    )
                    st.success(f"Venda #{venda_id} registrada!")
                    st.code(comprovante)
                    st.session_state.itens = []
                    st.balloons()
                else:
                    st.error("Erro ao registrar venda!")
            else:
                st.warning("Adicione pelo menos um produto!")

# =====================
# PRODUTOS
# =====================
elif menu == "📦 Produtos":
    st.title("📦 Produtos")

    with st.expander("➕ Cadastrar Novo Produto"):
        c1, c2, c3 = st.columns(3)
        codigo = c1.text_input("Código")
        nome = c2.text_input("Nome")
        categoria = c3.text_input("Categoria")
        c4, c5, c6 = st.columns(3)
        preco = c4.number_input("Preço (R$)", min_value=0.01, value=0.01)
        estoque = c5.number_input("Estoque", min_value=0, value=0)
        minimo = c6.number_input("Estoque Mínimo", min_value=0, value=5)

        if st.button("💾 Salvar Produto"):
            if codigo and nome:
                sucesso, msg = cadastrar_produto(
                    codigo, nome, preco, estoque, minimo, categoria
                )
                if sucesso:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Código e nome são obrigatórios!")

    st.markdown("---")
    busca = st.text_input("🔍 Buscar produto")
    produtos = buscar_produto_por_nome(busca) if busca else listar_produtos()

    if produtos:
        import pandas as pd

        df = pd.DataFrame(
            produtos,
            columns=[
                "ID",
                "Código",
                "Nome",
                "Preço",
                "Estoque",
                "Mín.",
                "Categoria",
                "Ativo",
            ],
        )
        df = df[["ID", "Código", "Nome", "Preço", "Estoque", "Mín.", "Categoria"]]
        df["Preço"] = df["Preço"].apply(lambda x: f"R$ {x:.2f}")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado.")

# =====================
# CLIENTES
# =====================
elif menu == "👥 Clientes":
    st.title("👥 Clientes")

    with st.expander("➕ Cadastrar Novo Cliente"):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome")
        cpf = c2.text_input("CPF")
        c3, c4 = st.columns(2)
        telefone = c3.text_input("Telefone")
        email = c4.text_input("Email")
        endereco = st.text_input("Endereço")

        if st.button("💾 Salvar Cliente"):
            if nome:
                sucesso, msg = cadastrar_cliente(nome, cpf, telefone, email, endereco)
                if sucesso:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("O nome é obrigatório!")

    st.markdown("---")
    clientes = listar_clientes()
    if clientes:
        import pandas as pd

        df = pd.DataFrame(
            clientes,
            columns=["ID", "Nome", "CPF", "Telefone", "Email", "Endereço", "Ativo"],
        )
        df = df[["ID", "Nome", "CPF", "Telefone", "Email", "Endereço"]]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum cliente cadastrado.")

# =====================
# RELATÓRIOS
# =====================
elif menu == "📊 Relatórios":
    st.title("📊 Relatórios")

    # Cards resumo
    resumo = resumo_estoque()
    total_dia = total_vendas_do_dia()
    vendas = vendas_do_dia()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Faturamento Hoje", f"R$ {total_dia:.2f}")
    c2.metric("🛒 Vendas Hoje", len(vendas))
    c3.metric("📦 Produtos Ativos", resumo[0] if resumo else 0)
    c4.metric("⚠️ Estoque Crítico", resumo[3] if resumo else 0)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Produtos Mais Vendidos")
        mais_vendidos = produtos_mais_vendidos()
        if mais_vendidos:
            import pandas as pd

            df = pd.DataFrame(
                mais_vendidos, columns=["Produto", "Qtd Vendida", "Faturamento"]
            )
            df["Faturamento"] = df["Faturamento"].apply(lambda x: f"R$ {x:.2f}")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nenhuma venda registrada.")

    with col2:
        st.subheader("📅 Faturamento Mensal")
        mensal = faturamento_mensal()
        if mensal:
            import pandas as pd

            df = pd.DataFrame(mensal, columns=["Mês", "Vendas", "Faturamento"])
            df["Faturamento"] = df["Faturamento"].apply(lambda x: f"R$ {x:.2f}")
            st.dataframe(df, use_container_width=True)
            st.bar_chart(
                pd.DataFrame(
                    mensal, columns=["Mês", "Vendas", "Faturamento"]
                ).set_index("Mês")["Faturamento"]
            )
        else:
            st.info("Nenhuma venda registrada.")
