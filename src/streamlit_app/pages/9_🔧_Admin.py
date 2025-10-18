"""
Admin page for OcciLan Stats
Manage teams and trigger data processing pipeline
"""

import streamlit as st
import pandas as pd
import os
from pathlib import Path
import sys
import io

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.data_manager import EditionDataManager, MultiEditionManager
from src.parsers.opgg_parser import OPGGParser
from src.pipeline.edition_processor import EditionProcessor
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(page_title="Admin - OcciLan Stats", page_icon="🔧", layout="wide")

# Custom CSS pour masquer la navigation par défaut
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - Navigation cohérente (AVANT l'authentification)
# ============================================================================

with st.sidebar:
    st.markdown("### 📂 Sélection d'édition")
    
    multi_manager_sidebar = MultiEditionManager()
    available_editions_sidebar = multi_manager_sidebar.list_editions(include_private=True)
    
    if not available_editions_sidebar:
        st.info("💡 Créez votre première édition ci-dessous")
        selected_edition_sidebar = None
    else:
        selected_edition_sidebar = st.selectbox(
            "Édition",
            available_editions_sidebar,
            format_func=lambda x: f"Edition {x}",
            label_visibility="collapsed",
            key="sidebar_edition_selector"
        )
        
        if selected_edition_sidebar:
            edition_manager_sidebar = EditionDataManager(selected_edition_sidebar)
            config_sidebar = edition_manager_sidebar.load_config()
            
            if config_sidebar:
                st.markdown(f"**{config_sidebar.get('name', 'N/A')}**")
                st.caption(f"📆 {config_sidebar.get('start_date', 'N/A')} → {config_sidebar.get('end_date', 'N/A')}")
    
    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    st.page_link("app.py", label="🏠 Accueil")
    st.page_link("pages/1_📊_Stats_Generales.py", label="📊 Stats Générales")
    st.page_link("pages/2_Liste_des_Matchs.py", label="📋 Liste des Matchs")
    st.page_link("pages/3_Stats_Equipes.py", label="🏆 Stats Équipes")
    st.page_link("pages/4_Stats_Joueurs.py", label="👤 Stats Joueurs")
    st.page_link("pages/5_Recherche.py", label="🔍 Recherche")
    st.page_link("pages/9_🔧_Admin.py", label="🔧 Admin")
    st.markdown("---")
    st.caption("🎮 OcciLan Stats v2.0")

# ============================================================================
# Check authentication (APRÈS la sidebar)
# ============================================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Administration")
    
    with st.form("login_form"):
        password = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Se connecter")
        
        if submit:
            # Simple password check (in production, use proper auth)
            if password == os.getenv("ADMIN_PASSWORD", "admin123"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Mot de passe incorrect")
    
    st.stop()

# Admin interface
st.title("🔧 Administration")
st.markdown("Gestion des équipes et traitement des données")

# Logout button
if st.button("🚪 Déconnexion", type="secondary"):
    st.session_state.authenticated = False
    st.rerun()

# Edition selector
multi_manager = MultiEditionManager()
editions = multi_manager.list_editions()

# Section pour créer une nouvelle édition
with st.expander("➕ Créer une nouvelle édition", expanded=False):
    with st.form("create_edition_form"):
        st.markdown("### Nouvelle édition")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculer le prochain numéro d'édition disponible
            next_edition = 1
            if editions:
                # Chercher le premier numéro disponible
                for i in range(1, 1000):
                    if i not in editions:
                        next_edition = i
                        break
            
            new_edition_number = st.number_input(
                "Numéro de l'édition",
                min_value=1,
                max_value=999,
                value=next_edition,
                step=1,
                help="Entrez un numéro d'édition entre 1 et 999"
            )
            edition_name = st.text_input(
                "Nom de l'édition",
                value=f"OcciLan Stats {new_edition_number}"
            )
        
        with col2:
            year = st.number_input(
                "Année",
                min_value=2020,
                max_value=2030,
                value=2025
            )
            is_private = st.checkbox(
                "🔒 Édition privée (visible uniquement par les admins)",
                value=False,
                help="Si cochée, cette édition ne sera pas visible sur la page publique"
            )
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                start_date = st.date_input("Date de début")
            with col_date2:
                end_date = st.date_input("Date de fin")
        
        submit_edition = st.form_submit_button("✅ Créer l'édition", type="primary")
        
        if submit_edition:
            if new_edition_number in editions:
                st.error(f"❌ L'édition {new_edition_number} existe déjà !")
            else:
                try:
                    new_manager = EditionDataManager(new_edition_number)
                    new_manager.initialize_edition(
                        edition_name=edition_name,
                        year=year,
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d"),
                        is_private=is_private
                    )
                    st.success(f"✅ Édition {new_edition_number} créée avec succès !")
                    st.info("🔄 Rechargez la page pour voir la nouvelle édition")
                except Exception as e:
                    st.error(f"❌ Erreur lors de la création : {str(e)}")

if not editions:
    st.warning("⚠️ Aucune édition trouvée. Créez-en une d'abord.")
    st.stop()

selected_edition = st.selectbox(
    "📂 Sélectionner l'édition",
    editions,
    format_func=lambda x: f"Edition {x}"
)

edition_manager = EditionDataManager(selected_edition)

# Afficher les infos de l'édition actuelle
config = edition_manager.load_config()
if config:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 Édition", f"#{selected_edition}")
    with col2:
        st.metric("📝 Nom", config.get("name", "N/A"))
    with col3:
        st.metric("📆 Période", f"{config.get('start_date', 'N/A')} → {config.get('end_date', 'N/A')}")
    with col4:
        is_private = config.get("is_private", False)
        if is_private:
            st.metric("🔒 Visibilité", "Privée")
        else:
            st.metric("🌐 Visibilité", "Publique")

# Section pour modifier/supprimer l'édition
with st.expander("⚙️ Gérer cette édition", expanded=False):
    tab_edit, tab_delete = st.tabs(["✏️ Modifier", "🗑️ Supprimer"])
    
    with tab_edit:
        st.markdown("### Modifier l'édition")
        
        with st.form("edit_edition_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                edit_name = st.text_input(
                    "Nom de l'édition",
                    value=config.get("name", "")
                )
                edit_year = st.number_input(
                    "Année",
                    min_value=2020,
                    max_value=2030,
                    value=config.get("year", 2025)
                )
            
            with col2:
                col_date1, col_date2 = st.columns(2)
                with col_date1:
                    from datetime import datetime
                    start_str = config.get("start_date", "2025-01-01")
                    edit_start = st.date_input(
                        "Date de début",
                        value=datetime.strptime(start_str, "%Y-%m-%d").date()
                    )
                with col_date2:
                    end_str = config.get("end_date", "2025-12-31")
                    edit_end = st.date_input(
                        "Date de fin",
                        value=datetime.strptime(end_str, "%Y-%m-%d").date()
                    )
                
                edit_private = st.checkbox(
                    "🔒 Édition privée (visible uniquement par les admins)",
                    value=config.get("is_private", False),
                    help="Si cochée, cette édition ne sera pas visible sur la page publique"
                )
            
            submit_edit = st.form_submit_button("💾 Enregistrer les modifications", type="primary")
            
            if submit_edit:
                try:
                    # Mettre à jour le config
                    config["name"] = edit_name
                    config["year"] = edit_year
                    config["start_date"] = edit_start.strftime("%Y-%m-%d")
                    config["end_date"] = edit_end.strftime("%Y-%m-%d")
                    config["is_private"] = edit_private
                    
                    edition_manager.save_config(config)
                    st.success("✅ Édition mise à jour avec succès !")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur : {str(e)}")
    
    with tab_delete:
        st.markdown("### Supprimer l'édition")
        st.warning(f"⚠️ **Attention** : Cette action supprimera définitivement l'édition {selected_edition} et toutes ses données !")
        
        st.markdown("""
        **Données qui seront supprimées :**
        - Toutes les équipes
        - Tous les joueurs avec PUUIDs et ranks
        - Tous les matchs sauvegardés
        - Toutes les statistiques calculées
        - La configuration de l'édition
        """)
        
        confirm_text = st.text_input(
            f"Pour confirmer, tapez le numéro de l'édition : **{selected_edition}**",
            key="delete_confirm"
        )
        
        if st.button("🗑️ SUPPRIMER DÉFINITIVEMENT", type="primary", use_container_width=True):
            if confirm_text == str(selected_edition):
                try:
                    import shutil
                    edition_path = edition_manager.edition_path
                    shutil.rmtree(edition_path)
                    st.success(f"✅ Édition {selected_edition} supprimée avec succès !")
                    st.info("🔄 Rechargement de la page...")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de la suppression : {str(e)}")
            else:
                st.error("❌ Confirmation incorrecte. La suppression a été annulée.")

st.markdown("---")

edition_manager = EditionDataManager(selected_edition)

# Tabs for different admin sections
tab1, tab2, tab3 = st.tabs(["➕ Ajouter équipes", "📋 Gérer équipes", "⚙️ Traiter données"])

# ========================
# TAB 1: ADD TEAMS
# ========================
with tab1:
    st.subheader("Ajouter des équipes")
    
    # Option selector
    add_method = st.radio(
        "Méthode d'ajout",
        ["📝 Formulaire manuel", "📤 Upload CSV"],
        horizontal=True
    )
    
    # OPTION 1: MANUAL FORM
    if add_method == "📝 Formulaire manuel":
        st.markdown("---")
        st.info("💡 Les rôles seront assignés dans l'ordre : TOP, JGL, MID, ADC, SUP. Vous pourrez les modifier après dans l'onglet 'Gérer équipes'.")
        
        with st.form("add_team_form"):
            team_name = st.text_input(
                "Nom de l'équipe",
                placeholder="Ex: Les Giga Chads"
            )
            
            opgg_link = st.text_input(
                "Lien OP.GG multisearch",
                placeholder="https://op.gg/fr/lol/multisearch/euw?summoners=Player1-EUW,Player2-EUW,..."
            )
            
            submit_team = st.form_submit_button("✅ Ajouter l'équipe", type="primary")
            
            if submit_team:
                if not team_name or not opgg_link:
                    st.error("❌ Veuillez remplir tous les champs")
                else:
                    # Validate OP.GG link
                    parser = OPGGParser()
                    if not parser.validate_opgg_link(opgg_link):
                        st.error("❌ Lien OP.GG invalide. Format attendu: https://op.gg/.../multisearch/...")
                    else:
                        try:
                            # Parse OP.GG link (returns list of tuples)
                            riot_ids = parser.parse_multisearch_url(opgg_link)
                            
                            if len(riot_ids) != 5:
                                st.error(f"❌ Le lien contient {len(riot_ids)} joueurs, 5 attendus")
                            else:
                                # Show preview
                                st.success(f"✅ 5 joueurs détectés pour l'équipe **{team_name}**")
                                
                                # Default roles (TOP, JGL, MID, ADC, SUP)
                                default_roles = ["TOP", "JGL", "MID", "ADC", "SUP"]
                                
                                preview_data = []
                                for role, (game_name, tag_line) in zip(default_roles, riot_ids):
                                    preview_data.append({
                                        "Rôle": role,
                                        "Pseudo": f"{game_name}#{tag_line}"
                                    })
                                
                                st.dataframe(
                                    pd.DataFrame(preview_data),
                                    width="stretch",
                                    hide_index=True
                                )
                                
                                # Build team data with default roles
                                team_data = {
                                    "opgg_link": opgg_link,
                                    "players": [
                                        {
                                            "role": role,
                                            "gameName": game_name,
                                            "tagLine": tag_line
                                        }
                                        for role, (game_name, tag_line) in zip(default_roles, riot_ids)
                                    ]
                                }
                                
                                # Add team to edition
                                edition_manager.add_team(team_name, team_data)
                                st.success(f"🎉 Équipe **{team_name}** ajoutée avec succès!")
                                st.info("➡️ Allez dans l'onglet 'Gérer équipes' pour modifier les rôles si nécessaire.")
                                
                        except Exception as e:
                            st.error(f"❌ Erreur lors du parsing: {str(e)}")
    
    # OPTION 2: CSV UPLOAD
    else:
        st.markdown("---")
        st.markdown("""
        **Format CSV attendu:**
        - Colonne 1: `team_name` (nom de l'équipe)
        - Colonne 2: `opgg_link` (lien multisearch OP.GG)
        
        Téléchargez le fichier modèle ci-dessous pour un exemple.
        """)
        
        # Download template
        template_df = pd.DataFrame({
            "team_name": ["Exemple Équipe 1", "Exemple Équipe 2"],
            "opgg_link": [
                "https://op.gg/fr/lol/multisearch/euw?summoners=Player1-EUW,Player2-EUW,Player3-EUW,Player4-EUW,Player5-EUW",
                "https://op.gg/fr/lol/multisearch/euw?summoners=Player6-EUW,Player7-EUW,Player8-EUW,Player9-EUW,Player10-EUW"
            ]
        })
        
        csv_template = template_df.to_csv(index=False)
        st.download_button(
            label="📥 Télécharger le modèle CSV",
            data=csv_template,
            file_name="template_teams.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        
        # File upload
        uploaded_file = st.file_uploader(
            "📤 Uploader le CSV avec les équipes",
            type=["csv"],
            help="Le fichier doit contenir les colonnes: team_name, opgg_link"
        )
        
        if uploaded_file is not None:
            try:
                # Read CSV
                df = pd.read_csv(uploaded_file)
                
                # Validate columns
                if "team_name" not in df.columns or "opgg_link" not in df.columns:
                    st.error("❌ Colonnes manquantes. Le CSV doit contenir: team_name, opgg_link")
                else:
                    st.success(f"✅ CSV chargé avec succès: {len(df)} équipes détectées")
                    
                    # Preview
                    st.dataframe(df, width="stretch")
                    
                    if st.button("➕ Ajouter toutes les équipes", type="primary"):
                        parser = OPGGParser()
                        success_count = 0
                        error_count = 0
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, row in df.iterrows():
                            team_name = row["team_name"]
                            opgg_link = row["opgg_link"]
                            
                            status_text.text(f"Traitement: {team_name}...")
                            
                            try:
                                # Validate and parse
                                if not parser.validate_opgg_link(opgg_link):
                                    st.warning(f"⚠️ Lien invalide pour {team_name}, ignoré")
                                    error_count += 1
                                    continue
                                
                                players = parser.parse_multisearch_url(opgg_link)
                                
                                if len(players) < 5:
                                    st.warning(f"⚠️ {team_name}: {len(players)} joueurs (minimum 5 requis), ignoré")
                                    error_count += 1
                                    continue
                                
                                # Si plus de 5 joueurs, prendre les 5 avec le meilleur ELO
                                if len(players) > 5:
                                    st.info(f"ℹ️ {team_name}: {len(players)} joueurs détectés, sélection des 5 meilleurs par ELO...")
                                    
                                    # Récupérer les ranks via l'API
                                    from src.core.riot_client import RiotAPIClient
                                    api_key = os.getenv("RIOT_API_KEY")
                                    
                                    if api_key:
                                        riot_client = RiotAPIClient(api_key)
                                        players_with_rank = []
                                        
                                        for game_name, tag_line in players:
                                            try:
                                                # Get PUUID
                                                account = riot_client.get_account_by_riot_id(game_name, tag_line)
                                                if account:
                                                    puuid = account["puuid"]
                                                    # Get rank
                                                    summoner = riot_client.get_summoner_by_puuid(puuid)
                                                    if summoner:
                                                        rank_info = riot_client.get_ranked_info(summoner["id"])
                                                        
                                                        # Calculer un score pour trier
                                                        tier_scores = {
                                                            "IRON": 1, "BRONZE": 2, "SILVER": 3, "GOLD": 4,
                                                            "PLATINUM": 5, "EMERALD": 6, "DIAMOND": 7,
                                                            "MASTER": 8, "GRANDMASTER": 15, "CHALLENGER": 20
                                                        }
                                                        
                                                        tier = rank_info.get("tier", "UNRANKED")
                                                        rank = rank_info.get("rank", "IV")
                                                        lp = rank_info.get("leaguePoints", 0)
                                                        
                                                        score = tier_scores.get(tier, 0) * 100 + lp
                                                        
                                                        players_with_rank.append({
                                                            "data": (game_name, tag_line),
                                                            "score": score,
                                                            "tier": tier
                                                        })
                                            except Exception as e:
                                                # Si erreur, score = 0
                                                players_with_rank.append({
                                                    "data": (game_name, tag_line),
                                                    "score": 0,
                                                    "tier": "UNRANKED"
                                                })
                                        
                                        # Trier par score décroissant et prendre les 5 meilleurs
                                        players_with_rank.sort(key=lambda x: x["score"], reverse=True)
                                        players = [p["data"] for p in players_with_rank[:5]]
                                        
                                        st.success(f"✅ 5 meilleurs joueurs sélectionnés : {', '.join([f'{p["data"][0]} ({p["tier"]})' for p in players_with_rank[:5]])}")
                                    else:
                                        # Pas d'API key, prendre les 5 premiers
                                        st.warning("⚠️ Pas de clé API, les 5 premiers joueurs seront utilisés")
                                        players = players[:5]
                                
                                # Construire team_data manuellement avec les joueurs sélectionnés
                                roles = ["TOP", "JGL", "MID", "ADC", "SUP"]
                                team_data = {
                                    "name": team_name,
                                    "opgg_link": opgg_link,
                                    "players": [
                                        {
                                            "role": roles[i],
                                            "gameName": game_name,
                                            "tagLine": tag_line
                                        }
                                        for i, (game_name, tag_line) in enumerate(players)
                                    ]
                                }
                                
                                edition_manager.add_team(team_name, team_data)
                                
                                success_count += 1
                                
                            except Exception as e:
                                st.error(f"❌ Erreur pour {team_name}: {str(e)}")
                                error_count += 1
                            
                            progress_bar.progress((idx + 1) / len(df))
                        
                        status_text.text("")
                        progress_bar.empty()
                        
                        st.success(f"🎉 Import terminé: {success_count} équipes ajoutées, {error_count} erreurs")
                        
            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture du CSV: {str(e)}")

# ========================
# TAB 2: MANAGE TEAMS
# ========================
with tab2:
    st.subheader("📋 Équipes enregistrées")
    
    teams = edition_manager.load_teams()
    
    # Convert dict to list if needed (teams.json format is dict)
    if isinstance(teams, dict):
        teams_list = [{"name": name, **data} for name, data in teams.items()]
    elif isinstance(teams, list):
        teams_list = teams
    else:
        teams_list = []
    
    if not teams_list:
        st.info("ℹ️ Aucune équipe enregistrée pour cette édition")
    else:
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            st.metric("Nombre d'équipes", len(teams_list))
        
        with col2:
            # Bouton supprimer les sélectionnées
            if st.button("🗑️ Supprimer les équipes sélectionnées", type="secondary", use_container_width=True):
                st.session_state.confirm_delete_selected = True
        
        with col3:
            # Bouton supprimer toutes
            if st.button("⚠️ Supprimer TOUTES les équipes", type="secondary", use_container_width=True):
                st.session_state.confirm_delete_all = True
        
        # Confirmation pour suppression sélectionnée
        if st.session_state.get("confirm_delete_selected", False):
            st.warning("⚠️ **Confirmer la suppression des équipes sélectionnées ?**")
            col_yes, col_no = st.columns(2)
            
            with col_yes:
                if st.button("✅ Oui, supprimer", type="primary", use_container_width=True):
                    selected_teams = [name for name, selected in st.session_state.items() 
                                    if name.startswith("select_team_") and selected]
                    
                    if selected_teams:
                        # Supprimer les équipes sélectionnées
                        teams_dict = teams if isinstance(teams, dict) else {t["name"]: t for t in teams_list}
                        
                        for team_key in selected_teams:
                            team_name = team_key.replace("select_team_", "")
                            if team_name in teams_dict:
                                del teams_dict[team_name]
                        
                        edition_manager.save_teams(teams_dict)
                        st.success(f"✅ {len(selected_teams)} équipe(s) supprimée(s) !")
                        st.session_state.confirm_delete_selected = False
                        st.rerun()
                    else:
                        st.warning("Aucune équipe sélectionnée")
                        st.session_state.confirm_delete_selected = False
            
            with col_no:
                if st.button("❌ Annuler", use_container_width=True):
                    st.session_state.confirm_delete_selected = False
                    st.rerun()
        
        # Confirmation pour suppression totale
        if st.session_state.get("confirm_delete_all", False):
            st.error("⚠️ **ATTENTION : Supprimer TOUTES les équipes ?**")
            st.markdown("Cette action est **irréversible** !")
            
            confirm_text = st.text_input("Pour confirmer, tapez : **SUPPRIMER TOUT**")
            
            col_yes, col_no = st.columns(2)
            
            with col_yes:
                if st.button("🗑️ SUPPRIMER TOUT", type="primary", use_container_width=True):
                    if confirm_text == "SUPPRIMER TOUT":
                        edition_manager.save_teams({})
                        st.success("✅ Toutes les équipes ont été supprimées !")
                        st.session_state.confirm_delete_all = False
                        st.rerun()
                    else:
                        st.error("❌ Confirmation incorrecte")
            
            with col_no:
                if st.button("❌ Annuler", use_container_width=True):
                    st.session_state.confirm_delete_all = False
                    st.rerun()
        
        st.markdown("---")
        
        # Sélection des équipes
        st.markdown("### ✅ Sélectionner les équipes à gérer")
        
        # Option: Tout sélectionner / Tout désélectionner
        col_select_all, col_deselect_all = st.columns(2)
        
        with col_select_all:
            if st.button("☑️ Tout sélectionner", use_container_width=True):
                for team in teams_list:
                    st.session_state[f"select_team_{team.get('name')}"] = True
                st.rerun()
        
        with col_deselect_all:
            if st.button("⬜ Tout désélectionner", use_container_width=True):
                for team in teams_list:
                    st.session_state[f"select_team_{team.get('name')}"] = False
                st.rerun()
        
        # Display teams avec checkboxes
        for idx, team in enumerate(teams_list):
            if not isinstance(team, dict):
                continue
            
            team_name = team.get('name', 'Équipe sans nom')
            
            # Checkbox pour sélection + Expander
            col_check, col_expand = st.columns([1, 20])
            
            with col_check:
                selected = st.checkbox(
                    "✓",
                    key=f"select_team_{team_name}",
                    label_visibility="collapsed"
                )
            
            with col_expand:
                with st.expander(f"🏆 {team_name}", expanded=False):
                    # Bouton pour rafraîchir les rangs de cette équipe
                    col_opgg, col_refresh = st.columns([3, 1])
                    
                    with col_opgg:
                        st.markdown(f"**Lien OP.GG:** {team.get('opgg_link', 'N/A')}")
                    
                    with col_refresh:
                        if st.button("🔄 Rafraîchir les rangs", key=f"refresh_{idx}", help="Met à jour uniquement les rangs de cette équipe"):
                            api_key = os.getenv("RIOT_API_KEY")
                            if not api_key:
                                st.error("❌ Clé API manquante")
                            else:
                                with st.spinner(f"Mise à jour des rangs pour {team_name}..."):
                                    try:
                                        # Import EditionProcessor pour utiliser ses méthodes
                                        processor = EditionProcessor(selected_edition, api_key)
                                        
                                        # Charger teams_with_puuid
                                        teams_with_puuid = edition_manager.load_teams_with_puuid()
                                        
                                        if not teams_with_puuid or team_name not in teams_with_puuid:
                                            st.warning("⚠️ Équipe non trouvée dans teams_with_puuid.json. Lancez d'abord le traitement complet.")
                                        else:
                                            # Mettre à jour seulement les rangs de cette équipe
                                            team_data = teams_with_puuid[team_name]
                                            updated_count = 0
                                            
                                            for player in team_data.get('players', []):
                                                if 'puuid' in player:
                                                    # Fetch rank via l'API
                                                    summoner_data = processor.riot_client.get_summoner_by_puuid(player['puuid'])
                                                    if summoner_data:
                                                        rank_data = processor.riot_client.get_rank(summoner_data['id'])
                                                        if rank_data:
                                                            player['tier'] = rank_data.get('tier', 'UNRANKED')
                                                            player['rank'] = rank_data.get('rank', '')
                                                            player['leaguePoints'] = rank_data.get('leaguePoints', 0)
                                                            updated_count += 1
                                            
                                            # Sauvegarder teams_with_puuid
                                            edition_manager.save_teams_with_puuid(teams_with_puuid)
                                            
                                            # Regénérer general_stats.json pour cette équipe
                                            general_stats = edition_manager.load_general_stats() or {}
                                            
                                            for player in team_data.get('players', []):
                                                player_key = f"{player['gameName']}#{player['tagLine']}"
                                                if player_key in general_stats:
                                                    general_stats[player_key]['tier'] = player.get('tier', 'UNRANKED')
                                                    general_stats[player_key]['rank'] = player.get('rank', '')
                                                    general_stats[player_key]['leaguePoints'] = player.get('leaguePoints', 0)
                                            
                                            edition_manager.save_general_stats(general_stats)
                                            
                                            st.success(f"✅ Rangs mis à jour pour {updated_count} joueurs de **{team_name}**!")
                                            st.rerun()
                                    
                                    except Exception as e:
                                        st.error(f"❌ Erreur: {str(e)}")
                    
                    st.markdown("---")
                    
                    # Edit mode toggle
                    edit_mode = st.checkbox(f"✏️ Modifier les rôles", key=f"edit_{idx}")
                    
                    if edit_mode:
                        st.markdown("**Modifier les rôles des joueurs:**")
                        
                        # Form for editing roles
                        with st.form(key=f"form_edit_{idx}"):
                            new_players = []
                            
                            for player_idx, player in enumerate(team.get("players", [])):
                                col1, col2, col3 = st.columns([2, 2, 1])
                                
                                with col1:
                                    st.text_input(
                                        f"Joueur {player_idx + 1}",
                                        value=f"{player.get('gameName', 'Unknown')}#{player.get('tagLine', '0000')}",
                                        disabled=True,
                                        key=f"player_{idx}_{player_idx}"
                                    )
                                
                                with col2:
                                    current_role = player.get("role", "TOP")
                                    role_options = ["TOP", "JGL", "MID", "ADC", "SUP"]
                                    current_index = role_options.index(current_role) if current_role in role_options else 0
                                    
                                    new_role = st.selectbox(
                                        f"Rôle",
                                        role_options,
                                        index=current_index,
                                        key=f"role_{idx}_{player_idx}"
                                    )
                                
                                with col3:
                                    st.write("")  # Spacing
                                
                                # Store new player data
                                new_players.append({
                                    "role": new_role,
                                    "gameName": player.get("gameName", "Unknown"),
                                    "tagLine": player.get("tagLine", "0000")
                                })
                            
                            submit_changes = st.form_submit_button("💾 Enregistrer les modifications", type="primary")
                            
                            if submit_changes:
                                # Update team data
                                team["players"] = new_players
                                
                                # Convert back to dict format for saving
                                teams_dict = {}
                                for t in teams_list:
                                    t_name = t.get("name", "Unknown")
                                    teams_dict[t_name] = {
                                        "players": t.get("players", []),
                                        "opgg_link": t.get("opgg_link", "")
                                    }
                                
                                edition_manager.save_teams(teams_dict)
                                st.success(f"✅ Rôles mis à jour pour l'équipe **{team_name}**!")
                                st.rerun()
                    
                    else:
                        # Display mode (read-only)
                        st.markdown("**Joueurs:**")
                        
                        # Sort players by role order
                        role_order = {"TOP": 0, "JGL": 1, "MID": 2, "ADC": 3, "SUP": 4}
                        players = team.get("players", [])
                        sorted_players = sorted(players, key=lambda p: role_order.get(p.get("role", "SUP"), 5))
                        
                        players_data = []
                        for player in sorted_players:
                            players_data.append({
                                "Rôle": player.get("role", "N/A"),
                                "Pseudo": f"{player.get('gameName', 'Unknown')}#{player.get('tagLine', '0000')}"
                            })
                        
                        if players_data:
                            st.dataframe(
                                pd.DataFrame(players_data),
                                use_container_width=True,
                                hide_index=True
                            )
                    
                    # Delete button (always visible dans l'expander)
                    st.markdown("---")
                    if st.button(f"🗑️ Supprimer l'équipe", key=f"delete_{idx}", type="secondary"):
                        # Remove from list
                        teams_list.remove(team)
                        
                        # Convert back to dict format for saving
                        teams_dict = {}
                        for t in teams_list:
                            t_name = t.get("name", "Unknown")
                            teams_dict[t_name] = {
                                "players": t.get("players", []),
                                "opgg_link": t.get("opgg_link", "")
                            }
                        
                        edition_manager.save_teams(teams_dict)
                        st.success(f"✅ Équipe **{team_name}** supprimée")
                        st.rerun()

# ========================
# TAB 3: PROCESS DATA
# ========================
with tab3:
    st.subheader("⚙️ Traitement des données")
    
    teams = edition_manager.load_teams()
    
    if not teams:
        st.warning("⚠️ Aucune équipe à traiter. Ajoutez des équipes d'abord.")
    else:
        # Show summary
        summary = edition_manager.get_summary()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Équipes", summary.get("total_teams", 0))
        with col2:
            st.metric("Joueurs", summary.get("total_players", 0))
        with col3:
            st.metric("Statut", summary.get("status", "N/A"))
        
        st.markdown("---")
        
        # Pipeline steps
        st.markdown("**Pipeline de traitement:**")
        st.markdown("""
        1. 🔍 **Fetch PUUID** - Récupération des identifiants Riot (Account-V1)
        2. 📊 **Fetch Rank** - Récupération des rangs (League-V4)
        3. 🎮 **Fetch Match IDs** - Récupération des IDs de matchs (Match-V5)
        4. 📝 **Fetch Match Details** - Récupération des détails (Match-V5)
        5. 📈 **Calculate Stats** - Calcul des statistiques agrégées
        """)
        
        st.markdown("---")
        
        # API Key check
        api_key = os.getenv("RIOT_API_KEY")
        if not api_key:
            st.error("❌ Clé API Riot manquante. Ajoutez RIOT_API_KEY dans le fichier .env")
        else:
            st.success("✅ Clé API Riot détectée")
            
            # Boutons séparés pour traitement modulaire
            col_fetch, col_full = st.columns(2)
            
            with col_fetch:
                if st.button("🎮 Fetch Matchs Tournoi", help="Récupère uniquement les matchs de tournoi (type='tourney')", use_container_width=True):
                    # Initialize processor
                    processor = EditionProcessor(
                        edition_id=selected_edition,
                        api_key=api_key
                    )
                    
                    # Check if teams_with_puuid exists
                    teams_with_puuid = edition_manager.load_teams_with_puuid()
                    if not teams_with_puuid:
                        st.error("❌ Lancez d'abord les étapes PUUID et Ranks (traitement complet)")
                    else:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        def progress_callback(message: str, progress: float):
                            status_text.text(message)
                            progress_bar.progress(min(int(progress), 100))
                        
                        processor.progress_callback = progress_callback
                        
                        try:
                            with st.spinner("🎮 Récupération des matchs de tournoi..."):
                                # Run step 4: fetch match IDs avec type="tourney"
                                tournament_matches = processor.step4_fetch_match_ids(
                                    use_tourney_filter=True  # 🎯 Filtre tournois !
                                )
                                
                                progress_bar.empty()
                                status_text.empty()
                                
                                if tournament_matches:
                                    st.success(f"✅ {len(tournament_matches)} équipes traitées!")
                                    
                                    # Afficher le résumé
                                    total_matches = sum(len(matches) for matches in tournament_matches.values())
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Équipes", len(tournament_matches))
                                    with col2:
                                        st.metric("Matchs trouvés", total_matches)
                                    
                                    # Afficher la liste des matchs par équipe
                                    with st.expander("📋 Matchs par équipe"):
                                        for team_name, match_ids in tournament_matches.items():
                                            st.markdown(f"**{team_name}**: {len(match_ids)} matchs")
                                            st.caption(", ".join(match_ids[:5]) + ("..." if len(match_ids) > 5 else ""))
                                else:
                                    st.warning("⚠️ Aucun match trouvé")
                        
                        except Exception as e:
                            progress_bar.empty()
                            status_text.empty()
                            st.error(f"❌ Erreur: {str(e)}")
                            st.exception(e)
            
            with col_full:
                # Process button (traitement complet)
                if st.button("🚀 Traitement Complet", type="primary", help="Pipeline complet: PUUID + Ranks + Matchs + Stats", use_container_width=True):
                    
                    # Initialize processor
                    processor = EditionProcessor(
                        edition_id=selected_edition,
                        api_key=api_key
                    )
                    
                    # Create progress containers
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    step_details = st.empty()
                    
                    # Progress callback for UI updates
                    def progress_callback(message: str, progress: float):
                        status_text.text(message)
                        progress_bar.progress(int(progress))
                    
                    processor.progress_callback = progress_callback
                    
                    try:
                        with st.spinner("Pipeline en cours d'exécution..."):
                            # Run full pipeline
                            results = processor.run_full_pipeline(use_cache=True)
                            
                            # Clear progress
                            progress_bar.empty()
                            status_text.empty()
                            
                            # Display results
                            if results.get("success"):
                                st.success("✅ Pipeline terminé avec succès!")
                                st.balloons()
                                
                                # Show summary
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    teams_count = results["steps"]["step2_puuids"]["teams_count"]
                                    st.metric("Équipes traitées", teams_count)
                                
                                with col2:
                                    matches_count = results["steps"]["step5_match_details"]["matches_fetched"]
                                    st.metric("Matchs analysés", matches_count)
                                
                                with col3:
                                    duration = results["duration_seconds"]
                                    st.metric("Durée", f"{duration:.1f}s")
                                
                                # Show detailed steps
                                with st.expander("📋 Détails du pipeline"):
                                    for step_name, step_data in results["steps"].items():
                                        status_icon = "✅" if step_data.get("success") else "❌"
                                        st.markdown(f"{status_icon} **{step_name}**: {step_data}")
                            
                            else:
                                st.error("❌ Le pipeline a rencontré des erreurs")
                                
                                # Show errors
                                if results.get("errors"):
                                    st.error("**Erreurs:**")
                                    for error in results["errors"]:
                                        st.error(f"- {error}")
                            
                            # Show warnings
                            if results.get("warnings"):
                                with st.expander("⚠️ Avertissements"):
                                    for warning in results["warnings"]:
                                        st.warning(warning)
                            
                            # Show full results in expander
                            with st.expander("🔍 Résultats complets (JSON)"):
                                st.json(results)
                    
                    except Exception as e:
                        progress_bar.empty()
                        status_text.empty()
                        st.error(f"❌ Erreur lors de l'exécution du pipeline: {str(e)}")
                        st.exception(e)

# Footer
st.markdown("---")
st.caption(f"Edition {selected_edition} - OcciLan Stats Admin Panel")

