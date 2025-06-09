from sqlite3 import connect
from platformdirs import user_config_path
from .provider.common import SearchResult

GUCKEN_DB = user_config_path("gucken").joinpath("gucken.db")

def init_db():
    conn = connect(GUCKEN_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS watched_episodes
                 (series TEXT, season INTEGER, episode INTEGER, provider TEXT,
                  PRIMARY KEY (series, season, episode, provider))''')
    c.execute('''CREATE TABLE IF NOT EXISTS watchtime
                 (series TEXT, season INTEGER, episode INTEGER, provider TEXT, time TEXT,
                  PRIMARY KEY (series, season, episode, provider))''')
    c.execute('''CREATE TABLE IF NOT EXISTS watchlist
                 (name TEXT, provider TEXT, PRIMARY KEY (name, provider))''')
    conn.commit()
    conn.close()

def mark_episode_watched(series, season, episode, provider):
    conn = connect(GUCKEN_DB)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO watched_episodes (series, season, episode, provider)
                 VALUES (?, ?, ?, ?)''', (series, season, episode, provider))
    conn.commit()
    conn.close()

def is_episode_watched(series, season, episode, provider):
    conn = connect(GUCKEN_DB)
    c = conn.cursor()
    c.execute('''SELECT 1 FROM watched_episodes WHERE series=? AND season=? AND episode=? AND provider=?''',
              (series, season, episode, provider))
    result = c.fetchone()
    conn.close()
    return result is not None

def save_watchtime(series, season, episode, provider, time_str):
    conn = connect(GUCKEN_DB)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO watchtime (series, season, episode, provider, time)
                 VALUES (?, ?, ?, ?, ?)''', (series, season, episode, provider, time_str))
    conn.commit()
    conn.close()

def get_unfinished_watchtime():
    conn = connect(GUCKEN_DB)
    c = conn.cursor()
    c.execute('SELECT series, season, episode, provider, time FROM watchtime')
    rows = c.fetchall()
    conn.close()
    return rows

def remove_watchtime(series, season, episode, provider):
    conn = connect(GUCKEN_DB)
    c = conn.cursor()
    c.execute('DELETE FROM watchtime WHERE series=? AND season=? AND episode=? AND provider=?',
              (series, season, episode, provider))
    conn.commit()
    conn.close()

def add_to_watchlist(series: SearchResult):
    conn = connect(GUCKEN_DB)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO watchlist VALUES (?, ?)",
              (series.name, series.provider_name))
    conn.commit()
    conn.close()

def remove_from_watchlist(series: SearchResult):
    conn = connect(GUCKEN_DB)
    c = conn.cursor()
    c.execute("DELETE FROM watchlist WHERE name=? AND provider=?", (series.name, series.provider_name))
    conn.commit()
    conn.close()

def is_in_watchlist(series: SearchResult) -> bool:
    conn = connect(GUCKEN_DB)
    c = conn.cursor()
    c.execute("SELECT 1 FROM watchlist WHERE name=? AND provider=?", (series.name, series.provider_name))
    result = c.fetchone()
    conn.close()
    return result is not None

def get_watchlist() -> list:
    conn = connect(GUCKEN_DB)
    c = conn.cursor()
    c.execute("SELECT name, provider FROM watchlist")
    rows = c.fetchall()
    conn.close()
    return rows  # [(name, provider_name), ...]
