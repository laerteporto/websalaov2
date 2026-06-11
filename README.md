## Visão Geral do sistema

Sistema voltado para pequenos e medios saloes de beleza, oferecendo controle de agenda, cadastro de
clientes, catalogo de servicos, gestao financeira, relatorios gerenciais e integracao com WhatsApp para
envio de lembretes e confirmacao de agendamentos pelos proprios clientes.

## Arquitetura Geral

O sistema e uma SPA (Single Page Application) puramente client-side. Nao ha servidor backend proprio -
toda a persistencia e feita diretamente via Firebase Firestore (client SDK). O roteamento de paginas e
feito via JavaScript no navegador, sem frameworks, utilizando funcoes de renderizacao que manipulam o
DOM diretamente.
-Interface unica: index.html contem todo o CSS e JavaScript do sistema
-Navegacao SPA: funcao navigate() gerencia troca de paginas
-Persistencia dupla: Firebase Firestore + localStorage (cache offline)
-Deploy: Vercel com redirecionamento para SPA

## Stack Tecnologica

FrontendHTML5 + CSS3 + JavaScriptES Modules
Backend/DatabaseFirebase Firestore10.12.0
AutenticacaoFirebase Auth + PBKDF2SHA-256
Hash de senhaPBKDF2 (100.000 iteracoes)Web Crypto API
Fonte tipograficaCormorant Garamond + JostGoogle Fonts
