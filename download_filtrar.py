import pandas as pd

# Dataset da Our World in Data
url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"

print("Baixando dados...")

# Lê somente as colunas que serão utilizadas
df = pd.read_csv(
    url,
    usecols=[
        "location",
        "date",
        "new_cases",
        "total_cases",
        "total_deaths",
        "people_vaccinated",
        "population"
    ]
)

print(f"Total de linhas do dataset original: {len(df):,}")

# Países escolhidos
paises = [
    "Brazil",
    "Argentina",
    "Chile",
    "United States",
    "Canada"
]

df = df[df["location"].isin(paises)]

# Converter data
df["date"] = pd.to_datetime(df["date"])

# Filtrar período
df = df[
    (df["date"] >= "2021-01-01") &
    (df["date"] <= "2023-12-31")
]

# Remover linhas totalmente vazias nas métricas principais
df = df.dropna(
    subset=[
        "new_cases",
        "total_cases",
        "total_deaths",
        "people_vaccinated"
    ],
    how="all"
)

# Salvar arquivo
arquivo = "dados/covid_filtrado.csv"

df.to_csv(arquivo, index=False)

print(f"Arquivo salvo em: {arquivo}")
print(f"Total de linhas após filtro: {len(df):,}")

print("\nPrimeiras linhas:")
print(df.head())