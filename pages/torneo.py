import streamlit as st
from assets.helper_funcs import  calcular_ranking_parejas,initialize_vars, calcular_ranking_individual,render_nombre
from models.AmericanoParejas.AmericanoParejasv1 import FixedPairsTournament
from assets.analyze_funcs import analyze_algorithm_results
from models.AllvsAll_Random_modelv3 import AmericanoTournament
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import itertools,random
import numpy as np

def app():
    num_canchas = st.session_state.num_fields
    puntos_partido =st.session_state.num_pts
    to_init = {"code_play": "", "ranking":""}
    initialize_vars(to_init)

    # Función Callback para actualizar inmediatamente
    def actualizar_resultado(p1_str, p2_str, k1, k2):
        # Leemos el valor actual de los inputs usando sus keys
        val1 = st.session_state[k1]
        val2 = st.session_state[k2]
        # Guardamos inmediatamente en el diccionario de resultados
        st.session_state.resultados[(p1_str, p2_str)] = (val1, val2)
    
    #divission logica parejas fijas vs aleatorias
    mod_parejas = st.session_state.mod
    if mod_parejas == "Parejas Fijas":
        st.markdown('<div class="main-title"> Torneo Americano - Parejas Fijas </div>', unsafe_allow_html=True)
        parejas = st.session_state.players
        
        # AUTO-GENERATE fixture on first load
        tournament_key = f"parejas_fijas_{len(parejas)}_{num_canchas}_{puntos_partido}"
        if 'tournament_key' not in st.session_state or st.session_state.tournament_key != tournament_key:
            with st.spinner("Generando fixture..."):
                generator = FixedPairsTournament(parejas, num_canchas)
                resultados_torneo = generator.generate_schedule()
                st.session_state.fixture = resultados_torneo["rondas"]
                st.session_state.code_play = "parejas_fijas"
                st.session_state.resultados = {}
                st.session_state.parejas = parejas
                st.session_state.tournament_key = tournament_key
        if st.session_state.code_play == "parejas_fijas" :
            st.markdown("""
                <style>
                .main-title {
                text-align: center;
                font-size: 32px;
                color: #6C13BF; /* Morado/Púrpura */
                font-weight: 700;
                margin-bottom: 40px;
                }
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
            
                # 1. Agrupar partidos por turno
                partidos_por_turno = {}
                for match in ronda['partidos']:
                    turno = match['turno']
                    if turno not in partidos_por_turno:
                        partidos_por_turno[turno] = []
                    partidos_por_turno[turno].append(match)

                # 2. Iterar sobre los turnos dentro de la ronda
                for turno, partidos_del_turno in partidos_por_turno.items():
                    
                    # Solo mostramos el número de turno si hay más de uno
                    if len(partidos_por_turno) > 1:
                        st.markdown(f"**Turno {turno}:**", unsafe_allow_html=True)

                    # Usamos st.columns para visualizar los partidos de ESTE TURNO
                    # El número de columnas es el número de canchas usadas en este turno
                    cols = st.columns(len(partidos_del_turno))

                    for c_i, match in enumerate(partidos_del_turno):
                        # 🎯 CLAVE: Usamos el nombre del equipo/pareja DIRECTAMENTE
                        p1_equipo_str = match['pareja1'] 
                        p2_equipo_str = match['pareja2'] 

                        with cols[c_i]:
                            st.markdown(f"""
                                <div class="match-card">
                                    <div class="match-title">Cancha {match['cancha']}</div>
                                    <div class="team-name">{p1_equipo_str}</div>
                                    <div class="vs">VS</div>
                                    <div class="team-name">{p2_equipo_str}</div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # --- Input de Resultados a nivel de EQUIPO ---
                            # Las keys y los strings de referencia usan el nombre completo de la pareja.
                            k1 = f"{p1_equipo_str}_vs_{p2_equipo_str}_p1"
                            k2 = f"{p1_equipo_str}_vs_{p2_equipo_str}_p2"
                            
                            # Recuperar resultados usando los nombres de los equipos
                            saved_s1, saved_s2 = st.session_state.resultados.get((p1_equipo_str, p2_equipo_str), (0, 0))

                            colA, colB = st.columns(2)
                            with colA:
                                # Etiqueta de input con el nombre del equipo
                                st.number_input(
                                    f"Puntos {p1_equipo_str}", 
                                    key=k1, 
                                    min_value=0,
                                    max_value=puntos_partido, 
                                    value=saved_s1,
                                    on_change=actualizar_resultado,
                                    kwargs={"p1_str": p1_equipo_str, "p2_str": p2_equipo_str, "k1": k1, "k2": k2}
                                )
                            with colB:
                                # Etiqueta de input con el nombre del equipo
                                st.number_input(
                                    f"Puntos {p2_equipo_str}", 
                                    key=k2, 
                                    min_value=0,
                                    max_value=puntos_partido, 
                                    value=saved_s2,
                                    on_change=actualizar_resultado,
                                    kwargs={"p1_str": p1_equipo_str, "p2_str": p2_equipo_str, "k1": k1, "k2": k2})

                # Mostrar parejas que descansan
                parejas_descansando = ronda['descansan'] # Directamente del diccionario
                if parejas_descansando:
                    st.info(f"Descansan en Ronda {i}: {', '.join(parejas_descansando)}")
            # --- Ranking Final ---            
            if st.button("¿Cómo va el ranking? 👀", key="ranking_parejas",use_container_width=True):
                ranking = calcular_ranking_parejas(st.session_state.parejas, st.session_state.resultados)
                st.session_state.ranking = ranking
                st.dataframe(ranking)


    elif mod_parejas == "Todos Contra Todos":
        def generar_torneo_todos_contra_todos(jugadores, num_canchas, seed=None):
            if seed:
                random.seed(seed)
            
            tournament = AmericanoTournament(st.session_state.players, num_canchas)
            schedule, helpers = tournament.generate_tournament()
            return tournament.format_for_streamlit(schedule, helpers)
        
        st.markdown('<div class="main-title"> Torneo Americano</div>', unsafe_allow_html=True)

        
        # AUTO-GENERATE fixture on first load (igual que en sets)
        jugadores = st.session_state.players
        tournament_key = f"todos_contra_todos_{len(jugadores)}_{num_canchas}_{puntos_partido}"
        
        if 'tournament_key' not in st.session_state or st.session_state.tournament_key != tournament_key:
            with st.spinner("Generando fixture optimizado..."):
                out = generar_torneo_todos_contra_todos(jugadores, num_canchas, seed=42)
                st.session_state.code_play = "AllvsAll"
                st.session_state.fixture = out["rondas"]
                st.session_state.out = out
                st.session_state.resultados = {}
                st.session_state.tournament_key = tournament_key


        # Visualización especial para Todos Contra Todos
        if st.session_state.code_play == "AllvsAll":
            st.markdown("""
                <style>
                .main-title {
                text-align: center;
                font-size: 32px;
                color: #6C13BF; /* Morado/Púrpura */
                font-weight: 700;
                margin-bottom: 40px;
                }
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
                st.subheader(f"Ronda {ronda_data['ronda']}")
                cols = st.columns(len(ronda_data["partidos"]))

                for c_i, partido in enumerate(ronda_data["partidos"]):
                    ayudantes = partido.get("ayudantes", []) or []
                    # aplicar ícono a los nombres que son ayudantes
                    p1_render = [render_nombre(j, ayudantes) for j in partido["pareja1"]]
                    p2_render = [render_nombre(j, ayudantes) for j in partido["pareja2"]]

                    pareja1 = " & ".join(p1_render)
                    pareja2 = " & ".join(p2_render)
                    if ayudantes:
                        lista_ayudantes = ", ".join([render_nombre(a, ayudantes) for a in ayudantes])
                        ayud_text = f"<div style='font-size:14px;color:#6C13BF;margin-top:5px;'>Ayudantes: {lista_ayudantes}</div>"
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

                        # --- keys seguras basadas en nombres reales ---
                        raw_p1 = "_".join(partido["pareja1"])
                        raw_p2 = "_".join(partido["pareja2"])

                        key_p1 = f"score_r{ronda_data['ronda']}_m{c_i}_{raw_p1}_p1"
                        key_p2 = f"score_r{ronda_data['ronda']}_m{c_i}_{raw_p2}_p2"

                        # --- CAMBIO: Recuperar valores guardados si existen ---
                        pareja1_str = " & ".join(partido["pareja1"])
                        pareja2_str = " & ".join(partido["pareja2"])
                        # Buscamos si ya hay un resultado guardado para este partido
                        saved_s1, saved_s2 = st.session_state.resultados.get((pareja1_str, pareja2_str), (0, 0))

                        colA, colB = st.columns(2)
                        with colA:
                            st.number_input(
                                f"Puntos {pareja1}", 
                                key=key_p1, 
                                min_value=0,
                                max_value=puntos_partido, 
                                value=saved_s1,
                                on_change=actualizar_resultado,
                                kwargs={"p1_str": pareja1_str, "p2_str": pareja2_str, "k1": key_p1, "k2": key_p2}
                            )
                        with colB:
                            st.number_input(
                                f"Puntos {pareja2}", 
                                key=key_p2, 
                                min_value=0,
                                max_value=puntos_partido, 
                                value=saved_s2,
                                on_change=actualizar_resultado,
                                kwargs={"p1_str": pareja1_str, "p2_str": pareja2_str, "k1": key_p1, "k2": key_p2}
                            )

                if ronda_data["descansan"]:
                    st.info(f"Descansan: {', '.join(ronda_data['descansan'])}")
                        
            # Mostrar resumen de partidos jugados y descansos
            if "out" in st.session_state and "resumen" in st.session_state.out:
                st.markdown("### Resumen de participación")
                st.dataframe(st.session_state.out["resumen"])
            
            # --- Ranking Final ---
            if st.button("¿Cómo va el ranking? 👀",use_container_width=True):
                ranking = calcular_ranking_individual(st.session_state.resultados, st.session_state.fixture)
                st.session_state.ranking = ranking
                st.dataframe(ranking)
            

    # --- Navegación inferior ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Volver y Reiniciar", key="back_button"):
            # Limpiar datos del torneo al volver
            if 'tournament_key' in st.session_state:
                del st.session_state.tournament_key
            if 'fixture' in st.session_state:
                del st.session_state.fixture
            if 'resultados' in st.session_state:
                del st.session_state.resultados
            st.session_state.page = "players_setup"
            st.rerun()
    with col4:
        if st.button("Ver Resultados Finales 🏆"):
            if mod_parejas == "Parejas Fijas":
                ranking = calcular_ranking_parejas(st.session_state.parejas, st.session_state.resultados)
            elif mod_parejas == "Todos Contra Todos":
                ranking = calcular_ranking_individual(st.session_state.resultados,st.session_state.fixture)
            st.session_state.ranking = ranking
            st.session_state.page = "z_ranking"
            st.rerun()