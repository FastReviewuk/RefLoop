# 🚀 Guida Deploy RefLoop Bot su Render

## Passo 1: Preparazione (2 minuti)

### A. Ottieni il tuo Telegram User ID
1. Apri Telegram
2. Cerca `@userinfobot`
3. Invia `/start`
4. **Copia il numero che ti dà** (es: 123456789)
   - Questo sarà il tuo ADMIN_USER_IDS

### B. Configura il Bot come Admin nel Canale
1. Apri il canale RefLoop su Telegram
2. Vai su Info Canale → Amministratori
3. Aggiungi `@refloop_bot` come amministratore
4. Dai questi permessi:
   - ✅ Inviare messaggi
   - ✅ Modificare messaggi
   - ✅ Eliminare messaggi
5. Salva

---

## Passo 2: Crea Account Render (1 minuto)

1. Vai su https://dashboard.render.com/
2. Clicca "Get Started"
3. Registrati con:
   - GitHub (consigliato)
   - GitLab
   - Email

---

## Passo 3: Carica il Codice su GitHub (3 minuti)

### Opzione A: Hai già GitHub?
```bash
# Nella cartella RefLoop
git init
git add .
git commit -m "RefLoop Bot v2.0"
git branch -M main
git remote add origin https://github.com/TUO_USERNAME/refloop-bot.git
git push -u origin main
```

### Opzione B: Non hai GitHub?
1. Vai su https://github.com/new
2. Crea repository "refloop-bot"
3. Segui le istruzioni per caricare il codice

### Opzione C: Usa Public Git Repository
Puoi anche usare l'opzione "Public Git Repository" su Render e inserire l'URL del tuo repo.

---

## Passo 4: Crea Database PostgreSQL (2 minuti)

1. Nel Dashboard Render, clicca **"New +"**
2. Seleziona **"PostgreSQL"**
3. Configura:
   ```
   Name: refloop-db
   Database: refloop_db
   User: (lascia auto-generato)
   Region: Frankfurt (o più vicino a te)
   PostgreSQL Version: 15
   Plan: Free
   ```
4. Clicca **"Create Database"**
5. Aspetta 1-2 minuti che si crei
6. **IMPORTANTE**: Copia l'"Internal Database URL"
   - Clicca sul database appena creato
   - Cerca "Internal Database URL"
   - Clicca l'icona copia
   - Inizia con: `postgresql://...`

---

## Passo 5: Crea Web Service (3 minuti)

1. Nel Dashboard Render, clicca **"New +"**
2. Seleziona **"Web Service"**
3. Connetti il tuo repository GitHub
   - Se non vedi il repo, clicca "Configure account"
   - Dai accesso al repository
4. Configura il servizio:

```
Name: refloop-bot
Environment: Python 3
Region: Frankfurt (stesso del database)
Branch: main
Build Command: pip install -r requirements.txt
Start Command: python bot.py
Plan: Free
```

5. Clicca **"Advanced"** per aggiungere variabili d'ambiente

---

## Passo 6: Configura Variabili d'Ambiente (2 minuti)

Clicca **"Add Environment Variable"** per ognuna:

### Variabile 1: BOT_TOKEN
```
Key: BOT_TOKEN
Value: 8384270899:AAHkMQ05e4SdCEUablOqYKc5LUXEUFfMsQg
```

### Variabile 2: DATABASE_URL
```
Key: DATABASE_URL
Value: [Incolla l'Internal Database URL dal Passo 4]
```
Esempio: `postgresql://refloop_user:abc123@dpg-xyz.frankfurt-postgres.render.com/refloop_db`

### Variabile 3: ADMIN_USER_IDS
```
Key: ADMIN_USER_IDS
Value: [Il tuo User ID dal Passo 1A]
```
Esempio: `123456789`

---

## Passo 7: Deploy! (3-5 minuti)

1. Clicca **"Create Web Service"**
2. Render inizierà il deploy automaticamente
3. Vedrai i log in tempo reale:
   ```
   ==> Cloning from https://github.com/...
   ==> Installing dependencies...
   ==> Starting service...
   ==> Database initialized successfully!
   ==> Bot started!
   ```
4. Aspetta che appaia **"Your service is live 🎉"**

---

## Passo 8: Verifica che Funzioni (1 minuto)

### A. Controlla i Log
Nel dashboard Render:
1. Clicca sul tuo servizio "refloop-bot"
2. Vai su "Logs"
3. Dovresti vedere:
   ```
   Database initialized successfully!
   Bot started!
   ```

### B. Testa su Telegram
1. Apri Telegram
2. Cerca `@refloop_bot`
3. Invia `/start`
4. Dovresti vedere:
   - Messaggio di benvenuto
   - Menu con bottoni nel canale RefLoop

### C. Testa il Menu
Nel canale RefLoop dovresti vedere:
```
👋 Welcome to RefLoop!

🔗 Share referral links and earn Telegram Stars!

💰 Pricing Plans:
• Plan A: 5 referrals → 25 ⭐
• Plan B: 10 referrals → 40 ⭐
• Plan C: 30 referrals → 100 ⭐

[🔗 Submit Referral Link]
[🔍 Browse Links]
[🎁 Claim Reward]
[📊 My Status]
```

---

## ✅ Checklist Finale

- [ ] Database PostgreSQL creato
- [ ] Internal Database URL copiato
- [ ] Web Service creato
- [ ] Tutte e 3 le variabili d'ambiente configurate
- [ ] Deploy completato con successo
- [ ] Log mostrano "Bot started!"
- [ ] Bot risponde su Telegram
- [ ] Menu appare nel canale
- [ ] Bot è admin nel canale

---

## 🐛 Risoluzione Problemi

### Errore: "could not connect to database"
- Verifica che DATABASE_URL sia corretto
- Usa "Internal Database URL" non "External"
- Controlla che database e bot siano nella stessa region

### Errore: "BOT_TOKEN not found"
- Verifica che la variabile sia scritta esattamente: `BOT_TOKEN`
- Controlla che il token sia corretto
- Riavvia il servizio

### Bot non risponde
- Controlla i log per errori
- Verifica che il servizio sia "Live"
- Prova a riavviare: Manual Deploy → "Clear build cache & deploy"

### Menu non appare nel canale
- Verifica che il bot sia admin nel canale
- Controlla che CHANNEL_ID sia corretto (-1003625306083)
- Dai i permessi corretti al bot

### "Admin commands don't work"
- Verifica che ADMIN_USER_IDS sia il TUO user ID
- Ottienilo da @userinfobot
- Riavvia il servizio dopo aver cambiato la variabile

---

## 🎉 Congratulazioni!

Il tuo bot è ora online 24/7 su Render!

### Prossimi Passi:
1. Testa tutte le funzionalità
2. Invita utenti nel canale
3. Monitora i log per eventuali errori
4. Leggi `ADMIN_GUIDE.md` per gestire le approvazioni

### Comandi Utili:
- **Riavvia bot**: Dashboard → Manual Deploy → Deploy latest commit
- **Vedi log**: Dashboard → Logs
- **Modifica variabili**: Dashboard → Environment → Edit

---

## 📊 Costi

**Piano Free Render include:**
- ✅ 750 ore/mese (sufficiente per 24/7)
- ✅ Database PostgreSQL 1GB
- ✅ Deploy automatici da GitHub
- ✅ SSL gratuito
- ✅ Logs in tempo reale

**Limitazioni Free:**
- Il servizio va in sleep dopo 15 min di inattività
- Si riattiva automaticamente alla prima richiesta
- Per mantenerlo sempre attivo: upgrade a piano Starter ($7/mese)

---

## 🆘 Serve Aiuto?

1. Controlla i log su Render
2. Leggi `README.md` per documentazione completa
3. Verifica `TROUBLESHOOTING.md`
4. Controlla che tutte le variabili siano corrette

**Il bot è pronto! Buon lavoro! 🚀⭐**
