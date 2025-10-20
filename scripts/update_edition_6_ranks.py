"""
Script pour mettre à jour les rangs des joueurs de l'édition 6 depuis le CSV
"""

import json
import csv
from pathlib import Path

# Mapping des rangs du CSV vers le format Riot API
TIER_MAPPING = {
    "Iron": "IRON",
    "Bronze": "BRONZE",
    "Silver": "SILVER",
    "Gold": "GOLD",
    "Platine": "PLATINUM",
    "Emeraude": "EMERALD",
    "Diamant": "DIAMOND",
    "Master": "MASTER",
    "Grandmaster": "GRANDMASTER",
    "Challenger": "CHALLENGER"
}

# Mapping des rôles CSV vers JSON
ROLE_MAPPING = {
    "Top": "TOP",
    "Jungle": "JGL",
    "Mid": "MID",
    "Adc": "ADC",
    "Supp": "SUP"
}

def parse_elo(elo_str):
    """Parse une chaîne d'elo du CSV et retourne tier, rank, lp"""
    if not elo_str or elo_str.strip() == "":
        return "UNRANKED", "IV", 0
    
    elo_str = elo_str.strip()
    
    # Cas Master/Grandmaster/Challenger avec LP entre parenthèses
    if "(" in elo_str and ")" in elo_str:
        tier_name = elo_str.split("(")[0].strip()
        lp = int(elo_str.split("(")[1].split(")")[0].strip())
        tier = TIER_MAPPING.get(tier_name, "UNRANKED")
        return tier, "I", lp
    
    # Cas rangs normaux (Iron à Diamond/Emerald)
    tier = TIER_MAPPING.get(elo_str, "UNRANKED")
    return tier, "IV", 0

def main():
    # Chemins
    csv_path = Path(r"c:\Users\alexc\Desktop\Occi'lan #6 - OPGG Adversaires.csv")
    json_path = Path("data/editions/edition_6/teams_with_puuid.json")
    
    # Lecture du CSV
    teams_elo = {}
    current_team = None
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0]:
                continue
            
            # Détection d'une nouvelle équipe
            if row[0] == "Equipe :":
                current_team = row[1].strip()
                teams_elo[current_team] = {}
            
            # Ligne des rôles
            elif row[0] == "Role :" and current_team:
                roles = [ROLE_MAPPING.get(r.strip(), r.strip()) for r in row[1:6] if r.strip()]
            
            # Ligne des pseudos (ignorée pour l'édition 6, on garde ceux du JSON)
            elif row[0] == "Pseudo :" and current_team:
                pass
            
            # Ligne des elos
            elif row[0] == "Elo :" and current_team:
                elos = row[1:6]
                for i, (role, elo) in enumerate(zip(roles, elos)):
                    if elo and elo.strip():
                        teams_elo[current_team][role] = elo.strip()
    
    # Lecture du JSON actuel
    with open(json_path, 'r', encoding='utf-8') as f:
        teams_data = json.load(f)
    
    # Mise à jour des rangs
    updated_count = 0
    for team_name, team_data in teams_data.items():
        if team_name not in teams_elo:
            print(f"⚠️  Équipe '{team_name}' non trouvée dans le CSV")
            continue
        
        print(f"\n📊 Mise à jour de l'équipe : {team_name}")
        
        for player in team_data["players"]:
            role = player["role"]
            
            if role in teams_elo[team_name]:
                elo_str = teams_elo[team_name][role]
                tier, rank, lp = parse_elo(elo_str)
                
                # Mise à jour des données
                player["tier"] = tier
                player["rank"] = rank
                player["leaguePoints"] = lp
                
                # Ajouter summonerLevel et profileIconId si absents (valeurs par défaut)
                if "summonerLevel" not in player:
                    player["summonerLevel"] = 100  # Valeur par défaut
                if "profileIconId" not in player:
                    player["profileIconId"] = 29  # Icône par défaut
                
                # Supprimer les anciens champs s'ils existent
                if "division" in player:
                    del player["division"]
                if "lp" in player:
                    del player["lp"]
                
                # Calculer le winrate si on a wins et losses (sinon mettre à 0)
                if "wins" not in player:
                    player["wins"] = 0
                if "losses" not in player:
                    player["losses"] = 0
                
                total = player["wins"] + player["losses"]
                player["winrate"] = round((player["wins"] / total * 100), 2) if total > 0 else 0.0
                
                print(f"  ✅ {player['gameName']}#{player['tagLine']} ({role}): {elo_str} → {tier} {rank} {lp}LP")
                updated_count += 1
            else:
                print(f"  ⚠️  Rôle {role} non trouvé pour {player['gameName']}")
    
    # Sauvegarde du JSON mis à jour
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(teams_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Mise à jour terminée ! {updated_count} joueurs mis à jour.")
    print(f"📝 Fichier sauvegardé : {json_path}")

if __name__ == "__main__":
    main()
