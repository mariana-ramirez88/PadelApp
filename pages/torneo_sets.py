import streamlit as st
from assets.helper_funcs import generar_fixture_parejas
from models.sets.All_pairs_sets import calcular_ranking_parejas_sets

def app():
    st.markdown('<div class="main-title"> Torneo por Sets </div>', unsafe_allow_html=True)    
    if 'num_fields' not in st.session_state: st.session_state.num_fields = 1
    if 'num_sets' not in st.session_state: st.session_state.num_sets = 3
    if 'players' not in st.session_state: st.session_state.players = []

    num_canchas = st.session_state.num_fields
    num_sets = st.session_state.num_sets
    
    # 1. 📌 FIX DE SEGURIDAD Y PREPARACIÓN DE VARIABLES
    # Garantiza que estas variables existan antes de ser usadas por el resto del script
    if 'parejas' not in st.session_state: st.session_state.parejas = st.session_state.players
    if 'resultados' not in st.session_state: st.session_state.resultados = {}
    if 'fixture' not in st.session_state: st.session_state.fixture = []
    if 'show_final' not in st.session_state: st.session_state.show_final = False
    if 'show_ranking' not in st.session_state: st.session_state.show_ranking = False # NUEVO ESTADO PARA EL RANKING
    if 'final_match_scores' not in st.session_state: st.session_state.final_match_scores = (0, 0)
    
    parejas = st.session_state.parejas
    
    # 2. 🔄 FUNCIÓN CALLBACK: Actualiza el diccionario 'resultados' (Fase de Grupos)
    def actualizar_resultado_sets(p1, p2, k1, k2):
        """Lee los valores de los number_input (usando sus keys) y actualiza el diccionario maestro."""
        val1 = st.session_state.get(k1, 0)
        val2 = st.session_state.get(k2, 0)
        st.session_state.resultados[(p1, p2)] = (val1, val2)
        
    # 3. 🏆 FUNCIÓN CALLBACK: Actualiza el resultado de la Final
    def actualizar_final_score(k1, k2):
        """Actualiza la variable específica de la final y el estado de session."""
        val1 = st.session_state.get(k1, 0)
        val2 = st.session_state.get(k2, 0)
        st.session_state.final_match_scores = (val1, val2)
    
    # Generación de fixture
    tournament_key = f"parejas_fijas_{len(parejas)}_{num_canchas}_{num_sets}_sets"
    if 'tournament_key' not in st.session_state or st.session_state.tournament_key != tournament_key:
        with st.spinner("Generando fixture optimizado..."):
            st.session_state.fixture = generar_fixture_parejas(parejas,num_canchas)
            st.session_state.resultados = {}
            st.session_state.parejas = parejas
            st.session_state.tournament_key = tournament_key
            
    # --- Estilos CSS (Se mantienen sin cambios) ---
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
        .final-match-card {
            background-color: #5E3187; 
            color: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .match-title {
            font-weight: 700;
            font-size: 18px;
            color: #0B0B19;
            margin-bottom: 10px;
        }
        .final-title {
            font-weight: 700;
            font-size: 24px;
            color: white;
            margin-bottom: 10px;
            text-align: center;
        }
        .team-name {
            font-weight: 600;
            color: #0B0B19;
            font-size: 16px;
            text-align: center;
        }
        .final-team-name {
            font-weight: 700;
            color: white;
            font-size: 20px;
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
        .final-vs {
            font-weight: 800;
            font-size: 24px;
            color: #00CED1; /* CAMBIO: Color turquesa estilizado */
            text-align: center;
            margin-top: 15px;
            margin-bottom: 15px;
        }
        /* Ajuste para que los number_input sean menos disruptivos visualmente */
        /* Nota: Streamlit aplica sus propios estilos, estos son hacks CSS */
        div[data-testid="stForm"] div.stNumberInput input { 
            text-align: center;
            font-weight: 700;
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
    
    # ----------------------------------------------------------------------
    # FASE DE GRUPOS (FIXTURE)
    # ----------------------------------------------------------------------
    for i, ronda in enumerate(st.session_state.fixture, start=1):
        st.subheader(f"Ronda {i}")
        cols = st.columns(len(ronda))

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
                
                # Keys
                match_key = f"{p1}_{p2}_ronda_{i}_cancha_{c_i}"
                score1_key = f"{match_key}_p1"
                score2_key = f"{match_key}_p2"
                
                # Recuperar valor guardado o 0
                # st.session_state.resultados usa tuplas inmutables como clave
                saved_s1, saved_s2 = st.session_state.resultados.get(tuple(sorted((p1, p2))), (0, 0))


                with colA:
                    st.number_input(
                        f"Sets {p1}", 
                        key=score1_key, 
                        min_value=0, 
                        value=saved_s1, # Usa el valor guardado
                        label_visibility="collapsed",
                        on_change=actualizar_resultado_sets, # ✅ CALLBACK GRUPOS P1
                        kwargs={"p1": p1, "p2": p2, "k1": score1_key, "k2": score2_key}
                    )
                with colB:
                    st.number_input(
                        f"Sets {p2}", 
                        key=score2_key, 
                        min_value=0, 
                        value=saved_s2, # Usa el valor guardado
                        label_visibility="collapsed",
                        on_change=actualizar_resultado_sets, # ✅ CALLBACK GRUPOS P2
                        kwargs={"p1": p1, "p2": p2, "k1": score1_key, "k2": score2_key}
                    )

    # ----------------------------------------------------------------------
    # BOTONES DE RANKING Y FINAL (EN COLUMNAS)
    # ----------------------------------------------------------------------
    colY, colX = st.columns(2)
    
    with colY:
        # Botón para mostrar/ocultar ranking temporal (MODIFICADO)
        btn_label = "Ocultar Ranking 🔼" if st.session_state.show_ranking else "¿Cómo va el ranking? 👀"
        if st.button(btn_label, use_container_width=True):
            st.session_state.show_ranking = not st.session_state.show_ranking # Toglea el estado
            st.rerun() # Dispara el renderizado
            
    with colX:
        # Lógica para botón de la Final
        df_ranking_temp = None
        try:
            df_ranking_temp = calcular_ranking_parejas_sets(parejas, st.session_state.resultados)
        except Exception:
            pass # Si hay error, df_ranking_temp será None

        if df_ranking_temp is not None and len(df_ranking_temp) >= 2 and not st.session_state.show_final:
            if st.button("🎉 Mostrar Gran Final 🎉", use_container_width=True):
                st.session_state.show_final = True
                st.rerun() # Disparar un nuevo renderizado para mostrar la final

    # ----------------------------------------------------------------------
    # 4. VISUALIZACIÓN DEL RANKING COMPLETO (FUERA DE COLUMNAS)
    # ----------------------------------------------------------------------
    if st.session_state.show_ranking:
        st.markdown("<hr style='border: 1px solid #ddd; margin: 30px 0;'>", unsafe_allow_html=True)
        st.header('📊 Clasificación Actual')
        st.info(f"Regla: 1 Punto por partido ganado. Desempate por Diferencia de Sets (SG - SP).")
        
        try:
            df_ranking = calcular_ranking_parejas_sets(parejas, st.session_state.resultados)
            
            col_config = {
                'Pareja': st.column_config.TextColumn("Pareja"), # Asegura que la columna Pareja sea TextColumn
                'Partidos Jugados': st.column_config.NumberColumn("Partidos Jugados", format="%d"),
                'Puntos': st.column_config.NumberColumn("Puntos", format="%d"),
                'Sets Ganados': st.column_config.NumberColumn("Sets Ganados", format="%d"),
                'Sets Perdidos': st.column_config.NumberColumn("Sets Perdidos", format="%d"),
                'Diferencia de Sets': st.column_config.NumberColumn("Diferencia de Sets", format="%d"),
            }
            
            # El uso de use_container_width=True aquí garantiza que ocupe todo el ancho disponible.
            st.dataframe(
                df_ranking, 
                column_order=('Pareja', 'Partidos Jugados', 'Puntos', 'Sets Ganados', 'Sets Perdidos', 'Diferencia de Sets'),
                column_config=col_config,
                use_container_width=True 
            )
        except Exception as e:
            st.error(f"❌ Error al calcular ranking: {str(e)}")


    # ----------------------------------------------------------------------
    # FASE FINALES: Gran Final (Top 2)
    # ----------------------------------------------------------------------
    
    # 1. Calcular el ranking de la fase de grupos para obtener los 2 finalistas
    df_ranking_final = None
    try:
        df_ranking_final = calcular_ranking_parejas_sets(parejas, st.session_state.resultados)
    except Exception:
        df_ranking_final = None # Se mantiene la lógica de error

    # Lógica de renderizado de la final
    if st.session_state.show_final and df_ranking_final is not None and len(df_ranking_final) >= 2:
        
        finalists = df_ranking_final.head(2)['Pareja'].tolist()
        final_p1 = finalists[0]
        final_p2 = finalists[1]
        
        # Separador visual
        st.markdown("<hr style='border: 1px solid #ddd; margin: 50px 0;'>", unsafe_allow_html=True)
        st.header('🏆 Fase Final: Gran Final')
        st.markdown(f"<p style='text-align:center; font-size:18px; font-weight:600;'>El partido final es entre:</p>", unsafe_allow_html=True)
        
        # Usa columnas para centrar la tarjeta de la final
        col_final_spacer_1, col_final_match, col_final_spacer_2 = st.columns([1, 2, 1])

        with col_final_match:
            st.markdown(f"""
                <div class="final-match-card">
                    <div class="final-title">GRAN FINAL</div>
                    <div class="final-team-name">{final_p1}</div>
                    <div class="final-vs">VS</div>
                    <div class="final-team-name">{final_p2}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"<p style='text-align:center; font-weight:600; color:#000000;'>Introduce los sets de la Final</p>", unsafe_allow_html=True)
            colA, colB = st.columns(2)
            
            # Usar claves únicas para el resultado de la final
            final_key_p1 = f"final_sets_{final_p1}"
            final_key_p2 = f"final_sets_{final_p2}"

            # Recuperar valores guardados de session_state (ya no depende de final_match_scores para el valor inicial)
            final_saved_s1 = st.session_state.get(final_key_p1, 0)
            final_saved_s2 = st.session_state.get(final_key_p2, 0)

            with colA:
                st.markdown(f"<p style='color: #000000; font-weight: 600; text-align: center; margin-bottom: 5px;'>{final_p1}</p>", unsafe_allow_html=True)
                st.number_input(
                    f"Sets {final_p1}", 
                    key=final_key_p1, 
                    min_value=0, 
                    value=final_saved_s1,
                    label_visibility="collapsed",
                    on_change=actualizar_final_score, # ✅ CALLBACK FINAL P1
                    kwargs={"k1": final_key_p1, "k2": final_key_p2}
                )
            with colB:
                st.markdown(f"<p style='color: #000000; font-weight: 600; text-align: center; margin-bottom: 5px;'>{final_p2}</p>", unsafe_allow_html=True)
                st.number_input(
                    f"Sets {final_p2}", 
                    key=final_key_p2, 
                    min_value=0, 
                    value=final_saved_s2,
                    label_visibility="collapsed",
                    on_change=actualizar_final_score, # ✅ CALLBACK FINAL P2
                    kwargs={"k1": final_key_p1, "k2": final_key_p2}
                )

            # Mostrar el ganador dinámicamente (lee de st.session_state.final_match_scores)
            final_score1, final_score2 = st.session_state.final_match_scores
            final_winner = ""
            if final_score1 > final_score2:
                final_winner = final_p1
            elif final_score2 > final_score1:
                final_winner = final_p2
            
            if final_winner:
                st.success(f"🎉 **Ganador de la Final:** {final_winner} ({final_score1}-{final_score2})")
            elif final_score1 > 0 or final_score2 > 0:
                st.warning("El partido es un empate (Sets iguales).")
            else:
                st.markdown("<p style='text-align:center;'>Pendiente de resultado</p>", unsafe_allow_html=True)


    # ----------------------------------------------------------------------
    # NAVEGACIÓN
    # ----------------------------------------------------------------------
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Volver", key="back_buttonS", use_container_width=True):
            # Limpiar datos del torneo al volver
            if 'tournament_key' in st.session_state:
                del st.session_state.tournament_key
            if 'fixture' in st.session_state:
                del st.session_state.fixture
            if 'resultados' in st.session_state:
                del st.session_state.resultados
            if 'show_final' in st.session_state:
                del st.session_state.show_final
            if 'final_match_scores' in st.session_state:
                del st.session_state.final_match_scores
            if 'show_ranking' in st.session_state: # Limpiar el nuevo estado
                del st.session_state.show_ranking
                
            st.session_state.page = "players_setup"
            st.rerun()

    with col3:
        if st.button("🏆 Ver Resultados Finales", use_container_width=True):
            try:
                # Calculate final ranking (based on group stage)
                df_ranking = calcular_ranking_parejas_sets(parejas, st.session_state.resultados)
                
                if df_ranking is not None and not df_ranking.empty:
                    st.session_state.ranking = df_ranking
                    st.session_state.page = "z_ranking"
                    st.rerun()
                else:
                    st.warning("⚠️ Debes ingresar al menos algunos resultados antes de ver el ranking final")
            except Exception as e:
                st.error(f"❌ Error al calcular ranking: {str(e)}")