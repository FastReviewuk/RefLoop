# ✅ Checklist Deploy Render - RefLoop Bot

## Prima di Iniziare

### 1. Ottieni il tuo Telegram User ID
- [ ] Apri Telegram
- [ ] Cerca `@userinfobot`
- [ ] Invia `/start`
- [ ] **Copia il numero** (es: 123456789)

### 2. Configura Bot nel Canale
- [ ] Apri canale RefLoop su Telegram
- [ ] Aggiungi `@refloop_bot` come admin
- [ ] Dai permessi: Inviare, Modificare, Eliminare messaggi

---

## Deploy su Render

### 3. Crea Account
- [ ] Vai su https://dashboard.render.com/
- [ ] Registrati (consigliato: con GitHub)

### 4. Carica Codice su GitHub
- [ ] Crea repository su GitHub
- [ ] Carica il codice della cartella RefLoop
- [ ] Verifica che tutti i file siano presenti

### 5. Crea Database PostgreSQL
- [ ] Dashboard Render → New + → PostgreSQL
- [ ] Name: `refloop-db`
- [ ] Database: `refloop_db`
- [ ] Region: Frankfurt
- [ ] Plan: Free
- [ ] Create Database
- [ ] **COPIA "Internal Database URL"** (inizia con postgresql://)

### 6. Crea Web Service
- [ ] Dashboard Render → New + → Web Service
- [ ] Connetti repository GitHub
- [ ] Name: `refloop-bot`
- [ ] Environment: Python 3
- [ ] Region: Frankfurt (stesso del database!)
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `python bot.py`
- [ ] Plan: Free

### 7. Aggiungi Variabili d'Ambiente
Clicca "Advanced" → "Add Environment Variable":

- [ ] **BOT_TOKEN**
  ```
  8384270899:AAHkMQ05e4SdCEUablOqYKc5LUXEUFfMsQg
  ```

- [ ] **DATABASE_URL**
  ```
  [Incolla Internal Database URL dal passo 5]
  ```

- [ ] **ADMIN_USER_IDS**
  ```
  [Il tuo User ID dal passo 1]
  ```

### 8. Deploy
- [ ] Clicca "Create Web Service"
- [ ] Aspetta 3-5 minuti
- [ ] Controlla i log: deve apparire "Bot started!"

---

## Verifica Funzionamento

### 9. Test Bot
- [ ] Apri Telegram
- [ ] Cerca `@refloop_bot`
- [ ] Invia `/start`
- [ ] Ricevi messaggio di benvenuto

### 10. Test Canale
- [ ] Apri canale RefLoop
- [ ] Verifica che appaia il menu con bottoni:
  - 🔗 Submit Referral Link
  - 🔍 Browse Links
  - 🎁 Claim Reward
  - 📊 My Status

### 11. Test Funzionalità
- [ ] Clicca "Submit Link" → Vedi 3 piani
- [ ] Clicca "Browse" → Vedi categorie
- [ ] Clicca "My Status" → Vedi statistiche
- [ ] Test comando admin: `/approve 1` (dovrebbe dire "Claim not found" se non ci sono claim)

---

## 🎉 Completato!

Se tutti i check sono ✅, il bot è online e funzionante!

## 📊 Monitoraggio

### Dove Controllare
- **Logs**: Dashboard Render → refloop-bot → Logs
- **Status**: Dashboard Render → refloop-bot (deve essere "Live")
- **Database**: Dashboard Render → refloop-db (deve essere "Available")

### Comandi Utili
- **Riavvia**: Manual Deploy → Deploy latest commit
- **Modifica variabili**: Environment → Edit
- **Vedi metriche**: Metrics tab

---

## ⚠️ Note Importanti

1. **Piano Free**: Il bot va in sleep dopo 15 min di inattività
   - Si riattiva automaticamente alla prima richiesta
   - Per mantenerlo sempre attivo: upgrade a Starter ($7/mese)

2. **Region**: Database e bot devono essere nella stessa region!

3. **Internal URL**: Usa sempre "Internal Database URL" non "External"

4. **Variabili**: Dopo aver modificato variabili, riavvia il servizio

---

## 🆘 Problemi?

### Bot non si avvia
1. Controlla i log per errori
2. Verifica tutte le variabili d'ambiente
3. Controlla che DATABASE_URL sia corretto

### Menu non appare nel canale
1. Verifica che bot sia admin nel canale
2. Controlla permessi del bot
3. Verifica CHANNEL_ID nel codice (-1003625306083)

### Comandi admin non funzionano
1. Verifica ADMIN_USER_IDS
2. Ottieni il tuo ID da @userinfobot
3. Riavvia il servizio

---

**Tempo totale stimato: 15 minuti**

**Guida dettagliata**: Vedi `DEPLOY_RENDER_GUIDA.md`
