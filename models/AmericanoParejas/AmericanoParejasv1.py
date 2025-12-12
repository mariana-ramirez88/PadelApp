import pandas as pd
from typing import List, Dict, Any, Tuple
from collections import deque
import math
import itertools

class FixedPairsTournament:
    def __init__(self, pairs: List[str], num_fields: int):
        self.num_fields = num_fields
        self.team_names = [
            p.replace("-", " & ") if "-" in p else p
            for p in pairs
        ]
        
    def generate_schedule(self) -> Dict[str, Any]:
        """
        1. Genera la secuencia completa de partidos (Round Robin).
        2. Asigna partidos a Rondas Logísticas fijas (tamaño = num_fields) 
           usando un algoritmo Codicioso para evitar la repetición de equipos.
        """
        teams = self.team_names.copy()
        
        # 1. Preparación y Generación de la Secuencia (Método del Círculo)
        # Esto genera todos los 15 partidos en un orden equilibrado.
        is_odd = len(teams) % 2 != 0
        if is_odd:
            teams.append("BYE") 
            
        n = len(teams)
        total_rounds_math = n - 1
        fixed_team = teams[0]
        rotating_teams = deque(teams[1:]) 
        
        all_matches_sequence = []
        
        for r in range(total_rounds_math):
            # 1. Fijo vs Rotador
            t1_fixed = fixed_team
            t2_fixed = rotating_teams[0]
            if "BYE" not in (t1_fixed, t2_fixed):
                all_matches_sequence.append((t1_fixed, t2_fixed))
            
            # 2. Rotadores entre sí
            num_rotating = len(rotating_teams)
            half_rotating = num_rotating // 2 
            
            for i in range(1, half_rotating + 1):
                t1 = rotating_teams[i] 
                t2 = rotating_teams[num_rotating - i] 
                
                if "BYE" not in (t1, t2):
                    if r % 2 == 0:
                         all_matches_sequence.append((t1, t2))
                    else:
                         all_matches_sequence.append((t2, t1))

            rotating_teams.rotate(1)
            
        # --- FASE 3: Creación de Rondas Logísticas con Asignación Codiciosa ---
        
        formatted_rounds = []
        ronda_counter = 1
        all_teams_names = set(self.team_names)
        
        # Creamos una lista mutable de los partidos pendientes
        matches_pendientes = all_matches_sequence.copy()
        
        # Iteramos mientras queden partidos por asignar
        while matches_pendientes:
            
            matches_in_this_round = []
            current_playing_teams = set()
            indices_a_remover = [] # Usamos esto para marcar los partidos asignados
            
            # Intentar llenar las canchas (algoritmo codicioso)
            for c_i in range(self.num_fields):
                
                match_asignado = None
                
                # 1. Buscar el primer partido disponible que no cause conflicto
                for idx_pend, match in enumerate(matches_pendientes):
                    team1, team2 = match
                    
                    # Chequeo de conflicto: ¿Alguno de los equipos ya está jugando en esta ronda?
                    if team1 not in current_playing_teams and team2 not in current_playing_teams:
                        # Partido encontrado y sin conflicto
                        match_asignado = match
                        # Guardamos el índice para removerlo después (no podemos modificar la lista mientras iteramos)
                        indices_a_remover.append(idx_pend)
                        break
                
                # 2. Asignar si se encontró un partido
                if match_asignado:
                    team1, team2 = match_asignado
                    
                    matches_in_this_round.append({
                        "cancha": c_i + 1,
                        "pareja1": team1,
                        "pareja2": team2,
                        "turno": 1 
                    })
                    
                    current_playing_teams.add(team1)
                    current_playing_teams.add(team2)
                else:
                    # Si no encontramos más partidos sin conflicto, rompemos el loop de canchas
                    break 

            # 3. Remover los partidos asignados de matches_pendientes
            # Debemos remover de mayor a menor índice para no alterar los índices restantes
            indices_a_remover.sort(reverse=True)
            for idx in indices_a_remover:
                del matches_pendientes[idx]

            # 4. Finalizar la Ronda Logística
            if matches_in_this_round:
                resting_teams = list(all_teams_names - current_playing_teams)
                
                formatted_rounds.append({
                    "ronda": ronda_counter,
                    "partidos": matches_in_this_round,
                    "descansan": resting_teams
                })
                ronda_counter += 1

        return self._format_output(formatted_rounds)

    def _format_output(self, rounds: List[Dict]) -> Dict[str, Any]:
        """Genera estructura compatible con tu frontend (sin cambios)"""
        games_played = {team: 0 for team in self.team_names}
        
        for r in rounds:
            for match in r['partidos']:
                if match['pareja1'] in games_played:
                    games_played[match['pareja1']] += 1
                if match['pareja2'] in games_played:
                    games_played[match['pareja2']] += 1
                
        resumen_df = pd.DataFrame([
            {"equipo": k, "partidos_jugados": v} for k, v in games_played.items()
        ])
        
        return {
            "rondas": rounds,
            "resumen": resumen_df,
            "stats": {
                "total_rounds": len(rounds),
                "players_count": len(self.team_names),
                "fields": self.num_fields
            }
        }