import pandas as pd


def main(archivo, modelo, doctores_sheet, asistentes_sheet, ausencias_sheet, dias_mes= range(1, 2)):

    # Leer archivos
    df_doctores = pd.read_csv("df_doctores.csv")#pd.read_excel(archivo, sheet_name=doctores_sheet)
    df_asistentes = pd.read_csv("df_asistentes.csv")#pd.read_excel(archivo, sheet_name=asistentes_sheet)
    df_ausencias = pd.read_csv("df_ausencias.csv")#pd.read_excel(archivo, sheet_name=ausencias_sheet)

    df_ausencias['Fecha'] = pd.to_datetime(df_ausencias['Fecha'])
    df_doctores['Necesita Asistente'] = df_doctores['Necesita Asistente'].replace('Si', True).replace('No', False)
    df_doctores['Atiende Ventanilla'] = df_doctores['Atiende Ventanilla'].replace('Si', True).replace('No', False)
    df_asistentes['Atiende Ventanilla'] = df_asistentes['Atiende Ventanilla'].replace('Si', True).replace('No', False)

    # Procesar doctores
    df_doctores['Disponibilidad'] = df_doctores['Disponibilidad'].str.replace('Lunes', 'Monday')\
                                                                .str.replace('Martes', 'Tuesday')\
                                                                .str.replace('Miércoles', 'Wednesday')\
                                                                .str.replace('Jueves', 'Thursday')\
                                                                .str.replace('Viernes', 'Friday')\
                                                                .str.replace('Sábado', 'Saturday')\
                                                                .str.replace('Domingo', 'Sunday')\
                                                                .str.replace('mediodía', 'mañana')\
                                                                .str.replace('mañana', 'Mañana')\
                                                                .str.replace('tarde', 'Tarde')
    
    
    # Procesar asistentes
    df_asistentes['Disponibilidad'] = df_asistentes['Disponibilidad'].str.replace('Lunes', 'Monday')\
                                                                .str.replace('Martes', 'Tuesday')\
                                                                .str.replace('Miércoles', 'Wednesday')\
                                                                .str.replace('Jueves', 'Thursday')\
                                                                .str.replace('Viernes', 'Friday')\
                                                                .str.replace('Sábado', 'Saturday')\
                                                                .str.replace('Domingo', 'Sunday')\
                                                                .str.replace('mediodía', 'mañana')\
                                                                .str.replace('mañana', 'Mañana')\
                                                                .str.replace('tarde', 'Tarde')
    # Ejecutar el modelo
    resultado, variables, valor_objetivo = modelo(df_doctores, df_asistentes, df_ausencias, dias_mes)

    return resultado, df_doctores, df_asistentes, df_ausencias, variables, valor_objetivo
