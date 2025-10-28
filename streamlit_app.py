import streamlit as st
import os,importlib
from assets.sidebar import sidebar_style
st.set_page_config(page_title="PlayZone Padel App",page_icon=":tennis:", layout="wide")

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "home"

# Cargar la lista de páginas desde la carpeta "pages"
pages_list = ["home"] + [f.replace(".py", "") for f in os.listdir("pages") if f.endswith(".py")]

def load_page(page_name):
    if page_name == "home":

        #st.title("Configuración del Torneo")
        st.markdown("""
        <style>
        .main-title {
            text-align: center;
            font-size: 36px;
            color: #6C13BF;
            font-weight: 700;
            margin-bottom: 50px;
        }

        /* === INPUTS NUMÉRICOS MÁS GRANDES === */
        .stNumberInput input {
            min-height: 52px !important;
            width: 100% !important;          /* ocupa todo el ancho posible */
            padding: 0 18px !important;
            font-size: 20px !important;
            border-radius: 10px !important;
            background-color: #f7f7fb !important;
            line-height: 52px !important;
        }
                    
        .stNumberInput button {
        color: white !important;           /* color de los signos + y - */
        }

        /* === SELECTBOX IGUALADOS === */
        div[data-baseweb="select"] > div {
            min-height: 52px !important;
            padding: 0 18px !important;
            font-size: 20px !important;
            border-radius: 10px !important;
            background-color: #f7f7fb !important;
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
        }

        /* === LABELS MÁS GRANDES Y EN NEGRILLA === */
        label, .stSelectbox label, .stNumberInput label {
            font-size: 32px !important;      /* más grandes */
            font-weight: 700 !important;     /* negrilla */
            color: #0B0B19 !important;       /* color oscuro */
            margin-bottom: 6px !important;
        }

        /* === ESPACIADO ENTRE CAMPOS === */
        .stSelectbox, .stNumberInput {
            margin-bottom: 25px !important;
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
                    
        div[data-testid="column"] { padding: 0 30px !important; } 
        section.main > div { padding-top: 30px; }            
        </style>
        """, unsafe_allow_html=True)



        # Título centrado
        st.markdown('<div class="main-title">🏆 PlayZone Padel App</div>', unsafe_allow_html=True)

        c1,c2 = st.columns(2)
        with c1:
            num_fields = st.number_input("Número de canchas", value=2)
            mod = st.selectbox("Modalidad", ["Todos Contra Todos","Parejas Fijas"])
            if mod == "Todos Contra Todos":
                mixto = st.selectbox("Composición Parejas", ["Aleatorio","Siempre Mixto"])
        with c2:
            num_players = st.number_input("Número de jugadores",value=8)
            pts = st.selectbox("Formato Puntaje", ["Sets","Puntos"])
            if pts == "Puntos":
                num_pts = st.number_input("Número de puntos",value=16)
                win = st.selectbox("Puntos Jugados", ["Suma","Fijo"])

        
    else:
        module = importlib.import_module(f"pages.{page_name}")
        module.app()
current_page = st.session_state.page
load_page(current_page)
# Obtener el índice de la página actual
current_index = pages_list.index(current_page)

if st.button("Continuar a Registro de Jugadores",key="button0"):
    st.session_state.page = pages_list[1]  # Avanzar a la siguiente página
    st.rerun()

sidebar_style()