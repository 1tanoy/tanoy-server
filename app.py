from flask import Flask, request, send_from_directory, render_template_string
import os
import mimetypes

app = Flask(__name__)
FOLDER = "."

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tanoy Server</title>
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

  html { scroll-behavior: smooth; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Mono', monospace;
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* ── Animated background grid ── */
  body::before {
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background-image:
      linear-gradient(rgba(56,217,245,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(56,217,245,0.03) 1px, transparent 1px);
    background-size: 48px 48px;
    animation: gridDrift 40s linear infinite;
  }
  @keyframes gridDrift {
    0%   { background-position: 0 0; }
    100% { background-position: 48px 48px; }
  }

  /* ── Glow orbs ── */
  .orb {
    position: fixed; border-radius: 50%;
    filter: blur(100px); opacity: 0.18; pointer-events: none; z-index: 0;
    animation: orbFloat 12s ease-in-out infinite alternate;
  }
  .orb1 { width:520px; height:520px; background:var(--accent2); top:-160px; left:-120px; animation-delay:0s; }
  .orb2 { width:420px; height:420px; background:var(--accent);  bottom:-100px; right:-100px; animation-delay:-4s; }
  .orb3 { width:300px; height:300px; background:#ff6eb5; top:45%; left:50%; animation-delay:-8s; opacity:0.10; }
  @keyframes orbFloat {
    from { transform: translate(0,0) scale(1); }
    to   { transform: translate(30px,40px) scale(1.08); }
  }

  /* ── Layout ── */
  .wrapper {
    position: relative; z-index: 1;
    max-width: 860px;
    margin: 0 auto;
    padding: 48px 24px 80px;
  }

  /* ── Header ── */
  header {
    text-align: center;
    margin-bottom: 60px;
    animation: fadeDown 0.7s ease both;
  }
  .logo-ring {
    width: 72px; height: 72px;
    border-radius: 50%;
    border: 2px solid var(--accent);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 20px;
    box-shadow: 0 0 28px rgba(56,217,245,0.35);
    animation: pulse 3s ease-in-out infinite;
    font-size: 28px;
  }
  @keyframes pulse {
    0%,100% { box-shadow: 0 0 28px rgba(56,217,245,0.35); }
    50%      { box-shadow: 0 0 52px rgba(56,217,245,0.65); }
  }
  header h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3.2rem);
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(135deg, #fff 30%, var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  header p {
    margin-top: 10px;
    color: var(--muted);
    font-size: 0.85rem;
    letter-spacing: 0.05em;
  }
  .status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--success);
    margin-right: 6px;
    animation: blink 2s step-end infinite;
    vertical-align: middle;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

  /* ── Stats bar ── */
  .stats {
    display: flex; gap: 16px; flex-wrap: wrap;
    margin-bottom: 40px;
    animation: fadeUp 0.7s 0.15s ease both;
  }
  .stat-card {
    flex: 1 1 120px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
    text-align: center;
    transition: border-color 0.3s, transform 0.3s;
  }
  .stat-card:hover { border-color: var(--accent); transform: translateY(-3px); }
  .stat-card .num {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem; font-weight: 700;
    color: var(--accent);
  }
  .stat-card .lbl { font-size: 0.72rem; color: var(--muted); margin-top: 4px; letter-spacing:0.06em; text-transform:uppercase; }

  /* ── Cards ── */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 32px;
    margin-bottom: 28px;
    animation: fadeUp 0.7s ease both;
  }
  .card:nth-child(1) { animation-delay: 0.25s; }
  .card:nth-child(2) { animation-delay: 0.35s; }

  .card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 20px;
    display: flex; align-items: center; gap: 10px;
  }
  .card-title::after {
    content:''; flex:1; height:1px;
    background: linear-gradient(90deg, var(--border), transparent);
  }

  /* ── Upload zone ── */
  .drop-zone {
    border: 2px dashed var(--border);
    border-radius: 14px;
    padding: 48px 24px;
    text-align: center;
    cursor: pointer;
    transition: border-color 0.3s, background 0.3s;
    position: relative;
    overflow: hidden;
  }
  .drop-zone:hover, .drop-zone.drag-over {
    border-color: var(--accent);
    background: rgba(56,217,245,0.04);
  }
  .drop-zone .icon { font-size: 2.6rem; margin-bottom: 14px; }
  .drop-zone p { color: var(--muted); font-size: 0.85rem; }
  .drop-zone p span { color: var(--accent); cursor: pointer; }

  #fileInput { display: none; }

  /* ── Selected Files Container ── */
  .selected-files {
    margin-top: 14px;
    display: none;
  }

  .selected-file {
    padding: 10px 16px;
    background: rgba(56,217,245,0.08);
    border: 1px solid rgba(56,217,245,0.25);
    border-radius: 8px;
    font-size: 0.82rem;
    color: var(--accent);
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    animation: slideIn 0.3s ease;
  }

  .selected-file .file-name {
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .selected-file .remove-btn {
    background: rgba(255,95,126,0.2);
    color: var(--danger);
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    margin-left: 10px;
    cursor: pointer;
    font-size: 0.7rem;
    transition: background 0.3s;
  }

  .selected-file .remove-btn:hover {
    background: rgba(255,95,126,0.4);
  }

  @keyframes slideIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .file-count {
    color: var(--muted);
    font-size: 0.75rem;
    margin-top: 8px;
  }

  .btn-upload {
    margin-top: 20px;
    display: inline-flex; align-items: center; gap: 10px;
    padding: 13px 32px;
    background: linear-gradient(135deg, var(--accent2), var(--accent));
    color: #fff;
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem; font-weight: 700;
    border: none; border-radius: 50px;
    cursor: pointer;
    transition: opacity 0.3s, transform 0.2s, box-shadow 0.3s;
    box-shadow: 0 0 24px rgba(124,110,247,0.4);
    letter-spacing: 0.04em;
  }
  .btn-upload:hover { opacity: 0.92; transform: translateY(-2px); box-shadow: 0 0 36px rgba(124,110,247,0.6); }
  .btn-upload:active { transform: translateY(0); }
  .btn-upload:disabled { opacity: 0.5; cursor: not-allowed; }

  /* ── Progress bar ── */
  .progress-wrap {
    margin-top: 18px;
    display: none;
  }
  .progress-bg {
    height: 6px; border-radius: 99px;
    background: rgba(255,255,255,0.07);
    overflow: hidden;
  }
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent2), var(--accent));
    width: 0%; transition: width 0.3s;
  }
  .progress-label {
    font-size: 0.7rem;
    color: var(--muted);
    margin-top: 6px;
    text-align: right;
  }

  /* ── Flash messages ── */
  .flash {
    padding: 16px 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    font-size: 0.9rem;
    animation: slideDown 0.4s ease;
    border-left: 4px solid;
  }
  .flash.success {
    background: rgba(52,217,139,0.12);
    color: var(--success);
    border-color: var(--success);
  }
  .flash.error {
    background: rgba(255,95,126,0.12);
    color: var(--danger);
    border-color: var(--danger);
  }
  @keyframes slideDown {
    from { opacity:0; transform:translateY(-20px); }
    to { opacity:1; transform:translateY(0); }
  }

  /* ── Search bar ── */
  .search-bar {
    width: 100%;
    padding: 12px 16px;
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 10px;
    margin-bottom: 16px;
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
    transition: border-color 0.3s;
  }
  .search-bar:focus { outline:none; border-color:var(--accent); }

  /* ── File list ── */
  .file-list {
    display: flex; flex-direction: column; gap: 10px;
  }
  .file-item {
    padding: 16px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 14px;
    text-decoration: none;
    color: var(--text);
    transition: border-color 0.3s, background 0.3s, transform 0.2s;
    cursor: pointer;
    animation: fadeUp 0.5s ease both;
  }
  .file-item:hover {
    border-color: var(--accent);
    background: rgba(56,217,245,0.04);
    transform: translateX(4px);
  }
  .file-icon {
    width: 44px; height: 44px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    flex-shrink: 0;
  }
  .file-meta {
    flex: 1; min-width: 0;
  }
  .file-name {
    display: block;
    font-weight: 600;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .file-sub {
    display: block;
    font-size: 0.75rem;
    color: var(--muted);
  }
  .file-badge {
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.7rem;
    text-transform: uppercase;
    margin-right: 10px;
  }
  .dl-btn {
    color: var(--accent);
    font-weight: 700;
    transition: opacity 0.3s;
  }
  .file-item:hover .dl-btn { opacity: 0.7; }

  .empty-state {
    text-align: center;
    padding: 48px 24px;
    color: var(--muted);
  }
  .empty-state .big { font-size: 3rem; margin-bottom: 12px; }

  /* ── Contact Grid ── */
  .contact-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px;
  }
  .contact-item {
    display: flex; gap: 12px; align-items: flex-start;
    padding: 16px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    text-decoration: none;
    color: var(--text);
    transition: border-color 0.3s;
  }
  .contact-item:hover { border-color: var(--accent); }
  .contact-icon { font-size: 1.6rem; }
  .contact-label { font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
  .contact-value { margin-top: 4px; font-weight: 600; }

  /* ── Animations ── */
  @keyframes fadeDown { from{opacity:0;transform:translateY(-20px)} to{opacity:1;transform:translateY(0)} }
  @keyframes fadeUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }

  /* ── Footer ── */
  footer {
    text-align: center;
    padding-top: 32px;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 0.8rem;
  }
  footer span { color: var(--accent); font-weight: 700; }

</style>
</head>
<body>

<div class="orb orb1"></div>
<div class="orb orb2"></div>
<div class="orb orb3"></div>

<div class="wrapper">
  <header>
    <div class="logo-ring">⚡</div>
    <h1>Tanoy Server run on windows</h1>
    <p><span class="status-dot"></span>File Management System</p>
  </header>

  <div class="stats">
    <div class="stat-card">
      <div class="num" id="statCount">{{ file_data|length }}</div>
      <div class="lbl">Total Files</div>
    </div>
    <div class="stat-card">
      <div class="num" id="statSize">{{ total_size }}</div>
      <div class="lbl">Total Size</div>
    </div>
    <div class="stat-card">
      <div class="num">8080</div>
      <div class="lbl">Port</div>
    </div>
    <div class="stat-card">
      <div class="num">ON</div>
      <div class="lbl">Status</div>
    </div>
  </div>

  <!-- Flash -->
  {% if message %}
  <div class="flash {{ message_type }}" style="display:block">{{ message }}</div>
  {% endif %}

  <!-- Upload Card -->
  <div class="card">
    <div class="card-title">⬆ Upload Files</div>
    <form id="uploadForm" method="POST" action="/upload" enctype="multipart/form-data">
      <div class="drop-zone" id="dropZone">
        <div class="icon">🗂</div>
        <p>Drag &amp; drop files here, or <span onclick="document.getElementById('fileInput').click()">browse</span></p>
        <p style="font-size:0.75rem;margin-top:6px;">Select multiple files at once</p>
        <div class="selected-files" id="selectedFiles"></div>
        <div class="file-count" id="fileCount"></div>
        <input type="file" name="files" id="fileInput" multiple>
      </div>
      <div class="progress-wrap" id="progressWrap">
        <div class="progress-bg"><div class="progress-fill" id="progressFill"></div></div>
        <div class="progress-label" id="progressLabel">0%</div>
      </div>
      <br>
      <button type="submit" class="btn-upload" id="uploadBtn" disabled>⚡ Upload Files</button>
    </form>
  </div>

  <!-- Files Card -->
  <div class="card">
    <div class="card-title">📁 Available Files &nbsp;<span style="color:var(--muted);font-size:0.7rem;letter-spacing:0.04em;">newest first</span></div>
    <input class="search-bar" id="searchBar" placeholder="Search files…" oninput="filterFiles(this.value)">
    <div class="file-list" id="fileList">
      {% if file_data %}
        {% for f in file_data %}
        <a class="file-item" href="/download/{{ f.name }}" data-name="{{ f.name.lower() }}">
          <div class="file-icon" style="background:{{ loop.index | file_color }}">{{ f.name | file_icon }}</div>
          <div class="file-meta">
            <span class="file-name">{{ f.name }}</span>
            <span class="file-sub">{{ f.size }} &nbsp;·&nbsp; {{ f.time }}</span>
          </div>
          <span class="file-badge" style="background:rgba(56,217,245,0.1);color:var(--accent);">{{ f.name | file_ext }}</span>
          <span class="dl-btn">↓ DL</span>
        </a>
        {% endfor %}
      {% else %}
        <div class="empty-state">
          <div class="big">📭</div>
          <p>No files yet — upload something above!</p>
        </div>
      {% endif %}
    </div>
  </div>

  <!-- Contact Card -->
  <div class="card" style="animation-delay:0.45s;">
    <div class="card-title">✉ Contact Tanoy Dutta</div>
    <div class="contact-grid">
      <a class="contact-item" href="tel:+918900405420">
        <div class="contact-icon">📞</div>
        <div>
          <div class="contact-label">Phone</div>
          <div class="contact-value">+91 8900 405 420</div>
        </div>
      </a>
      <a class="contact-item" href="mailto:tanoydutta968@gmail.com">
        <div class="contact-icon">📧</div>
        <div>
          <div class="contact-label">Email</div>
          <div class="contact-value">tanoydutta968@gmail.com</div>
        </div>
      </a>
      <a class="contact-item" href="https://linkedin.com/in/tanoy-dutta-00a2a4284" target="_blank" rel="noopener">
        <div class="contact-icon">🔗</div>
        <div>
          <div class="contact-label">LinkedIn</div>
          <div class="contact-value">tanoy-dutta-00a2a4284</div>
        </div>
      </a>
    </div>
  </div>

  <footer>
    Built by <span>Tanoy Dutta</span> &nbsp;·&nbsp; Powered by Flask &nbsp;·&nbsp; {{ file_data|length }} file(s) served
  </footer>
</div>

<script>
// Drag & drop
const dz = document.getElementById('dropZone');
const fi = document.getElementById('fileInput');
const sf = document.getElementById('selectedFiles');
const fc = document.getElementById('fileCount');
const ub = document.getElementById('uploadBtn');

dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('drag-over'); });
dz.addEventListener('dragleave', () => dz.classList.remove('drag-over'));
dz.addEventListener('drop', e => {
  e.preventDefault();
  dz.classList.remove('drag-over');
  if (e.dataTransfer.files.length) {
    fi.files = e.dataTransfer.files;
    showSelectedFiles();
  }
});

fi.addEventListener('change', () => { showSelectedFiles(); });

function showSelectedFiles() {
  sf.innerHTML = '';
  const files = Array.from(fi.files);
  
  if (files.length === 0) {
    sf.style.display = 'none';
    fc.textContent = '';
    ub.disabled = true;
    return;
  }

  sf.style.display = 'block';
  ub.disabled = false;

  files.forEach((file, index) => {
    const fileDiv = document.createElement('div');
    fileDiv.className = 'selected-file';
    fileDiv.innerHTML = `
      <span class="file-name">📎 ${file.name}</span>
      <button type="button" class="remove-btn" onclick="removeFile(${index})">✕ Remove</button>
    `;
    sf.appendChild(fileDiv);
  });

  fc.textContent = `${files.length} file${files.length !== 1 ? 's' : ''} selected`;
}

function removeFile(index) {
  const dt = new DataTransfer();
  const files = Array.from(fi.files);
  files.splice(index, 1);
  
  files.forEach(file => {
    dt.items.add(file);
  });
  
  fi.files = dt.files;
  showSelectedFiles();
}

// Upload progress simulation
document.getElementById('uploadForm').addEventListener('submit', function() {
  const pw = document.getElementById('progressWrap');
  const pf = document.getElementById('progressFill');
  const pl = document.getElementById('progressLabel');
  pw.style.display = 'block';
  let p = 0;
  const t = setInterval(() => {
    p = Math.min(p + Math.random() * 18, 92);
    pf.style.width = p + '%';
    pl.textContent = Math.round(p) + '%';
  }, 150);
});

// File search
function filterFiles(q) {
  document.querySelectorAll('.file-item').forEach(el => {
    el.style.display = el.dataset.name.includes(q.toLowerCase()) ? 'flex' : 'none';
  });
}

// Staggered file-item animation
document.querySelectorAll('.file-item').forEach((el, i) => {
  el.style.animationDelay = (i * 0.05) + 's';
});
</script>
</body>
</html>
'''

def human_size(total_bytes):
    for unit in ['B','KB','MB','GB']:
        if total_bytes < 1024: return f"{total_bytes:.1f}{unit}"
        total_bytes /= 1024
    return f"{total_bytes:.1f}TB"

def get_file_icon(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    icons = {
        'pdf':'📄','py':'🐍','js':'🟨','ts':'🔷','html':'🌐','css':'🎨',
        'png':'🖼','jpg':'🖼','jpeg':'🖼','gif':'🖼','svg':'🖼','webp':'🖼',
        'mp4':'🎬','mov':'🎬','avi':'🎬','mkv':'🎬',
        'mp3':'🎵','wav':'🎵','flac':'🎵',
        'zip':'📦','rar':'📦','gz':'📦','tar':'📦',
        'txt':'📝','md':'📝','csv':'📊','xlsx':'📊','xls':'📊',
        'json':'🔧','xml':'🔧','yaml':'🔧','yml':'🔧',
        'exe':'⚙️','sh':'⚙️','bat':'⚙️',
        'docx':'📘','doc':'📘','pptx':'📙',
    }
    return icons.get(ext, '📁')

def get_file_color(n):
    colors = [
        'rgba(124,110,247,0.18)','rgba(56,217,245,0.15)',
        'rgba(255,95,126,0.15)','rgba(52,217,139,0.15)',
        'rgba(255,165,0,0.15)','rgba(200,100,250,0.15)',
    ]
    return colors[(n-1) % len(colors)]

def get_file_ext(filename):
    return filename.rsplit('.', 1)[-1].upper() if '.' in filename else 'FILE'

from jinja2 import Environment
app.jinja_env.filters['file_icon']  = lambda f: get_file_icon(f)
app.jinja_env.filters['file_color'] = lambda n: get_file_color(n)
app.jinja_env.filters['file_ext']   = lambda f: get_file_ext(f)

def get_files_sorted():
    """Return list of (filename, modified_time_str, size_str) sorted newest first."""
    import datetime
    raw = [f for f in os.listdir(FOLDER) if os.path.isfile(os.path.join(FOLDER, f))]
    def mtime(f):
        return os.path.getmtime(os.path.join(FOLDER, f))
    raw.sort(key=mtime, reverse=True)
    result = []
    for f in raw:
        mt = datetime.datetime.fromtimestamp(mtime(f))
        now = datetime.datetime.now()
        diff = now - mt
        if diff.total_seconds() < 60:
            label = "just now"
        elif diff.total_seconds() < 3600:
            label = f"{int(diff.total_seconds()//60)}m ago"
        elif diff.total_seconds() < 86400:
            label = f"{int(diff.total_seconds()//3600)}h ago"
        else:
            label = mt.strftime("%d %b %Y")
        sz = human_size(os.path.getsize(os.path.join(FOLDER, f)))
        result.append({'name': f, 'time': label, 'size': sz})
    return result

@app.route('/')
def index():
    file_data = get_files_sorted()
    total_bytes = sum(os.path.getsize(os.path.join(FOLDER, f['name'])) for f in file_data)
    return render_template_string(HTML, file_data=file_data, total_size=human_size(total_bytes), message='', message_type='')

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    
    # Filter out empty files
    files = [f for f in files if f and f.filename != '']
    
    if not files:
        file_data = get_files_sorted()
        total_bytes = sum(os.path.getsize(os.path.join(FOLDER, x['name'])) for x in file_data)
        return render_template_string(HTML, file_data=file_data, total_size=human_size(total_bytes),
                                      message='⚠ No files selected.', message_type='error')
    
    # Save all files
    saved_files = []
    for f in files:
        f.save(os.path.join(FOLDER, f.filename))
        saved_files.append(f.filename)
    
    file_data = get_files_sorted()
    total_bytes = sum(os.path.getsize(os.path.join(FOLDER, x['name'])) for x in file_data)
    
    if len(saved_files) == 1:
        message = f'✅ "{saved_files[0]}" uploaded successfully!'
    else:
        message = f'✅ {len(saved_files)} files uploaded successfully!'
    
    return render_template_string(HTML, file_data=file_data, total_size=human_size(total_bytes),
                                  message=message, message_type='success')

@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(FOLDER, filename, as_attachment=True)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)