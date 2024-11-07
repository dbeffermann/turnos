import pandas as pd
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpBinary, PULP_CBC_CMD
from datetime import datetime
import numpy as np
import re

def ejecutar_modelo(df_doctores, df_asistentes, df_ausencias, dias_mes = range(1, 2)):
    # Definición de conjuntos
    doctores = df_doctores["Nombre"].tolist()
    asistentes = df_asistentes["Nombre"].tolist()
    asistentes_ventanilla = df_asistentes[df_asistentes["Atiende Ventanilla"] == True]["Nombre"].tolist()
    turnos = ["Mañana", "Tarde"]

    # Grupos de doctores
    doctores_con_asistente = df_doctores[df_doctores["Necesita Asistente"] == True]["Nombre"].tolist()
    doctores_sin_asistente = df_doctores[df_doctores["Necesita Asistente"] == False]["Nombre"].tolist()

    # Disponibilidad de doctores y asistentes por días de la semana y fechas específicas

    # Expresión regular para extraer los turnos de los doctores y asistentes
    regex = r'(\w+)\s*\(([^)]+)\)'

    disponibilidad_doctores = {
        row['Nombre']: {day: turns.split(", ") for day, turns in re.findall(regex, row['Disponibilidad'])}
        for index, row in df_doctores.iterrows()
    }

    disponibilidad_asistentes = {
        row['Nombre']: {day: turns.split(", ") for day, turns in re.findall(regex, row['Disponibilidad'])}
        for index, row in df_asistentes.iterrows()
    }

    df_ausencias = df_ausencias[df_ausencias["Fecha"].isin(dias_mes)] # Corrije bug
    ausencias_doctores = {d: df_ausencias[(df_ausencias["Nombre"] == d) & (df_ausencias["Tipo"] == "Doctor")]["Fecha"].tolist() for d in doctores}
    ausencias_asistentes = {a: df_ausencias[(df_ausencias["Nombre"] == a) & (df_ausencias["Tipo"] == "Asistente")]["Fecha"].tolist() for a in asistentes}

    # Días de la semana para cada día de octubre
    dias_semana = {int(dia.day): dia.strftime("%A") for dia in dias_mes}

    # Definición del problema
    model = LpProblem("Asignacion_Doctores_Asistentes", LpMaximize)


    # Variables de decisión
    x = LpVariable.dicts("Asignacion", (doctores + ["ventanilla"], asistentes, dias_mes, turnos), cat=LpBinary)

    # Función objetivo (maximizar la asignación de asistentes)
    model += lpSum(x[d][a][dia][t] for d in doctores + ["ventanilla"] for a in asistentes for dia in dias_mes for t in turnos)

    # Restricción 1: Máximo un doctor por oficina, día y turno
    for d in doctores:
        for dia in dias_mes:
            for t in turnos:
                model += lpSum(x[d][a][dia][t] for a in asistentes) <= 1

    # Restricción 2: Máximo un asistente por oficina, día y turno
    for d in doctores:
        for dia in dias_mes:
            for t in turnos:
                model += lpSum(x[d][a][dia][t] for a in asistentes) <= 1

    # Restricción 3: Mínimo un asistente en ventanilla, día y turno
    for dia in dias_mes:
        for t in turnos:
            model += lpSum(x["ventanilla"][a][dia][t] for a in asistentes_ventanilla) >= 1

    # Restricción 4: Máximo dos asistentes en ventanilla, día y turno
    for dia in dias_mes:
        for t in turnos:
            model += lpSum(x["ventanilla"][a][dia][t] for a in asistentes_ventanilla) <= 2

    # Restriccion 5: Los asistentes que no hacen ventanilla no pueden hacerlo
    for a in asistentes:
        for dia in dias_mes:
            for t in turnos:
                if a not in asistentes_ventanilla:
                    model += x["ventanilla"][a][dia][t] == 0

    # Restricción 6: Los doctores que no necesitan asistente solo pueden tener al asistente comodín
    for d in doctores_sin_asistente:
        for dia in dias_mes:
            for t in turnos:
                # Solo se permite la asignación de los asistentes comodín
                model += lpSum(x[d][a][dia][t] for a in asistentes) in [x[d]['-'][dia][t] , x[d]['--'][dia][t] , x[d]['---'][dia][t]]
                

    # Restriccion 7: Los doctores que necesitan asistente no pueden tener al asistente comodín
    for d in doctores_con_asistente:
        for dia in dias_mes:
            for t in turnos:
                # No permite la asignación del asistente comodín a ese doctor
                model += x[d]['-'][dia][t] == 0
                model += x[d]['--'][dia][t] == 0
                model += x[d]['---'][dia][t] == 0

    # Restricción 8: No se trabaja sábados ni domingos
    for dia in dias_mes:
        if dias_semana[int(dia.day)] in ["Saturday", "Sunday"]:
            for d in doctores:
                for t in turnos:
                    model += lpSum(x[d][a][dia][t] for a in asistentes) == 0

    # Restricción 9: Disponibilidad semanal de doctores
    for d in doctores:
        for dia in dias_mes:
            dia_semana = dias_semana[int(dia.day)]
            for t in turnos:
                #print(d,t, dia, disponibilidad_doctores[d].get(dia_semana, []), t not in disponibilidad_doctores[d].get(dia_semana, []))
                if t not in disponibilidad_doctores[d].get(dia_semana, []):
                    model += lpSum(x[d][a][dia][t] for a in asistentes) == 0

    # Restricción 10: Disponibilidad semanal de asistentes
    for a in asistentes:
        for dia in dias_mes:
            dia_semana = dias_semana[int(dia.day)]
            for t in turnos:
                if t not in disponibilidad_asistentes[a].get(dia_semana, []):
                    model += lpSum(x[d][a][dia][t] for d in doctores + ["ventanilla"]) == 0

    # Restricción 11: Ausencias específicas de doctores
    for d in doctores:
        for fecha in ausencias_doctores[d]:
            dia = fecha
            for t in turnos:
                model += lpSum(x[d][a][dia][t] for a in asistentes) == 0

    # Restricción 12: Ausencias específicas de asistentes
    for a in asistentes:
        for fecha in ausencias_asistentes[a]:
            dia = int(fecha.split("-")[2])
            for t in turnos:
                model += lpSum(x[d][a][dia][t] for d in doctores + ["ventanilla"]) == 0

    # Restricción 13: Exclusividad para asistentes
    for a in asistentes:
        for dia in dias_mes:
            for t in turnos:
                # Asegurarse de que no esté asignado a un doctor y a la ventanilla al mismo tiempo
                model += lpSum(x[d][a][dia][t] for d in doctores) + x["ventanilla"][a][dia][t] <= 1, f"Exclusividad_Asistente_{a}_dia_{dia}_turno_{t}"

    # Resolver el modelo estricto
    model.solve(PULP_CBC_CMD(msg=1, options=['--no-relax']))

    variables = pd.DataFrame({
    'Variable': [variable.name for variable in model.variables()],
    'Valor': [variable.varValue for variable in model.variables()]
        })
    
    valor_objetivo = model.objective.value()

    # Procesar resultados
    resultados = []
    for d in doctores + ["ventanilla"]:
        for a in asistentes:
            for dia in dias_mes:
                for t in turnos:
                    if x[d][a][dia][t].value() == 1:
                        resultados.append({
                            "Doctor/Asistente": d if d != "ventanilla" else "Asistente en Ventanilla",
                            "Asistente": a,
                            "Día": dia,
                            "Día de la semana": dia,
                            "Turno": t
                        })

    # Convertir a DataFrame y retornar
    df_resultados = pd.DataFrame(resultados)
    #print('resultados',df_resultados)
    return df_resultados, variables, valor_objetivo
