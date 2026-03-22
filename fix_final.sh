#!/bin/bash
# Fix final — corrige o SyntaxError: Unexpected end of input
# Execute: bash fix_final.sh

FILE="/home/laerte/Downloads/websalaov2/index.html"

echo "📄 Arquivo: $FILE"
echo "📦 Tamanho atual: $(wc -c < $FILE) bytes"

# Verificar o problema
echo ""
echo "=== Diagnóstico ==="
echo "Linha com 'if (!agId)':"
grep -n "if (!agId)" "$FILE"
echo ""
echo "Linha com 'async function()':"  
grep -n "(async function()" "$FILE"
echo ""
echo "Linha com 'fim IIFE':"
grep -n "fim IIFE" "$FILE"

# Aplicar correção com Python
python3 - << 'PYEOF'
import sys

FILE = "/home/laerte/Downloads/websalaov2/index.html"
with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

fixes = 0

# Problema: o script de overlay tem "else {" sem fechar
# Detectar e corrigir qualquer variação
import re

# Padrão problemático: if (!agId) ... else { (sem fechar)
pattern_else = "    if (!agId) { /* não é link de confirmação, nada a fazer */ }\n    else {"
if pattern_else in content:
    # Substituir pelo padrão correto com IIFE
    content = content.replace(
        "    var params = new URLSearchParams(window.location.search);\n    var agId   = params.get('id');\n    if (!agId) { /* não é link de confirmação, nada a fazer */ }\n    else {",
        "    (async function() {\n    var params = new URLSearchParams(window.location.search);\n    var agId   = params.get('id');\n    if (!agId) return; // não é link de confirmação"
    )
    # Fechar a IIFE
    if "})(); // fim IIFE async" not in content:
        content = content.replace(
            "    } catch(e) {\n      console.error(e);\n      showError();\n    }\n  </script>\n\n  <!-- SIDEBAR -->",
            "    } catch(e) {\n      console.error(e);\n      showError();\n    }\n    })(); // fim IIFE async\n  </script>\n\n  <!-- SIDEBAR -->"
        )
    fixes += 1
    print("✅ else solto corrigido!")

# Verificar se já tem IIFE mas falta o fechamento
elif "(async function()" in content and "})(); // fim IIFE async" not in content:
    old = "    } catch(e) {\n      console.error(e);\n      showError();\n    }\n  </script>\n\n  <!-- SIDEBAR -->"
    new = "    } catch(e) {\n      console.error(e);\n      showError();\n    }\n    })(); // fim IIFE async\n  </script>\n\n  <!-- SIDEBAR -->"
    if old in content:
        content = content.replace(old, new)
        fixes += 1
        print("✅ IIFE fechada!")

elif "(async function()" in content and "})(); // fim IIFE async" in content:
    print("✓ Script de overlay já está correto")
else:
    print("⚠️ Padrão não reconhecido — verifique manualmente")

if fixes > 0:
    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📦 Novo tamanho: {len(content)} bytes")
    print("✅ Arquivo salvo!")
else:
    print(f"📦 Tamanho: {len(content)} bytes (sem mudanças)")

# Verificação final
lines = content.split('\n')
for i, line in enumerate(lines[2412:2420], start=2413):
    print(f"  Linha {i}: {line}")
PYEOF

echo ""
echo "=== Deploy ==="
echo "Execute: vercel --prod"
