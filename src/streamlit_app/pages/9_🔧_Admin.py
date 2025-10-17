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

# Check authentication
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

if not editions:
    st.warning("⚠️ Aucune édition trouvée. Créez-en une d'abord.")
    st.stop()

selected_edition = st.selectbox(
    "📂 Sélectionner l'édition",
    editions,
    format_func=lambda x: f"Edition {x}"
)

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
                                
                                if len(players) != 5:
                                    st.warning(f"⚠️ {team_name}: {len(players)} joueurs (5 attendus), ignoré")
                                    error_count += 1
                                    continue
                                
                                # Add team
                                roles = ["TOP", "JGL", "MID", "ADC", "SUP"]
                                team_data = parser.parse_team_opgg(team_name, opgg_link, roles)
                                edition_manager.add_team(team_data)
                                
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
        st.metric("Nombre d'équipes", len(teams_list))
        
        # Display teams
        for idx, team in enumerate(teams_list):
            if not isinstance(team, dict):
                continue
            
            team_name = team.get('name', 'Équipe sans nom')
            
            with st.expander(f"🏆 {team_name}"):
                st.markdown(f"**Lien OP.GG:** {team.get('opgg_link', 'N/A')}")
                
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
                            width="stretch",
                            hide_index=True
                        )
                
                # Delete button (always visible)
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
            
            # Process button
            if st.button("🚀 Lancer le traitement complet", type="primary", width="stretch"):
                
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

