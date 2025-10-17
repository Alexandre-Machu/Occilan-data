import streamlit as st
from pathlib import Path
from jinja2 import Template

def load_template(template_name: str) -> Template:
    template_path = Path(__file__).parent / "templates" / template_name
    return Template(template_path.read_text())

def load_css(css_file: str) -> str:
    css_path = Path(__file__).parent.parent.parent / "static" / "css" / css_file
    return css_path.read_text()

def display_champion_stats(df):
    # Charger le CSS et le template
    st.markdown(f"<style>{load_css('tables.css')}</style>", unsafe_allow_html=True)
    template = load_template("champion_stats.html")
    
    # Préparer les données
    champions_data = prepare_champions_data(df)
    
    # Rendre le template
    html = template.render(champions=champions_data)
    st.markdown(html, unsafe_allow_html=True)