import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import json
import os

def format_duration(minutes):
    """Convertit les minutes en format MM:SS"""
    total_minutes = int(minutes)
    seconds = int((minutes - total_minutes) * 60)
    return f"{total_minutes}:{seconds:02d}"

def create_records_sheet(wb, general_stats):
    """Crée la feuille avec les records du tournoi"""
    ws = wb.create_sheet("Records")
    
    # Styles
    title_font = Font(bold=True, size=12)
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")

    # Titre
    ws['A1'] = "Records du tournoi"
    ws['A1'].font = title_font
    ws.merge_cells('A1:D1')
    ws['A1'].alignment = Alignment(horizontal="center")

    # En-têtes
    headers = ["Statistique", "Joueur", "Équipe", "Valeur"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=2, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    # Records
    row = 3
    stats_mapping = {
        "total_kills": "Plus grand nombre de kills",
        "total_deaths": "Plus grand nombre de morts",
        "total_assists": "Plus grand nombre d'assists",
        "average_kills": "Meilleure moyenne de kills",
        "average_deaths": "Plus faible moyenne de morts",
        "average_assists": "Meilleure moyenne d'assists",
        "average_kda": "Meilleur KDA",
        "average_cs_per_minute": "Meilleur CS/min",
        "average_vision_score": "Meilleur score de vision",
        "unique_champions_played": "Plus de champions joués"
    }

    for stat, display_name in stats_mapping.items():
        if stat in general_stats["records"]:
            record = general_stats["records"][stat]
            ws.cell(row=row, column=1, value=display_name)
            ws.cell(row=row, column=2, value=record["player"])
            ws.cell(row=row, column=3, value=record["team"])
            ws.cell(row=row, column=4, value=record["value"])
            
            # Centre les cellules
            for col in range(1, 5):
                ws.cell(row=row, column=col).alignment = Alignment(horizontal="center")
            row += 1

    # Ajuste la largeur des colonnes
    for col in range(1, 5):
        ws.column_dimensions[get_column_letter(col)].width = 25

def create_team_sheet(wb, team_name: str, team_data: dict):
    """Crée une feuille pour une équipe spécifique"""
    ws = wb.create_sheet(team_name[:31])
    
    # Styles
    title_font = Font(bold=True, size=12)
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")

    # Stats globales de l'équipe
    ws['A1'] = f"Statistiques de {team_name}"
    ws['A1'].font = title_font
    ws.merge_cells('A1:H1')
    ws['A1'].alignment = Alignment(horizontal="center")

    # Stats de l'équipe
    team_stats = team_data["team_stats"]
    stats_row = 3
    team_stats_data = [
        ("Matchs joués", team_stats["total_games"]),
        ("Victoires", team_stats["wins"]),
        ("Défaites", team_stats["losses"]),
        ("Winrate", f"{team_stats['winrate']}%"),
        ("Durée moyenne", format_duration(team_stats["average_game_duration"])),
        ("Plus court", format_duration(team_stats["shortest_game"])),
        ("Plus long", format_duration(team_stats["longest_game"]))
    ]

    for stat, value in team_stats_data:
        ws.cell(row=stats_row, column=1, value=stat)
        ws.cell(row=stats_row, column=2, value=value)
        stats_row += 1

    # Stats des joueurs
    players_row = stats_row + 2
    ws.cell(row=players_row, column=1, value="Statistiques des joueurs")
    ws.cell(row=players_row, column=1).font = title_font
    
    # En-têtes des stats joueurs
    headers = ["Joueur", "KDA", "Kills/G", "Deaths/G", "Assists/G", "CS/min", "Vision/G", "Champions"]
    players_row += 1
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=players_row, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    # Données des joueurs
    for player_name, player_stats in team_data["players"].items():
        players_row += 1
        player_data = [
            player_name,
            player_stats["average_kda"],
            player_stats["average_kills"],
            player_stats["average_deaths"],
            player_stats["average_assists"],
            player_stats["average_cs_per_minute"],
            player_stats["average_vision_score"],
            ", ".join(player_stats["champions_played"])
        ]
        
        for col, value in enumerate(player_data, 1):
            cell = ws.cell(row=players_row, column=col, value=value)
            if col < len(player_data):  # Ne pas centrer la dernière colonne (champions)
                cell.alignment = Alignment(horizontal="center")

    # Ajuste la largeur des colonnes
    ws.column_dimensions['A'].width = 20  # Joueur
    for col in range(2, 8):
        ws.column_dimensions[get_column_letter(col)].width = 12
    ws.column_dimensions['H'].width = 40  # Champions

def create_excel(team_stats: dict, general_stats: dict, output_path: str):
    """Crée le fichier Excel complet"""
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Supprime la feuille par défaut

    # Crée la feuille des records
    create_records_sheet(wb, general_stats)
    
    # Crée une feuille par équipe
    for team_name, team_data in team_stats.items():
        create_team_sheet(wb, team_name, team_data)
    
    wb.save(output_path)
    print(f"Fichier Excel créé avec succès : {output_path}")

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, "../data")
    output_dir = os.path.join(current_dir, "../output")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Charge les données
    team_stats_path = os.path.join(data_dir, "team_stats.json")
    general_stats_path = os.path.join(data_dir, "general_stats.json")
    excel_output_path = os.path.join(output_dir, "OccilanStats.xlsx")
    
    with open(team_stats_path, "r", encoding="utf-8") as f:
        team_stats = json.load(f)
    with open(general_stats_path, "r", encoding="utf-8") as f:
        general_stats = json.load(f)
    
    create_excel(team_stats, general_stats, excel_output_path)