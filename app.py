"""
FC Zürich Stats Web Application
Displays statistics for FC Zürich from the Swiss Super League
"""

import os
from datetime import datetime
from flask import Flask, render_template
import requests

app = Flask(__name__)

# API Configuration
# Using API-Football (api-sports.io) which supports Swiss Super League
# - Swiss Super League ID: 207
# - FC Zürich team ID: 684
# API documentation: https://www.api-football.com/documentation-v3
# Free tier: 100 requests/day
# Using a fallback approach with sample data if API is unavailable

# Try to load API key from config.py first, then fall back to environment variable
try:
    from config import API_KEY
except ImportError:
    API_KEY = os.environ.get('FOOTBALL_API_KEY', '')
FCZ_TEAM_NAME = "FC Zürich"
FCZ_TEAM_ID = 684  # FC Zürich team ID in API-Football
SWISS_SUPER_LEAGUE_ID = 207  # Swiss Super League ID in API-Football


def format_date(date_str):
    """Format ISO date string to readable format"""
    if not date_str:
        return 'TBD'
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%d.%m.%Y %H:%M')
    except ValueError:
        return date_str


def get_fcz_stats():
    """
    Fetch FC Zürich statistics from API or return sample data
    """
    try:
        # Try to get data from API-Football
        if API_KEY:
            return get_stats_from_api()
    except Exception as e:
        app.logger.error(f"API Error: {e}")
    
    # Return sample/demo data if API is not available
    return get_sample_data()


def get_stats_from_api():
    """
    Fetch real data from API-Football (api-sports.io)
    Swiss Super League ID: 207
    FC Zürich team ID: 684
    """
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    base_url = 'https://v3.football.api-sports.io'
    
    # Get current season year
    current_year = datetime.now().year
    season = current_year if datetime.now().month >= 7 else current_year - 1
    
    stats = {
        'team_name': FCZ_TEAM_NAME,
        'league': 'Swiss Super League',
        'season': f'{season}/{str(season + 1)[-2:]}',
        'position': None,
        'played': 0,
        'won': 0,
        'drawn': 0,
        'lost': 0,
        'goals_for': 0,
        'goals_against': 0,
        'goal_difference': 0,
        'points': 0,
        'next_match': None,
        'standings': [],
        'recent_matches': []
    }
    
    # Get standings
    try:
        standings_url = f'{base_url}/standings'
        params = {'league': SWISS_SUPER_LEAGUE_ID, 'season': season}
        response = requests.get(standings_url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('response') and len(data['response']) > 0:
                league_data = data['response'][0].get('league', {})
                standings_data = league_data.get('standings', [])
                if standings_data and len(standings_data) > 0:
                    table = standings_data[0]  # First group (main standings)
                    formatted_standings = []
                    for team in table[:10]:  # Only process first 10 teams
                        team_data = team.get('team', {})
                        team_name = team_data.get('name', '')
                        team_id = team_data.get('id')
                        all_stats = team.get('all', {})
                        
                        formatted_team = {
                            'position': team.get('rank'),
                            'team': {
                                'name': team_name,
                                'crest': team_data.get('logo', '')
                            },
                            'playedGames': all_stats.get('played', 0),
                            'won': all_stats.get('win', 0),
                            'draw': all_stats.get('draw', 0),
                            'lost': all_stats.get('lose', 0),
                            'goalsFor': all_stats.get('goals', {}).get('for', 0),
                            'goalsAgainst': all_stats.get('goals', {}).get('against', 0),
                            'goalDifference': team.get('goalsDiff', 0),
                            'points': team.get('points', 0)
                        }
                        formatted_standings.append(formatted_team)
                        
                        # Check if this is FC Zürich by team ID
                        if team_id == FCZ_TEAM_ID:
                            stats['position'] = team.get('rank')
                            stats['played'] = all_stats.get('played', 0)
                            stats['won'] = all_stats.get('win', 0)
                            stats['drawn'] = all_stats.get('draw', 0)
                            stats['lost'] = all_stats.get('lose', 0)
                            stats['goals_for'] = all_stats.get('goals', {}).get('for', 0)
                            stats['goals_against'] = all_stats.get('goals', {}).get('against', 0)
                            stats['goal_difference'] = team.get('goalsDiff', 0)
                            stats['points'] = team.get('points', 0)
                    
                    stats['standings'] = formatted_standings
    except Exception as e:
        app.logger.error(f"Error fetching standings: {e}")
    
    # Get next match
    try:
        fixtures_url = f'{base_url}/fixtures'
        params = {'team': FCZ_TEAM_ID, 'next': 1}
        response = requests.get(fixtures_url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('response') and len(data['response']) > 0:
                match = data['response'][0]
                fixture = match.get('fixture', {})
                teams = match.get('teams', {})
                league = match.get('league', {})
                venue = fixture.get('venue', {})
                
                stats['next_match'] = {
                    'home_team': teams.get('home', {}).get('name', 'TBD'),
                    'away_team': teams.get('away', {}).get('name', 'TBD'),
                    'date': fixture.get('date', ''),
                    'competition': league.get('name', 'Swiss Super League'),
                    'venue': venue.get('name', 'TBD')
                }
    except Exception as e:
        app.logger.error(f"Error fetching next match: {e}")
    
    # Get recent matches
    try:
        fixtures_url = f'{base_url}/fixtures'
        params = {'team': FCZ_TEAM_ID, 'last': 5}
        response = requests.get(fixtures_url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('response'):
                recent = []
                for match in data['response']:
                    fixture = match.get('fixture', {})
                    teams = match.get('teams', {})
                    goals = match.get('goals', {})
                    
                    home_team = teams.get('home', {})
                    away_team = teams.get('away', {})
                    home_goals = goals.get('home', 0)
                    away_goals = goals.get('away', 0)
                    
                    # Determine opponent and result using team ID
                    is_home = home_team.get('id') == FCZ_TEAM_ID
                    opponent = away_team.get('name', '') if is_home else home_team.get('name', '')
                    
                    if is_home:
                        fcz_goals = home_goals
                        opp_goals = away_goals
                    else:
                        fcz_goals = away_goals
                        opp_goals = home_goals
                    
                    if fcz_goals > opp_goals:
                        result = 'W'
                    elif fcz_goals < opp_goals:
                        result = 'L'
                    else:
                        result = 'D'
                    
                    # Format date using helper function
                    match_date = fixture.get('date', '')
                    if match_date:
                        formatted = format_date(match_date)
                        # Convert to YYYY-MM-DD format for recent matches display
                        try:
                            dt = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
                            match_date = dt.strftime('%Y-%m-%d')
                        except ValueError:
                            match_date = formatted
                    
                    recent.append({
                        'opponent': opponent,
                        'result': result,
                        'score': f'{home_goals}-{away_goals}',
                        'date': match_date
                    })
                
                stats['recent_matches'] = recent
    except Exception as e:
        app.logger.error(f"Error fetching recent matches: {e}")
    
    return stats


def get_sample_data():
    """
    Return sample data for demonstration purposes
    Based on typical Swiss Super League statistics for season 2024/25
    """
    return {
        'team_name': FCZ_TEAM_NAME,
        'league': 'Swiss Super League',
        'season': '2024/25',
        'position': 5,
        'played': 15,
        'won': 6,
        'drawn': 4,
        'lost': 5,
        'goals_for': 22,
        'goals_against': 18,
        'goal_difference': 4,
        'points': 22,
        'next_match': {
            'home_team': 'FC Zürich',
            'away_team': 'BSC Young Boys',
            'date': '2024-12-07T17:30:00Z',
            'competition': 'Swiss Super League',
            'venue': 'Letzigrund'
        },
        'standings': [
            {'position': 1, 'team': {'name': 'FC Lugano', 'crest': ''}, 'playedGames': 15, 'won': 10, 'draw': 3, 'lost': 2, 'goalsFor': 28, 'goalsAgainst': 12, 'goalDifference': 16, 'points': 33},
            {'position': 2, 'team': {'name': 'FC Basel 1893', 'crest': ''}, 'playedGames': 15, 'won': 9, 'draw': 4, 'lost': 2, 'goalsFor': 30, 'goalsAgainst': 15, 'goalDifference': 15, 'points': 31},
            {'position': 3, 'team': {'name': 'Servette FC', 'crest': ''}, 'playedGames': 15, 'won': 8, 'draw': 4, 'lost': 3, 'goalsFor': 24, 'goalsAgainst': 14, 'goalDifference': 10, 'points': 28},
            {'position': 4, 'team': {'name': 'BSC Young Boys', 'crest': ''}, 'playedGames': 15, 'won': 7, 'draw': 5, 'lost': 3, 'goalsFor': 25, 'goalsAgainst': 16, 'goalDifference': 9, 'points': 26},
            {'position': 5, 'team': {'name': 'FC Zürich', 'crest': ''}, 'playedGames': 15, 'won': 6, 'draw': 4, 'lost': 5, 'goalsFor': 22, 'goalsAgainst': 18, 'goalDifference': 4, 'points': 22},
            {'position': 6, 'team': {'name': 'FC St. Gallen', 'crest': ''}, 'playedGames': 15, 'won': 5, 'draw': 5, 'lost': 5, 'goalsFor': 20, 'goalsAgainst': 20, 'goalDifference': 0, 'points': 20},
            {'position': 7, 'team': {'name': 'FC Luzern', 'crest': ''}, 'playedGames': 15, 'won': 5, 'draw': 4, 'lost': 6, 'goalsFor': 18, 'goalsAgainst': 22, 'goalDifference': -4, 'points': 19},
            {'position': 8, 'team': {'name': 'FC Sion', 'crest': ''}, 'playedGames': 15, 'won': 4, 'draw': 5, 'lost': 6, 'goalsFor': 16, 'goalsAgainst': 21, 'goalDifference': -5, 'points': 17},
            {'position': 9, 'team': {'name': 'Grasshopper Club', 'crest': ''}, 'playedGames': 15, 'won': 3, 'draw': 4, 'lost': 8, 'goalsFor': 14, 'goalsAgainst': 25, 'goalDifference': -11, 'points': 13},
            {'position': 10, 'team': {'name': 'FC Winterthur', 'crest': ''}, 'playedGames': 15, 'won': 2, 'draw': 4, 'lost': 9, 'goalsFor': 12, 'goalsAgainst': 28, 'goalDifference': -16, 'points': 10},
        ],
        'recent_matches': [
            {'opponent': 'FC Lugano', 'result': 'L', 'score': '1-2', 'date': '2024-11-23'},
            {'opponent': 'FC St. Gallen', 'result': 'W', 'score': '3-1', 'date': '2024-11-09'},
            {'opponent': 'Servette FC', 'result': 'D', 'score': '1-1', 'date': '2024-11-02'},
            {'opponent': 'FC Sion', 'result': 'W', 'score': '2-0', 'date': '2024-10-26'},
            {'opponent': 'FC Basel 1893', 'result': 'L', 'score': '0-1', 'date': '2024-10-19'},
        ],
        # Additional detailed statistics for 2024/25 season
        'home_stats': {
            'played': 8,
            'won': 4,
            'drawn': 2,
            'lost': 2,
            'goals_for': 14,
            'goals_against': 8,
            'points': 14
        },
        'away_stats': {
            'played': 7,
            'won': 2,
            'drawn': 2,
            'lost': 3,
            'goals_for': 8,
            'goals_against': 10,
            'points': 8
        },
        'monthly_stats': [
            {'month': 'Juli', 'played': 2, 'won': 1, 'drawn': 1, 'lost': 0, 'goals_for': 4, 'goals_against': 2, 'points': 4},
            {'month': 'August', 'played': 4, 'won': 2, 'drawn': 1, 'lost': 1, 'goals_for': 7, 'goals_against': 5, 'points': 7},
            {'month': 'September', 'played': 3, 'won': 1, 'drawn': 1, 'lost': 1, 'goals_for': 4, 'goals_against': 4, 'points': 4},
            {'month': 'Oktober', 'played': 3, 'won': 1, 'drawn': 0, 'lost': 2, 'goals_for': 3, 'goals_against': 4, 'points': 3},
            {'month': 'November', 'played': 3, 'won': 1, 'drawn': 1, 'lost': 1, 'goals_for': 4, 'goals_against': 3, 'points': 4},
        ],
        'points_progression': [4, 7, 10, 11, 14, 15, 16, 16, 17, 18, 18, 19, 22, 22, 22],
        'goals_by_matchday': {
            'scored': [2, 2, 1, 2, 1, 1, 1, 0, 1, 1, 0, 1, 3, 0, 1],
            'conceded': [1, 1, 2, 1, 1, 0, 1, 2, 1, 0, 2, 1, 1, 2, 2]
        },
        'top_scorers': [
            {'name': 'Jonathan Okita', 'goals': 6, 'assists': 3},
            {'name': 'Juan José Perea', 'goals': 5, 'assists': 2},
            {'name': 'Labinot Bajrami', 'goals': 4, 'assists': 4},
            {'name': 'Mirlind Kryeziu', 'goals': 3, 'assists': 1},
            {'name': 'Nikola Katic', 'goals': 2, 'assists': 0},
        ],
        'clean_sheets': 5,
        'avg_goals_per_match': 1.47,
        'avg_conceded_per_match': 1.20,
        'win_percentage': 40,
        'form_last_5': ['L', 'W', 'D', 'W', 'L']
    }


@app.route('/')
def index():
    """Main page showing FC Zürich statistics"""
    stats = get_fcz_stats()
    return render_template('index.html', stats=stats, format_date=format_date)


@app.route('/health')
def health():
    """Health check endpoint for Docker"""
    return {'status': 'healthy'}, 200


if __name__ == '__main__':
    # Debug mode is controlled via environment variable for security
    # In production, use gunicorn as specified in Dockerfile
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
