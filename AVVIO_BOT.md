# Come Avviare RefLoop Bot

## ⚠️ Requisiti

Il bot richiede:
1. ✅ **Bot Token** (già configurato: 8384270899:AAHkMQ05e4SdCEUablOqYKc5LUXEUFfMsQg)
2. ❌ **Database PostgreSQL** (da configurare)
3. ✅ **Python 3.8+** (già installato)
4. ✅ **Dipendenze Python** (già installate)

## 🚀 Opzione 1: Deploy su Render (CONSIGLIATO)

### Vantaggi
- Database PostgreSQL gratuito incluso
- Sempre online 24/7
- Nessuna configurazione locale
- Deploy in 5 minuti

### Passi
1. Vai su [render.com](https://dashboard.render.com/)
2. Crea nuovo PostgreSQL database
3. Crea nuovo Web Service
4. Collega questo repository
5. Configura variabili d'ambiente:
   - `BOT_TOKEN`: 8384270899:AAHkMQ05e4SdCEUablOqYKc5LUXEUFfMsQg
   - `DATABASE_URL`: [URL dal database Render]
   - `ADMIN_USER_IDS`: [Il tuo Telegram user ID]
6. Deploy!

**Guida completa**: Vedi `QUICK_START.md`

## 🏠 Opzione 2: Avvio Locale

### Requisiti Aggiuntivi
- PostgreSQL installato localmente
- Database creato

### Installazione PostgreSQL (macOS)
```bash
# Installa PostgreSQL
brew install postgresql@14

# Avvia servizio
brew services start postgresql@14

# Crea database
createdb refloop_db
```

### Configurazione
1. Aggiorna `.env` con il database locale:
```env
DATABASE_URL=postgresql://localhost:5432/refloop_db
```

2. Installa psycopg2:
```bash
source venv/bin/activate
pip install psycopg2-binary
```

3. Avvia il bot:
```bash
source venv/bin/activate
python bot.py
```

## 📱 Configurazione Telegram

### 1. Ottieni il tuo User ID
1. Apri Telegram
2. Cerca `@userinfobot`
3. Invia `/start`
4. Copia il tuo ID

### 2. Aggiorna .env
```env
ADMIN_USER_IDS=IL_TUO_USER_ID
```

### 3. Configura il Canale
Il bot deve essere admin nel canale RefLoop (ID: -1003625306083)

Permessi necessari:
- ✅ Post messages
- ✅ Edit messages
- ✅ Delete messages

## 🧪 Test

Una volta avviato, testa:
```
1. Apri Telegram
2. Cerca @refloop_bot
3. Invia /start
4. Verifica che il menu appaia nel canale
```

## ❌ Errori Comuni

### "No module named 'psycopg2'"
```bash
source venv/bin/activate
pip install psycopg2-binary
```

### "could not connect to server"
PostgreSQL non è in esecuzione:
```bash
brew services start postgresql@14
```

### "database does not exist"
Crea il database:
```bash
createdb refloop_db
```

## 📞 Supporto

- **Documentazione completa**: `README.md`
- **Setup rapido**: `QUICK_START.md`
- **Guida v2.0**: `V2_SUMMARY.md`

---

**Consiglio**: Usa Render per un'esperienza senza problemi! 🚀
