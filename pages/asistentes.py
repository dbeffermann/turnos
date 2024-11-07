import streamlit as st
from funciones import dataframe_editor, obtener_datos
import configparser
import pandas as pd

# Configuración de la página
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

config = configparser.ConfigParser()
config.read('config.ini')

sheet_id = config['google_sheet']['sheet_id']
gid_asistentes = config['google_sheet']['gid_asistentes']
#df_asistentes = obtener_datos(sheet_id, gid_asistentes).replace('Si', True).replace('No', False)

df_asistentes = pd.read_csv("df_asistentes.csv")#pd.read_excel(archivo, sheet_name=asistentes_sheet)
df_asistentes['Atiende Ventanilla'] = df_asistentes['Atiende Ventanilla'].replace('Si', True).replace('No', False)

# Llamada a la función genérica
dataframe_editor("df_asistentes.csv", "Asistentes", df_asistentes)
