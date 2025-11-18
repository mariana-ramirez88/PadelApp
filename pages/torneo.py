import streamlit as st
from assets.helper_funcs import generar_fixture_parejas, calcular_ranking_parejas,initialize_vars, calcular_ranking_individual
from models.AllvsAll_Random_modelv4 import generar_torneo_todos_contra_todos
from assets.analyze_funcs import analyze_algorithm_results
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import itertools
import numpy as np

def app():
    num_canchas = st.session_state.num_fields
    puntos_partido =st.session_state.num_pts
    to_init = {"code_play": "", "ranking":""}
    initialize_vars(to_init)
    
    #divission logica parejas fijas vs aleatorias
    mod_parejas = st.session_state.mod
    if mod_parejas == "Parejas Fijas":
        st.title("Torneo Americano - Parejas Fijas - Suma")
        parejas = st.session_state.players
        if st.button("Generar Fixture"):
            st.session_state.fixture = generar_fixture_parejas(parejas, num_canchas)
            st.session_state.code_play = "parejas_fijas"
            st.session_state.resultados = {}
            st.session_state.parejas = parejas

    elif mod_parejas == "Todos Contra Todos":
        st.title("Torneo Americano - Todos contra Todos - Suma")
        if st.button("Generar Fixture"):
            out = generar_torneo_todos_contra_todos(st.session_state.players, num_canchas, seed=42)
            st.session_state.code_play = "AllvsAll"
            st.session_state.fixture = out["rondas"]
            st.session_state.out = out
            st.session_state.resultados = {}

    # Visualización especial para Todos Contra Todos
    if st.session_state.code_play == "AllvsAll":
        st.markdown("""
            <style>
            .match-card {
                background: linear-gradient(145deg, #ffffff, #f0f0f5); /* leve degradado para volumen */
                border-radius: 18px;
                padding: 22px;
                margin-bottom: 25px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.15); /* sombra más profunda */
                border: 1px solid rgba(108, 19, 191, 0.1); /* borde tenue en tono principal */
                transition: transform 0.15s ease, box-shadow 0.15s ease; /* efecto al pasar el mouse */
            }
            .match-title {
                font-weight: 700;
                font-size: 18px;
                color: #0B0B19;
                margin-bottom: 10px;
            }
            .team-name {
                font-weight: 600;
                color: #0B0B19;
                font-size: 16px;
                text-align: center;
            }
            .vs {
                font-weight: 800;
                font-size: 20px;
                color: #6C13BF;
                text-align: center;
                margin-top: 8px;
                margin-bottom: 8px;
            }
            .stNumberInput input {
            background-color: #5E3187 !important;
            color: white !important;                 /* makes the number white */
            font-weight: 700 !important;             /* makes it bold */
            }
                    
            .stNumberInput button {
            color: white !important;           /* color de los signos + y - */
            }
            /* === BOTÓN === */
            .stButton button {
                width: 100%;
                background-color: #0B0B19;
                color: white;
                font-weight: 700;
                font-size: 18px;
                padding: 1em;
                border-radius: 10px;
                margin-top: 40px;
            }
            </style>
        """, unsafe_allow_html=True)

        for ronda_data in st.session_state.fixture:
            with st.expander(f"DEBUG Ronda {ronda_data['ronda']}"):
                st.write("Partidos:")
                st.write(ronda_data["partidos"])
                st.write("Descansan crudo:", ronda_data["descansan"])
                st.write("Descansan únicos:", list(set(ronda_data["descansan"])))

            st.subheader(f"Ronda {ronda_data['ronda']}")
            cols = st.columns(len(ronda_data["partidos"]))

            for c_i, partido in enumerate(ronda_data["partidos"]):
                pareja1 = " & ".join(partido["pareja1"])
                pareja2 = " & ".join(partido["pareja2"])
                ayudantes = partido.get("ayudantes", [])
                if ayudantes:
                    ayud_text = f"<div style='font-size:14px;color:#6C13BF;margin-top:5px;'>Ayudantes: {', '.join(ayudantes)}</div>"
                else:
                    ayud_text = ""
                cancha = partido["cancha"]

                with cols[c_i]:
                    st.markdown(f"""
                        <div class="match-card">
                            <div class="match-title">Cancha {cancha}</div>
                            <div class="team-name">{pareja1}</div>
                            <div class="vs">VS</div>
                            <div class="team-name">{pareja2}</div>
                            {ayud_text}
                        </div>
                    """, unsafe_allow_html=True)

                    colA, colB = st.columns(2)
                    with colA:
                        score1 = st.number_input(f"Puntos {pareja1}", key=f"{pareja1}_{pareja2}_p1", min_value=0)
                    with colB:
                        score2 = st.number_input(f"Puntos {pareja2}", key=f"{pareja1}_{pareja2}_p2", min_value=0)

                    st.session_state.resultados[(pareja1, pareja2)] = (score1, score2)

                # mostrar ayudantes o descansos
                if ayudantes:
                    st.caption(f"Ayudantes: {', '.join(ayudantes)}")
            if ronda_data["descansan"]:
                st.info(f"Descansan: {', '.join(ronda_data['descansan'])}")
                    # Mostrar resumen de partidos jugados y descansos
        if "out" in st.session_state and "resumen" in st.session_state.out:
            st.markdown("### Resumen de participación")
            st.dataframe(st.session_state.out["resumen"])
        # --- Sección de análisis del algoritmo ---
        st.markdown("## 🔍 Análisis de Resultados del Algoritmo")
        analyze_algorithm_results(st.session_state.fixture)
        
        # --- Ranking Final ---
        if "ranking" not in st.session_state:
            ranking = calcular_ranking_individual(st.session_state.resultados)
        if st.button("¿Cómo va el ranking? 👀"):
            ranking = calcular_ranking_individual(st.session_state.resultados)
            st.session_state.ranking = ranking
            st.dataframe(ranking)
            
            
    st.write(f"se jugara un torneo americano - {mod_parejas} - en {num_canchas} canchas a la suma de {puntos_partido} puntos")

    

    if st.session_state.code_play == "parejas_fijas" :
        st.markdown("""
            <style>
            .match-card {
                background-color: #f7f7fb;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 25px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.07);
            }
            .match-title {
                font-weight: 700;
                font-size: 18px;
                color: #0B0B19;
                margin-bottom: 10px;
            }
            .team-name {
                font-weight: 600;
                color: #0B0B19;
                font-size: 16px;
                text-align: center;
            }
            .vs {
                font-weight: 800;
                font-size: 20px;
                color: #6C13BF;
                text-align: center;
                margin-top: 8px;
                margin-bottom: 8px;
            }
            
            .stNumberInput input {
            background-color: #5E3187 !important;
            color: white !important;                 /* makes the number white */
            font-weight: 700 !important;             /* makes it bold */
            }
                    
            .stNumberInput button {
            color: white !important;           /* color de los signos + y - */
            }
            /* === BOTÓN === */
            .stButton button {
                width: 100%;
                background-color: #0B0B19;
                color: white;
                font-weight: 700;
                font-size: 18px;
                padding: 1em;
                border-radius: 10px;
                margin-top: 40px;
            }
            </style>
        """, unsafe_allow_html=True)
        for i, ronda in enumerate(st.session_state.fixture, start=1):
            st.subheader(f"Ronda {i}")
            cols = st.columns(len(ronda))  # una columna por cancha

            for c_i, match in enumerate(ronda):
                p1, p2 = match
                with cols[c_i]:
                    st.markdown(f"""
                        <div class="match-card">
                            <div class="match-title">Cancha {c_i+1}</div>
                            <div class="team-name">{p1}</div>
                            <div class="vs">VS</div>
                            <div class="team-name">{p2}</div>
                        </div>
                    """, unsafe_allow_html=True)

                    colA, colB = st.columns(2)
                    with colA:
                        score1 = st.number_input(f"Puntos {p1}", key=f"{p1}_{p2}_p1", min_value=0)
                    with colB:
                        score2 = st.number_input(f"Puntos {p2}", key=f"{p1}_{p2}_p2", min_value=0)

                    st.session_state.resultados[(p1, p2)] = (score1, score2)
            
        # --- Ranking Final ---            
        if st.button("¿Cómo va el ranking? 👀"):
            ranking = calcular_ranking_parejas(st.session_state.parejas, st.session_state.resultados)
            st.session_state.ranking = ranking
            st.dataframe(ranking)

    # --- Navegación inferior ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Volver", key="back_button"):
            st.session_state.page = "players_setup"
            st.rerun()
    with col4:
        if st.button("Ver Resultados Finales"):
            if mod_parejas == "Parejas Fijas":
                ranking = calcular_ranking_parejas(st.session_state.parejas, st.session_state.resultados)
            elif mod_parejas == "Todos Contra Todos":
                ranking = calcular_ranking_individual(st.session_state.resultados)
            st.session_state.ranking = ranking
            st.session_state.page = "z_ranking"
            st.rerun()
   
#TODO seguimiento ranking 
# verificacion puntaje = suma
