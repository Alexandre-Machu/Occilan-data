-- ============================================================================
-- OcciLan Stats Database Schema
-- ============================================================================
-- Database: DuckDB / SQLite
-- Version: 1.0
-- Last Updated: 2025-10-17
-- ============================================================================

-- ============================================================================
-- TABLE: edition
-- Description: Stores tournament edition information
-- ============================================================================
CREATE TABLE IF NOT EXISTS edition (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    region VARCHAR(10) DEFAULT 'EUW',
    format VARCHAR(50) DEFAULT 'swiss_playoffs',
    num_teams INTEGER DEFAULT 16,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, year)
);

-- ============================================================================
-- TABLE: team
-- Description: Stores team information and roster
-- ============================================================================
CREATE TABLE IF NOT EXISTS team (
    id INTEGER PRIMARY KEY,
    edition_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    tag VARCHAR(10),
    opgg_link TEXT,
    seed INTEGER,
    final_rank INTEGER,
    swiss_record VARCHAR(10),  -- e.g., "3-2"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (edition_id) REFERENCES edition(id) ON DELETE CASCADE,
    UNIQUE(edition_id, name)
);

-- ============================================================================
-- TABLE: player
-- Description: Stores player information with Riot account details
-- ============================================================================
CREATE TABLE IF NOT EXISTS player (
    id INTEGER PRIMARY KEY,
    team_id INTEGER NOT NULL,
    riot_id VARCHAR(100),  -- Riot ID (e.g., "Player#EUW")
    game_name VARCHAR(50),
    tag_line VARCHAR(10),
    puuid VARCHAR(100) UNIQUE,
    summoner_id VARCHAR(100),
    account_id VARCHAR(100),
    role VARCHAR(20),  -- TOP, JUNGLE, MID, ADC, SUPPORT
    nickname VARCHAR(50),  -- Display name in tournament
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES team(id) ON DELETE CASCADE
);

-- ============================================================================
-- TABLE: match
-- Description: Stores match/game information
-- ============================================================================
CREATE TABLE IF NOT EXISTS match (
    id INTEGER PRIMARY KEY,
    match_id VARCHAR(100) UNIQUE NOT NULL,  -- Riot match ID
    edition_id INTEGER NOT NULL,
    game_creation BIGINT,
    game_start BIGINT,
    game_end BIGINT,
    game_duration INTEGER,  -- in seconds
    game_mode VARCHAR(50),
    game_type VARCHAR(50),
    game_version VARCHAR(50),
    map_id INTEGER,
    platform_id VARCHAR(10),
    queue_id INTEGER,
    tournament_code VARCHAR(100),
    phase VARCHAR(20),  -- swiss, quarterfinals, semifinals, finals
    match_number INTEGER,
    blue_team_id INTEGER,
    red_team_id INTEGER,
    winning_team VARCHAR(10),  -- blue or red
    first_blood_team VARCHAR(10),
    first_tower_team VARCHAR(10),
    first_baron_team VARCHAR(10),
    first_dragon_team VARCHAR(10),
    first_inhibitor_team VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (edition_id) REFERENCES edition(id) ON DELETE CASCADE,
    FOREIGN KEY (blue_team_id) REFERENCES team(id),
    FOREIGN KEY (red_team_id) REFERENCES team(id)
);

-- ============================================================================
-- TABLE: participant
-- Description: Stores individual player performance in each match
-- ============================================================================
CREATE TABLE IF NOT EXISTS participant (
    id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    participant_id INTEGER,  -- 1-10 in game
    team_position VARCHAR(20),
    champion_id INTEGER,
    champion_name VARCHAR(50),
    summoner1_id INTEGER,
    summoner2_id INTEGER,
    
    -- Combat stats
    kills INTEGER DEFAULT 0,
    deaths INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    double_kills INTEGER DEFAULT 0,
    triple_kills INTEGER DEFAULT 0,
    quadra_kills INTEGER DEFAULT 0,
    penta_kills INTEGER DEFAULT 0,
    first_blood_kill BOOLEAN DEFAULT FALSE,
    first_blood_assist BOOLEAN DEFAULT FALSE,
    
    -- Farming stats
    total_minions_killed INTEGER DEFAULT 0,
    neutral_minions_killed INTEGER DEFAULT 0,
    cs_per_min REAL,
    
    -- Gold stats
    gold_earned INTEGER DEFAULT 0,
    gold_spent INTEGER DEFAULT 0,
    gold_per_min REAL,
    
    -- Damage stats
    total_damage_dealt INTEGER DEFAULT 0,
    physical_damage_dealt INTEGER DEFAULT 0,
    magic_damage_dealt INTEGER DEFAULT 0,
    true_damage_dealt INTEGER DEFAULT 0,
    total_damage_to_champions INTEGER DEFAULT 0,
    physical_damage_to_champions INTEGER DEFAULT 0,
    magic_damage_to_champions INTEGER DEFAULT 0,
    true_damage_to_champions INTEGER DEFAULT 0,
    damage_dealt_to_objectives INTEGER DEFAULT 0,
    damage_dealt_to_turrets INTEGER DEFAULT 0,
    damage_per_min REAL,
    
    -- Damage taken
    total_damage_taken INTEGER DEFAULT 0,
    physical_damage_taken INTEGER DEFAULT 0,
    magic_damage_taken INTEGER DEFAULT 0,
    true_damage_taken INTEGER DEFAULT 0,
    damage_self_mitigated INTEGER DEFAULT 0,
    
    -- Healing & Shielding
    total_heal INTEGER DEFAULT 0,
    total_heals_on_teammates INTEGER DEFAULT 0,
    total_damage_shielded_on_teammates INTEGER DEFAULT 0,
    
    -- Vision stats
    vision_score INTEGER DEFAULT 0,
    wards_placed INTEGER DEFAULT 0,
    wards_killed INTEGER DEFAULT 0,
    control_wards_placed INTEGER DEFAULT 0,
    vision_score_per_min REAL,
    
    -- Objectives
    turret_kills INTEGER DEFAULT 0,
    inhibitor_kills INTEGER DEFAULT 0,
    baron_kills INTEGER DEFAULT 0,
    dragon_kills INTEGER DEFAULT 0,
    rift_herald_kills INTEGER DEFAULT 0,
    
    -- CC & Utility
    time_ccing_others INTEGER DEFAULT 0,
    total_time_crowd_control_dealt INTEGER DEFAULT 0,
    
    -- Items
    item0 INTEGER,
    item1 INTEGER,
    item2 INTEGER,
    item3 INTEGER,
    item4 INTEGER,
    item5 INTEGER,
    item6 INTEGER,
    
    -- Game outcome
    win BOOLEAN DEFAULT FALSE,
    game_ended_in_early_surrender BOOLEAN DEFAULT FALSE,
    team_early_surrendered BOOLEAN DEFAULT FALSE,
    
    -- Derived stats (calculated)
    kda REAL,
    kill_participation REAL,
    damage_share REAL,
    gold_share REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (match_id) REFERENCES match(id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES player(id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES team(id) ON DELETE CASCADE,
    UNIQUE(match_id, player_id)
);

-- ============================================================================
-- TABLE: player_stats
-- Description: Aggregated statistics per player (across all matches)
-- ============================================================================
CREATE TABLE IF NOT EXISTS player_stats (
    id INTEGER PRIMARY KEY,
    player_id INTEGER UNIQUE NOT NULL,
    edition_id INTEGER NOT NULL,
    
    -- Match counts
    games_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    win_rate REAL,
    
    -- Combat averages
    avg_kills REAL DEFAULT 0,
    avg_deaths REAL DEFAULT 0,
    avg_assists REAL DEFAULT 0,
    avg_kda REAL DEFAULT 0,
    
    -- Totals
    total_kills INTEGER DEFAULT 0,
    total_deaths INTEGER DEFAULT 0,
    total_assists INTEGER DEFAULT 0,
    total_double_kills INTEGER DEFAULT 0,
    total_triple_kills INTEGER DEFAULT 0,
    total_quadra_kills INTEGER DEFAULT 0,
    total_penta_kills INTEGER DEFAULT 0,
    
    -- Economy averages
    avg_cs_per_min REAL DEFAULT 0,
    avg_gold_per_min REAL DEFAULT 0,
    avg_damage_per_min REAL DEFAULT 0,
    avg_vision_score_per_min REAL DEFAULT 0,
    
    -- Performance metrics
    avg_kill_participation REAL DEFAULT 0,
    avg_damage_share REAL DEFAULT 0,
    avg_gold_share REAL DEFAULT 0,
    
    -- Special achievements
    first_bloods INTEGER DEFAULT 0,
    solo_kills INTEGER DEFAULT 0,
    
    -- Most played
    most_played_champion VARCHAR(50),
    most_played_champion_games INTEGER DEFAULT 0,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (player_id) REFERENCES player(id) ON DELETE CASCADE,
    FOREIGN KEY (edition_id) REFERENCES edition(id) ON DELETE CASCADE
);

-- ============================================================================
-- TABLE: player_champion_stats
-- Description: Per-champion statistics for each player
-- ============================================================================
CREATE TABLE IF NOT EXISTS player_champion_stats (
    id INTEGER PRIMARY KEY,
    player_id INTEGER NOT NULL,
    edition_id INTEGER NOT NULL,
    champion_id INTEGER NOT NULL,
    champion_name VARCHAR(50) NOT NULL,
    
    games_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    win_rate REAL,
    
    avg_kills REAL DEFAULT 0,
    avg_deaths REAL DEFAULT 0,
    avg_assists REAL DEFAULT 0,
    avg_kda REAL DEFAULT 0,
    
    avg_cs_per_min REAL DEFAULT 0,
    avg_gold_per_min REAL DEFAULT 0,
    avg_damage_per_min REAL DEFAULT 0,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (player_id) REFERENCES player(id) ON DELETE CASCADE,
    FOREIGN KEY (edition_id) REFERENCES edition(id) ON DELETE CASCADE,
    UNIQUE(player_id, edition_id, champion_id)
);

-- ============================================================================
-- TABLE: team_stats
-- Description: Aggregated statistics per team
-- ============================================================================
CREATE TABLE IF NOT EXISTS team_stats (
    id INTEGER PRIMARY KEY,
    team_id INTEGER UNIQUE NOT NULL,
    edition_id INTEGER NOT NULL,
    
    games_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    win_rate REAL,
    
    -- Team combat
    avg_kills REAL DEFAULT 0,
    avg_deaths REAL DEFAULT 0,
    avg_assists REAL DEFAULT 0,
    
    -- Team economy
    avg_gold_per_min REAL DEFAULT 0,
    avg_cs_per_min REAL DEFAULT 0,
    
    -- Objectives
    avg_turrets REAL DEFAULT 0,
    avg_dragons REAL DEFAULT 0,
    avg_barons REAL DEFAULT 0,
    avg_heralds REAL DEFAULT 0,
    
    -- Game control
    first_blood_rate REAL DEFAULT 0,
    first_tower_rate REAL DEFAULT 0,
    first_dragon_rate REAL DEFAULT 0,
    first_baron_rate REAL DEFAULT 0,
    
    -- Game duration
    avg_game_duration REAL DEFAULT 0,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (team_id) REFERENCES team(id) ON DELETE CASCADE,
    FOREIGN KEY (edition_id) REFERENCES edition(id) ON DELETE CASCADE
);

-- ============================================================================
-- INDEXES for performance optimization
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_team_edition ON team(edition_id);
CREATE INDEX IF NOT EXISTS idx_player_team ON player(team_id);
CREATE INDEX IF NOT EXISTS idx_player_puuid ON player(puuid);
CREATE INDEX IF NOT EXISTS idx_match_edition ON match(edition_id);
CREATE INDEX IF NOT EXISTS idx_match_teams ON match(blue_team_id, red_team_id);
CREATE INDEX IF NOT EXISTS idx_participant_match ON participant(match_id);
CREATE INDEX IF NOT EXISTS idx_participant_player ON participant(player_id);
CREATE INDEX IF NOT EXISTS idx_participant_team ON participant(team_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_edition ON player_stats(edition_id);
CREATE INDEX IF NOT EXISTS idx_player_champion_stats_player ON player_champion_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_team_stats_edition ON team_stats(edition_id);

-- ============================================================================
-- VIEWS for common queries
-- ============================================================================

-- View: Player overview with team info
CREATE VIEW IF NOT EXISTS v_player_overview AS
SELECT 
    p.id as player_id,
    p.game_name,
    p.tag_line,
    p.riot_id,
    p.role,
    p.nickname,
    t.name as team_name,
    t.tag as team_tag,
    e.name as edition_name,
    e.year as edition_year,
    ps.games_played,
    ps.wins,
    ps.losses,
    ps.win_rate,
    ps.avg_kda,
    ps.avg_kills,
    ps.avg_deaths,
    ps.avg_assists,
    ps.avg_cs_per_min,
    ps.avg_gold_per_min,
    ps.avg_damage_per_min,
    ps.most_played_champion
FROM player p
LEFT JOIN team t ON p.team_id = t.id
LEFT JOIN edition e ON t.edition_id = e.id
LEFT JOIN player_stats ps ON p.id = ps.player_id;

-- View: Team overview with aggregated stats
CREATE VIEW IF NOT EXISTS v_team_overview AS
SELECT 
    t.id as team_id,
    t.name as team_name,
    t.tag as team_tag,
    t.seed,
    t.final_rank,
    t.swiss_record,
    e.name as edition_name,
    e.year as edition_year,
    ts.games_played,
    ts.wins,
    ts.losses,
    ts.win_rate,
    ts.avg_kills,
    ts.avg_deaths,
    ts.first_blood_rate,
    ts.first_tower_rate,
    ts.avg_game_duration
FROM team t
LEFT JOIN edition e ON t.edition_id = e.id
LEFT JOIN team_stats ts ON t.id = ts.team_id;

-- View: Match results with team names
CREATE VIEW IF NOT EXISTS v_match_results AS
SELECT 
    m.id as match_id,
    m.match_id as riot_match_id,
    m.phase,
    m.match_number,
    bt.name as blue_team,
    rt.name as red_team,
    m.winning_team,
    m.game_duration,
    m.game_creation,
    e.name as edition_name
FROM match m
LEFT JOIN team bt ON m.blue_team_id = bt.id
LEFT JOIN team rt ON m.red_team_id = rt.id
LEFT JOIN edition e ON m.edition_id = e.id;

-- ============================================================================
-- End of schema
-- ============================================================================
