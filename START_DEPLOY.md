# 🚀 INIZIA QUI - Deploy RefLoop Bot

## ✅ Tutto Pronto!

Il codice del bot è completo e pronto per il deploy su Render.

---

## 📋 PRIMA DI INIZIARE (5 minuti)

### 1. Ottieni il tuo Telegram User ID
```
1. Apri Telegram
2. Cerca: @userinfobot
3. Invia: /start
4. COPIA IL NUMERO che ti dà (es: 123456789)
```

### 2. Configura il Bot nel Canale RefLoop
```
1. Apri il canale RefLoop su Telegram
2. Vai su: Info Canale → Amministratori
3. Aggiungi: @refloop_bot
4. Dai permessi:
   ✅ Inviare messaggi
   ✅ Modificare messaggi
   ✅ Eliminare messaggi
5. Salva
```

---

## 🎯 DEPLOY IN 3 PASSI

### PASSO 1: Carica su GitHub (3 minuti)

#### Opzione A: Automatico
```bash
# Esegui questo script
./git_commands.sh

# Poi segui le istruzioni che appariranno
```

#### Opzione B: Manuale
```bash
# 1. Inizializza Git
git init
git add .
git commit -m "RefLoop Bot v2.0"
git branch -M main

# 2. Crea repository su GitHub
# Vai su: https://github.com/new
# Nome: refloop-bot

# 3. Collega e pusha
git remote add origin https://github.com/TUO_USERNAME/refloop-bot.git
git push -u origin main
```

---

### PASSO 2: Deploy su Render (10 minuti)

#### A. Crea Database
```
1. Vai su: https://dashboard.render.com/
2. Clicca: New + → PostgreSQL
3. Configura:
   Name: refloop-db
   Database: refloop_db
   Region: Frankfurt
   Plan: Free
4. Create Database
5. COPIA "Internal Database URL"
```

#### B. Crea Web Service
```
1. Clicca: New + → Web Service
2. Connetti il tuo repository GitHub
3. Configura:
   Name: refloop-bot
   Environment: Python 3
   Region: Frankfurt
   Build: pip install -r requirements.txt
   Start: python bot.py
   Plan: Free
```

#### C. Aggiungi Variabili d'Ambiente
```
Clicca "Advanced" → "Add Environment Variable"

BOT_TOKEN:
8384270899:AAHkMQ05e4SdCEUablOqYKc5LUXEUFfMsQg

DATABASE_URL:
[Incolla Internal Database URL dal punto A]

ADMIN_USER_IDS:
[Il tuo User ID dal punto 1]
```

#### D. Deploy!
```
1. Clicca: Create Web Service
2. Aspetta 3-5 minuti
3. Controlla i log
```

---

### PASSO 3: Verifica (2 minuti)

```
1. Apri Telegram
2. Cerca: @refloop_bot
3. Invia: /start
4. Verifica menu nel canale RefLoop
```

---

## 📚 GUIDE DISPONIBILI

### Per il Deploy
- **INFO_DEPLOY.txt** ← LEGGI QUESTO PRIMA
- **DEPLOY_RENDER_GUIDA.md** - Guida dettagliata
- **DEPLOY_CHECKLIST.md** - Checklist passo-passo

### Per l'Uso
- **V2_SUMMARY.md** - Novità versione 2.0
- **QUICK_REFERENCE_V2.md** - Riferimento rapido
- **ADMIN_GUIDE.md** - Guida amministratore

---

## 🎯 INFORMAZIONI ESSENZIALI

```
Bot Token:    8384270899:AAHkMQ05e4SdCEUablOqYKc5LUXEUFfMsQg
Bot Username: @refloop_bot
Channel ID:   -1003625306083
```

### Piani Disponibili
```
Plan A:  5 referrals  → 25 ⭐
Plan B: 10 referrals  → 40 ⭐
Plan C: 30 referrals  → 100 ⭐

Ricompensa: 3 ⭐ per claim verificato
```

### Categorie
```
🎮 Games
💰 Crypto
🏦 Banks
📱 Telecom
📦 Other
```

---

## ⏱️ TEMPO TOTALE: ~15 minuti

```
Preparazione:  5 min
GitHub:        3 min
Render:       10 min
Test:          2 min
─────────────────────
TOTALE:       20 min
```

---

## ✅ CHECKLIST RAPIDA

- [ ] User ID ottenuto da @userinfobot
- [ ] Bot aggiunto come admin nel canale
- [ ] Codice caricato su GitHub
- [ ] Database creato su Render
- [ ] Web Service creato su Render
- [ ] 3 variabili d'ambiente configurate
- [ ] Deploy completato
- [ ] Bot risponde su Telegram
- [ ] Menu appare nel canale

---

## 🆘 PROBLEMI?

### Bot non si avvia
→ Controlla i log su Render Dashboard

### Menu non appare
→ Verifica che bot sia admin nel canale

### Comandi admin non funzionano
→ Controlla ADMIN_USER_IDS

### Database error
→ Usa "Internal Database URL" non "External"

---

## 🎉 PRONTO!

Una volta completati tutti i passi, il bot sarà:
- ✅ Online 24/7
- ✅ Pronto per ricevere utenti
- ✅ Funzionante con tutti i piani
- ✅ Integrato con il canale

---

## 📞 LINK UTILI

- Render: https://dashboard.render.com/
- GitHub: https://github.com/new
- Bot: https://t.me/refloop_bot
- User ID Bot: https://t.me/userinfobot

---

**INIZIA ORA! Apri INFO_DEPLOY.txt e segui i passi! 🚀**
