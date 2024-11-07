import streamlit as st
from funciones import dataframe_editor, obtener_datos
import configparser
import pandas as pd

# Configuración de la página
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

config = configparser.ConfigParser()
config.read('config.ini')

sheet_id = config['google_sheet']['sheet_id']
gid_ausencias = config['google_sheet']['gid_ausencias']
#df_ausencias = obtener_datos(sheet_id, gid_ausencias).replace('Si', True).replace('No', False)

df_ausencias = pd.read_csv("df_ausencias.csv")#pd.read_excel(archivo, sheet_name=ausencias_sheet)
df_ausencias['Fecha'] = pd.to_datetime(df_ausencias['Fecha'])

# Llamada a la función genérica
dataframe_editor("df_ausencias.csv", "Ausencias", df_ausencias)
