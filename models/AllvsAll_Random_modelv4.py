import random
import itertools
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple
import pandas as pd

def generar_torneo_todos_contra_todos(
    jugadores: List[str],
    num_canchas: int,
    seed: int | None = None,
    allow_rounds_offset: int = 1  # intentar j-2, si no posible j-1 (offset=1)
) -> Dict[str, Any]:
    """
    Heurístico que intenta cumplir prioridades:
      1) minimizar rondas (j-2 preferido, j-1 máximo)
      2) igualar partidos válidos por jugador (ayudantes no cuentan)
      3) balancear descansos y evitar descansos consecutivos
      4) minimizar repetición de parejas
    Devuelve estructura similar a tu versión original.
    Limitaciones: heurístico, no garantiza optimalidad.
    """
    if seed is not None:
        random.seed(seed)

    n = len(jugadores)
    if n < 4:
        raise ValueError("Se requieren al menos 4 jugadores para dobles 2vs2.")

    # metas de rondas
    if n == 8 and num_canchas == 2:
        # caso especial solicitado
        min_rounds = 7
        max_rounds = 7
    else:
        min_rounds = max(1, n - 2)
        max_rounds = max(1, n - 1)

    target_rounds = min_rounds
    max_total_rounds = max_rounds

    # pares que deben cubrirse (enfrentamientos "opuesto a pareja": cada jugador contra otro)
    todos_pares = set(tuple(sorted(p)) for p in itertools.combinations(jugadores, 2))

    # estados
    partidos_jugados = defaultdict(int)   # solo partidas válidas cuentan
    descansos = defaultdict(int)
    descansos_ult_ronda = {j: -100 for j in jugadores}  # ronda index de último descanso (evitar consecutivos)
    parejas_formadas = Counter()  # conteo de veces que dos jugadores fueron pareja
    enfrentamientos_cubiertos = set()

    rondas: List[Dict[str, Any]] = []
    ronda_idx = 0

    # función de scoring para elegir quad de 4
    def score_quad(quad: List[str], partitions: List[Tuple[Tuple[str,str], Tuple[str,str]]]):
        """Devuelve mejor (score, (p1,p2), valid_dict)."""
        best = (-1e9, None, None)
        for p1, p2 in partitions:
            # cuanto nuevo cubre (enfrentamiento entre jugadores de parejas opuestas)
            new_cover = 0
            for a in p1:
                for b in p2:
                    pair = tuple(sorted((a,b)))
                    if pair not in enfrentamientos_cubiertos:
                        new_cover += 1
            # penalizar repeticiones de pareja
            pair_penalty = 0
            for pair_in in (itertools.combinations(p1,2) if len(p1)==2 else []):
                pair_penalty += parejas_formadas[tuple(sorted(pair_in))]
            for pair_in in (itertools.combinations(p2,2) if len(p2)==2 else []):
                pair_penalty += parejas_formadas[tuple(sorted(pair_in))]
            # balance partidos_jugados: preferir jugadores con menos partidos válidos
            worst_count = max(partidos_jugados[a] for a in p1 + p2)
            sum_counts = sum(partidos_jugados[a] for a in p1 + p2)
            # score compone prioridades: nuevo enfrentamiento > baja carga de partidos > evitar parejas repetidas
            score = (10 * new_cover) - (1.5 * sum_counts) - (5 * pair_penalty) - (2 * worst_count)
            # return candidate
            valido_dict = {pl: True for pl in p1 + p2}  # por defecto válidos; ayudantes fijados fuera
            if score > best[0]:
                best = (score, (tuple(p1), tuple(p2)), valido_dict)
        return best  # (score, (p1,p2), valido_dict)

    # función auxiliar para seleccionar ayudantes cuando faltan jugadores
    def select_ayudantes(need: int, disponibles: set, ronda_actual):
        """
        Selecciona 'need' ayudantes prefiriendo jugadores con más partidos válidos
        y que no hayan descansado excesivamente. Marcarán como no válidos.
        """
        candidatos = [g for g in jugadores if g not in disponibles]
        # ordenar por: más partidos válidos (para que no pierdan igualdad), y preferir los que descansaron menos
        candidatos_sorted = sorted(candidatos, key=lambda g: (-partidos_jugados[g], descansos[g], ronda_actual - descansos_ult_ronda.get(g, -100)))
        return candidatos_sorted[:need]

    # límite de iteraciones para evitar ciclo infinito
    max_round_iters = max_total_rounds

    while ronda_idx < max_round_iters:
        ronda_idx += 1
        disponibles = set(jugadores)
        # ordenar por menos partidos válidos y menos descansos
        jugadores_ordenados = sorted(disponibles, key=lambda g: (partidos_jugados[g], descansos[g], parejas_formadas.get(g, 0)))
        # decidir cuántos descansos deben ocurrir esta ronda para mantener equilibrio y evitar consecutivos
        sobrantes = len(disponibles) % 4
        descansan: List[str] = []

        if sobrantes > 0:
            # elegir quienes descansan: los que menos descansos tienen y que no descansaron en la ronda anterior (evitar consecutivos)
            min_desc = min(descansos.values()) if descansos else 0
            candidatos = [j for j in disponibles if descansos[j] == min_desc and (ronda_idx - descansos_ult_ronda.get(j, -100) > 0)]
            # si no alcanzan, relajar criterio
            if len(candidatos) < sobrantes:
                candidatos = [j for j in disponibles if descansos[j] == min_desc]
            random.shuffle(candidatos)
            descansan = candidatos[:sobrantes]
            for j in descansan:
                descansos[j] += 1
                descansos_ult_ronda[j] = ronda_idx
            disponibles -= set(descansan)

        partidos_ronda = []
        # armar matches por cancha
        for cancha_idx in range(num_canchas):
            if len(disponibles) >= 4:
                candidatos = list(disponibles)
                # probamos varios cuartetos al azar y los puntuamos
                best_quad = None
                best_score = -1e9
                trials = min(80, max(20, len(candidatos)))
                for _ in range(trials):
                    quad = random.sample(candidatos, 4)
                    partitions = [
                        ((quad[0], quad[1]), (quad[2], quad[3])),
                        ((quad[0], quad[2]), (quad[1], quad[3])),
                        ((quad[0], quad[3]), (quad[1], quad[2])),
                    ]
                    sc, qp, vdict = score_quad(quad, partitions)
                    if sc > best_score:
                        best_score = sc
                        best_quad = (qp, vdict)
                if best_quad is None:
                    take = list(disponibles)[:4]
                    p1 = (take[0], take[1])
                    p2 = (take[2], take[3])
                    valido_dict = {pl: True for pl in p1 + p2}
                else:
                    (p1, p2), valido_dict = best_quad

                partidos_ronda.append({
                    "cancha": cancha_idx + 1,
                    "pareja1": tuple(p1),
                    "pareja2": tuple(p2),
                    "ayudantes": [],
                    "valido_para": valido_dict
                })
                disponibles -= set(p1) | set(p2)

            else:
                # faltan jugadores para completar cancha
                if len(disponibles) == 0:
                    break
                needed = 4 - len(disponibles)
                # selección de ayudantes
                ayudantes = select_ayudantes(needed, disponibles, ronda_idx)
                take4 = list(disponibles) + ayudantes
                # cortar por si hay exceso
                take4 = take4[:4]
                p1 = (take4[0], take4[1])
                p2 = (take4[2], take4[3])

                valido_dict = {}
                for pl in p1 + p2:
                    valido_dict[pl] = (pl not in ayudantes)

                partidos_ronda.append({
                    "cancha": cancha_idx + 1,
                    "pareja1": tuple(p1),
                    "pareja2": tuple(p2),
                    "ayudantes": list(ayudantes),
                    "valido_para": valido_dict
                })
                # eliminar disponibles y también (no los ayudantes porque estaban fuera de disponibles)
                disponibles -= set([p for p in (p1 + p2) if p in disponibles])

        # asignar descansos para los que no se usaron en la ronda
        # los que quedaron en 'disponibles' son exactamente quienes no jugaron (no incluyen los que ya seleccionamos como descansos)
        no_usados = list(disponibles)
        for j in no_usados:
            descansos[j] += 1
            descansos_ult_ronda[j] = ronda_idx
        descansan += no_usados

        # actualizar estructuras: enfrentamientos, partidos válidos, parejas_formadas
        for partido in partidos_ronda:
            p1 = tuple(partido["pareja1"])
            p2 = tuple(partido["pareja2"])
            # registrar parejas formadas (dentro de cada pareja)
            for pair_in in itertools.combinations(p1, 2):
                parejas_formadas[tuple(sorted(pair_in))] += 1
            for pair_in in itertools.combinations(p2, 2):
                parejas_formadas[tuple(sorted(pair_in))] += 1

            # registrar enfrentamientos cubiertos solo si al menos uno de los dos en el par tiene valido True
            for a in p1:
                for b in p2:
                    pair = tuple(sorted((a, b)))
                    # si ambos son ayudantes y por tanto no válidos, no cuentan
                    if not (partido["valido_para"].get(a, False) or partido["valido_para"].get(b, False)):
                        continue
                    enfrentamientos_cubiertos.add(pair)

            for pl, valido in partido["valido_para"].items():
                if valido:
                    partidos_jugados[pl] += 1

        rondas.append({
            "ronda": ronda_idx,
            "partidos": partidos_ronda,
            "descansan": descansan
        })

        # condición para cortar anticipadamente si ya cubrimos pares y además tenemos igualdad razonable
        if enfrentamientos_cubiertos == todos_pares:
            # intentar balancear partidos válidos: si hay diferencias pequeñas, es tolerable
            if not (n == 8 and num_canchas == 2):
                break

    # si no se alcanzó en target rounds, permitir una ronda más hasta max_total_rounds
    # (el while ya limita con max_round_iters)

    # preparar resumen
    resumen_df = pd.DataFrame({
        "jugador": jugadores,
        "partidos_jugados": [partidos_jugados[j] for j in jugadores],
        "descansos": [descansos[j] for j in jugadores]
    }).sort_values(by=["partidos_jugados", "descansos"], ascending=[False, True]).reset_index(drop=True)

    meta_alcanzada = (enfrentamientos_cubiertos == todos_pares)
    return {
        "rondas": rondas,
        "enfrentamientos_cubiertos": enfrentamientos_cubiertos,
        "todos_pares": todos_pares,
        "meta_alcanzada": meta_alcanzada,
        "partidos_jugados": dict(partidos_jugados),
        "descansos": dict(descansos),
        "resumen": resumen_df
    }
