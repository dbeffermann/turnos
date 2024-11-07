import pandas as pd
import streamlit as st
from datetime import datetime

def obtener_datos(sheet_id, gid):
    return pd.read_csv(f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}')

def convertir_dias_semana(serie, esp_to_eng=True):
    if esp_to_eng:
        return serie.str.replace('Lunes', 'Monday')\
                            .str.replace('Martes', 'Tuesday')\
                            .str.replace('Miércoles', 'Wednesday')\
                            .str.replace('Jueves', 'Thursday')\
                            .str.replace('Viernes', 'Friday')\
                            .str.replace('Sábado', 'Saturday')\
                            .str.replace('Domingo', 'Sunday')\
                            .str.replace('mediodía', 'Mañana')\
                            .str.replace('mañana', 'Mañana')\
                            .str.replace('tarde', 'Tarde')
                            
    else:
        return serie.str.replace('Monday', 'Lunes')\
                            .str.replace('Tuesday', 'Martes')\
                            .str.replace('Wednesday', 'Miércoles')\
                            .str.replace('Thursday', 'Jueves')\
                            .str.replace('Friday', 'Viernes')\
                            .str.replace('Saturday', 'Sábado')\
                            .str.replace('Sunday', 'Domingo')\
                            .str.replace('mediodía', 'Mañana')\
                            .str.replace('mañana', 'Mañana')\
                            .str.replace('tarde', 'Tarde')
                            

conversion_dias = {
 'Lunes': 'Monday',
 'Martes': 'Tuesday',
 'Miércoles': 'Wednesday',
 'Jueves': 'Thursday',
 'Viernes': 'Friday',
 'Sábado': 'Saturday',
 'Domingo': 'Sunday'
}



# Función genérica para cargar un DataFrame
@st.cache_data
def load_dataframe(csv_file, default_data):
    try:
        return pd.read_csv(csv_file)
    except FileNotFoundError:
        # Si el archivo no existe, retorna un DataFrame con datos de ejemplo
        return pd.DataFrame(default_data)

# Función genérica para guardar cambios en un DataFrame
def save_dataframe(df, csv_file):
    df.to_csv(csv_file, index=False)

# Función genérica para el editor de DataFrames
def dataframe_editor(csv_file, title, df):
    st.title(f"Editor de {title}")

    # Editor interactivo para el DataFrame
    df_editado = st.data_editor(df, num_rows="dynamic")

    # Guardar cambios con marca de tiempo
    if st.button(f"Guardar Cambios en {title}"):
        df_editado["Modificación"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_dataframe(df_editado, csv_file)
        st.success(f"Cambios en {title} guardados correctamente.")

