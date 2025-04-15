import pyodbc
import pandas as pd
from datetime import datetime
import os
import glob
import time
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Correções dos erros ortográficos
correcoes_meses = {
    'Fevreiro': 'Fevereiro',
    'Maiu': 'Maio',
    'Setembr': 'Setembro',
    'Novembr': 'Novembro',
    'Feverero': 'Fevereiro',
    'Janiero': 'Janeiro',
    'Outbro': 'Outubro',
    'Dezembo': 'Dezembro'
}

def conectar_banco():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost,1435;'
            'DATABASE=MacarraoDB;'
            'UID=sa;'
            'PWD=SenhaForte123!'
        )
        logging.info("✅ Conexão bem-sucedida!")
        return conn
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def tratar_dados(df):
    try:
        for col in ['Mes', 'Ano', 'Vendas']:
            if col not in df.columns:
                raise ValueError(f"Coluna essencial '{col}' não encontrada!")

        df = df.copy()

        df['Mes'] = df['Mes'].replace(correcoes_meses).str.capitalize()
        meses_validos = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                         'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        df['Mes'] = df['Mes'].apply(lambda x: x if x in meses_validos else None)
        if df['Mes'].isnull().any():
            logging.warning("Alguns valores de 'Mes' não são válidos. Verifique os dados de entrada.")
            df['Mes'] = df['Mes'].fillna('Janeiro')
        # Ordenar os meses corretamente
        df['Mes'] = pd.Categorical(df['Mes'], categories=meses_validos, ordered=True)

        # Tratar vendas: converter para numérico, substituir nulos por 0, e forçar valores não-negativos
        df['Vendas'] = pd.to_numeric(df['Vendas'], errors='coerce').fillna(0)
        df['Vendas'] = df['Vendas'].apply(lambda x: max(0, x)).astype(int)

        df['Publicidade'] = pd.to_numeric(df.get('Publicidade', 0), errors='coerce').fillna(0).astype(int)
        df['Publicidade'] = df['Publicidade'].apply(lambda x: 1 if x == 1 else 0)

        # Criar a coluna 'Data' 
        df['Data'] = pd.to_datetime(
            df['Ano'].astype(str) + '-' + (df['Mes'].cat.codes + 1).astype(str) + '-01',
            errors='coerce'
        )

        if df['Data'].isnull().any():
            logging.warning("⚠️ Alguns valores de data não puderam ser convertidos corretamente.")

        logging.info(f"📊 Linhas tratadas: {len(df)}")
        return df
    except Exception as e:
        logging.error(f"Erro no tratamento de dados: {e}")
        return None

def salvar_dados(df):
    try:
        os.makedirs("Data", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"Data/vendas_macarrao_tratadas_{timestamp}.csv"
        df.to_csv(output_path, index=False)
        logging.info(f"📁 Dados salvos em: {output_path}")
    except Exception as e:
        logging.error(f"Erro ao salvar os dados: {e}")

def limpar_arquivos_antigos():
    try:
        for f in glob.glob("Data/vendas_macarrao_tratadas_*.csv"):
            if time.time() - os.path.getmtime(f) > 7 * 86400:
                os.remove(f)
                logging.info(f"🗑️ Arquivo removido: {f}")
    except Exception as e:
        logging.error(f"Erro ao remover arquivos antigos: {e}")

def main():
    logging.info("Iniciando o processo de tratamento...")
    conn = conectar_banco()
    if not conn:
        return

    try:
        df = pd.read_sql("SELECT * FROM VendasMacarrao", conn)
        conn.close()
        logging.info(f"Arquivo lido. Total de linhas lidas: {len(df)}")

        # Tratar os dados
        df_tratado = tratar_dados(df)
        if df_tratado is None:
            logging.error("❌ Tratamento de dados falhou. Processo interrompido.")
            return

        salvar_dados(df_tratado)
        limpar_arquivos_antigos()

    except Exception as e:
        logging.error(f"Erro inesperado no processo principal: {e}")

if __name__ == "__main__":
    main()
