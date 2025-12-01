import itertools
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st


def get_unique_players(fixture):
    """Devuelve lista ordenada de jugadores únicos del fixture."""
    return sorted({p for r in fixture for m in r["partidos"] for p in (m["pareja1"] + m["pareja2"])})


def build_matrices(fixture, players):
    """Construye matrices de parejas y enfrentamientos."""
    matrix_parejas = pd.DataFrame(0, index=players, columns=players)
    matrix_enfrentamientos = pd.DataFrame(0, index=players, columns=players)

    for ronda in fixture:
        for partido in ronda["partidos"]:
            p1, p2 = partido["pareja1"], partido["pareja2"]

            # compañeros
            for a, b in itertools.combinations(p1, 2):
                matrix_parejas.loc[a, b] += 1
                matrix_parejas.loc[b, a] += 1
            for a, b in itertools.combinations(p2, 2):
                matrix_parejas.loc[a, b] += 1
                matrix_parejas.loc[b, a] += 1

            # enfrentamientos
            for a in p1:
                for b in p2:
                    matrix_enfrentamientos.loc[a, b] += 1
                    matrix_enfrentamientos.loc[b, a] += 1

    return matrix_parejas, matrix_enfrentamientos


def plot_heatmap(matrix, title, cmap, cbar_label):
    """Genera y muestra un mapa de calor triangular superior."""
    mask = np.tril(np.ones_like(matrix, dtype=bool))
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(matrix, mask=mask, annot=True, fmt="d", cmap=cmap, ax=ax,
                cbar_kws={"label": cbar_label})
    plt.title(title)
    st.pyplot(fig)


def analyze_descansos(fixture, players):
    """Analiza descansos consecutivos y genera mapa de calor."""
    descanso_data = []
    for p in players:
        pattern = [1 if p in r["descansan"] else 0 for r in fixture]
        descanso_data.append(pattern)

    df_desc = pd.DataFrame(descanso_data, index=players)
    df_desc["consec_descansos"] = df_desc.apply(
        lambda x: max((sum(1 for _ in g) for k, g in itertools.groupby(x) if k == 1), default=0), axis=1
    )

    st.dataframe(df_desc[["consec_descansos"]].rename(columns={"consec_descansos": "Descansos consecutivos"}))

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(pd.DataFrame(descanso_data, index=players), cmap="YlOrRd", cbar=False, ax=ax)
    plt.title("Mapa de descansos por ronda (1 = descanso)")
    plt.xlabel("Ronda")
    plt.ylabel("Jugador")
    st.pyplot(fig)


def analyze_algorithm_results(fixture):
    """Ejecuta todo el análisis visual y estadístico del algoritmo."""
    st.markdown("## 🔍 Análisis de Resultados del Algoritmo")

    players = get_unique_players(fixture)
    matrix_parejas, matrix_enfrentamientos = build_matrices(fixture, players)

    st.markdown("#### 🤝 Mapa de calor: quién jugó con quién (parejas)")
    plot_heatmap(matrix_parejas, "Frecuencia de jugadores que compartieron pareja", "PuBuGn", "Veces como pareja")

    st.markdown("#### ⚔️ Mapa de calor: quién jugó contra quién")
    plot_heatmap(matrix_enfrentamientos, "Frecuencia de jugadores que se enfrentaron", "OrRd", "Veces como oponentes")

    st.markdown("#### 💤 Análisis de descansos consecutivos")
    analyze_descansos(fixture, players)


def heatmap_parejas_mixtas(fixture, male_players, female_players):
    # Crear matriz mujer vs hombre
    matrix = pd.DataFrame(0, index=female_players, columns=male_players)

    for ronda in fixture:
        for partido in ronda["partidos"]:
            p1a, p1b = partido["pareja1"]
            p2a, p2b = partido["pareja2"]

            # --- Pareja 1 ---
            # Detectar quién es mujer y quién es hombre
            for f, m in [(p1a, p1b), (p1b, p1a)]:
                if f in female_players and m in male_players:
                    matrix.loc[f, m] += 1

            # --- Pareja 2 ---
            for f, m in [(p2a, p2b), (p2b, p2a)]:
                if f in female_players and m in male_players:
                    matrix.loc[f, m] += 1

    # === Heatmap ===
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(matrix, annot=True, cmap="Purples", linewidths=.5, ax=ax)
    ax.set_title("Combinaciones de Parejas Mixtas (Mujer con Hombre)")

    return matrix, fig


def heatmap_descansos_por_ronda(fixture, all_players):
    # Matriz jugadores x rondas
    matrix = pd.DataFrame(
        0,
        index=all_players,
        columns=[f"Ronda {r['ronda']}" for r in fixture]
    )

    # Rellenar descansos
    for ronda in fixture:
        col = f"Ronda {ronda['ronda']}"
        for p in ronda["descansan"]:
            if p in matrix.index:
                matrix.loc[p, col] = 1

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(matrix, cmap="Reds", linewidths=.5, ax=ax)
    ax.set_title("Descansos por Ronda (1 = descansó)")
    ax.set_xlabel("Ronda")
    ax.set_ylabel("Jugador")

    return matrix, fig

import itertools

def heatmap_enfrentamientos(fixture, all_players):
    # Matriz base
    matrix = pd.DataFrame(0, index=all_players, columns=all_players)

    # Contabilizar enfrentamientos
    for ronda in fixture:
        for partido in ronda["partidos"]:
            p1 = partido["pareja1"]
            p2 = partido["pareja2"]

            for a in p1:
                for b in p2:
                    matrix.loc[a, b] += 1
                    matrix.loc[b, a] += 1

    # Mostrar solo parte superior para evitar duplicados
    mask = np.tril(np.ones_like(matrix, dtype=bool))

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(matrix, mask=mask, annot=True, cmap="Blues",
                linewidths=.5, ax=ax, square=True)
    ax.set_title("Enfrentamientos entre Jugadores")
    ax.set_xlabel("Jugador")
    ax.set_ylabel("Jugador")

    return matrix, fig
