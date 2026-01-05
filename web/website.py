from flask import Flask, render_template_string, abort, send_from_directory
import ssl
from mob_data import mob_metadata
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import summon_db

app = Flask(__name__, static_folder='mob_images', static_url_path='/mob_images')

PLAYER_LOG_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
        <title>Player Log: {{ player_name }}</title>
        <style>
                body { font-family: Arial; }
                .player-log { max-width: 800px; margin: auto; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
                .mob-link img { width: 50px; height: 50px; object-fit: contain; vertical-align: middle; }
                .map-link { font-size: 0.9em; }
        </style>
</head>
<body>
        <div class="player-log">
                <h1>Player Log: {{ player_name }}</h1>
                <table>
                        <tr><th>Mob/Item</th><th>Date</th><th>Location</th></tr>
                        {% for entry in discoveries %}
                        <tr>
                                <td>
                                    <a class="mob-link" href="/mob/{{ entry.mob_id }}">
                                        <img src="/mob/{{ entry.mob_id }}.png" alt="{{ entry.mob_id }}"> {{ entry.mob_id }}
                                    </a>
                                </td>
                                <td>{{ entry.timestamp }}</td>
                                <td>
                                    {% if entry.gps_lat and entry.gps_lon %}
                                        <a class="map-link" href="https://maps.google.com/?q={{ entry.gps_lat }},{{ entry.gps_lon }}" target="_blank">{{ entry.gps_lat }},{{ entry.gps_lon }}</a>
                                    {% else %}
                                        —
                                    {% endif %}
                                </td>
                        </tr>
                        {% else %}
                        <tr><td colspan="3">No discoveries yet.</td></tr>
                        {% endfor %}
                </table>
                <p><a href="/log">Back to all mobs</a></p>
        </div>
</body>
</html>
'''

GLOBAL_LOG_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>All Mob Discoveries</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        .mob-list { display: flex; flex-wrap: wrap; gap: 15px; }
        .mob-item { 
            width: 150px; 
            text-align: center; 
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 5px;
            background: #f9f9f9;
        }
        .mob-item:hover { background: #e9e9e9; }
        .mob-item img { 
            width: 100px; 
            height: 100px; 
            object-fit: contain;
            display: block;
            margin: 0 auto 10px;
        }
        .mob-name { 
            font-weight: bold; 
            color: #333;
            text-decoration: none;
        }
        .mob-count {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        a { text-decoration: none; color: inherit; }
    </style>
</head>
<body>
    <h1>All Discovered Mobs</h1>
    <p>{{ total_count }} total summons across {{ mobs|length }} different mob types</p>
    <div class="mob-list">
        {% for mob in mobs %}
        <div class="mob-item">
            <a href="/mob/{{ mob.mob_id }}">
                <img src="/mob_images/{{ mob.mob_id }}.png" alt="" onerror="this.src='/mob/{{ mob.mob_id }}.png'">
                <div class="mob-name">{{ mob.mob_id }}</div>
                <div class="mob-count">{{ mob.count }} summon{{ 's' if mob.count != 1 else '' }}</div>
            </a>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

# Player log page
@app.route('/player/<player_name>')
def player_log(player_name):
    db_discoveries = summon_db.get_summons_by_player(player_name)
    discoveries = []
    for entry in db_discoveries:
        discoveries.append({
            'mob_id': entry.get('summoned_object_type', ''),
            'timestamp': entry.get('timestamp_utc', ''),
            'gps_lat': entry.get('gps_lat'),
            'gps_lon': entry.get('gps_lon'),
        })
    return render_template_string(PLAYER_LOG_TEMPLATE, player_name=player_name, discoveries=discoveries)

LIST_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Mobs List</title>
    <style>
        body { font-family: Arial; }
        .mob-list { display: flex; flex-wrap: wrap; }
        .mob-item { margin: 10px; text-align: center; }
        .mob-item img { width: 100px; height: 100px; object-fit: contain; }
    </style>
</head>
<body>
    <h1>Minecraft Mobs</h1>
    <div class="mob-list">
        {% for mob_id, mob in mobs.items() %}
        <div class="mob-item">
            <a href="/mob/{{ mob_id }}">
                <img src="/{{ mob.image }}" alt="{{ mob.name }}"><br>
                {{ mob.name }}
            </a>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

DETAIL_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ mob_name }}</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #f5f5f5; }
        .mob-detail { max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .mob-header { display: flex; align-items: center; gap: 30px; margin-bottom: 30px; border-bottom: 2px solid #ddd; padding-bottom: 20px; }
        .mob-header img { width: 200px; height: 200px; object-fit: contain; border: 2px solid #ddd; border-radius: 8px; padding: 10px; background: #fafafa; }
        .mob-info { flex: 1; }
        .mob-info h1 { margin: 0 0 10px 0; font-size: 2em; color: #333; text-transform: capitalize; }
        .mob-stats { color: #666; font-size: 1.1em; }
        h2 { color: #333; margin: 30px 0 15px 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { background: #f0f0f0; font-weight: bold; padding: 12px; text-align: left; border-bottom: 2px solid #ddd; position: sticky; top: 0; }
        td { border: 1px solid #eee; padding: 10px; vertical-align: top; }
        tr:hover { background: #f9f9f9; }
        .action-badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; text-transform: uppercase; }
        .action-summon { background: #4CAF50; color: white; }
        .action-spawn { background: #2196F3; color: white; }
        .action-give { background: #FF9800; color: white; }
        .action-default { background: #757575; color: white; }
        .map-link { color: #0366d6; text-decoration: none; }
        .map-link:hover { text-decoration: underline; }
        .back-link { display: inline-block; margin-top: 20px; color: #0366d6; text-decoration: none; }
        .back-link:hover { text-decoration: underline; }
        .empty-message { text-align: center; padding: 40px; color: #999; }
        .timestamp { white-space: nowrap; }
    </style>
</head>
<body>
    <div class="mob-detail">
        <div class="mob-header">
            <img src="/mob_images/{{ mob_id }}.png" alt="{{ mob_name }}" onerror="this.src='/mob/{{ mob_id }}.png'">
            <div class="mob-info">
                <h1>{{ mob_name }}</h1>
                <div class="mob-stats">
                    <strong>{{ total_count }}</strong> total summons
                    {% if action_counts %}
                    <br>
                    {% for action, count in action_counts.items() %}
                        {{ action }}: {{ count }}{% if not loop.last %}, {% endif %}
                    {% endfor %}
                    {% endif %}
                </div>
            </div>
        </div>

        <h2>Summon History</h2>
        <table>
            <tr>
                <th>Action</th>
                <th>Player</th>
                <th>Target</th>
                <th>Date</th>
                <th>Location</th>
            </tr>
            {% for entry in all_entries %}
            <tr>
                <td>
                    <span class="action-badge action-{{ entry.action_type }}">{{ entry.action_type }}</span>
                </td>
                <td>{{ entry.summoning_player }}</td>
                <td>{{ entry.summoned_player }}</td>
                <td class="timestamp">{{ entry.timestamp }}</td>
                <td>
                  {% if entry.gps_lat and entry.gps_lon %}
                    <a class="map-link" href="https://maps.google.com/?q={{ entry.gps_lat }},{{ entry.gps_lon }}" target="_blank">
                        📍 {{ "%.4f"|format(entry.gps_lat) }}, {{ "%.4f"|format(entry.gps_lon) }}
                    </a>
                  {% else %}
                    —
                  {% endif %}
                </td>
            </tr>
            {% else %}
            <tr><td colspan="5" class="empty-message">No summons recorded yet</td></tr>
            {% endfor %}
        </table>

        <a href="/" class="back-link">← Back to all mobs</a>
    </div>
</body>
</html>
'''


# Home page redirects to the global log
@app.route('/')
def home():
    # Get all unique mob types from database with counts
    all_summons = summon_db.get_all_summons()
    mob_counts = {}
    for summon in all_summons:
        mob_id = summon.get('summoned_object_type', 'unknown')
        mob_counts[mob_id] = mob_counts.get(mob_id, 0) + 1
    
    # Convert to list for template
    mobs = [{'mob_id': mob_id, 'count': count} for mob_id, count in sorted(mob_counts.items())]
    total_count = sum(mob_counts.values())
    
    return render_template_string(GLOBAL_LOG_TEMPLATE, mobs=mobs, total_count=total_count)

# Global log page (all mobs)
@app.route('/log')
def global_log():
    # Get all unique mob types from database with counts
    all_summons = summon_db.get_all_summons()
    mob_counts = {}
    for summon in all_summons:
        mob_id = summon.get('summoned_object_type', 'unknown')
        mob_counts[mob_id] = mob_counts.get(mob_id, 0) + 1
    
    # Convert to list for template
    mobs = [{'mob_id': mob_id, 'count': count} for mob_id, count in sorted(mob_counts.items())]
    total_count = sum(mob_counts.values())
    
    return render_template_string(GLOBAL_LOG_TEMPLATE, mobs=mobs, total_count=total_count)

@app.route('/mob/<mob_id>')
def mob_detail(mob_id):
    # Get all summons for this mob from database
    db_discoveries = summon_db.get_summons_by_mob(mob_id)
    
    if not db_discoveries:
        # Mob exists but no summons yet, or doesn't exist
        return render_template_string(DETAIL_TEMPLATE, 
                                     mob_id=mob_id,
                                     mob_name=mob_id.replace('_', ' ').title(),
                                     total_count=0,
                                     action_counts={},
                                     actions=[],
                                     all_entries=[],
                                     entries_by_action={})
    
    # Organize data by action type
    entries_by_action = {}
    action_counts = {}
    all_entries = []
    
    for entry in db_discoveries:
        action_type = entry.get('action_type', 'summon')
        if action_type not in entries_by_action:
            entries_by_action[action_type] = []
            action_counts[action_type] = 0
        
        entry_data = {
            'action_type': action_type,
            'summoning_player': entry.get('summoning_player', ''),
            'summoned_player': entry.get('summoned_player', ''),
            'timestamp': entry.get('timestamp_utc', ''),
            'gps_lat': entry.get('gps_lat'),
            'gps_lon': entry.get('gps_lon'),
        }
        entries_by_action[action_type].append(entry_data)
        action_counts[action_type] += 1
        all_entries.append(entry_data)
    
    actions = sorted(entries_by_action.keys())
    total_count = len(all_entries)
    mob_name = mob_id.replace('_', ' ').title()
    
    return render_template_string(DETAIL_TEMPLATE,
                                 mob_id=mob_id,
                                 mob_name=mob_name,
                                 total_count=total_count,
                                 action_counts=action_counts,
                                 actions=actions,
                                 all_entries=all_entries,
                                 entries_by_action=entries_by_action)

@app.route('/mob/<filename>')
def serve_mob_image(filename):
    """Serve mob images from the mob/ directory as fallback"""
    mob_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mob'))
    return send_from_directory(mob_dir, filename)

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('web/server.crt', 'web/server.key')
    app.run(host='0.0.0.0', port=8080, ssl_context=context)
