#!/usr/bin/env python3
"""
Corrige a duplicação de (async function() no script de overlay
Execute: python3 fix_duplo.py
"""
import os, sys

FILE = "/home/laerte/Downloads/websalaov2/index.html"

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"📦 Tamanho original: {len(content)} bytes")

# Encontrar o script de confirmação completo e reescrever do zero
marker_start = "  <!-- Script de confirmação -->"
marker_end   = "  <!-- SIDEBAR -->"

i1 = content.find(marker_start)
i2 = content.find(marker_end)

if i1 == -1 or i2 == -1:
    print("❌ Marcadores não encontrados")
    sys.exit(1)

old_script = content[i1:i2]
print(f"Script de overlay encontrado: {len(old_script)} chars")
print(f"Ocorrências de '(async function': {old_script.count('(async function')}")
print(f"Ocorrências de 'if (!agId)': {old_script.count('if (!agId)')}")

# Script correto sem duplicação
new_script = """  <!-- Script de confirmação -->
  <script type="module">
    import { initializeApp }       from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
    import { getFirestore, doc, getDoc, updateDoc }
                                   from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";

    (async function() {
    var params = new URLSearchParams(window.location.search);
    var agId   = params.get('id');
    if (!agId) return; // não é link de confirmação, sai

    // Mostra overlay imediatamente
    document.getElementById('confirmacao-overlay').style.display = 'flex';

    // Inicializa Firebase próprio (independente do app)
    const _cfg = {
      apiKey:            "AIzaSyBQcTGkiastpRAjGthU9nHy_uqpQjUMdu0",
      authDomain:        "websalao-2a9d1.firebaseapp.com",
      projectId:         "websalao-2a9d1",
      storageBucket:     "websalao-2a9d1.firebasestorage.app",
      messagingSenderId: "731611795568",
      appId:             "1:731611795568:web:103e44f116e152961024b5"
    };

    let _app, _db;
    try {
      _app = initializeApp(_cfg, 'confirmacao');
    } catch(e) {
      _app = initializeApp(_cfg);
    }
    _db = getFirestore(_app);

    function fmtDate(str) {
      if (!str) return '—';
      var p = str.split('-');
      return p.length === 3 ? p[2]+'/'+p[1]+'/'+p[0] : str;
    }

    function showError() {
      document.getElementById('c-loading').style.display = 'none';
      document.getElementById('c-error').classList.add('show');
    }

    function showMain() {
      document.getElementById('c-loading').style.display = 'none';
      document.getElementById('c-main').style.display = 'block';
    }

    function showAlready(status) {
      document.getElementById('c-action').style.display = 'none';
      var icon  = document.getElementById('c-already-icon');
      var title = document.getElementById('c-already-title');
      var msg   = document.getElementById('c-already-msg');
      if (status === 'confirmado') {
        icon.textContent  = '✅';
        title.textContent = 'Agendamento já confirmado';
        title.style.color = '#22c55e';
        msg.textContent   = 'Você já confirmou este agendamento. Até logo! 💛';
      } else {
        icon.textContent  = '❌';
        title.textContent = 'Agendamento já cancelado';
        title.style.color = '#ef4444';
        msg.textContent   = 'Este agendamento já foi cancelado anteriormente.';
      }
      document.getElementById('c-already').classList.add('show');
    }

    try {
      const ref  = doc(_db, 'agendamentos', String(agId));
      const snap = await getDoc(ref);

      if (!snap.exists()) { showError(); }
      else {
        const ag = snap.data();
        document.getElementById('c-cliente').textContent = ag.clienteNome || '—';
        document.getElementById('c-servico').textContent = ag.servicoNome || '—';
        document.getElementById('c-data').textContent    = fmtDate(ag.data);
        document.getElementById('c-hora').textContent    = ag.hora || '—';
        showMain();

        if (ag.status === 'confirmado' || ag.status === 'cancelado') {
          showAlready(ag.status);
        }

        window.confResponder = async function(novoStatus) {
          document.getElementById('c-btn-sim').disabled = true;
          document.getElementById('c-btn-nao').disabled = true;
          try {
            await updateDoc(ref, {
              status: novoStatus,
              confirmadoEm: new Date().toISOString(),
              confirmadoPeloCliente: true
            });
            document.getElementById('c-action').style.display = 'none';
            document.getElementById('c-fb-' + novoStatus).classList.add('show');
          } catch(e) {
            document.getElementById('c-btn-sim').disabled = false;
            document.getElementById('c-btn-nao').disabled = false;
            alert('Erro ao salvar. Tente novamente.');
          }
        };
      }
    } catch(e) {
      console.error(e);
      showError();
    }
    })(); // fim IIFE async
  </script>

  """

content = content[:i1] + new_script + content[i2:]

print(f"✅ Script de overlay reescrito sem duplicação")
print(f"   Ocorrências de '(async function': {new_script.count('(async function')}")

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"📦 Novo tamanho: {len(content)} bytes")
print(f"\n✅ Pronto! Agora execute: vercel --prod")
