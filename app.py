
import streamlit as st
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime
import pandas as pd
import plotly.express as px

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="E-Shop Brasil",
    page_icon="🛒",
    layout="wide"
)

# CONEXÃO COM MONGODB
try:
    cliente_mongo = MongoClient(
        "mongodb://localhost:27017/",
        serverSelectionTimeoutMS=3000
    )
    cliente_mongo.admin.command("ping")

    db = cliente_mongo["eshop_brasil"]
    clientes = db["clientes"]
    pedidos = db["pedidos"]

except (ConnectionFailure, ServerSelectionTimeoutError):
    st.error("Não foi possível conectar ao MongoDB.")
    st.stop()

# CABEÇALHO
st.title("🛒 E-Shop Brasil")
st.subheader("Sistema de Gestão de Dados")
st.write(
    "Sistema de gerenciamento de clientes, pedidos e vendas."
)
st.success("Conectado ao MongoDB com sucesso!")

# CONSULTA DOS DADOS
lista_clientes = list(clientes.find().sort("nome", 1))
lista_pedidos = list(pedidos.find().sort("data", -1))

total_clientes = clientes.count_documents({})
total_pedidos = pedidos.count_documents({})

vendas_totais = sum(
    float(p.get("valor_total", 0))
    for p in lista_pedidos
)

# INDICADORES
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Clientes cadastrados", total_clientes)

with col2:
    st.metric("Pedidos registrados", total_pedidos)

with col3:
    st.metric(
        "Vendas totais",
        f"R$ {vendas_totais:,.2f}"
    )

st.divider()

# ABAS
aba_inicio, aba_clientes, aba_pedidos, aba_consultas = st.tabs(
    ["Visão geral", "Gerenciar clientes", "Gerenciar pedidos", "Consultas e análises"]
)

# ABA VISÃO GERAL
with aba_inicio:
    st.subheader("Visão geral da loja")

    st.write(
        "Os indicadores são atualizados diretamente "
        "com os dados armazenados no MongoDB."
    )

    if lista_pedidos:
        dados_grafico = pd.DataFrame([
            {
                "Pedido": str(p["_id"]),
                "Valor": float(p.get("valor_total", 0))
            }
            for p in lista_pedidos
        ])

        st.subheader("Valores dos pedidos")

        grafico = px.bar(
            dados_grafico,
            x="Pedido",
            y="Valor",
            title="Valor total por pedido"
        )

        st.plotly_chart(grafico, use_container_width=True)
    else:
        st.info("Ainda não existem pedidos para exibir.")

# ABA GERENCIAR CLIENTES
with aba_clientes:
    st.subheader("Cadastro de clientes")

    # IMPORTAÇÃO DE CLIENTES POR CSV
    st.divider()
    st.subheader("Importar clientes por CSV")

    st.write(
        "Envie um arquivo CSV com as colunas: "
        "nome, email e cidade."
    )

    arquivo_csv = st.file_uploader(
        "Selecione o arquivo CSV",
        type=["csv"],
        key="importar_clientes"
    )

    if arquivo_csv is not None:
        try:
            dados_csv = pd.read_csv(
                arquivo_csv,
                encoding="utf-8-sig"
            )

            dados_csv.columns = (
                dados_csv.columns.str.strip().str.lower()
            )

            colunas_obrigatorias = ["nome", "email", "cidade"]

            if not all(
                coluna in dados_csv.columns
                for coluna in colunas_obrigatorias
            ):
                st.error(
                    "O CSV precisa conter as colunas: "
                    "nome, email e cidade."
                )

            else:
                dados_csv = dados_csv[colunas_obrigatorias].copy()
                dados_csv = dados_csv.fillna("")

                for coluna in colunas_obrigatorias:
                    dados_csv[coluna] = (
                        dados_csv[coluna].astype(str).str.strip()
                    )

                dados_csv["email"] = (
                    dados_csv["email"].str.lower()
                )

                st.write("Prévia dos clientes encontrados:")
                st.dataframe(
                    dados_csv,
                    use_container_width=True
                )

                if st.button(
                    "Importar clientes para o MongoDB",
                    key="botao_importar_csv"
                ):
                    novos_clientes = []
                    emails_arquivo = set()

                    # Buscar e-mails já cadastrados
                    emails_cadastrados = {
                        c.get("email", "").strip().lower()
                        for c in clientes.find({}, {"email": 1})
                        if c.get("email")
                    }

                    # Verificar cada linha do CSV
                    for _, linha in dados_csv.iterrows():
                        nome_csv = linha["nome"]
                        email_csv = linha["email"]
                        cidade_csv = linha["cidade"]

                        if not nome_csv or not email_csv or not cidade_csv:
                            continue

                        if email_csv in emails_cadastrados:
                            continue

                        if email_csv in emails_arquivo:
                            continue

                        novos_clientes.append({
                            "nome": nome_csv,
                            "email": email_csv,
                            "cidade": cidade_csv
                        })

                        emails_arquivo.add(email_csv)

                    if novos_clientes:
                        clientes.insert_many(novos_clientes)

                        st.success(
                            f"{len(novos_clientes)} cliente(s) "
                            "importado(s) com sucesso!"
                        )

                        st.rerun()

                    else:
                        st.warning(
                            "Nenhum cliente novo para importar. "
                            "Verifique se os dados estão preenchidos "
                            "e se os e-mails já estão cadastrados."
                        )

        except Exception as erro:
            st.error(f"Erro ao importar o CSV: {erro}")

    # CADASTRO MANUAL
    st.divider()

    with st.form("form_cadastro_cliente"):
        nome = st.text_input("Nome do cliente")
        email = st.text_input("E-mail")
        cidade = st.text_input("Cidade")

        cadastrar = st.form_submit_button("Cadastrar cliente")

        if cadastrar:
            if nome.strip() and email.strip() and cidade.strip():
                email = email.strip().lower()

                if clientes.find_one({"email": email}):
                    st.warning("Este e-mail já está cadastrado.")
                else:
                    clientes.insert_one({
                        "nome": nome.strip(),
                        "email": email,
                        "cidade": cidade.strip()
                    })

                    st.success("Cliente cadastrado com sucesso!")
                    st.rerun()
            else:
                st.warning("Preencha todos os campos.")

    st.divider()
    st.subheader("Clientes cadastrados")

    lista_clientes = list(clientes.find().sort("nome", 1))

    if lista_clientes:
        dados_clientes = [
            {
                "Nome": c.get("nome", ""),
                "E-mail": c.get("email", ""),
                "Cidade": c.get("cidade", "")
            }
            for c in lista_clientes
        ]

        st.dataframe(
            dados_clientes,
            use_container_width=True
        )

        st.divider()
        st.subheader("Editar ou excluir cliente")

        opcoes_clientes = {
            f"{c.get('nome', '')} - {c.get('email', '')}": c
            for c in lista_clientes
        }

        selecionado = st.selectbox(
            "Selecione um cliente",
            list(opcoes_clientes.keys())
        )

        cliente_atual = opcoes_clientes[selecionado]
        cliente_id = cliente_atual["_id"]

        with st.form("form_edicao_cliente"):
            novo_nome = st.text_input(
                "Nome",
                value=cliente_atual.get("nome", "")
            )

            novo_email = st.text_input(
                "E-mail",
                value=cliente_atual.get("email", "")
            )

            nova_cidade = st.text_input(
                "Cidade",
                value=cliente_atual.get("cidade", "")
            )

            salvar = st.form_submit_button("Salvar alterações")

            if salvar:
                if novo_nome.strip() and novo_email.strip() and nova_cidade.strip():
                    novo_email = novo_email.strip().lower()

                    email_existente = clientes.find_one({
                        "email": novo_email,
                        "_id": {"$ne": cliente_id}
                    })

                    if email_existente:
                        st.warning("Este e-mail já pertence a outro cliente.")
                    else:
                        clientes.update_one(
                            {"_id": cliente_id},
                            {"$set": {
                                "nome": novo_nome.strip(),
                                "email": novo_email,
                                "cidade": nova_cidade.strip()
                            }}
                        )

                        st.success("Cliente atualizado!")
                        st.rerun()
                else:
                    st.warning("Preencha todos os campos.")

        if st.button("Excluir cliente selecionado"):
            pedidos.delete_many({"cliente_id": cliente_id})
            clientes.delete_one({"_id": cliente_id})

            st.success("Cliente excluído!")
            st.rerun()

    else:
        st.info("Ainda não existem clientes cadastrados.")

# ABA GERENCIAR PEDIDOS
with aba_pedidos:
    st.subheader("Cadastro de pedidos")

    lista_clientes = list(clientes.find().sort("nome", 1))

    if lista_clientes:
        opcoes = {
            f"{c.get('nome', '')} - {c.get('email', '')}": c
            for c in lista_clientes
        }

        with st.form("form_cadastro_pedido"):
            cliente_escolhido = st.selectbox(
                "Selecione o cliente",
                list(opcoes.keys())
            )

            produto = st.text_input("Nome do produto")

            quantidade = st.number_input(
                "Quantidade",
                min_value=1,
                value=1,
                step=1
            )

            valor_unitario = st.number_input(
                "Valor unitário (R$)",
                min_value=0.01,
                value=10.00,
                step=1.00
            )

            cadastrar_pedido = st.form_submit_button(
                "Registrar pedido"
            )

            if cadastrar_pedido:
                if produto.strip():
                    cliente_escolhido_dados = opcoes[cliente_escolhido]

                    valor_total = quantidade * valor_unitario

                    pedidos.insert_one({
                        "cliente_id": cliente_escolhido_dados["_id"],
                        "cliente_nome": cliente_escolhido_dados.get("nome", ""),
                        "produto": produto.strip(),
                        "quantidade": quantidade,
                        "valor_unitario": valor_unitario,
                        "valor_total": valor_total,
                        "data": datetime.now()
                    })

                    st.success("Pedido registrado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Informe o nome do produto.")

    else:
        st.warning(
            "Cadastre pelo menos um cliente antes de registrar pedidos."
        )

    st.divider()
    st.subheader("Pedidos registrados")

    lista_pedidos = list(pedidos.find().sort("data", -1))

    if lista_pedidos:
        dados_pedidos = []

        for p in lista_pedidos:
            data_pedido = p.get("data")

            dados_pedidos.append({
                "Cliente": p.get("cliente_nome", ""),
                "Produto": p.get("produto", ""),
                "Quantidade": p.get("quantidade", 0),
                "Valor unitário": f"R$ {p.get('valor_unitario', 0):.2f}",
                "Valor total": f"R$ {p.get('valor_total', 0):.2f}",
                "Data": (
                    data_pedido.strftime("%d/%m/%Y %H:%M")
                    if isinstance(data_pedido, datetime)
                    else ""
                )
            })

        st.dataframe(
            dados_pedidos,
            use_container_width=True
        )

        st.divider()
        st.subheader("Excluir pedido")

        opcoes_pedidos = {
            f"{p.get('cliente_nome', '')} - "
            f"{p.get('produto', '')} - "
            f"R$ {p.get('valor_total', 0):.2f}": p
            for p in lista_pedidos
        }

        pedido_selecionado = st.selectbox(
            "Selecione um pedido",
            list(opcoes_pedidos.keys())
        )

        if st.button("Excluir pedido selecionado"):
            pedido_atual = opcoes_pedidos[pedido_selecionado]

            pedidos.delete_one({
                "_id": pedido_atual["_id"]
            })

            st.success("Pedido excluído!")
            st.rerun()

    else:
        st.info("Ainda não existem pedidos cadastrados.")

# ABA CONSULTAS E ANÁLISES
with aba_consultas:
    st.subheader("Consultas e filtros de pedidos")

    st.write(
        "Pesquise pedidos usando filtros e consulte "
        "informações combinadas de clientes e pedidos."
    )

    # FILTROS
    col1, col2 = st.columns(2)

    with col1:
        filtro_cliente = st.text_input(
            "Pesquisar cliente"
        )

        filtro_produto = st.text_input(
            "Pesquisar produto"
        )

    with col2:
        valor_minimo = st.number_input(
            "Valor mínimo do pedido (R$)",
            min_value=0.0,
            value=0.0,
            step=50.0
        )

        data_inicio = st.date_input(
            "Data inicial",
            value=None
        )

        data_fim = st.date_input(
            "Data final",
            value=None
        )

    if st.button("Pesquisar pedidos"):
        filtro = {}

        if filtro_cliente.strip():
            filtro["cliente_nome"] = {
                "$regex": filtro_cliente.strip(),
                "$options": "i"
            }

        if filtro_produto.strip():
            filtro["produto"] = {
                "$regex": filtro_produto.strip(),
                "$options": "i"
            }

        if valor_minimo > 0:
            filtro["valor_total"] = {
                "$gte": valor_minimo
            }

        if data_inicio and data_fim:
            if data_inicio > data_fim:
                st.error("A data inicial não pode ser posterior à final.")
                st.stop()

            filtro["data"] = {
                "$gte": datetime.combine(
                    data_inicio, datetime.min.time()
                ),
                "$lt": datetime.combine(
                    data_fim + pd.Timedelta(days=1),
                    datetime.min.time()
                )
            }

        elif data_inicio:
            filtro["data"] = {
                "$gte": datetime.combine(
                    data_inicio, datetime.min.time()
                )
            }

        elif data_fim:
            filtro["data"] = {
                "$lt": datetime.combine(
                    data_fim + pd.Timedelta(days=1),
                    datetime.min.time()
                )
            }

        resultados = list(
            pedidos.find(filtro).sort("data", -1)
        )

        st.subheader("Resultados da pesquisa")

        if resultados:
            dados = [
                {
                    "Cliente": p.get("cliente_nome", ""),
                    "Produto": p.get("produto", ""),
                    "Quantidade": p.get("quantidade", 0),
                    "Valor total": f"R$ {p.get('valor_total', 0):.2f}"
                }
                for p in resultados
            ]

            st.dataframe(dados, use_container_width=True)

            soma = sum(
                float(p.get("valor_total", 0))
                for p in resultados
            )

            st.metric("Pedidos encontrados", len(resultados))
            st.metric("Valor total encontrado", f"R$ {soma:,.2f}")

        else:
            st.info("Nenhum pedido encontrado com esses filtros.")

    st.divider()

    # COMBINAÇÃO DE CLIENTES E PEDIDOS COM LOOKUP
    st.subheader("Clientes e seus pedidos")
    st.write(
        "Esta consulta utiliza o recurso $lookup do MongoDB "
        "para combinar documentos de duas coleções."
    )

    resultado_combinado = list(
        pedidos.aggregate([
            {
                "$lookup": {
                    "from": "clientes",
                    "localField": "cliente_id",
                    "foreignField": "_id",
                    "as": "dados_cliente"
                }
            },
            {
                "$unwind": {
                    "path": "$dados_cliente",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "cliente": {
                        "$ifNull": [
                            "$dados_cliente.nome",
                            "$cliente_nome"
                        ]
                    },
                    "email": {
                        "$ifNull": [
                            "$dados_cliente.email",
                            "Não disponível"
                        ]
                    },
                    "cidade": {
                        "$ifNull": [
                            "$dados_cliente.cidade",
                            "Não disponível"
                        ]
                    },
                    "produto": 1,
                    "quantidade": 1,
                    "valor_total": 1
                }
            }
        ])
    )

    if resultado_combinado:
        dados_combinados = [
            {
                "Cliente": p.get("cliente", ""),
                "E-mail": p.get("email", ""),
                "Cidade": p.get("cidade", ""),
                "Produto": p.get("produto", ""),
                "Quantidade": p.get("quantidade", 0),
                "Valor total": f"R$ {p.get('valor_total', 0):.2f}"
            }
            for p in resultado_combinado
        ]

        st.dataframe(
            dados_combinados,
            use_container_width=True
        )

    else:
        st.info(
            "Ainda não existem pedidos para combinar com os clientes."
        )

    st.divider()

    # CLIENTES QUE MAIS COMPRARAM
    st.subheader("Ranking de clientes por compras")

    ranking = list(
        pedidos.aggregate([
            {
                "$group": {
                    "_id": "$cliente_nome",
                    "total_pedidos": {"$sum": 1},
                    "total_gasto": {"$sum": "$valor_total"}
                }
            },
            {
                "$sort": {
                    "total_gasto": -1
                }
            }
        ])
    )

    if ranking:
        dados_ranking = [
            {
                "Cliente": r["_id"],
                "Quantidade de pedidos": r["total_pedidos"],
                "Total gasto": f"R$ {r['total_gasto']:,.2f}"
            }
            for r in ranking
        ]

        st.dataframe(
            dados_ranking,
            use_container_width=True
        )

    else:
        st.info("Ainda não existem compras para gerar um ranking.")
