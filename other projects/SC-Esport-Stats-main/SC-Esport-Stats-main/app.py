import streamlit as st
from src.components.player_stats_display import display_player_stats
from src.utils.formatters import format_champion_name, get_champion_icon_url

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/champions')
def champions():
    return render_template('champions.html')

if __name__ == '__main__':
    app.run(debug=True)
