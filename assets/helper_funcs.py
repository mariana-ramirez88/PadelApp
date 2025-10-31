import streamlit as st
import itertools,random
import pandas as pd
from typing import List, Dict, Tuple

#Streamlit Functions
def initialize_vars(defaults:dict):
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
            print(f"{key} no estaba en session state. asignando valor: {value}")
        else:
            pass

#Tournament Logic Functions
def generar_fixture(parejas, num_canchas):
    """Genera las rondas con máximo num_canchas partidos por ronda.Parejas fijas previamente establecidas"""
    enfrentamientos = list(itertools.combinations(parejas, 2))
    random.shuffle(enfrentamientos)
    rondas = []
    pendientes = enfrentamientos.copy()

    while pendientes:
        ronda = []
        disponibles = set(parejas)
        for _ in range(num_canchas):
            for match in pendientes:
                p1, p2 = match
                if p1 in disponibles and p2 in disponibles:
                    ronda.append(match)
                    disponibles.remove(p1)
                    disponibles.remove(p2)
                    pendientes.remove(match)
                    break
        rondas.append(ronda)
    return rondas

def calcular_ranking(parejas:List[str], resultados:Dict[Tuple[str,str], Tuple[int,int]]) ->pd.DataFrame:
    """Calcula el ranking acumulado según los resultados ingresados."""
    puntajes = {p: 0 for p in parejas}
    for (p1, p2), (r1, r2) in resultados.items():
        puntajes[p1] += r1
        puntajes[p2] += r2
    ranking = pd.DataFrame(sorted(puntajes.items(), key=lambda x: x[1], reverse=True),
                           columns=["Pareja", "Puntos"])
    return ranking