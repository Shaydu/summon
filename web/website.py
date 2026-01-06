from flask import Flask, render_template_string, abort, send_from_directory, jsonify
import ssl
from mob_data import mob_metadata
import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import summon_db
from tokens_template import TOKENS_MAP_TEMPLATE

app = Flask(__name__, static_folder='mob_images', static_url_path='/mob_images')

PLAYER_LOG_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
        <title>Summon - Player Log: {{ player_name }}</title>
        <style>
                :root {
                    --summon-purple: #8B4CB8;
                    --summon-teal: #1BC9C3;
                }
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                    background: #ffffff;
                    color: #333;
                }
                .site-header {
                    background: var(--summon-purple);
                    color: white;
                    padding: 20px 30px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }
                .site-header h1 {
                    font-size: 32px;
                    font-weight: bold;
                    letter-spacing: 1px;
                    margin: 0;
                    color: white;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                .logo-circle {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background: white;
                    color: var(--summon-purple);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 24px;
                }
                .site-header .tagline {
                    font-size: 14px;
                    color: rgba(255, 255, 255, 0.9);
                    margin-top: 5px;
                }
                .player-log { 
                    max-width: 1000px; 
                    margin: 30px auto;
                    padding: 0 30px;
                }
                .player-log h2 {
                    color: var(--summon-purple);
                    margin-bottom: 20px;
                }
                table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin-top: 20px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    border-radius: 8px;
                    overflow: hidden;
                }
                th { 
                    background: var(--summon-purple);
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                }
                td { 
                    border: 1px solid #f0f0f0; 
                    padding: 10px; 
                    text-align: left; 
                }
                tr:hover { background: #f9f9f9; }
                .mob-link { 
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    color: inherit;
                    text-decoration: none;
                }
                .mob-link:hover { color: var(--summon-purple); }
                .mob-link img { 
                    width: 50px; 
                    height: 50px; 
                    object-fit: contain;
                    border: 1px solid #f0f0f0;
                    border-radius: 6px;
                    padding: 4px;
                }
                .map-link { 
                    color: var(--summon-teal);
                    text-decoration: none;
                    font-weight: 500;
                }
                .map-link:hover { text-decoration: underline; }
                .back-link {
                    display: inline-block;
                    margin-top: 20px;
                    color: var(--summon-purple);
                    text-decoration: none;
                    font-weight: 600;
                }
                .back-link:hover { text-decoration: underline; }
        </style>
</head>
<body>
        <div class="site-header">
            <h1><span class="logo-circle">◈</span>Summon</h1>
            <div class="tagline">Player Discovery Log</div>
        </div>
        <div class="player-log">
                <h2>Player Log: {{ player_name }}</h2>
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
                <a href="/log" class="back-link">← Back to all mobs</a>
        </div>
</body>
</html>
'''

GLOBAL_LOG_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Summon - Mob Browser</title>
    <style>
        :root {
            --summon-purple: #8B4CB8;
            --summon-teal: #1BC9C3;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            background: #ffffff;
            color: #333;
        }
        .site-header {
            background: var(--summon-purple);
            color: white;
            padding: 25px 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .site-header h1 {
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 1px;
            margin: 0;
            color: white;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .logo-circle {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: white;
            color: var(--summon-purple);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
        }
        .site-header .tagline {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9);
            margin-top: 5px;
        }
        .content {
            padding: 30px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .header { margin-bottom: 25px; }
        .header h2 {
            color: var(--summon-purple);
            font-size: 24px;
            margin-bottom: 15px;
        }
        .toggle-container { margin: 20px 0; }
        .toggle-btn { 
            padding: 12px 24px;
            margin-right: 10px;
            border: 2px solid var(--summon-purple);
            background: white;
            color: var(--summon-purple);
            cursor: pointer;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.2s;
        }
        .toggle-btn.active { 
            background: var(--summon-purple);
            color: white;
        }
        .toggle-btn:hover { 
            background: var(--summon-purple);
            color: white;
        }
        .toggle-btn.active:hover { 
            background: #7339a3;
        }
        .mob-list { display: flex; flex-wrap: wrap; gap: 20px; }
        .mob-item { 
            width: 150px; 
            text-align: center; 
            border: 2px solid #f0f0f0;
            padding: 15px;
            border-radius: 12px;
            background: white;
            transition: all 0.2s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .mob-item:hover { 
            border-color: var(--summon-purple);
            box-shadow: 0 4px 12px rgba(139, 76, 184, 0.3);
            transform: translateY(-2px);
        }
        .mob-item img { 
            width: 100px; 
            height: 100px; 
            object-fit: contain;
            display: block;
            margin: 0 auto 10px;
        }
        .mob-name { 
            font-weight: 600; 
            color: #333;
            text-decoration: none;
            margin-top: 8px;
        }
        .mob-count {
            <span class="logo-circle">◈</span>font-size: 0.85em;
            color: var(--summon-teal);
            margin-top: 5px;
            font-weight: 500;
        }
        .undiscovered {
            opacity: 0.5;
        }
        a { text-decoration: none; color: inherit; }
    </style>
</head>
<body>
    <div class="site-header">
        <h1><span class="logo-circle">◈</span>Summon</h1>
        <div class="tagline">NFC Token Discovery & Mob Browser</div>
    </div>
    <div class="content">
    <div class="header">
        <h2>Minecraft Mobs</h2>
        <div class="toggle-container">
            <button class="toggle-btn {% if not show_discovered_only %}active{% endif %}" onclick="window.location.href='/'">
                All Types ({{ all_mobs_count }})
            </button>
            <button class="toggle-btn {% if show_discovered_only %}active{% endif %}" onclick="window.location.href='/?discovered_only=true'">
                Discovered Only ({{ discovered_count }})
            </button>
        </div>
        <p>
            {% if show_discovered_only %}
                Showing {{ mobs|length }} discovered mob types ({{ total_count }} total summons)
            {% else %}
                Showing all {{ all_mobs_count }} mob types with find counts — {{ discovered_count }} discovered ({{ total_count }} summons), {{ all_mobs_count - discovered_count }} undiscovered
            {% endif %}
        </p>
    </div>
    <div class="mob-list">
        {% for mob in mobs %}
        <div class="mob-item {% if mob.count == 0 %}undiscovered{% endif %}">
            <a href="/mob/{{ mob.mob_id }}">
                <img src="/mob_images/{{ mob.mob_id }}.png" alt="" onerror="if(this.src.indexOf('/mob_images/')>-1)this.src='/mob/{{ mob.mob_id }}.png';else this.style.display='none';">
                <div class="mob-name">{{ mob.mob_name }}</div>
                <div class="mob-count">
                    {% if mob.count > 0 %}
                        {{ mob.count }} summon{{ 's' if mob.count != 1 else '' }}
                    {% else %}
                        Not discovered
                    {% endif %}
                </div>
            </a>
        </div>
        {% endfor %}
    </div>
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
            <img src="/mob_images/{{ mob_id }}.png" alt="{{ mob_name }}" onerror="if(this.src.indexOf('/mob_images/')>-1)this.src='/mob/{{ mob_id }}.png';else this.style.display='none';">
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


# Home page - show all mobs with counts
@app.route('/')
def home():
    from flask import request
    # Default to showing all types, filter to discovered only if specified
    show_discovered_only = request.args.get('discovered_only', '').lower() == 'true'
    
    # Get summon counts for discovered mobs
    all_summons = summon_db.get_all_summons()
    mob_counts = {}
    for summon in all_summons:
        mob_id = summon.get('summoned_object_type', 'unknown')
        mob_counts[mob_id] = mob_counts.get(mob_id, 0) + 1
    
    discovered_count = len(mob_counts)
    total_count = sum(mob_counts.values())
    
    # Get all mobs from database
    all_db_mobs = summon_db.get_all_mobs()
    mobs = []
    for mob in all_db_mobs:
        minecraft_id = mob.get('minecraft_id', '')
        mob_name = mob.get('name', minecraft_id.replace('_', ' ').title())
        count = mob_counts.get(minecraft_id, 0)
        
        # Skip undiscovered mobs if filtering to discovered only
        if show_discovered_only and count == 0:
            continue
            
        mobs.append({
            'mob_id': minecraft_id,
            'mob_name': mob_name,
            'count': count
        })
    
    # Sort by count (highest first), then alphabetically by name
    mobs.sort(key=lambda x: (-x['count'], x['mob_name']))
    
    all_mobs_count = len(all_db_mobs)
    
    return render_template_string(GLOBAL_LOG_TEMPLATE, 
                                 mobs=mobs, 
                                 total_count=total_count,
                                 discovered_count=discovered_count,
                                 all_mobs_count=all_mobs_count,
                                 show_discovered_only=show_discovered_only)

# Global log page - redirects to home
@app.route('/log')
def global_log():
    from flask import redirect
    return redirect('/')

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
@app.route('/tokens')
def tokens_map():
    """Display all tokens on an interactive map"""
    try:
        # Get all tokens from database with GPS coordinates
        all_tokens = summon_db.get_all_tokens(limit=1000)
        
        # Filter tokens with GPS coordinates
        tokens_with_gps = [
            t for t in all_tokens 
            if t.get('gps_write_lat') is not None and t.get('gps_write_lon') is not None
        ]
        
        # Calculate statistics
        total_tokens = len(tokens_with_gps)
        summon_count = sum(1 for t in tokens_with_gps if t.get('action_type') == 'summon_entity')
        give_count = sum(1 for t in tokens_with_gps if t.get('action_type') == 'give_item')
        time_count = sum(1 for t in tokens_with_gps if t.get('action_type') == 'set_time')
        
        # Calculate center point (average of all positions)
        if total_tokens > 0:
            center_lat = sum(t['gps_write_lat'] for t in tokens_with_gps) / total_tokens
            center_lon = sum(t['gps_write_lon'] for t in tokens_with_gps) / total_tokens
        else:
            center_lat = 40.7580  # Default to Fort Collins
            center_lon = -105.3009
        
        # Prepare token data for JavaScript (get mob/item metadata)
        token_data = []
        for token in tokens_with_gps:
            token_info = {
                'token_id': str(token['token_id']),
                'action_type': token['action_type'],
                'lat': float(token['gps_write_lat']),
                'lon': float(token['gps_write_lon']),
                'written_by': token.get('written_by'),
                'written_at': token.get('written_at').isoformat() if token.get('written_at') else None,
                'entity': token.get('entity'),
                'item': token.get('item'),
            }
            
            # Get metadata from mobs or items tables
            if token['action_type'] == 'summon_entity' and token.get('entity'):
                mobs = summon_db.get_all_mobs()
                mob = next((m for m in mobs if m.get('minecraft_id') == token['entity']), None)
                if mob:
                    token_info['name'] = mob.get('name', token['entity'])
                    token_info['rarity'] = mob.get('rarity')
                    token_info['mob_type'] = mob.get('mob_type')
                    token_info['image_url'] = mob.get('image_url')
            
            elif token['action_type'] == 'give_item' and token.get('item'):
                items = summon_db.get_all_items()
                item = next((i for i in items if i.get('minecraft_id') == token['item']), None)
                if item:
                    token_info['name'] = item.get('name', token['item'])
                    token_info['rarity'] = item.get('rarity')
                    token_info['image_url'] = item.get('image_url')
            
            token_data.append(token_info)
        
        return render_template_string(
            TOKENS_MAP_TEMPLATE,
            tokens_json=json.dumps(token_data),
            total_tokens=total_tokens,
            summon_count=summon_count,
            give_count=give_count,
            time_count=time_count,
            center_lat=center_lat,
            center_lon=center_lon
        )
    
    except Exception as e:
        return f"Error loading token map: {str(e)}", 500

@app.route('/api/tokens-data')
def tokens_data():
    """API endpoint for fetching token data (for auto-refresh)"""
    try:
        # Get all tokens with GPS coordinates
        all_tokens = summon_db.get_all_tokens(limit=1000)
        tokens_with_gps = [
            t for t in all_tokens 
            if t.get('gps_write_lat') is not None and t.get('gps_write_lon') is not None
        ]
        
        # Prepare token data with metadata
        token_data = []
        for token in tokens_with_gps:
            token_info = {
                'token_id': str(token['token_id']),
                'action_type': token['action_type'],
                'lat': float(token['gps_write_lat']),
                'lon': float(token['gps_write_lon']),
                'written_by': token.get('written_by'),
                'written_at': token.get('written_at').isoformat() if token.get('written_at') else None,
                'entity': token.get('entity'),
                'item': token.get('item'),
            }
            
            # Get metadata
            if token['action_type'] == 'summon_entity' and token.get('entity'):
                mobs = summon_db.get_all_mobs()
                mob = next((m for m in mobs if m.get('minecraft_id') == token['entity']), None)
                if mob:
                    token_info['name'] = mob.get('name', token['entity'])
                    token_info['rarity'] = mob.get('rarity')
                    token_info['mob_type'] = mob.get('mob_type')
                    token_info['image_url'] = mob.get('image_url')
            
            elif token['action_type'] == 'give_item' and token.get('item'):
                items = summon_db.get_all_items()
                item = next((i for i in items if i.get('minecraft_id') == token['item']), None)
                if item:
                    token_info['name'] = item.get('name', token['item'])
                    token_info['rarity'] = item.get('rarity')
                    token_info['image_url'] = item.get('image_url')
            
            token_data.append(token_info)
        
        return jsonify({'tokens': token_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('web/server.crt', 'web/server.key')
    app.run(host='0.0.0.0', port=8080, ssl_context=context)

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('web/server.crt', 'web/server.key')
    app.run(host='0.0.0.0', port=8080, ssl_context=context)
