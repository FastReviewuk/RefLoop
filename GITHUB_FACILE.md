# 📦 Come Caricare il Codice su GitHub - Guida Semplice

## 🎯 Cosa Devi Fare

Caricare il codice del bot su GitHub così Render può usarlo.

---

## ✅ PASSO 1: Crea Account GitHub (se non ce l'hai)

1. Vai su: **https://github.com**
2. Clicca **"Sign up"** (in alto a destra)
3. Inserisci:
   - Email
   - Password
   - Username (scegli quello che vuoi)
4. Verifica email
5. Login

---

## ✅ PASSO 2: Crea Nuovo Repository

1. Una volta loggato, clicca il **"+"** in alto a destra
2. Clicca **"New repository"**
3. Compila:
   ```
   Repository name: refloop-bot
   Description: RefLoop Telegram Bot v2.0
   Public ✅ (lascia selezionato)
   
   NON selezionare:
   ❌ Add a README file
   ❌ Add .gitignore
   ❌ Choose a license
   ```
4. Clicca **"Create repository"**

---

## ✅ PASSO 3: Carica il Codice

Dopo aver creato il repository, GitHub ti mostrerà una pagina con dei comandi.

### A. Apri il Terminale

**Su Mac:**
1. Premi `Cmd + Spazio`
2. Scrivi "Terminal"
3. Premi Invio

### B. Vai nella Cartella del Bot

```bash
cd Desktop/RefLoop
```
(o dove hai la cartella RefLoop)

### C. Esegui Questi Comandi

**Copia e incolla UNO alla volta:**

```bash
# 1. Inizializza Git
git init
```
Premi Invio, aspetta che finisca.

```bash
# 2. Aggiungi tutti i file
git add .
```
Premi Invio, aspetta che finisca.

```bash
# 3. Crea il commit
git commit -m "RefLoop Bot v2.0"
```
Premi Invio, aspetta che finisca.

```bash
# 4. Rinomina branch
git branch -M main
```
Premi Invio, aspetta che finisca.

```bash
# 5. Collega a GitHub
git remote add origin https://github.com/TUO_USERNAME/refloop-bot.git
```
⚠️ **IMPORTANTE**: Sostituisci `TUO_USERNAME` con il tuo username GitHub!

Esempio: Se il tuo username è "mario123":
```bash
git remote add origin https://github.com/mario123/refloop-bot.git
```

Premi Invio.

```bash
# 6. Carica il codice
git push -u origin main
```
Premi Invio.

Ti chiederà username e password:
- **Username**: il tuo username GitHub
- **Password**: usa un **Personal Access Token** (vedi sotto)

---

## 🔑 Come Ottenere il Token GitHub

GitHub non accetta più la password normale. Devi creare un "token":

1. Vai su: **https://github.com/settings/tokens**
2. Clicca **"Generate new token"** → **"Generate new token (classic)"**
3. Compila:
   ```
   Note: RefLoop Bot
   Expiration: 90 days
   
   Seleziona:
   ✅ repo (tutti i sotto-checkbox)
   ```
4. Clicca **"Generate token"** (in fondo)
5. **COPIA IL TOKEN** (lo vedi solo una volta!)
   - Inizia con `ghp_...`
6. Usa questo token come "password" quando fai `git push`

---

## ✅ PASSO 4: Verifica

1. Vai su: **https://github.com/TUO_USERNAME/refloop-bot**
2. Dovresti vedere tutti i file del bot:
   - bot.py
   - database.py
   - requirements.txt
   - README.md
   - ecc.

---

## 🎉 FATTO!

Ora il codice è su GitHub e puoi passare a Render!

---

## 🆘 Problemi Comuni

### "git: command not found"
Git non è installato. Installa con:
```bash
brew install git
```

### "Permission denied"
Hai sbagliato username o token. Riprova con:
```bash
git push -u origin main
```

### "Repository not found"
Hai sbagliato l'URL. Controlla che sia:
```
https://github.com/TUO_USERNAME/refloop-bot.git
```

### "Already exists"
Hai già inizializzato Git. Salta il comando `git init`.

---

## 📝 Comandi Riassunti

```bash
cd Desktop/RefLoop
git init
git add .
git commit -m "RefLoop Bot v2.0"
git branch -M main
git remote add origin https://github.com/TUO_USERNAME/refloop-bot.git
git push -u origin main
```

Sostituisci `TUO_USERNAME` con il tuo username GitHub!

---

## 🎯 Prossimo Passo

Una volta caricato su GitHub, vai su Render e segui **DEPLOY_RENDER_GUIDA.md**!
