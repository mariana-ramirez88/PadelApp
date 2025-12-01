import random
from itertools import combinations, product
from collections import defaultdict
import pandas as pd
from typing import List, Dict, Any, Tuple, Set

class AmericanoMixtoTournament:
    def __init__(self, male_players: List[str], female_players: List[str], num_fields: int):
        """
        Initialize Americano Mixed Padel Tournament
        
        Args:
            male_players: List of male player names
            female_players: List of female player names (must be equal to males)
            num_fields: Number of available padel fields
        """
        if len(male_players) != len(female_players):
            raise ValueError("Debe haber el mismo número de hombres y mujeres")
        
        self.male_players = male_players
        self.female_players = female_players
        self.num_males = len(male_players)
        self.num_females = len(female_players)
        self.num_fields = num_fields
        self.all_players = male_players + female_players
        
        # Gender mapping
        self.gender = {}
        for m in male_players:
            self.gender[m] = 'M'
        for f in female_players:
            self.gender[f] = 'F'
        
        # Statistics tracking
        self.mixed_partner_count = defaultdict(int)  # (male, female) pairs
        self.opponent_count = defaultdict(lambda: defaultdict(int))
        self.total_games_played = defaultdict(int)
        self.consecutive_rests = defaultdict(int)
        self.last_round_played = defaultdict(lambda: -1)
        
    def calculate_optimal_rounds(self) -> int:
        """
        Calculate optimal rounds for mixed tournament
        
        OBJETIVO: Cada mujer debe ser pareja de cada hombre al menos una vez
        
        Total de parejas mixtas únicas = num_males × num_females
        Parejas formadas por ronda = num_fields × 2
        Rondas mínimas = ceil(parejas_totales ÷ parejas_por_ronda)
        
        Ejemplos:
        - 5H + 5M con 2 canchas: 25 parejas ÷ 4 = 6.25 → 7 rondas
        - 4H + 4M con 2 canchas: 16 parejas ÷ 4 = 4 rondas
        """
        total_mixed_pairs = self.num_males * self.num_females
        pairs_per_round = self.num_fields * 2
        
        # Redondear hacia arriba para cubrir todas las parejas
        optimal_rounds = (total_mixed_pairs + pairs_per_round - 1) // pairs_per_round
        
        return optimal_rounds
    
    def get_uncovered_mixed_pairs(self) -> Set[Tuple[str, str]]:
        """Get list of (male, female) pairs that haven't partnered yet"""
        all_pairs = set(product(self.male_players, self.female_players))
        covered = set(self.mixed_partner_count.keys())
        return all_pairs - covered
    
    def count_uncovered_partners(self, player: str) -> int:
        """Count how many potential partners this player hasn't played with"""
        if self.gender[player] == 'M':
            potential = self.female_players
            return sum(1 for f in potential if self.mixed_partner_count[(player, f)] == 0)
        else:
            potential = self.male_players
            return sum(1 for m in potential if self.mixed_partner_count[(m, player)] == 0)
    
    def get_match_score(self, match: Tuple[str, str, str, str], round_num: int) -> float:
        """
        Score a potential match for mixed tournament
        Lower score is better
        
        Match format: (male1, female1, male2, female2)
        Teams: (male1 & female1) vs (male2 & female2)
        """
        m1, f1, m2, f2 = match
        score = 0.0
        
        # PRIORIDAD 1: Maximizar parejas mixtas NUEVAS (CRÍTICO)
        pair1 = (m1, f1)
        pair2 = (m2, f2)
        
        # Recompensa masiva por parejas no usadas
        if self.mixed_partner_count[pair1] == 0:
            score -= 10000
        else:
            score += self.mixed_partner_count[pair1] * 8000
        
        if self.mixed_partner_count[pair2] == 0:
            score -= 10000
        else:
            score += self.mixed_partner_count[pair2] * 8000
        
        # PRIORIDAD 2: Balance de partidos jugados
        games_sum = sum(self.total_games_played[p] for p in match)
        score += games_sum * 500
        
        # Penalizar diferencias grandes
        games_list = [self.total_games_played[p] for p in match]
        variance = max(games_list) - min(games_list)
        score += variance * 300
        
        # PRIORIDAD 3: Nuevos enfrentamientos
        opponents = [(m1, m2), (m1, f2), (f1, m2), (f1, f2)]
        for opp1, opp2 in opponents:
            opp_count = self.opponent_count[opp1][opp2]
            if opp_count == 0:
                score -= 800
            else:
                score += opp_count * 400
        
        # PRIORIDAD 4: Evitar descansos consecutivos
        for p in match:
            if self.last_round_played[p] == round_num - 1:
                score -= 200
            elif self.last_round_played[p] < round_num - 1:
                score += 150
        
        return score
    
    def generate_all_possible_matches(self, available_males: List[str], 
                                     available_females: List[str]) -> List[Tuple]:
        """Generate all possible match configurations"""
        if len(available_males) < 2 or len(available_females) < 2:
            return []
        
        possible_matches = []
        
        # Try all combinations of 2 males and 2 females
        for m1, m2 in combinations(available_males, 2):
            for f1, f2 in combinations(available_females, 2):
                # Two possible configurations
                possible_matches.append((m1, f1, m2, f2))
                possible_matches.append((m1, f2, m2, f1))
        
        return possible_matches
    
    def generate_round_matches(self, round_num: int) -> Tuple[List[Dict], List[str]]:
        """Generate matches for a round prioritizing uncovered pairs"""
        matches = []
        
        # Get uncovered pairs
        uncovered = self.get_uncovered_mixed_pairs()
        
        # If all pairs are covered, we're done
        if not uncovered:
            return [], self.all_players
        
        # Find players that need more coverage
        males_priority = sorted(self.male_players, 
                               key=lambda m: (self.total_games_played[m], 
                                            -self.count_uncovered_partners(m)))
        females_priority = sorted(self.female_players,
                                 key=lambda f: (self.total_games_played[f],
                                              -self.count_uncovered_partners(f)))
        
        remaining_males = set(males_priority)
        remaining_females = set(females_priority)
        
        for field_idx in range(self.num_fields):
            if len(remaining_males) < 2 or len(remaining_females) < 2:
                break
            
            # Generate all possible matches with remaining players
            possible_matches = self.generate_all_possible_matches(
                list(remaining_males), 
                list(remaining_females)
            )
            
            if not possible_matches:
                break
            
            # Score and select best match
            best_match = None
            best_score = float('inf')
            
            for match_config in possible_matches:
                score = self.get_match_score(match_config, round_num)
                if score < best_score:
                    best_score = score
                    best_match = match_config
            
            if best_match:
                m1, f1, m2, f2 = best_match
                matches.append({
                    "players": (m1, f1, m2, f2),
                    "field": field_idx
                })
                
                # Remove used players
                remaining_males.discard(m1)
                remaining_males.discard(m2)
                remaining_females.discard(f1)
                remaining_females.discard(f2)
        
        # Resting players
        resting = list(remaining_males | remaining_females)
        return matches, resting
    
    def update_statistics(self, match: Dict, round_num: int):
        """Update tracking statistics after a match"""
        m1, f1, m2, f2 = match["players"]
        
        # Update mixed partnerships
        pair1 = (m1, f1)
        pair2 = (m2, f2)
        self.mixed_partner_count[pair1] += 1
        self.mixed_partner_count[pair2] += 1
        
        # Update opponents
        team1 = [m1, f1]
        team2 = [m2, f2]
        
        for t1_player in team1:
            for t2_player in team2:
                self.opponent_count[t1_player][t2_player] += 1
                self.opponent_count[t2_player][t1_player] += 1
        
        # Update total games played
        for p in [m1, f1, m2, f2]:
            self.total_games_played[p] += 1
            self.last_round_played[p] = round_num
    
    def identify_helpers(self, tournament_schedule: List[List[Dict]]) -> Dict[str, List[Tuple[int, int]]]:
        """
        Identify helpers AFTER tournament generation
        
        RULE: Valid games = MINIMUM games played by any player
        Players who played MORE than minimum → extra games are as helper
        """
        if not self.total_games_played:
            return {}
        
        min_games = min(self.total_games_played.values())
        helpers = defaultdict(list)
        
        # For each player who played MORE than minimum
        for player in self.all_players:
            if self.total_games_played[player] > min_games:
                extra_games = self.total_games_played[player] - min_games
                
                # Mark their LAST N games as helper games
                games_found = 0
                for round_num in range(len(tournament_schedule) - 1, -1, -1):
                    for field_idx, match in enumerate(tournament_schedule[round_num]):
                        if player in match["players"]:
                            games_found += 1
                            if games_found <= extra_games:
                                helpers[player].append((round_num, field_idx))
                            if games_found >= extra_games:
                                break
                    if games_found >= extra_games:
                        break
        
        return helpers
    
    def generate_tournament(self) -> Tuple[List[List[Dict]], Dict, Dict]:
        """Generate complete mixed tournament schedule"""
        optimal_rounds = self.calculate_optimal_rounds()
        tournament_schedule = []
        
        for round_num in range(optimal_rounds):
            matches, resting = self.generate_round_matches(round_num)
            
            # If no matches possible, stop
            if not matches:
                # Check if we've covered all pairs
                uncovered = self.get_uncovered_mixed_pairs()
                if uncovered:
                    # Still have uncovered pairs - continue
                    continue
                else:
                    break
            
            tournament_schedule.append(matches)
            
            for match in matches:
                self.update_statistics(match, round_num)
            
            # Update consecutive rests
            for p in resting:
                self.consecutive_rests[p] += 1
            for match in matches:
                for p in match["players"]:
                    self.consecutive_rests[p] = 0
        
        # Identify helpers AFTER tournament generation
        helpers = self.identify_helpers(tournament_schedule)
        
        # Calculate statistics
        min_games = min(self.total_games_played.values()) if self.total_games_played else 0
        
        stats = {
            "total_games_played": dict(self.total_games_played),
            "helpers": {p: len(games) for p, games in helpers.items()},
            "valid_games_target": min_games,
            "mixed_pairs_covered": len(self.mixed_partner_count),
            "total_mixed_pairs": self.num_males * self.num_females,
            "coverage_percentage": (len(self.mixed_partner_count) / (self.num_males * self.num_females)) * 100,
            "total_rounds_played": len(tournament_schedule),
            "uncovered_pairs": list(self.get_uncovered_mixed_pairs())
        }
        
        return tournament_schedule, helpers, stats
    
    def format_for_streamlit(self, tournament_schedule: List[List[Dict]], 
                            helpers: Dict, stats: Dict) -> Dict[str, Any]:
        """Format tournament output for Streamlit visualization"""
        rondas = []
        
        for round_num, matches in enumerate(tournament_schedule, 1):
            playing = set()
            for match in matches:
                playing.update(match["players"])
            descansan = [p for p in self.all_players if p not in playing]
            
            partidos = []
            for field_idx, match in enumerate(matches):
                m1, f1, m2, f2 = match["players"]
                
                # Determine helpers for this specific match
                match_helpers = []
                valido_para = [m1, f1, m2, f2]
                
                for player in [m1, f1, m2, f2]:
                    if player in helpers:
                        for helper_round, helper_field in helpers[player]:
                            if helper_round == round_num - 1 and helper_field == field_idx:
                                match_helpers.append(player)
                                valido_para.remove(player)
                                break
                
                partido = {
                    "cancha": field_idx + 1,
                    "pareja1": [m1, f1],
                    "pareja2": [m2, f2],
                    "ayudantes": match_helpers,
                    "valido_para": valido_para
                }
                partidos.append(partido)
            
            ronda_data = {
                "ronda": round_num,
                "partidos": partidos,
                "descansan": descansan
            }
            rondas.append(ronda_data)
        
        # Create summary DataFrame
        resumen_data = []
        min_games = stats["valid_games_target"]
        
        for player in self.all_players:
            total_games = self.total_games_played[player]
            helper_games_count = len(helpers.get(player, []))
            valid_games = total_games - helper_games_count
            genero = "Hombre" if self.gender[player] == 'M' else "Mujer"
            
            resumen_data.append({
                "Jugador": player,
                "Género": genero,
                "Partidos Totales": total_games,
                "Partidos Válidos": valid_games,
                "Partidos Ayudante": helper_games_count
            })
        
        output = {
            "rondas": rondas,
            "resumen": resumen_data,
            "stats": stats
        }
        
        return output


def generar_torneo_mixto(male_players: List[str], female_players: List[str], 
                         num_canchas: int, puntos_partido: int = 32, 
                         seed: int = None) -> Dict[str, Any]:
    """
    Main function to generate mixed tournament
    
    OBJETIVO: Cada mujer juega con cada hombre al menos una vez
    
    Args:
        male_players: List of male player names
        female_players: List of female player names (equal length)
        num_canchas: Number of fields/courts available
        puntos_partido: Points per match (not used in algorithm, for reference)
        seed: Random seed for reproducibility
    
    Returns:
        Dictionary with:
        - 'rondas': List of rounds with matches
        - 'resumen': Summary statistics per player
        - 'stats': Tournament statistics including coverage
    """
    if seed:
        random.seed(seed)
    
    tournament = AmericanoMixtoTournament(male_players, female_players, num_canchas)
    schedule, helpers, stats = tournament.generate_tournament()
    return tournament.format_for_streamlit(schedule, helpers, stats)