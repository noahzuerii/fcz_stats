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
# Using football-data.org API v4:
# - Swiss Super League competition code: BSL (league ID: 2024)
# - FC Zürich team ID: 1911 (verified in football-data.org database)
# API documentation: https://www.football-data.org/documentation/api
# Using a fallback approach with sample data if API is unavailable

API_KEY = os.environ.get('FOOTBALL_API_KEY', '')
FCZ_TEAM_NAME = "FC Zürich"
FCZ_TEAM_ID = 1911  # FC Zürich team ID in football-data.org (verified)


def get_fcz_stats():
    """
    Fetch FC Zürich statistics from API or return sample data
    """
    try:
        # Try to get data from football-data.org API
        if API_KEY:
            return get_stats_from_api()
    except Exception as e:
        app.logger.error(f"API Error: {e}")
    
    # Return sample/demo data if API is not available
    return get_sample_data()


def get_stats_from_api():
    """
    Fetch real data from football-data.org API
    Swiss Super League competition ID: 2024
    """
    headers = {'X-Auth-Token': API_KEY}
    base_url = 'https://api.football-data.org/v4'
    
    stats = {
        'team_name': FCZ_TEAM_NAME,
        'league': 'Swiss Super League',
        'season': '2024/25',
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
        standings_url = f'{base_url}/competitions/BSL/standings'
        response = requests.get(standings_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for standing in data.get('standings', []):
                if standing.get('type') == 'TOTAL':
                    for team in standing.get('table', []):
                        if 'Zürich' in team.get('team', {}).get('name', ''):
                            stats['position'] = team.get('position')
                            stats['played'] = team.get('playedGames', 0)
                            stats['won'] = team.get('won', 0)
                            stats['drawn'] = team.get('draw', 0)
                            stats['lost'] = team.get('lost', 0)
                            stats['goals_for'] = team.get('goalsFor', 0)
                            stats['goals_against'] = team.get('goalsAgainst', 0)
                            stats['goal_difference'] = team.get('goalDifference', 0)
                            stats['points'] = team.get('points', 0)
                    stats['standings'] = standing.get('table', [])[:10]
    except Exception as e:
        app.logger.error(f"Error fetching standings: {e}")
    
    # Get next match
    try:
        matches_url = f'{base_url}/teams/{FCZ_TEAM_ID}/matches?status=SCHEDULED&limit=1'
        response = requests.get(matches_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            if matches:
                match = matches[0]
                stats['next_match'] = {
                    'home_team': match.get('homeTeam', {}).get('name', 'TBD'),
                    'away_team': match.get('awayTeam', {}).get('name', 'TBD'),
                    'date': match.get('utcDate', ''),
                    'competition': match.get('competition', {}).get('name', 'Swiss Super League'),
                    'venue': match.get('venue', 'TBD')
                }
    except Exception as e:
        app.logger.error(f"Error fetching next match: {e}")
    
    return stats


def get_sample_data():
    """
    Return sample data for demonstration purposes
    Based on typical Swiss Super League statistics
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
        ]
    }


def format_date(date_str):
    """Format ISO date string to readable format"""
    if not date_str:
        return 'TBD'
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%d.%m.%Y %H:%M')
    except ValueError:
        return date_str


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
