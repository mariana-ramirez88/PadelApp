import streamlit as st
import os,importlib
from assets.sidebar import sidebar_style
from assets.helper_funcs import initialize_vars
st.set_page_config(page_title="PlayZone Padel App",page_icon=":tennis:", layout="wide")

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Cargar la lista de páginas desde la carpeta "pages"
pages_list = ["home"] + [f.replace(".py", "") for f in os.listdir("pages") if f.endswith(".py")]
if "page" not in st.session_state:
    st.session_state.page = "home"  # Start with the homepage    

def load_page(page_name):
    if page_name == "home":

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
            num_fields = st.number_input("Número de canchas",value = 2,key="fields_input",min_value=1)
            st.session_state.num_fields = num_fields
            mod = st.selectbox("Modalidad", ["Todos Contra Todos","Parejas Fijas"],key="modalidad_input",index=1)
            st.session_state.mod = mod
            if mod == "Todos Contra Todos":
                mixto = st.selectbox("Composición Parejas", ["Aleatorio","Siempre Mixto"],key="mixto_input",index=0)
                st.session_state.mixto_op = mixto
                allow_step = 1
            elif mod == "Parejas Fijas":
                allow_step = 2
        with c2:
            num_players = st.number_input("Número de jugadores",value=8,key="select_players",step=allow_step)
            st.session_state.num_players = num_players
            pts = st.selectbox("Formato Puntaje", ["Sets","Puntos"],key="scoring",index=1)
            if pts == "Puntos":
                num_pts = st.number_input("Número de puntos",value=16,key="num_point_input")
                st.session_state.num_pts = num_pts
                win = st.selectbox("Puntos Jugados", ["Suma","Fijo"],key="end_format_input",index=0)
                st.session_state.win = win
    
        
    else:
        module = importlib.import_module(f"pages.{page_name}")
        module.app()
current_page = st.session_state.page
load_page(current_page)
# Obtener el índice de la página actual
current_index = pages_list.index(current_page)

if current_page == "home":
    if st.button("Continuar a Registro de Jugadores",key="button0",use_container_width=True):
        st.session_state.page = pages_list[1]  # Avanzar a la siguiente página
        st.rerun()

sidebar_style()

#TODO arreglar ancho de boton en version desplegada
#TODO poner labels en negrilla 
#incluir resumen de modalidad