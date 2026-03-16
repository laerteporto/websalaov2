#!/usr/bin/env python3
"""
APLICAR_FIREBASE.py
Edita o index.html diretamente por número de linha e faz git push + vercel deploy.
Execute: python3 APLICAR_FIREBASE.py
"""
import os, sys, subprocess

# ── Localiza o index.html ──────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(SCRIPT_DIR, "index.html")

if not os.path.exists(INDEX):
    print(f"❌ index.html não encontrado em {SCRIPT_DIR}")
    sys.exit(1)

with open(INDEX, "r", encoding="utf-8") as f:
    linhas = f.readlines()

total = len(linhas)
print(f"📄 index.html carregado: {total} linhas")

# ── Localiza os blocos por conteúdo ───────────────────────────────────────────
def find_line(texto, start=0):
    for i, l in enumerate(linhas[start:], start):
        if texto in l:
            return i
    return -1

ln_backend   = find_line("async function enviarWhatsAppBackend(agId)")
ln_wpp_panel = find_line("// ─── WhatsApp Connection Panel")
ln_getwppbtn = find_line("function getWppBtnHTML(sent)")

# Fim de enviarWhatsAppBackend (próximo "}" sozinho na linha após ln_backend)
ln_backend_end = ln_backend
for i in range(ln_backend + 1, ln_backend + 25):
    if linhas[i].strip() == "}":
        ln_backend_end = i
        break

# Fim de getWppBtnHTML (próximo "}" depois)
ln_getwppbtn_end = ln_getwppbtn
for i in range(ln_getwppbtn + 1, ln_getwppbtn + 10):
    if linhas[i].strip() == "}":
        ln_getwppbtn_end = i
        break

print(f"  enviarWhatsAppBackend: linha {ln_backend+1} → {ln_backend_end+1}")
print(f"  WhatsApp Panel:        linha {ln_wpp_panel+1} → {ln_getwppbtn_end+1}")

if ln_backend < 0 or ln_wpp_panel < 0:
    print("❌ Blocos não encontrados. O arquivo pode já estar atualizado.")
    sys.exit(1)

# ── Novo bloco 1: enviarWhatsAppBackend ───────────────────────────────────────
NOVO_BACKEND = """\
async function enviarWhatsAppBackend(agId) {
  enviarWhatsApp(agId);
}
"""

# ── Novo bloco 2: painel WhatsApp completo ────────────────────────────────────
NOVO_PAINEL = """\
// ─── WhatsApp Connection Panel ────────────────────────────────────────────────
function renderWppConfig(container) {
  const msgs        = State.data.wppMensagens || [];
  const aguardando  = msgs.filter(m => m.enviadoEm && !m.resposta).length;
  const confirmados = msgs.filter(m => m.resposta === 'sim').length;
  const cancelados  = msgs.filter(m => m.resposta === 'nao').length;
  const pendentes   = msgs.filter(m => !m.lida).length;
  const fbOk        = _fbReady && window.FirebaseDB;

  container.innerHTML = `
  <div class="page-section">

    <div class="kpi-grid page-section">
      <div class="kpi-card" style="--kpi-color:var(--blue)">
        <div class="kpi-icon">📨</div>
        <div class="kpi-value">${msgs.length}</div>
        <div class="kpi-label">Total enviadas</div>
      </div>
      <div class="kpi-card" style="--kpi-color:var(--gold)">
        <div class="kpi-icon">⏳</div>
        <div class="kpi-value">${aguardando}</div>
        <div class="kpi-label">Aguardando</div>
      </div>
      <div class="kpi-card" style="--kpi-color:var(--green)">
        <div class="kpi-icon">✅</div>
        <div class="kpi-value">${confirmados}</div>
        <div class="kpi-label">Confirmados</div>
      </div>
      <div class="kpi-card" style="--kpi-color:var(--red)">
        <div class="kpi-icon">❌</div>
        <div class="kpi-value">${cancelados}</div>
        <div class="kpi-label">Cancelados</div>
      </div>
    </div>

    <div class="card page-section" style="margin-bottom:20px;">
      <div class="card-header">
        <div>
          <div class="card-title">📱 WhatsApp via Firebase</div>
          <div class="card-subtitle">Sem servidor externo — integração direta</div>
        </div>
        <span style="font-size:13px;font-weight:600;color:${fbOk ? '#25D366' : 'var(--red)'};">
          ${fbOk ? '🟢 Firebase conectado' : '🔴 Firebase offline'}
        </span>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;">
        <div style="background:var(--bg-card2);border-radius:var(--radius-sm);padding:14px;">
          <div style="font-size:20px;margin-bottom:6px;">1️⃣</div>
          <div style="font-size:13px;font-weight:600;color:var(--text);">Abra um agendamento</div>
          <div style="font-size:12px;color:var(--text-muted);margin-top:4px;">Na Agenda, clique em qualquer agendamento</div>
        </div>
        <div style="background:var(--bg-card2);border-radius:var(--radius-sm);padding:14px;">
          <div style="font-size:20px;margin-bottom:6px;">2️⃣</div>
          <div style="font-size:13px;font-weight:600;color:var(--text);">Clique em Enviar WhatsApp</div>
          <div style="font-size:12px;color:var(--text-muted);margin-top:4px;">Abre o WhatsApp com a mensagem pronta</div>
        </div>
        <div style="background:var(--bg-card2);border-radius:var(--radius-sm);padding:14px;">
          <div style="font-size:20px;margin-bottom:6px;">3️⃣</div>
          <div style="font-size:13px;font-weight:600;color:var(--text);">Registre a resposta</div>
          <div style="font-size:12px;color:var(--text-muted);margin-top:4px;">Use os botões abaixo para confirmar ou cancelar</div>
        </div>
      </div>
    </div>

    <div class="card page-section">
      <div class="card-header">
        <div>
          <div class="card-title" style="display:flex;align-items:center;gap:8px;">
            📬 Confirmações
            ${pendentes > 0 ? `<span class="nav-badge">${pendentes}</span>` : ''}
          </div>
          <div class="card-subtitle">Registre a resposta de cada cliente</div>
        </div>
        <button class="btn btn-ghost btn-sm"
          onclick="renderWppConfig(document.getElementById('page-content'))">↻ Atualizar</button>
      </div>
      <div id="wpp-lista"></div>
    </div>

  </div>`;

  renderWppLista();
}

function renderWppLista() {
  const el = document.getElementById('wpp-lista');
  if (!el) return;
  const msgs = (State.data.wppMensagens || []).slice().reverse();

  if (!msgs.length) {
    el.innerHTML = `<div class="empty-state" style="padding:32px;">
      <div class="empty-icon">📭</div>
      <h3>Nenhuma mensagem ainda</h3>
      <p>Abra um agendamento na Agenda e clique no botão WhatsApp.</p>
    </div>`;
    return;
  }

  el.innerHTML = msgs.map(m => {
    const [y,mo,d] = (m.data||'--').split('-');
    const dataFmt  = m.data ? d+'/'+mo+'/'+y : '—';
    const envio    = m.enviadoEm
      ? new Date(m.enviadoEm).toLocaleString('pt-BR',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'})
      : '—';

    const tag = m.resposta === 'sim'
      ? '<span class="wpp-tag-sim">✓ CONFIRMADO</span>'
      : m.resposta === 'nao'
        ? '<span class="wpp-tag-nao">✕ CANCELADO</span>'
        : '<span class="wpp-tag-pending">⏳ Aguardando</span>';

    const btns = !m.resposta ? `
      <div style="display:flex;gap:6px;margin-top:10px;">
        <button class="btn btn-success btn-sm" style="flex:1;"
          onclick="processarResposta(${m.id},'sim');renderWppConfig(document.getElementById('page-content'))">
          ✓ Confirmar
        </button>
        <button class="btn btn-danger btn-sm" style="flex:1;"
          onclick="processarResposta(${m.id},'nao');renderWppConfig(document.getElementById('page-content'))">
          ✕ Cancelar
        </button>
      </div>` : '';

    return `
    <div style="display:flex;align-items:flex-start;gap:12px;padding:14px 16px;
      border-bottom:1px solid var(--border-soft);
      ${!m.lida ? 'background:rgba(37,211,102,0.03);' : ''}">
      <div class="wpp-avatar">${(m.clienteNome||'?').charAt(0)}</div>
      <div style="flex:1;min-width:0;">
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
          <span style="font-size:14px;font-weight:600;color:var(--text);">${m.clienteNome}</span>
          ${!m.lida ? '<span style="width:7px;height:7px;background:#25D366;border-radius:50%;display:inline-block;"></span>' : ''}
          ${tag}
        </div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:3px;">
          📅 ${dataFmt} às ${m.hora||'—'} · ✂️ ${m.servico||'—'}
        </div>
        <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">
          Enviado: ${envio}${m.clienteTel ? ' · 📞 '+m.clienteTel : ''}
        </div>
        ${btns}
      </div>
      <button onclick="enviarWhatsApp(${m.agId});setTimeout(()=>renderWppConfig(document.getElementById('page-content')),400)"
        style="background:rgba(37,211,102,0.12);border:1px solid rgba(37,211,102,0.25);
          border-radius:8px;padding:6px 10px;font-size:13px;cursor:pointer;
          color:#25D366;white-space:nowrap;flex-shrink:0;">
        📤 Reenviar
      </button>
    </div>`;
  }).join('');
}

function getWppBtnHTML(sent) {
  return `<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
  ${sent ? 'Reenviar WhatsApp' : 'Enviar via WhatsApp'}`;
}
"""

# ── Monta o novo arquivo linha a linha ────────────────────────────────────────
novas = []
i = 0
while i < total:
    if i == ln_backend:
        novas.append(NOVO_BACKEND)
        i = ln_backend_end + 1
    elif i == ln_wpp_panel:
        novas.append(NOVO_PAINEL)
        i = ln_getwppbtn_end + 1
    else:
        novas.append(linhas[i])
        i += 1

novo_conteudo = "".join(novas)

# ── Verifica ──────────────────────────────────────────────────────────────────
erros = []
if "readonly" in novo_conteudo:
    erros.append("readonly ainda presente")
if "evolution-api-production-a563" in novo_conteudo:
    erros.append("URL evolution ainda presente")
if "BackendAPI.post" in novo_conteudo:
    erros.append("BackendAPI.post ainda presente")
if "BackendAPI.get('/api/" in novo_conteudo:
    erros.append("BackendAPI.get /api ainda presente")

if erros:
    print("❌ Erros encontrados:")
    for e in erros: print(f"   - {e}")
    sys.exit(1)

print("✅ Verificação passou — nenhuma referência antiga encontrada")

# ── Salva ─────────────────────────────────────────────────────────────────────
with open(INDEX, "w", encoding="utf-8") as f:
    f.write(novo_conteudo)

print(f"✅ index.html salvo ({novo_conteudo.count(chr(10))} linhas)")

# ── Git + Deploy ──────────────────────────────────────────────────────────────
os.chdir(SCRIPT_DIR)

print("\n📤 Fazendo git add + commit + push...")
subprocess.run(["git", "add", "index.html"], check=True)
subprocess.run(["git", "commit", "-m", "fix: WhatsApp direto via Firebase sem Evolution API"], check=True)
subprocess.run(["git", "push"], check=True)

print("\n🚀 Fazendo vercel --prod...")
subprocess.run(["vercel", "--prod", "--yes"], check=True)

print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("✅ PRONTO! Acesse o site → WhatsApp")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
