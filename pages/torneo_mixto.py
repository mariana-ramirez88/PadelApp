import streamlit as st
from models.AmericanoMixto.AllvsAll_MixtoV2 import AmericanoPadelTournament, generar_torneo_mixto
from assets.helper_funcs import initialize_vars, calcular_ranking_individual, render_nombre
from assets.analyze_funcs import heatmap_parejas_mixtas,heatmap_descansos_por_ronda, heatmap_enfrentamientos
from collections import defaultdict
import random
import pandas as pd
def app():
    st.title("Torneo Americano Mixto")
    
    # Initialize resultados if not exists
    if 'resultados' not in st.session_state:
        st.session_state.resultados = {}
    
    # Get players and settings from session state
    male_players = st.session_state.hombres
    female_players = st.session_state.mujeres
    num_canchas = st.session_state.num_fields
    puntos_partido = st.session_state.num_pts

    # Validate equal numbers
    if len(male_players) != len(female_players):
        st.error(f"❌ Debes tener el mismo número de hombres y mujeres. Tienes {len(male_players)} hombres y {len(female_players)} mujeres.")
        if st.button("Volver a configuración"):
            st.session_state.page = "players_setup"
            st.rerun()
        return
    
    # Create a unique key for this tournament configuration
    tournament_key = f"mixto_{len(male_players)}_{len(female_players)}_{num_canchas}_{puntos_partido}"
    
    # Generate fixture ONLY if it doesn't exist or configuration changed
    if 'tournament_key' not in st.session_state or st.session_state.tournament_key != tournament_key:
        with st.spinner("Generando fixture optimizado..."):
            out = generar_torneo_mixto(male_players, female_players, 
                                        num_canchas, puntos_partido)
            st.session_state.fixture = out["rondas"]
            st.session_state.out = out
            st.session_state.resultados = {}
            st.session_state.tournament_key = tournament_key

    # Custom CSS
    st.markdown("""
        <style>
        .match-card {
            background: linear-gradient(145deg, #ffffff, #f0f0f5);
            border-radius: 18px;
            padding: 22px;
            margin-bottom: 25px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            border: 1px solid rgba(108, 19, 191, 0.1);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .match-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(0,0,0,0.2);
        }
        .match-title {
            font-weight: 700;
            font-size: 18px;
            color: #0B0B19;
            margin-bottom: 10px;
            text-align: center;
        }
        .team-name {
            font-weight: 600;
            color: #0B0B19;
            font-size: 16px;
            text-align: center;
            padding: 8px;
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
            color: white !important;
            font-weight: 700 !important;
        }
        .stNumberInput button {
            color: white !important;
        }
        .stButton button {
            width: 100%;
            background-color: #0B0B19;
            color: white;
            font-weight: 700;
            font-size: 18px;
            padding: 1em;
            border-radius: 10px;
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Display each round
    for ronda_data in st.session_state.fixture:
        st.markdown(f"### Ronda {ronda_data['ronda']}")
        
        # Create columns for matches
        num_partidos = len(ronda_data["partidos"])
        if num_partidos > 0:
            cols = st.columns(num_partidos)
            
            for c_i, partido in enumerate(ronda_data["partidos"]):
                ayudantes = partido.get("ayudantes", []) or []
                
                # Render player names
                p1_render = [render_nombre(j, ayudantes) for j in partido["pareja1"]]
                p2_render = [render_nombre(j, ayudantes) for j in partido["pareja2"]]
                
                pareja1 = " & ".join(p1_render)
                pareja2 = " & ".join(p2_render)
                
                cancha = partido["cancha"]
                
                with cols[c_i]:
                    # Display match card
                    st.markdown(f"""
                        <div class="match-card">
                            <div class="match-title">Cancha {cancha}</div>
                            <div class="team-name">{pareja1}</div>
                            <div class="vs">VS</div>
                            <div class="team-name">{pareja2}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Score inputs with safe keys
                    raw_p1 = "_".join(partido["pareja1"])
                    raw_p2 = "_".join(partido["pareja2"])
                    
                    key_p1 = f"score_r{ronda_data['ronda']}_m{c_i}_{raw_p1}_p1"
                    key_p2 = f"score_r{ronda_data['ronda']}_m{c_i}_{raw_p2}_p2"
                    
                    # Create unique match key for storing results
                    pareja1_str = " & ".join(partido["pareja1"])
                    pareja2_str = " & ".join(partido["pareja2"])
                    
                    colA, colB = st.columns(2)
                    with colA:
                        score1 = st.number_input(
                            f"Puntos {pareja1}", 
                            key=key_p1, 
                            min_value=0,
                            max_value=puntos_partido
                        )
                    with colB:
                        score2 = st.number_input(
                            f"Puntos {pareja2}", 
                            key=key_p2, 
                            min_value=0,
                            max_value=puntos_partido
                        )
                    
                    # Store results immediately - tuple key for calcular_ranking_individual
                    st.session_state.resultados[(pareja1_str, pareja2_str)] = (score1, score2)
        
        # Show resting players
        if ronda_data["descansan"]:
            st.info(f"Descansan: {', '.join(ronda_data['descansan'])}")
        
        st.markdown("---")
    
    # Debug section (optional - can be removed in production)
    with st.expander("🔍 Ver Datos de Depuración"):
        st.write("**Resultados almacenados:**")
        # Convert to displayable format
        debug_results = {}
        for key, value in st.session_state.resultados.items():
            if isinstance(key, tuple):
                debug_results[f"{key[0]} vs {key[1]}"] = f"{value[0]} - {value[1]}"
            else:
                debug_results[str(key)] = str(value)
        st.json(debug_results)
        st.write("**Número de partidos con resultados:**", len(st.session_state.resultados))
        
        # Show raw data
        st.write("**Formato crudo para debugging:**")
        for match, scores in st.session_state.resultados.items():
            if isinstance(scores, tuple) and scores[0] > 0 or scores[1] > 0:
                st.write(f"- {match[0]} vs {match[1]}: {scores[0]} - {scores[1]}")

    # =========================================================
    #      🔍 SECCIÓN: ANÁLISIS DE TORNEO MIXTO
    # =========================================================
    st.markdown("## 🔍 Análisis del Algoritmo (Mixto)")

    mat_parejas, fig_parejas = heatmap_parejas_mixtas(
    st.session_state.fixture,
    st.session_state.hombres,
    st.session_state.mujeres
    )
    st.pyplot(fig_parejas)
    st.dataframe(mat_parejas)

    players = st.session_state.hombres + st.session_state.mujeres
    st.write("Descansos consecutivos por jugador:")

    matrix_desc,fig_desc = heatmap_descansos_por_ronda(st.session_state.fixture,players)

    st.pyplot(fig_desc)
    st.dataframe(matrix_desc)
    matrix2, fig2 = heatmap_enfrentamientos(st.session_state.fixture,players)
    st.pyplot(fig2)
    st.dataframe(matrix2)

        
    # Show summary
    if "out" in st.session_state and "resumen" in st.session_state.out:
        st.markdown("### 📊 Resumen de Participación")
        df_resumen = pd.DataFrame(st.session_state.out["resumen"])
        st.dataframe(df_resumen, use_container_width=True)
    
    # Ranking buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👀 ¿Cómo va el ranking?", use_container_width=True):
            try:
                # Calculate ranking
                ranking = calcular_ranking_individual(st.session_state.resultados, st.session_state.fixture)
                
                if ranking is not None and not ranking.empty:
                    st.session_state.ranking = ranking
                    st.success("✅ Ranking calculado correctamente")
                    st.dataframe(ranking, use_container_width=True)
                else:
                    st.warning("⚠️ No hay suficientes resultados para calcular el ranking")
            except Exception as e:
                st.error(f"❌ Error al calcular ranking: {str(e)}")
                st.write("Detalles del error:", e)
    
    with col2:
        if st.button("🏆 Ver Resultados Finales", use_container_width=True):
            try:
                # Calculate final ranking
                ranking = calcular_ranking_individual(st.session_state.resultados, st.session_state.fixture)
                
                if ranking is not None and not ranking.empty:
                    st.session_state.ranking = ranking
                    st.session_state.page = "z_ranking"
                    st.rerun()
                else:
                    st.warning("⚠️ Debes ingresar al menos algunos resultados antes de ver el ranking final")
            except Exception as e:
                st.error(f"❌ Error al calcular ranking: {str(e)}")

    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Volver", key="back_button", use_container_width=True):
            # Clear tournament data when going back
            if 'tournament_key' in st.session_state:
                del st.session_state.tournament_key
            if 'fixture' in st.session_state:
                del st.session_state.fixture
            if 'out' in st.session_state:
                del st.session_state.out
            if 'resultados' in st.session_state:
                del st.session_state.resultados
            st.session_state.page = "players_setupMixto"
            st.rerun()