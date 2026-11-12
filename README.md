# E-Shop Brasil — Sistema de Gestão de Dados

## 1. Introdução

O E-Shop Brasil é um projeto acadêmico desenvolvido para simular o gerenciamento de dados de uma loja virtual utilizando tecnologias de banco de dados NoSQL e visualização de dados.

O projeto representa uma loja com grande volume de clientes e pedidos, demonstrando operações de armazenamento, consulta, atualização, exclusão e análise de informações.

## 2. Objetivo

Desenvolver uma aplicação funcional capaz de gerenciar clientes e pedidos, utilizando MongoDB como banco de dados não relacional e Streamlit como interface gráfica.

## 3. Tecnologias utilizadas

- **Python 3.12:** linguagem de programação.
- **MongoDB:** banco de dados NoSQL.
- **Streamlit:** criação da interface web.
- **Pandas:** manipulação e importação de dados CSV.
- **Plotly:** criação de gráficos e visualizações.
- **PyMongo:** conexão entre Python e MongoDB.

## 4. Funcionalidades

O sistema possui quatro áreas principais:

### Visão geral
- Quantidade de clientes cadastrados.
- Quantidade de pedidos registrados.
- Valor total das vendas.
- Gráfico de valores dos pedidos.

### Gerenciar clientes
- Cadastro de clientes.
- Listagem de clientes.
- Edição de informações.
- Exclusão de clientes.
- Importação de clientes por arquivo CSV.
- Verificação de e-mails duplicados.

### Gerenciar pedidos
- Registro de pedidos.
- Associação de pedidos aos clientes.
- Cálculo automático do valor total.
- Listagem e exclusão de pedidos.

### Consultas e análises
- Pesquisa por cliente.
- Pesquisa por produto.
- Filtro por valor mínimo.
- Filtro por período.
- Combinação de dados com `$lookup`.
- Ranking de clientes por compras.

## 5. Estrutura do banco de dados

O banco utilizado é `eshop_brasil`, composto por duas coleções:

- `clientes`: armazena nome, e-mail e cidade.
- `pedidos`: armazena cliente, produto, quantidade, valores e data.

A aplicação utiliza o recurso de agregação `$lookup` para combinar informações das duas coleções.

## 6. Como executar o projeto

### Pré-requisitos

- Python instalado.
- MongoDB Community Server instalado e em execução.
- Visual Studio Code (ou outro editor de código).

### Instalação das dependências

No terminal, dentro da pasta do projeto, execute:

```bash
pip install streamlit pymongo pandas plotly
```

### Executar a aplicação

Com o serviço do MongoDB em execução, utilize:

```bash
python -m streamlit run app.py
```

O Streamlit disponibilizará um endereço local para abrir a aplicação no navegador.

## 7. Testes realizados

Foram realizados testes das principais funcionalidades:

- Conexão com o MongoDB.
- Cadastro, edição e exclusão de clientes.
- Cadastro e exclusão de pedidos.
- Importação de clientes por CSV.
- Verificação de registros duplicados.
- Consultas e filtros.
- Combinação de dados com `$lookup`.
- Ranking de clientes.
- Exibição de indicadores e gráficos.

## 8. Considerações finais

O projeto demonstra, de forma prática, a utilização de tecnologias NoSQL para gerenciar informações de uma loja virtual.

A aplicação permite compreender operações de banco de dados, manipulação de dados em Python, consultas e visualização de informações, simulando funcionalidades importantes de um sistema de comércio eletrônico.