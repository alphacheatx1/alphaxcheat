from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
import datetime
import logging
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)

logging.basicConfig(level=logging.INFO)

ADMIN_USER = "CHEAT"
ADMIN_PASS = "ALPHA"

update_panel_active = False
UPDATE_URL = "https://example.com/alpha_cheat_update.apk"

SERVER_START_TIME = datetime.datetime.now()

valid_keys = {
    "ALPHA": {
        "expiry": datetime.datetime.now() + datetime.timedelta(days=30),
        "max_devices": 2,
        "connected_ips": set()
    }
}

system_logs = []
def add_log(message, log_type="info"):
    time_str = datetime.datetime.now().strftime("%H:%M:%S")
    system_logs.insert(0, {"time": time_str, "msg": message, "type": log_type})
    if len(system_logs) > 10:
        system_logs.pop()

add_log("Serveur ALPHA CHEAT initialisé sans erreurs.", "success")

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALPHA CHEAT - Dashboard Sécurisé</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-dark: #000000;
            --card-bg: rgba(8, 8, 14, 0.9);
            --neon-cyan: #00f3ff;
            --neon-purple: #bf00ff;
            --neon-red: #ff0055;
            --text-main: #ffffff;
            --text-muted: #8a8a9e;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Rajdhani', sans-serif; }
        
        body { 
            background-color: var(--bg-dark); 
            color: var(--text-main); 
            display: flex; height: 100vh; overflow: hidden; 
        }

        .login-wrapper { display: flex; justify-content: center; align-items: center; width: 100%; height: 100vh; z-index: 1; position: relative; }
        
        .neon-border {
            position: relative; border-radius: 12px; background: var(--card-bg);
            padding: 30px; border: 1px solid rgba(0, 243, 255, 0.3);
            box-shadow: 0 0 20px rgba(191, 0, 255, 0.2);
        }

        .sidebar { 
            width: 260px; background: #030305; 
            border-right: 1px solid rgba(191, 0, 255, 0.25); 
            display: flex; flex-direction: column; justify-content: space-between; z-index: 2; 
        }
        
        .main-content { flex: 1; display: flex; flex-direction: column; overflow-y: auto; z-index: 2; }

        .topbar { 
            height: 80px; padding: 0 30px; display: flex; justify-content: space-between; align-items: center; 
            border-bottom: 1px solid rgba(255, 255, 255, 0.05); background: #020203; flex-shrink: 0;
        }
        
        .title-neon {
            font-family: 'Orbitron', sans-serif; font-weight: 900;
            background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }

        .content-body { padding: 25px 30px; max-width: 1200px; width: 100%; margin: 0 auto; }

        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px; }
        .stat-card { 
            background: #040407; border: 1px solid rgba(0, 243, 255, 0.2); 
            border-radius: 10px; padding: 18px; display: flex; align-items: center; gap: 15px; 
        }
        .stat-icon { 
            width: 45px; height: 45px; border-radius: 10px; background: rgba(191, 0, 255, 0.15); 
            display: flex; justify-content: center; align-items: center; font-size: 20px; color: var(--neon-cyan);
        }
        .stat-info h4 { font-size: 11px; color: var(--text-muted); font-weight: 700; margin-bottom: 3px; }
        .stat-info .num { font-size: 20px; font-weight: 900; color: #fff; font-family: 'Orbitron', sans-serif; }

        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .card-header h3 { font-size: 16px; font-weight: 700; display: flex; align-items: center; gap: 8px; font-family: 'Orbitron', sans-serif; }

        .input-group { position: relative; margin-bottom: 15px; width: 100%; text-align: left; }
        .input-group label { display: block; font-size: 12px; color: var(--text-muted); margin-bottom: 5px; font-weight: 700; }
        input { 
            width: 100%; padding: 12px 15px; background: #020204; 
            border: 1px solid rgba(0, 243, 255, 0.3); color: #fff; border-radius: 8px; 
            font-size: 14px; outline: none; transition: 0.3s;
        }
        input:focus { border-color: var(--neon-cyan); box-shadow: 0 0 10px rgba(0, 243, 255, 0.3); }

        .btn-gradient { 
            background: linear-gradient(90deg, var(--neon-purple), var(--neon-cyan)); 
            color: #fff; border: none; padding: 12px 20px; border-radius: 8px; 
            font-size: 14px; font-weight: 700; cursor: pointer; transition: 0.3s; 
            display: flex; justify-content: center; align-items: center; gap: 8px; width: 100%;
            font-family: 'Orbitron', sans-serif;
        }
        .btn-gradient:hover { box-shadow: 0 0 15px var(--neon-purple); }

        .btn-update-panel {
            background: linear-gradient(90deg, #00e676, #00b0ff);
            color: #000; font-weight: 900; border: none; padding: 8px 14px;
            border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-flex;
            align-items: center; gap: 6px; font-family: 'Orbitron', sans-serif; font-size: 11px;
        }
        .btn-update-panel.active-alert {
            background: linear-gradient(90deg, var(--neon-red), #ff5252) !important;
            color: #fff !important;
            box-shadow: 0 0 12px var(--neon-red);
        }

        .key-list { display: flex; flex-direction: column; gap: 10px; }
        .key-item { 
            background: #040407; border: 1px solid rgba(255,255,255,0.05); 
            border-radius: 8px; padding: 12px 15px; display: flex; justify-content: space-between; align-items: center;
        }
        .key-code { color: var(--neon-cyan); font-family: monospace; font-size: 14px; font-weight: 700; }
        .btn-delete { background: rgba(255, 0, 85, 0.15); color: var(--neon-red); border: 1px solid var(--neon-red); padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: 700;}

        .terminal-box { 
            background: #000000; border-radius: 8px; padding: 12px; font-family: monospace; 
            font-size: 11px; height: 140px; overflow-y: auto; border: 1px solid rgba(0, 243, 255, 0.2);
        }
        .log-entry { margin-bottom: 6px; border-bottom: 1px dashed rgba(255,255,255,0.05); padding-bottom: 3px; }
        .log-success { color: #00ff88; } .log-error { color: var(--neon-red); } .log-warning { color: #ffaa00; }

        .sidebar-menu { padding: 20px; list-style: none; }
        .sidebar-menu li a, .sidebar-menu button { 
            display: flex; align-items: center; gap: 10px; padding: 12px; color: var(--text-muted); 
            text-decoration: none; border-radius: 8px; font-size: 14px; font-weight: 600; 
            background: none; border: none; cursor: pointer; width: 100%; text-align: left;
        }
        .sidebar-menu li.active a { background: linear-gradient(90deg, rgba(191, 0, 255, 0.2), transparent); color: #fff; border-left: 3px solid var(--neon-purple); }
    </style>
</head>
<body>

    {% if not session.get('logged_in') %}
    <div class="login-wrapper">
        <div class="neon-border" style="width: 100%; max-width: 380px; text-align: center;">
            <div style="margin-bottom: 25px;">
                <h1 class="title-neon" style="font-size: 26px;">ALPHA CHEAT</h1>
                <p style="color: var(--text-muted); font-size: 12px;">Portail d'Authentification Sécurisé</p>
            </div>
            {% if error %}<div style="color: var(--neon-red); margin-bottom: 15px; font-size: 13px;">{{ error }}</div>{% endif %}
            <form method="POST" action="/login">
                <div class="input-group">
                    <label><i class="fas fa-user"></i> USERNAME</label>
                    <input type="text" name="username" placeholder="Entrez le nom d'utilisateur" required>
                </div>
                <div class="input-group">
                    <label><i class="fas fa-lock"></i> PASSWORD</label>
                    <input type="password" name="password" placeholder="Entrez le mot de passe" required>
                </div>
                <button type="submit" class="btn-gradient" style="margin-top: 15px;">SE CONNECTER <i class="fas fa-shield-alt"></i></button>
            </form>
        </div>
    </div>
    {% else %}
    
    <div class="sidebar">
        <div>
            <div style="padding: 20px; text-align: center;">
                <h2 class="title-neon" style="font-size: 20px;">ALPHA CHEAT</h2>
            </div>
            <ul class="sidebar-menu">
                <li class="active"><a href="/"><i class="fas fa-th-large"></i> Tableau de bord</a></li>
                <li style="margin-top: 10px;">
                    <form method="POST" action="/toggle_update" style="margin:0;">
                        <button type="submit" class="btn-update-panel {% if update_active %}active-alert{% endif %}" style="width:100%; justify-content: center; padding: 10px;">
                            <i class="fas fa-sync-alt"></i> {% if update_active %}UPDATE: ACTIVÉ{% else %}UPDATE: DÉSACTIVÉ{% endif %}
                        </button>
                    </form>
                </li>
                <li style="margin-top: 10px;">
                    <form method="POST" action="/logout" style="margin:0;">
                        <button type="submit" style="color: var(--neon-red);"><i class="fas fa-sign-out-alt"></i> Déconnexion</button>
                    </form>
                </li>
            </ul>
        </div>
        
        <div style="padding: 20px; text-align: center;">
            <p style="font-size: 11px; color: var(--text-muted); font-family: monospace;">ALPHA SYSTEM V2</p>
        </div>
    </div>

    <div class="main-content">
        <div class="topbar">
            <div>
                <h1 class="title-neon" style="font-size: 18px;">PANNEAU DE CONTRÔLE PRINCIPAL</h1>
                <p style="font-size: 11px; color: var(--text-muted); font-family: monospace;">admin@alpha.secure</p>
            </div>
            <div>
                <a href="/check_update" target="_blank" class="btn-update-panel {% if update_active %}active-alert{% endif %}"><i class="fas fa-download"></i> UPDATE PANEL</a>
            </div>
        </div>

        <div class="content-body">
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-key"></i></div>
                    <div class="stat-info">
                        <h4>CLÉS ACTIVES</h4>
                        <div class="num">{{ stats.total_keys }}</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="color: var(--neon-purple);"><i class="fas fa-mobile-alt"></i></div>
                    <div class="stat-info">
                        <h4>APPAREILS CONNECTÉS</h4>
                        <div class="num">{{ stats.connected_devices }}</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="color: #00ff88;"><i class="fas fa-shield-alt"></i></div>
                    <div class="stat-info">
                        <h4>STATUT DU SERVEUR</h4>
                        <div class="num" style="font-size: 14px; color: #00ff88;">PROTÉGÉ</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="color: #ffaa00;"><i class="fas fa-clock"></i></div>
                    <div class="stat-info">
                        <h4>UPTIME</h4>
                        <div class="num" style="font-size: 13px;">{{ stats.uptime }}</div>
                    </div>
                </div>
            </div>

            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                
                <div style="flex: 1; min-width: 280px;">
                    <div class="neon-border">
                        <div class="card-header">
                            <h3>Générer une Clé <i class="fas fa-plus-circle" style="color: var(--neon-cyan);"></i></h3>
                        </div>
                        <form method="POST" action="/add">
                            <div class="input-group">
                                <label>Nom de la Clé</label>
                                <input type="text" name="custom_key" value="ALPHA-" required autocomplete="off">
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <div class="input-group">
                                    <label>Jours</label>
                                    <input type="number" name="duration_days" value="30" min="1" required>
                                </div>
                                <div class="input-group">
                                    <label>Appareils</label>
                                    <input type="number" name="max_devices" value="2" min="1" required>
                                </div>
                            </div>
                            <button type="submit" class="btn-gradient">CRÉER ET ACTIVER <i class="fas fa-arrow-right"></i></button>
                        </form>
                    </div>

                    <div class="neon-border" style="margin-top: 20px; padding: 15px;">
                        <div class="card-header" style="margin-bottom: 10px;">
                            <h3 style="font-size: 13px;">Journal Système <i class="fas fa-terminal" style="color: var(--neon-purple);"></i></h3>
                        </div>
                        <div class="terminal-box">
                            {% for log in logs %}
                            <div class="log-entry log-{{ log.type }}">
                                <span style="color: var(--text-muted);">[{{ log.time }}]</span> {{ log.msg }}
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>

                <div style="flex: 2; min-width: 320px;">
                    <div class="neon-border" style="height: 100%;">
                        <div class="card-header">
                            <h3>Base de Données: Clés Actives <i class="fas fa-database" style="color: var(--neon-purple);"></i></h3>
                        </div>
                        
                        <div class="key-list">
                            {% for key, data in active_keys.items() %}
                            <div class="key-item">
                                <span class="key-code">{{ key }}</span>
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <span style="font-size: 11px; color: #00ff88; font-weight: 700;">{{ data.expiry_str }}</span>
                                    <span style="font-size: 11px; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px; color: var(--text-muted);">
                                        {{ data.connected }}/{{ data.max_devices }} <i class="fas fa-mobile-alt"></i>
                                    </span>
                                </div>
                                <form method="POST" action="/delete" style="margin:0;">
                                    <input type="hidden" name="key_to_delete" value="{{ key }}">
                                    <button type="submit" class="btn-delete"><i class="fas fa-trash"></i></button>
                                </form>
                            </div>
                            {% else %}
                            <div style="text-align: center; padding: 30px; color: var(--text-muted); font-size: 13px;">Aucune clé active...</div>
                            {% endfor %}
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
    {% endif %}
</body>
</html>
"""

def calculate_uptime():
    diff = datetime.datetime.now() - SERVER_START_TIME
    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    if days > 0: return f"{days}j {hours}h"
    elif hours > 0: return f"{hours}h {minutes}m"
    else: return f"{minutes}m"

@app.route('/', methods=['GET'])
def home():
    now = datetime.datetime.now()
    expired = [k for k, data in valid_keys.items() if now >= data["expiry"]]
    for k in expired: 
        del valid_keys[k]

    formatted_keys = {}
    total_connected = 0
    
    for k, data in valid_keys.items():
        exp = data["expiry"]
        conn_count = len(data["connected_ips"])
        total_connected += conn_count
        rem = exp - now
        days = rem.days
        expiry_str = f"{days} Jours" if days > 0 else "Expiré"
        formatted_keys[k] = {"expiry_str": expiry_str, "max_devices": data["max_devices"], "connected": conn_count}

    stats = {
        "total_keys": len(valid_keys),
        "connected_devices": total_connected,
        "uptime": calculate_uptime()
    }

    return render_template_string(
        DASHBOARD_TEMPLATE, 
        active_keys=formatted_keys, 
        host_ip=request.host.split(':')[0],
        stats=stats,
        logs=system_logs,
        error=None,
        update_active=update_panel_active
    )

@app.route('/login', methods=['POST'])
def login():
    if request.form.get('username') == ADMIN_USER and request.form.get('password') == ADMIN_PASS:
        session['logged_in'] = True
        add_log("Connexion administrateur réussie.", "success")
    else:
        add_log("Échec de tentative de connexion.", "error")
        return render_template_string(DASHBOARD_TEMPLATE, error="Identifiants incorrects.", active_keys={}, logs=system_logs, update_active=update_panel_active)
    return redirect(url_for('home'))

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    add_log("Déconnexion de l'administrateur.", "warning")
    return redirect(url_for('home'))

@app.route('/toggle_update', methods=['POST'])
def toggle_update():
    global update_panel_active
    if not session.get('logged_in'): return redirect(url_for('home'))
    update_panel_active = not update_panel_active
    status_msg = "activé" if update_panel_active else "désactivé"
    add_log(f"Le panneau de mise à jour a été {status_msg}.", "warning" if update_panel_active else "success")
    return redirect(url_for('home'))

@app.route('/add', methods=['POST'])
def add_key():
    if not session.get('logged_in'): return redirect(url_for('home'))
    key = request.form.get('custom_key', '').strip()
    max_devices = int(request.form.get('max_devices', 2))
    duration_days = int(request.form.get('duration_days', 30))
    
    if key:
        valid_keys[key] = {
            "expiry": datetime.datetime.now() + datetime.timedelta(days=duration_days),
            "max_devices": max_devices,
            "connected_ips": set()
        }
        add_log(f"Clé créée: {key} ({duration_days} jours)", "success")
    return redirect(url_for('home'))

@app.route('/delete', methods=['POST'])
def delete_key():
    if not session.get('logged_in'): return redirect(url_for('home'))
    k = request.form.get('key_to_delete')
    if k in valid_keys:
        valid_keys.pop(k, None)
        add_log(f"Clé supprimée: {k}", "error")
    return redirect(url_for('home'))

@app.route('/check_update', methods=['GET'])
def check_update():
    if update_panel_active:
        return jsonify({"update_required": True, "update_url": UPDATE_URL, "message": "Mise à jour obligatoire requise !"}), 200
    return redirect(UPDATE_URL)

@app.route('/verify', methods=['POST'])
def verify():
    if update_panel_active:
        return jsonify({"success": False, "force_update": True, "message": "Mise à jour requise", "update_url": UPDATE_URL}), 403

    data = request.get_json() or {}
    user_key = data.get('key')
    
    if not user_key or user_key not in valid_keys:
        return jsonify({"success": False, "message": "Clé invalide"}), 403

    now = datetime.datetime.now()
    client_ip = request.remote_addr
    key_data = valid_keys[user_key]

    if now > key_data["expiry"]:
        valid_keys.pop(user_key, None)
        return jsonify({"success": False, "message": "Clé expirée"}), 403

    if client_ip not in key_data["connected_ips"]:
        if len(key_data["connected_ips"]) >= key_data["max_devices"]:
            return jsonify({"success": False, "message": "Limite d'appareils atteinte"}), 403
        key_data["connected_ips"].add(client_ip)

    return jsonify({"success": True, "message": "Accès autorisé"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
