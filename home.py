import streamlit as st
import pandas as pd
from main import main
import numpy as np
from modelo6 import ejecutar_modelo as modelo_6

# Configuración de la página
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Leer archivos
archivo = "Archivo.xlsx"  # Nombre del archivo Excel

# st.sidebar.slider para el rango
rango = st.sidebar.date_input('Rango de fechas', [pd.to_datetime('2024-10-01'), pd.to_datetime('2024-10-01')])

rango = [i for i in pd.date_range(rango[0], rango[1], freq='D')]

# Ejecutar el Modelo
resultado, df_doctores, df_asistentes, df_ausencias, variables, valor_objetivo = main(archivo, 
                                                                                        modelo=modelo_6, 
                                                                                        doctores_sheet="Doctores", 
                                                                                        asistentes_sheet="Asistentes", 
                                                                                        ausencias_sheet="Ausencias",
                                                                                        dias_mes=rango)  
print(resultado.head)
# Configurar la vista
vista = resultado.merge(df_doctores, 
                        how='left', 
                        left_on = 'Doctor/Asistente', 
                        right_on = 'Nombre')\
                            .merge(df_asistentes, 
                            how='left', 
                            left_on = 'Asistente', 
                            right_on = 'Nombre', 
                            suffixes=['_Doctor', '_Asistente'])

# Nombres de los días de la semana de inglés a español
dias_semana = {
    "Monday": "Lunes", 
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}

# Convertir los nombres de los días en el DataFrame
vista['Día de la semana'] = vista['Día de la semana'].replace(dias_semana)

## Separar los dataframes en 1 por dia
dataframes_por_dia = {dia: datos for dia, datos in vista.groupby("Día")}

## Crear la aplicación en Streamlit
st.title("Asignaciones Semanales")
st.write("Esta vista muestra las asignaciones de doctores y asistentes por día y oficina.")

## Mostrar expanders de la semana actual
for dia, dataframe in dataframes_por_dia.items():
    
    with st.expander(f"{dias_semana[dia.strftime('%A')]}, {dia.strftime('%d de %B de %Y')}"):

        if dataframe.empty:
            st.write("No hay asignaciones para este día.")
        else:
            dataframe['dupla'] = np.where(dataframe['Doctor/Asistente'] == 'Asistente en Ventanilla', 
                                          dataframe['Nombre_Asistente'] + " (ventanilla)",
                                          dataframe['Nombre_Doctor'] + ' / ' + dataframe['Nombre_Asistente'])            
            
            z = pd.pivot_table(dataframe.fillna('-'), 
                               index=['Oficina', 'Doctor/Asistente'], 
                               columns = ['Turno'], 
                               values='dupla', 
                               aggfunc=lambda x: x, fill_value='').reset_index().drop(columns=['Doctor/Asistente'])
    
            # Mostar la tabla  
            col1, col2 = st.columns(2)    

            col1.write("Asignaciones del día")  
            col1.dataframe(z.astype(str), use_container_width=True)
            
            # Mostrar ausencias
            col2.write("Ausencias del día")
            ausencias_periodo = df_ausencias[df_ausencias['Fecha'].isin([dia])]
            ausencias_periodo['Fecha'] = ausencias_periodo['Fecha'].dt.strftime('%Y/%m/%d')

            col2.dataframe(ausencias_periodo.set_index('Fecha').loc[:, ['Nombre', 'Motivo']], use_container_width=True)

            # Mostrar los doctores disponibles este dia
            #doctores_disponibles = df_doctores[df_doctores['Disponibilidad'].apply(lambda x: dia.strftime('%A') in x)].loc[:, ['Nombre', 'Disponibilidad']]
            #asistentes_disponibles = df_asistentes[df_asistentes['Disponibilidad'].apply(lambda x: dia.strftime('%A') in x)].loc[:, ['Nombre', 'Disponibilidad']]
            #
            #st.dataframe(doctores_disponibles)
            #st.dataframe(asistentes_disponibles)
st.sidebar.write(f"Turnos máximos: {valor_objetivo}")




            

