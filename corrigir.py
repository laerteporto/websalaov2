#!/usr/bin/env python3
"""
Script de correção do websalaov2/index.html - versão 2
Execute: python3 corrigir.py
"""
import os, sys, re

ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
if not os.path.exists(ARQUIVO):
    print(f"❌ Arquivo não encontrado: {ARQUIVO}")
    sys.exit(1)

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"📄 {ARQUIVO}")
print(f"📦 Tamanho original: {len(content)} bytes")
fixes = 0

# ── FIX 1: Corrigir script de confirmação (overlay) ─────────────────────────
# Remove qualquer versão problemática e substitui pela correta

# Padrão A: return ilegal no topo
if "if (!agId) return; // não é link de confirmação" in content and "(async function()" not in content:
    old = "    var params = new URLSearchParams(window.location.search);\n    var agId   = params.get('id');\n    if (!agId) return; // não é link de confirmação, sai"
    new = "    (async function() {\n    var params = new URLSearchParams(window.location.search);\n    var agId   = params.get('id');\n    if (!agId) return; // não é link de confirmação, sai"
    if old in content:
        content = content.replace(old, new)
        fixes += 1
        print("✅ Fix 1a: async IIFE adicionada")

# Padrão B: else { solto (versão anterior do fix)
if "if (!agId) { /* não é link de confirmação" in content:
    old = "    var params = new URLSearchParams(window.location.search);\n    var agId   = params.get('id');\n    if (!agId) { /* não é link de confirmação, nada a fazer */ }\n    else {"
    new = "    (async function() {\n    var params = new URLSearchParams(window.location.search);\n    var agId   = params.get('id');\n    if (!agId) return; // não é link de confirmação, sai"
    if old in content:
        content = content.replace(old, new)
        fixes += 1
        print("✅ Fix 1b: else solto removido e IIFE corrigida")

# Fechar a IIFE async se ainda não fechou
if "(async function()" in content and "})(); // fim IIFE async" not in content:
    old = "    } catch(e) {\n      console.error(e);\n      showError();\n    }\n  </script>\n\n  <!-- SIDEBAR -->"
    new = "    } catch(e) {\n      console.error(e);\n      showError();\n    }\n    })(); // fim IIFE async\n  </script>\n\n  <!-- SIDEBAR -->"
    if old in content:
        content = content.replace(old, new)
        fixes += 1
        print("✅ Fix 1c: IIFE async fechada")
elif "})(); // fim IIFE async" in content:
    print("✓  Fix 1: overlay script OK")

# ── FIX 2: Link de confirmação ───────────────────────────────────────────────
old = "const link = `https://websalaov2.vercel.app/?id=${ag.id}`;"
new = "const link = `https://websalaov2.vercel.app/confirmacao?id=${ag.id}`;"
if old in content:
    content = content.replace(old, new)
    fixes += 1
    print("✅ Fix 2: link de confirmação corrigido")
elif "confirmacao?id=" in content:
    print("✓  Fix 2: link OK")

# ── FIX 3: fbBatchSet com chunks ─────────────────────────────────────────────
old = """    async function fbBatchSet(col, items) {
      if (!items || !items.length) return;
      const batch = writeBatch(db);
      items.forEach(item => batch.set(doc(db, col, String(item.id)), item, { merge: true }));
      await batch.commit();
    }"""
new = """    async function fbBatchSet(col, items) {
      if (!items || !items.length) return;
      for (let i = 0; i < items.length; i += 499) {
        const chunk = items.slice(i, i + 499);
        const batch = writeBatch(db);
        chunk.forEach(item => batch.set(doc(db, col, String(item.id)), item, { merge: true }));
        await batch.commit();
      }
    }"""
if old in content:
    content = content.replace(old, new)
    fixes += 1
    print("✅ Fix 3: fbBatchSet com chunks aplicado")
elif "chunks" in content and "fbBatchSet" in content:
    print("✓  Fix 3: fbBatchSet OK")

# ── FIX 4: Bloco de inicialização Firebase ───────────────────────────────────
old4 = "      // Firebase em background"
new4_check = "Dados carregados com sucesso"
if old4 in content and new4_check not in content:
    idx = content.find(old4)
    # Encontrar fim do bloco async
    end_block = content.find("      })();\n    });", idx) + len("      })();\n    });")
    old_block = content[idx:end_block]
    new_block = """      // Firebase — carrega dados e inicia listeners em tempo real
      (async () => {
        try {
          await new Promise(resolve => {
            if (_fbReady && window.FirebaseDB) { resolve(); return; }
            const t = setTimeout(resolve, 8000);
            window.addEventListener('firebase-ready', () => { clearTimeout(t); resolve(); }, { once: true });
          });
          if (!window.FirebaseDB) { startPolling(); return; }
          const { fbGetAll, fbBatchSet } = window.FirebaseDB;
          console.log('[Firebase] Carregando dados...');
          const [agFb, cliFb, svcFb, finFb, wppFb] = await Promise.all([
            fbGetAll('agendamentos'), fbGetAll('clientes'), fbGetAll('servicos'),
            fbGetAll('financeiro'), fbGetAll('wppMensagens')
          ]);
          console.log('[Firebase] agendamentos:', agFb.length, '| wppMensagens:', wppFb.length);
          if (agFb.length > 0) { State.data.agendamentos = agFb; Storage.save('agendamentos', agFb); }
          else { const loc = Storage.load('agendamentos')||[]; if(loc.length) await fbBatchSet('agendamentos',loc); }
          if (cliFb.length > 0) { State.data.clientes = cliFb; Storage.save('clientes', cliFb); }
          if (svcFb.length > 0) { State.data.servicos = svcFb; Storage.save('servicos', svcFb); }
          if (finFb.length > 0) { State.data.financeiro = finFb; Storage.save('financeiro', finFb); }
          const wppLocal = Storage.load('wppMensagens')||[];
          const wppMerge = [...wppFb];
          wppLocal.forEach(l => { if(!wppMerge.find(n=>String(n.id)===String(l.id))) wppMerge.push(l); });
          State.data.wppMensagens = wppMerge; Storage.save('wppMensagens', wppMerge);
          navigate(State.currentPage); updateWppBadge();
          console.log('[Firebase] \u2713 Dados carregados com sucesso');
          startPolling();
        } catch (e) { console.warn('[Firebase] Erro:', e.message); startPolling(); }
      })();
    });"""
    content = content[:idx] + new_block + content[end_block:]
    fixes += 1
    print("✅ Fix 4: inicialização Firebase reescrita")
elif new4_check in content:
    print("✓  Fix 4: inicialização Firebase OK")

# ── FIX 5: startPolling com onSnapshot correto ───────────────────────────────
old5_check = "function startPolling()"
new5_check = "Listener agendamentos"
if old5_check in content and new5_check not in content:
    # Encontrar e substituir startPolling
    i1 = content.find("    function startPolling() {")
    i2 = content.find("\n    // ─── SYNC", i1)
    if i1 > 0 and i2 > 0:
        new_polling = """    function startPolling() {
      if (!window.FirebaseDB) return;
      const { db, collection, onSnapshot, fbGetAll, fbBatchSet } = window.FirebaseDB;

      // Listener agendamentos — atualiza status em tempo real
      onSnapshot(collection(db, 'agendamentos'), snap => {
        const doFb = snap.docs.map(d => {
          const dado = d.data();
          const numId = isNaN(d.id) ? dado.id : Number(d.id);
          return { ...dado, id: numId !== undefined ? numId : d.id };
        });
        if (!doFb.length) return;
        const prev = State.data.agendamentos || [];
        doFb.forEach(ag => {
          const ant = prev.find(x => String(x.id) === String(ag.id));
          if (ant && ant.status !== ag.status) {
            if (ag.status === 'confirmado') toast(`\u2705 ${(ag.clienteNome||'').split(' ')[0]} confirmou!`, 'success');
            else if (ag.status === 'cancelado') toast(`\u274C ${(ag.clienteNome||'').split(' ')[0]} cancelou.`, 'error');
            if (State.data.wppMensagens) {
              const mi = State.data.wppMensagens.findIndex(m => String(m.agId) === String(ag.id));
              if (mi >= 0) { State.data.wppMensagens[mi].resposta = ag.status==='confirmado'?'sim':'nao'; State.data.wppMensagens[mi].lida=false; Storage.save('wppMensagens',State.data.wppMensagens); }
            }
          }
        });
        State.data.agendamentos = doFb; Storage.save('agendamentos', doFb);
        if (State.currentPage === 'agenda') renderAgendaGrid();
        if (document.getElementById('wpp-inbox-inner')) renderWppInboxCard();
        updateWppBadge();
      });

      // Listener wppMensagens
      onSnapshot(collection(db, 'wppMensagens'), snap => {
        const novas = snap.docs.map(d => { const data=d.data(); const numId=isNaN(d.id)?data.id:Number(d.id); return {...data,id:numId!==undefined?numId:d.id}; });
        const locais = State.data.wppMensagens || [];
        const merged = [...novas];
        locais.forEach(l => { if(!merged.find(n=>String(n.id)===String(l.id))) merged.push(l); });
        State.data.wppMensagens = merged; Storage.save('wppMensagens', merged);
        updateWppBadge();
        if (document.getElementById('wpp-inbox-inner')) renderWppInboxCard();
        if (State.currentPage === 'whatsapp') renderWppConfig(document.getElementById('page-content'));
      });

      // Polling 10s de segurança
      setInterval(async () => {
        try {
          const doFb = await fbGetAll('agendamentos');
          if (!doFb.length) return;
          State.data.agendamentos = doFb; Storage.save('agendamentos', doFb);
          if (State.currentPage === 'agenda') renderAgendaGrid();
          updateWppBadge();
        } catch(e) {}
      }, 10000);
    }"""
        content = content[:i1] + new_polling + content[i2:]
        fixes += 1
        print("✅ Fix 5: startPolling reescrito")
elif new5_check in content:
    print("✓  Fix 5: startPolling OK")

# ── Salvar ────────────────────────────────────────────────────────────────────
with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n{'='*50}")
print(f"✅ {fixes} correções aplicadas")
print(f"📦 Novo tamanho: {len(content)} bytes")
print(f"\nAgora execute:")
print(f"  vercel --prod")
print(f"  curl -s https://websalaov2.vercel.app | grep -c 'async function'")
print(f"  # deve retornar 12 ou mais")
