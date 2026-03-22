#!/usr/bin/env python3
"""
Fix: ordem das mensagens (recentes no topo) + botão atualizar funcional
Execute: python3 fix_ordem.py
"""
import os, sys

FILE = "/home/laerte/Downloads/websalaov2/index.html"
with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"📦 Tamanho original: {len(content)} bytes")
fixes = 0

# ── FIX 1: Ordenar mensagens por data de envio (mais recente no topo) ─────────
# Ambas as funções usam .slice().reverse() que inverte a ordem do array
# Mas o array pode não estar ordenado por data — precisamos ordenar por enviadoEm

old1 = "      const msgs = (State.data.wppMensagens || []).slice().reverse();\n\n      if (!msgs.length) {\n        el.innerHTML = `<div class=\"empty-state\" style=\"padding:24px 0;\">"
new1 = "      const msgs = (State.data.wppMensagens || []).slice().sort((a,b) => new Date(b.enviadoEm||0) - new Date(a.enviadoEm||0));\n\n      if (!msgs.length) {\n        el.innerHTML = `<div class=\"empty-state\" style=\"padding:24px 0;\">"

if old1 in content:
    content = content.replace(old1, new1)
    fixes += 1
    print("✅ Fix 1a: renderWppInboxCard — ordenado por data (recente no topo)")
else:
    print("⚠️  Fix 1a: padrão não encontrado")

# Mesma correção na renderWppLista
old2 = "      const msgs = (State.data.wppMensagens || []).slice().reverse();\n\n      if (!msgs.length) {\n        el.innerHTML = `<div class=\"empty-state\" style=\"padding:32px;\">"
new2 = "      const msgs = (State.data.wppMensagens || []).slice().sort((a,b) => new Date(b.enviadoEm||0) - new Date(a.enviadoEm||0));\n\n      if (!msgs.length) {\n        el.innerHTML = `<div class=\"empty-state\" style=\"padding:32px;\">"

if old2 in content:
    content = content.replace(old2, new2)
    fixes += 1
    print("✅ Fix 1b: renderWppLista — ordenado por data (recente no topo)")
else:
    print("⚠️  Fix 1b: padrão não encontrado")

# ── FIX 2: Botão ↻ da caixa de confirmações — buscar do Firebase ─────────────
old3 = '            <button class="btn btn-ghost btn-sm" onclick="renderWppInboxCard()">↻</button>'
new3 = '            <button class="btn btn-ghost btn-sm" title="Atualizar do Firebase" onclick="(async()=>{if(!window.FirebaseDB)return;try{const [agFb,wppFb]=await Promise.all([window.FirebaseDB.fbGetAll(\'agendamentos\'),window.FirebaseDB.fbGetAll(\'wppMensagens\')]);if(agFb.length){State.data.agendamentos=agFb;Storage.save(\'agendamentos\',agFb);}const wppLocal=State.data.wppMensagens||[];const merged=[...wppFb];wppLocal.forEach(l=>{if(!merged.find(n=>String(n.id)===String(l.id)))merged.push(l);});State.data.wppMensagens=merged;Storage.save(\'wppMensagens\',merged);renderWppInboxCard();updateWppBadge();toast(\'Atualizado ✓\',\'success\');}catch(e){toast(\'Erro ao atualizar\',\'error\');}})()">↻</button>'

if old3 in content:
    content = content.replace(old3, new3)
    fixes += 1
    print("✅ Fix 2: botão ↻ agora busca do Firebase")
else:
    print("⚠️  Fix 2: botão ↻ não encontrado")

# ── FIX 3: Texto "N mensagens anteriores" → mais descritivo ──────────────────
old4 = '        html += `<div style="padding:10px 16px;text-align:center;font-size:12px;color:var(--text-muted);">+${msgs.length - 8} mensagens anteriores</div>`;'
new4 = '        html += `<div style="padding:10px 16px;text-align:center;font-size:12px;color:var(--text-muted);">↓ +${msgs.length - 8} mensagens mais antigas</div>`;'

if old4 in content:
    content = content.replace(old4, new4)
    fixes += 1
    print("✅ Fix 3: texto 'mensagens anteriores' atualizado")

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n{'='*50}")
print(f"✅ {fixes} correções aplicadas")
print(f"📦 Novo tamanho: {len(content)} bytes")
print(f"\nAgora execute: vercel --prod")
