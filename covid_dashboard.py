# Bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px
import snowflake.connector

# Dashboard
st.set_page_config(
    page_title="Dashboard COVID-19",
    layout="wide"
)

st.title("🌍 Dashboard COVID-19")

st.markdown("""
Este dashboard apresenta indicadores públicos da COVID-19 para 5 países selecionados entre 01/01/2021 e 31/12/2023, utilizando dados da
**Our World in Data**, armazenados no **Snowflake** e visualizados com **Streamlit**.
""")

# Conexão com o Snowflake
conn = snowflake.connector.connect(
    account=st.secrets["snowflake"]["account"],
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"]
)

@st.cache_data
def carregar_dados():

    query = """
    SELECT *
    FROM COVID_DATA
    """

    df = pd.read_sql(query, conn)
    df["DATE"] = pd.to_datetime(df["DATE"])

    return df

df = carregar_dados()

# ---------------------------------------------------------
# Abas do Dashboard
aba_dashboard, aba_dados = st.tabs(
    ["📊 Dashboard", "📋 Dados Brutos"]
)

# ---------------------------------------------------------
# Aba 1
with aba_dashboard:

    st.header("📊 Indicadores") # Indicadores

    col1, col2, col3 = st.columns(3)

    total_casos = int(df["TOTAL_CASES"].max())
    total_mortes = int(df["TOTAL_DEATHS"].max())
    total_vacinados = int(df["PEOPLE_VACCINATED"].max())

    col1.metric("Total de casos", f"{total_casos:,}")
    col2.metric("Total de mortes", f"{total_mortes:,}")
    col3.metric("Pessoas vacinadas", f"{total_vacinados:,}")

    st.header("🌍 Filtros") # Filtro país

    pais = st.selectbox(
        "Selecione um país",
        sorted(df["LOCATION"].unique())
    )

    df_filtrado = df[df["LOCATION"] == pais]

    col1, col2 = st.columns(2) # Filtro período

    with col1:
        data_inicial = st.date_input(
            "Data inicial",
            df["DATE"].min()
        )

    with col2:
        data_final = st.date_input(
            "Data final",
            df["DATE"].max()
        )

    df_filtrado = df[
        (df["LOCATION"] == pais) &
        (df["DATE"] >= pd.to_datetime(data_inicial)) &
        (df["DATE"] <= pd.to_datetime(data_final))
    ]

    st.header("📈 Evolução dos novos casos") # Gráfico de linhas

    fig = px.line(
        df_filtrado,
        x="DATE",
        y="NEW_CASES",
        title=f"Novos casos - {pais}"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.header("📊 Total de óbitos por país") # Gráfico de barras

    obitos = (
        df.groupby("LOCATION")["TOTAL_DEATHS"]
        .max()
        .reset_index()
    )

    fig_bar = px.bar(
        obitos,
        x="LOCATION",
        y="TOTAL_DEATHS",
        color="LOCATION",
        title="Total de óbitos"
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    st.header("🥧 Proporção de pessoas vacinadas") # Gráfico de pizza

    vacinados = (
        df.groupby("LOCATION")["PEOPLE_VACCINATED"]
        .max()
        .reset_index()
    )

    fig_pizza = px.pie(
        vacinados,
        names="LOCATION",
        values="PEOPLE_VACCINATED",
        title="Proporção de vacinados"
    )

    st.plotly_chart(fig_pizza, use_container_width=True)

    col_esq, col_dir = st.columns(2)

    st.header("⚪ População × Total de casos") # Gráfico de dispersão

    dispersao = (
        df.groupby("LOCATION")[["POPULATION", "TOTAL_CASES"]]
        .max()
        .reset_index()
    )

    fig_scatter = px.scatter(
        dispersao,
        x="POPULATION",
        y="TOTAL_CASES",
        color="LOCATION",
        size="TOTAL_CASES",
        hover_name="LOCATION",
        title="População x Total de Casos"
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------------------------------------------------
# Aba 2
with aba_dados:

    st.header("📋 Dados brutos")

    st.dataframe(df_filtrado)

    csv = df_filtrado.to_csv(index=False).encode("utf-8") # Botão exportar CSV

    st.download_button(
        label="⬇️ Exportar CSV",
        data=csv,
        file_name="covid_filtrado.csv",
        mime="text/csv"
    )

# ---------------------------------------------------------
# Fechando a conexão
conn.close()