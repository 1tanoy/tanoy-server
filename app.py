from flask import Flask, request, send_from_directory, render_template_string, session, jsonify
import os
import json
import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'tanoy_server_secret_2025_kali_v2')

FOLDER = "files"
METADATA_FILE = "file_metadata.json"
ACCOUNTS_FILE = "accounts.json"
CHAT_FILE = "chat_messages.json"

os.makedirs(FOLDER, exist_ok=True)
if not os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, 'w') as f:
        json.dump([], f)

# --- SYSTEM STORES UTILITIES ---
def load_metadata():
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_metadata(data):
    with open(METADATA_FILE, 'w') as f: json.dump(data, f, indent=2)

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_accounts(data):
    with open(ACCOUNTS_FILE, 'w') as f: json.dump(data, f, indent=2)

# --- UNIFIED DASHBOARD UI TEMPLATE ---
HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>T Server </title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:        #050810;
    --surface:   #0c1120;
    --border:    rgba(99,210,255,0.12);
    --accent:    #38d9f5;
    --accent2:   #7c6ef7;
    --text:      #e2eaf6;
    --muted:     #5a6a84;
    --danger:    #ff5f7e;
    --success:   #34d98b;
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Mono', monospace;
    min-height: 100vh;
    overflow-x: hidden;
  }

  body::before {
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background-image:
      linear-gradient(rgba(56,217,245,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(56,217,245,0.03) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
  }

  .wrapper {
    position: relative; z-index: 1;
    max-width: 1000px;
    margin: 0 auto;
    padding: 32px 16px 40px;
  }

  header { text-align: center; margin-bottom: 32px; }
  .logo-ring {
    width: 64px; height: 64px; border-radius: 50%; border: 2px solid var(--accent);
    display: flex; align-items: center; justify-content: center; margin: 0 auto 16px;
    box-shadow: 0 0 24px rgba(56,217,245,0.3); font-size: 24px;
  }
  header h1 {
    font-family: 'Syne', sans-serif; font-size: 2.2rem; font-weight: 800;
    background: linear-gradient(135deg, #fff 40%, var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  header p { color: var(--muted); font-size: 0.85rem; margin-top: 6px; }

  .card { background: var(--surface); border: 1px solid var(--border); border-radius: 20px; padding: 24px; margin-bottom: 24px; }
  .card-title {
    font-family: 'Syne', sans-serif; font-size: 0.75rem; letter-spacing: 0.15em;
    text-transform: uppercase; color: var(--accent); margin-bottom: 20px;
    display: flex; align-items: center; gap: 10px;
  }
  .card-title::after { content:''; flex:1; height:1px; background: linear-gradient(90deg, var(--border), transparent); }

  /* UNIFIED LINEAR STACK SYSTEM (No Side-by-Side Viewport Columns) */
  .grid-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  /* File System Form Controls */
  .mode-toggle { display: flex; gap: 12px; margin-bottom: 20px; }
  .mode-btn {
    flex: 1; padding: 12px; border: 2px solid var(--border); background: var(--bg);
    color: var(--muted); border-radius: 10px; cursor: pointer; font-family: 'Syne', sans-serif;
    font-weight: 700; font-size: 0.85rem; text-transform: uppercase; transition: all 0.2s;
  }
  .mode-btn.active {
    background: linear-gradient(135deg, var(--accent2), var(--accent));
    border-color: var(--accent); color: #fff; box-shadow: 0 0 16px rgba(124,110,247,0.3);
  }
  .form-group { margin-bottom: 14px; }
  .form-label { display: block; font-size: 0.7rem; color: var(--muted); margin-bottom: 6px; text-transform: uppercase; }
  .form-input {
    width: 100%; padding: 12px; background: var(--bg); border: 2px solid var(--border);
    color: var(--text); border-radius: 8px; font-family: monospace; font-size: 0.85rem;
  }
  .form-input:focus { outline: none; border-color: var(--accent); }
  .scft-section { display: none; margin-bottom: 14px; padding: 14px; background: rgba(255,95,126,0.05); border: 1px solid rgba(255,95,126,0.15); border-radius: 10px; }
  .scft-section.show { display: block; }

  .drop-zone { border: 2px dashed var(--border); border-radius: 12px; padding: 32px 16px; text-align: center; cursor: pointer; margin-bottom: 14px; }
  .drop-zone p { color: var(--muted); font-size: 0.8rem; }
  .drop-zone p span { color: var(--accent); font-weight: 700; }
  #fileInput { display: none; }
  .selected-file { padding: 8px 12px; background: rgba(56,217,245,0.05); border: 1px solid rgba(56,217,245,0.15); border-radius: 6px; font-size: 0.8rem; color: var(--accent); margin-bottom: 6px; display: flex; justify-content: space-between; }
  .remove-btn { background: none; color: var(--danger); border: none; cursor: pointer; font-weight: bold; }

  .btn-action {
    width: 100%; padding: 12px; background: linear-gradient(135deg, var(--accent2), var(--accent));
    color: #fff; font-family: 'Syne', sans-serif; font-weight: 700; border: none; border-radius: 50px; cursor: pointer;
  }
  .btn-action:disabled { opacity: 0.5; cursor: not-allowed; }

  .file-list { display: flex; flex-direction: column; gap: 8px; max-height: 350px; overflow-y: auto; }
  .file-item { padding: 12px; background: var(--bg); border: 1px solid var(--border); border-radius: 10px; display: flex; align-items: center; gap: 12px; text-decoration: none; color: var(--text); }
  .file-icon { width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; background: rgba(255,255,255,0.05); }
  .file-meta { flex: 1; min-width: 0; }
  .file-name { display: block; font-weight: 600; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .file-sub { display: block; font-size: 0.7rem; color: var(--muted); }
  .file-badge { padding: 3px 6px; border-radius: 4px; font-size: 0.6rem; text-transform: uppercase; font-weight: bold; }
  .file-badge.public { background: rgba(52,217,139,0.15); color: var(--success); }
  .file-badge.secret { background: rgba(255,95,126,0.15); color: var(--danger); }

  /* Chat Engine Container Adjustments (Expanded Viewport Height) */
  .chat-box { display: flex; flex-direction: column; height: 700px; background: var(--bg); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
  .chat-messages { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
  .msg-bubble { background: rgba(255,255,255,0.03); border: 1px solid var(--border); padding: 10px 14px; border-radius: 12px; max-width: 85%; width: fit-content; }
  .msg-bubble.self { background: rgba(124,110,247,0.08); border-color: rgba(124,110,247,0.2); align-self: flex-end; }
  .msg-header { display: flex; gap: 8px; font-size: 0.7rem; margin-bottom: 4px; }
  .msg-author { color: var(--accent); font-weight: 700; }
  .msg-time { color: var(--muted); }
  .msg-body { font-size: 0.85rem; line-height: 1.4; word-break: break-word; white-space: pre-wrap; }
  .chat-controls { padding: 14px; background: var(--surface); border-top: 1px solid var(--border); display: flex; flex-direction: column; gap: 10px; }

  /* OWNER SYSTEM DATA CARDS */
  .contact-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-top: 4px; }
  .contact-item { padding: 16px; background: var(--bg); border: 1px solid var(--border); border-radius: 12px; font-size: 0.9rem; display: flex; flex-direction: column; gap: 4px; }
  .contact-item strong { color: var(--accent); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
  .contact-item a { color: #fff; text-decoration: none; border-bottom: 1px dashed var(--accent2); width: fit-content; transition: color 0.2s; }
  .contact-item a:hover { color: var(--accent); }

  .flash { padding: 12px; border-radius: 8px; margin-bottom: 16px; font-size: 0.85rem; border-left: 4px solid; }
  .flash.success { background: rgba(52,217,139,0.1); color: var(--success); border-color: var(--success); }
  .flash.error { background: rgba(255,95,126,0.1); color: var(--danger); border-color: var(--danger); }
  
  .login-info { font-size: 0.75rem; color: var(--success); margin-bottom: 12px; padding: 10px; background: rgba(52,217,139,0.05); border-left: 3px solid var(--success); display: flex; justify-content: space-between; align-items: center; }
  .logout-btn { padding: 4px 8px; background: rgba(255,95,126,0.15); color: var(--danger); border: none; border-radius: 4px; cursor: pointer; font-size: 0.75rem; }
  footer { text-align: center; padding: 24px 0 10px; color: var(--muted); font-size: 0.75rem; border-top: 1px solid var(--border); margin-top: 24px; }
</style>
</head>
<body>

<div class="wrapper">
  <header>
    <div class="logo-ring">⚡</div>
    <h1>T Server </h1>
    <p>Adaptive Cloud File Transfer Platform</p>
  </header>

  {% if message %}
  <div class="flash {{ message_type }}">{{ message }}</div>
  {% endif %}

  <div class="grid-container">
    
    <div class="system-pane">
      <div class="card">
        <div class="card-title">⬆ Vault Dispatcher (GPFT / SCFT)</div>
        
        <div class="mode-toggle">
          <button class="mode-btn active" id="gpftBtn" onclick="setMode('gpft')">🟢 GPFT</button>
          <button class="mode-btn" id="scftBtn" onclick="setMode('scft')">🔴 SCFT</button>
        </div>

        <div class="scft-section" id="scftSection">
          <div class="form-group">
            <label class="form-label">🆔 Vault User Identifier</label>
            <input type="text" id="scftUserId" class="form-input" placeholder="User Profile ID">
          </div>
          <div class="form-group">
            <label class="form-label">🔐 Security Passkey</label>
            <input type="password" id="scftPassword" class="form-input" placeholder="Create Access Key">
          </div>
        </div>

        <form id="uploadForm" method="POST" action="/upload" enctype="multipart/form-data">
          <input type="hidden" name="transfer_mode" id="transferMode" value="gpft">
          <input type="hidden" name="scft_user_id" id="scftUserIdField" value="">
          <input type="hidden" name="scft_password" id="scftPasswordField" value="">

          <div class="drop-zone" id="dropZone">
            <p>Drag target storage files here or <span>browse local path</span></p>
            <div class="selected-files" id="selectedFiles"></div>
            <input type="file" name="files" id="fileInput" multiple>
          </div>
          <button type="submit" class="btn-action" id="uploadBtn" disabled>⚡ Process Payload Upload</button>
        </form>
      </div>

      <div class="card">
        <div class="card-title">📁 Protected File Storage Directories</div>
        
        {% if logged_in %}
        <div class="login-info">
          <span>Active Tunnel: <strong>{{ logged_in_user }}</strong></span>
          <button class="logout-btn" onclick="logout()">Disconnect</button>
        </div>
        {% else %}
        <div style="margin-bottom: 16px;">
          <div class="form-group"><input type="text" id="loginUserId" class="form-input" placeholder="SCFT User ID"></div>
          <div class="form-group"><input type="password" id="loginPassword" class="form-input" placeholder="Security Passkey"></div>
          <button class="btn-action" style="padding: 8px 16px; font-size:0.8rem;" onclick="doLogin()">🔓 Mount Private Account</button>
        </div>
        {% endif %}

        <div class="file-list">
          {% if file_data %}
            {% for f in file_data %}
            <a class="file-item" href="/download/{{ f.name }}">
              <div class="file-icon">{{ f.icon }}</div>
              <div class="file-meta">
                <span class="file-name">{{ f.name }}</span>
                <span class="file-sub">{{ f.size }} · {{ f.time }}</span>
              </div>
              <span class="file-badge {% if f.is_secret %}secret{% else %}public{% endif %}">
                {% if f.is_secret %}🔒 Secret{% else %}🌐 Public{% endif %}
              </span>
            </a>
            {% endfor %}
          {% else %}
            <div style="text-align:center; padding: 20px; color: var(--muted); font-size: 0.8rem;">No files accessible.</div>
          {% endif %}
        </div>
      </div>
    </div>

    <div class="system-pane">
      <div class="card">
        <div class="card-title">💬 Live Chat Terminal</div>
        
        <div class="chat-box">
          <div class="chat-messages" id="chatMessages"></div>
          
          <div class="chat-controls">
            <div style="display: flex; gap: 10px;">
              <input type="text" id="chatName" class="form-input" style="width: 25%;" placeholder="Handle" value="Anonymous">
              <input type="text" id="chatMsg" class="form-input" style="width: 75%;" placeholder="Write localized packet transmission..." onkeydown="if(event.key==='Enter') sendChatMessage()">
            </div>
            <button type="button" class="btn-action" style="background: var(--accent2);" onclick="sendChatMessage()">📡 Transmit Message</button>
          </div>
        </div>
      </div>
    </div>

    <div class="system-pane">
      <div class="card">
        <div class="card-title">📬 Contact with System Owner</div>
        <div class="contact-grid">
          <div class="contact-item">
            <strong>System Developer</strong>
            <span>TANOY DUTTA</span>
          </div>
          <div class="contact-item">
            <strong>Mobile Terminal</strong>
            <a href="tel:+918900405420">+91 8900405420</a>
          </div>
          <div class="contact-item">
            <strong>Secure Mail Relay</strong>
            <a href="mailto:tanoydutta968@gmail.com">tanoydutta968@gmail.com</a>
          </div>
          <div class="contact-item">
            <strong>Linkedin Contact</strong>
            <a href="https://linkedin.com/in/tanoy-dutta-00a2a4284" target="_blank">LinkedIn Profile</a>
          </div>
        </div>
      </div>
    </div>

  </div>

  <footer>
    Built by <span>Tanoy Dutta</span> 
  </footer>
</div>

<script>
function setMode(mode) {
  const gpftBtn = document.getElementById('gpftBtn');
  const scftBtn = document.getElementById('scftBtn');
  const scftSection = document.getElementById('scftSection');
  const transferMode = document.getElementById('transferMode');

  if (mode === 'gpft') {
    gpftBtn.classList.add('active'); scftBtn.classList.remove('active');
    scftSection.classList.remove('show'); transferMode.value = 'gpft';
  } else {
    gpftBtn.classList.remove('active'); scftBtn.classList.add('active');
    scftSection.classList.add('show'); transferMode.value = 'scft';
  }
}

function doLogin() {
  const userId = document.getElementById('loginUserId').value.trim();
  const password = document.getElementById('loginPassword').value;
  if (!userId || !password) return alert('Credentials verification required.');

  fetch('/login_scft', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, password: password })
  })
  .then(r => r.json()).then(data => {
    if (data.success) location.reload(); else alert('Security credential validation mismatch.');
  });
}

function logout() { fetch('/logout_scft', { method: 'POST' }).then(() => location.reload()); }

const dz = document.getElementById('dropZone'), fi = document.getElementById('fileInput'), sf = document.getElementById('selectedFiles'), ub = document.getElementById('uploadBtn');
dz.addEventListener('click', () => fi.click());
dz.addEventListener('dragover', e => { e.preventDefault(); });
dz.addEventListener('drop', e => {
  e.preventDefault();
  if (e.dataTransfer.files.length) { fi.files = e.dataTransfer.files; showSelectedFiles(); }
});
fi.addEventListener('change', showSelectedFiles);

function showSelectedFiles() {
  sf.innerHTML = '';
  if (!fi.files.length) return ub.disabled = true;
  ub.disabled = false;
  Array.from(fi.files).forEach((f, i) => {
    const d = document.createElement('div'); d.className = 'selected-file';
    d.innerHTML = `<span>📎 ${f.name}</span><button type="button" class="remove-btn" onclick="event.stopPropagation(); removeFile(${i})">✕</button>`;
    sf.appendChild(d);
  });
}

function removeFile(i) {
  const dt = new DataTransfer();
  Array.from(fi.files).forEach((f, idx) => { if(idx !== i) dt.items.add(f); });
  fi.files = dt.files; showSelectedFiles();
}

document.getElementById('uploadForm').addEventListener('submit', function(e) {
  if (document.getElementById('transferMode').value === 'scft') {
    const u = document.getElementById('scftUserId').value.trim();
    const p = document.getElementById('scftPassword').value;
    if (!u || !p) { e.preventDefault(); return alert('SCFT parameters missing!'); }
    document.getElementById('scftUserIdField').value = u;
    document.getElementById('scftPasswordField').value = p;
  }
});

let lastTimestamp = 0;
function fetchChatMessages() {
  fetch('/messages').then(r => r.json()).then(messages => {
    const container = document.getElementById('chatMessages');
    const userHandle = document.getElementById('chatName').value.trim();
    let updated = false;

    messages.forEach(m => {
      if (m.timestamp > lastTimestamp) {
        const item = document.createElement('div');
        item.className = `msg-bubble ${m.name === userHandle ? 'self' : ''}`;
        item.innerHTML = `<div class="msg-header"><span class="msg-author">${escapeHTML(m.name)}</span><span class="msg-time">${m.time}</span></div><div class="msg-body">${escapeHTML(m.message)}</div>`;
        container.appendChild(item);
        lastTimestamp = m.timestamp;
        updated = true;
      }
    });
    if (updated) container.scrollTop = container.scrollHeight;
  });
}

function sendChatMessage() {
  const nameInput = document.getElementById('chatName'), msgInput = document.getElementById('chatMsg');
  const name = nameInput.value.trim(), message = msgInput.value.trim();
  if(!name || !message) return;

  fetch('/send-message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: name, message: message })
  })
  .then(r => r.json()).then(res => { if(res.success) { msgInput.value = ''; fetchChatMessages(); } });
}

function escapeHTML(str) { return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); }

fetchChatMessages();
setInterval(fetchChatMessages, 2000);
</script>
</body>
</html>
'''

# --- STORAGE FORMATTERS ---
def get_file_icon(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    icons = {'pdf':'📄','py':'🐍','js':'🟨','zip':'📦','txt':'📝','png':'🖼','jpg':'🖼','mp4':'🎬'}
    return icons.get(ext, '📁')

def human_size(total_bytes):
    for unit in ['B','KB','MB','GB']:
        if total_bytes < 1024: return f"{total_bytes:.1f}{unit}"
        total_bytes /= 1024
    return f"{total_bytes:.1f}TB"

def get_files_sorted(user_id=None):
    metadata = load_metadata()
    try: raw = [f for f in os.listdir(FOLDER) if os.path.isfile(os.path.join(FOLDER, f))]
    except: return []
    
    raw.sort(key=lambda f: os.path.getmtime(os.path.join(FOLDER, f)), reverse=True)
    result = []
    
    for f in raw:
        try:
            mt = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(FOLDER, f)))
            now = datetime.datetime.now()
            diff = now - mt
            
            if diff.total_seconds() < 60: label = "just now"
            elif diff.total_seconds() < 3600: label = f"{int(diff.total_seconds()//60)}m ago"
            elif diff.total_seconds() < 86400: label = f"{int(diff.total_seconds()//3600)}h ago"
            else: label = mt.strftime("%d %b")
            
            sz = human_size(os.path.getsize(os.path.join(FOLDER, f)))
            file_meta = metadata.get(f, {})
            is_secret = file_meta.get('secret', False)
            file_user_id = file_meta.get('user_id', '')
            
            if is_secret:
                if user_id and file_user_id == user_id:
                    result.append({'name': f, 'time': label, 'size': sz, 'is_secret': True, 'icon': get_file_icon(f)})
            else:
                result.append({'name': f, 'time': label, 'size': sz, 'is_secret': False, 'icon': get_file_icon(f)})
        except: pass
    return result

# --- ROUTE APP LOGIC ENDPOINTS ---
@app.route('/')
def index(): return render_dashboard('', '')

def render_dashboard(msg, msg_type):
    logged_in_user = session.get('scft_user_id', None)
    file_data = get_files_sorted(user_id=logged_in_user)
    return render_template_string(HTML, file_data=file_data, logged_in=logged_in_user is not None, logged_in_user=logged_in_user, message=msg, message_type=msg_type)

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    transfer_mode = request.form.get('transfer_mode', 'gpft')
    scft_user_id = request.form.get('scft_user_id', '').strip()
    scft_password = request.form.get('scft_password', '')
    
    files = [f for f in files if f and f.filename != '']
    if not files: return render_dashboard('⚠️ No files selected', 'error')
    if transfer_mode == 'scft' and (not scft_user_id or not scft_password):
        return render_dashboard('⚠️ Identity parameters required for SCFT!', 'error')
    
    metadata = load_metadata()
    accounts = load_accounts()
    saved_count = 0
    
    for f in files:
        try:
            f.save(os.path.join(FOLDER, f.filename))
            saved_count += 1
            if transfer_mode == 'scft':
                accounts[scft_user_id] = scft_password
                metadata[f.filename] = {'secret': True, 'user_id': scft_user_id, 'uploaded': datetime.datetime.now().isoformat()}
            else:
                metadata[f.filename] = {'secret': False, 'uploaded': datetime.datetime.now().isoformat()}
        except: pass
            
    save_metadata(metadata)
    save_accounts(accounts)
    if saved_count > 0: return render_dashboard(f"Uploaded {saved_count} file(s) safely!", 'success')
    return render_dashboard('Transfer management fault.', 'error')

@app.route('/login_scft', methods=['POST'])
def login_scft():
    data = request.json or {}
    user_id = data.get('user_id', '').strip()
    password = data.get('password', '')
    accounts = load_accounts()
    if user_id in accounts and accounts[user_id] == password:
        session['scft_user_id'] = user_id
        return {'success': True}
    return {'success': False}

@app.route('/logout_scft', methods=['POST'])
def logout_scft():
    session.pop('scft_user_id', None)
    return {'success': True}

@app.route('/download/<path:filename>')
def download(filename):
    metadata = load_metadata()
    file_meta = metadata.get(filename, {})
    if file_meta.get('secret', False):
        logged_in_user = session.get('scft_user_id', None)
        if not logged_in_user or logged_in_user != file_meta.get('user_id', ''):
            return "❌ Secure partition key mismatch.", 403
    return send_from_directory(FOLDER, filename, as_attachment=True)

@app.route('/messages')
def get_messages():
    try:
        with open(CHAT_FILE, 'r') as f:
            messages = json.load(f)
            return jsonify(messages[-100:])  # Expanded data display to fit long panel
    except: return jsonify([])

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json() or {}
    name = data.get('name', '').strip()[:50]
    message = data.get('message', '').strip()[:5000]
    if not name or not message: return jsonify({'success': False})
    
    try:
        try:
            with open(CHAT_FILE, 'r') as f: messages = json.load(f)
        except: messages = []
            
        now = datetime.datetime.now()
        messages.append({'name': name, 'message': message, 'time': now.strftime("%H:%M"), 'timestamp': now.timestamp()})
        messages = messages[-500:] # Window tracking expansion
        with open(CHAT_FILE, 'w') as f: json.dump(messages, f)
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
