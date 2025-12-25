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
    </style>
</head>
<body>
    <div class="mob-detail">
        <h1>{{ mob.name }}</h1>
        <img src="/mob/{{ mob_id }}.png" alt="{{ mob.name }}"><br>
        <p>{{ mob.description }}</p>
        <h2>Players Who Found This Mob</h2>
        <table>
            <tr><th>Player</th><th>Timestamp</th><th>NFC Token</th><th>GPS</th></tr>
            {% for entry in discoveries %}
            <tr>
                <td>{{ entry.player }}</td>
                <td>{{ entry.timestamp }}</td>
                <td>{{ entry.nfc_token }}</td>
                <td>{{ entry.gps or '' }}</td>
            </tr>
            {% else %}
            <tr><td colspan="4">No discoveries yet.</td></tr>
            {% endfor %}
        </table>
        <p><a href="/">Back to list</a></p>
    </div>
</body>
</html>
'''

@app.route('/')
def mob_list():
    return render_template_string(LIST_TEMPLATE, mobs=mob_metadata)

@app.route('/mob/<mob_id>')
def mob_detail(mob_id):
    mob = mob_metadata.get(mob_id)
    if not mob:
        abort(404)
    # Fetch discoveries from the database
    db_discoveries = summon_db.get_summons_by_mob(mob_id)
    # Map DB fields to template fields
    discoveries = []
    for entry in db_discoveries:
        discoveries.append({
            'player': entry.get('summoning_player', ''),
            'timestamp': entry.get('timestamp_utc', ''),
            'nfc_token': entry.get('summoned_player', ''),
            'gps': f"{entry.get('gps_lat','')},{entry.get('gps_lon','')}" if entry.get('gps_lat') and entry.get('gps_lon') else ''
        })
    return render_template_string(DETAIL_TEMPLATE, mob=mob, discoveries=discoveries)

@app.route('/mob/<path:filename>')
def mob_image(filename):
    # Serve mob images from the mob/ directory
    return app.send_static_file(os.path.join('mob', filename))

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('web/server.crt', 'web/server.key')
    app.run(host='0.0.0.0', port=8080, ssl_context=context)
