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
GLOBAL_LOG_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>All Mob Discoveries</title>
    <style>
        body { font-family: Arial; }
        .mob-list { display: flex; flex-wrap: wrap; }
        .mob-item { margin: 10px; text-align: center; }
        .mob-item img { width: 100px; height: 100px; object-fit: contain; }
    </style>
</head>
<body>
    <h1>All Mobs</h1>
    <div class="mob-list">
        {% for mob_id, mob in mobs.items() %}
        <div class="mob-item">
            <a href="/mob/{{ mob_id }}">
                <img src="/mob/{{ mob_id }}.png" alt="{{ mob.name }}"><br>
                {{ mob.name }}
            </a>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''
from flask import Flask, render_template_string, abort
import ssl
from mob_data import mob_metadata
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import summon_db

app = Flask(__name__)

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
    <title>{{ mob.name }}</title>
    <style>
        body { font-family: Arial; }
        .mob-detail { max-width: 600px; margin: auto; }
        .mob-detail img { width: 200px; height: 200px; object-fit: contain; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        .map-link { font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="mob-detail">
        <h1>{{ mob.name }}</h1>
        <img src="/mob/{{ mob_id }}.png" alt="{{ mob.name }}"><br>
        <p>{{ mob.description }}</p>
        <h2>Summoning Log</h2>
        <table>
            <tr><th>Player</th><th>Date</th><th>Location</th></tr>
            {% for entry in discoveries %}
            <tr>
                <td>{{ entry.player }}</td>
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


# Home page redirects to the global log
@app.route('/')
def home():
    return render_template_string(GLOBAL_LOG_TEMPLATE, mobs=mob_metadata)

# Global log page (all mobs)
@app.route('/log')
def global_log():
    return render_template_string(GLOBAL_LOG_TEMPLATE, mobs=mob_metadata)

@app.route('/mob/<mob_id>')
def mob_detail(mob_id):
    mob = mob_metadata.get(mob_id)
    if not mob:
        abort(404)
    db_discoveries = summon_db.get_summons_by_mob(mob_id)
    discoveries = []
    for entry in db_discoveries:
        discoveries.append({
            'player': entry.get('summoning_player', ''),
            'timestamp': entry.get('timestamp_utc', ''),
            'gps_lat': entry.get('gps_lat'),
            'gps_lon': entry.get('gps_lon'),
        })
    return render_template_string(DETAIL_TEMPLATE, mob=mob, discoveries=discoveries, mob_id=mob_id)

@app.route('/mob/<path:filename>')
def mob_image(filename):
    # Serve mob images from the mob/ directory
    return app.send_static_file(os.path.join('mob', filename))

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('web/server.crt', 'web/server.key')
    app.run(host='0.0.0.0', port=8080, ssl_context=context)
