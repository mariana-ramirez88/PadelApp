import streamlit as st
from assets.helper_funcs import generar_fixture, calcular_ranking

def app():
    st.title("Torneo Americano - Parejas Fijas - Suma")
    parejas = st.session_state.players
    num_canchas = st.session_state.num_fields
    puntos_partido =st.session_state.num_pts
    st.write(f"se jugara un partido con parejas fijas en {num_canchas} canchas a la suma de {puntos_partido} puntos")

    if st.button("Generar Fixture"):
        if len(parejas) < 2:
            st.warning("Se requieren al menos 2 parejas.")
        else:
            st.session_state.fixture = generar_fixture(parejas, num_canchas)
            st.session_state.resultados = {}
            st.session_state.parejas = parejas
            st.success("Fixture generado.")

    if "fixture" in st.session_state:
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
        if st.button("Calcular Ranking Final"):
            ranking = calcular_ranking(st.session_state.parejas, st.session_state.resultados)
            st.dataframe(ranking)

    # --- Navegación inferior ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Volver", key="back_button"):
            st.session_state.page = "players_setup"
            st.rerun()
   
#TODO seguimiento ranking 
# verificacion puntaje = suma