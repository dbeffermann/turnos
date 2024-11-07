import streamlit as st
from funciones import dataframe_editor, obtener_datos
import configparser
import pandas as pd

# Configuración de la página
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

config = configparser.ConfigParser()
config.read('config.ini')

sheet_id = config['google_sheet']['sheet_id']
gid_doctores = config['google_sheet']['gid_doctores']
df_doctores = obtener_datos(sheet_id, gid_doctores).replace('Si', True).replace('No', False)

df_doctores = pd.read_csv("df_doctores.csv")#pd.read_excel(archivo, sheet_name=doctores_sheet)
df_doctores['Necesita Asistente'] = df_doctores['Necesita Asistente'].replace('Si', True).replace('No', False)
df_doctores['Atiende Ventanilla'] = df_doctores['Atiende Ventanilla'].replace('Si', True).replace('No', False)

# Llamada a la función genérica
dataframe_editor("df_doctores.csv", "Doctores", df_doctores)
