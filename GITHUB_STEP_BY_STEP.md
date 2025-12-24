# 🎯 GitHub - Passo per Passo (SUPER SEMPLICE)

## Cosa Stai Per Fare

Caricare il codice del bot su GitHub (è come Google Drive ma per codice).

---

## 📍 PASSO 1: Vai su GitHub

1. Apri il browser
2. Vai su: **github.com**
3. Se non hai account:
   - Clicca "Sign up"
   - Crea account (email, password, username)
4. Se hai già account:
   - Clicca "Sign in"
   - Fai login

---

## 📍 PASSO 2: Crea Spazio per il Codice

1. Una volta dentro GitHub, guarda in alto a destra
2. Vedi un **"+"**? Cliccalo
3. Clicca **"New repository"**

Ora compila il form:

```
┌─────────────────────────────────────────┐
│ Repository name *                       │
│ [refloop-bot]                          │ ← Scrivi questo
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Description (optional)                  │
│ [RefLoop Telegram Bot]                 │ ← Scrivi questo
└─────────────────────────────────────────┘

○ Public  ● Private                        ← Lascia Public

Initialize this repository with:
☐ Add a README file                       ← NON selezionare
☐ Add .gitignore                          ← NON selezionare
☐ Choose a license                        ← NON selezionare
```

4. Clicca il bottone verde **"Create repository"**

---

## 📍 PASSO 3: Copia l'Indirizzo del Tuo Repository

Dopo aver creato il repository, vedrai una pagina con dei comandi.

In alto c'è un box con un indirizzo tipo:
```
https://github.com/TUO_USERNAME/refloop-bot.git
```

**COPIA QUESTO INDIRIZZO** (clicca l'icona copia a destra)

---

## 📍 PASSO 4: Apri il Terminale

**Su Mac:**
1. Premi `Cmd + Spazio` (insieme)
2. Scrivi: `terminal`
3. Premi Invio

Si apre una finestra nera/bianca con del testo.

---

## 📍 PASSO 5: Vai nella Cartella del Bot

Nel terminale, scrivi:

```bash
cd Desktop/RefLoop
```

Premi **Invio**.

Se la cartella è in un altro posto, scrivi il percorso corretto.
Esempio: `cd Documents/RefLoop` o `cd Downloads/RefLoop`

---

## 📍 PASSO 6: Carica il Codice

Ora copia e incolla questi comandi **UNO ALLA VOLTA**.

### Comando 1
```bash
git init
```
Premi **Invio**. Aspetta che finisca (1 secondo).

### Comando 2
```bash
git add .
```
Premi **Invio**. Aspetta (2-3 secondi).

### Comando 3
```bash
git commit -m "RefLoop Bot v2.0"
```
Premi **Invio**. Aspetta (1 secondo).

### Comando 4
```bash
git branch -M main
```
Premi **Invio**. Aspetta (1 secondo).

### Comando 5
```bash
git remote add origin INDIRIZZO_CHE_HAI_COPIATO
```

⚠️ **IMPORTANTE**: Sostituisci `INDIRIZZO_CHE_HAI_COPIATO` con l'indirizzo che hai copiato al PASSO 3!

Esempio completo:
```bash
git remote add origin https://github.com/mario123/refloop-bot.git
```

Premi **Invio**.

### Comando 6
```bash
git push -u origin main
```
Premi **Invio**.

Ti chiederà:
```
Username: [scrivi il tuo username GitHub]
Password: [usa il token - vedi sotto]
```

---

## 🔑 Come Ottenere il Token (Password Speciale)

GitHub non usa più la password normale. Devi creare un "token":

### Passo A
1. Vai su: **github.com/settings/tokens**
2. Clicca **"Generate new token"**
3. Clicca **"Generate new token (classic)"**

### Passo B
Compila il form:
```
Note: RefLoop Bot
Expiration: 90 days

Select scopes:
✅ repo (seleziona la checkbox principale)
```

### Passo C
1. Scorri in fondo
2. Clicca **"Generate token"** (bottone verde)
3. Vedrai un codice tipo: `ghp_abc123xyz...`
4. **COPIA QUESTO CODICE** (lo vedi solo ora!)

### Passo D
Quando il terminale ti chiede "Password", incolla questo token.

---

## ✅ VERIFICA CHE HA FUNZIONATO

1. Vai su: **github.com/TUO_USERNAME/refloop-bot**
2. Dovresti vedere tutti i file:
   - bot.py ✅
   - database.py ✅
   - requirements.txt ✅
   - README.md ✅
   - E tanti altri file ✅

---

## 🎉 PERFETTO!

Ora il codice è su GitHub!

**Prossimo passo**: Vai su Render e collega questo repository.

---

## 🆘 Aiuto! Qualcosa Non Funziona

### Errore: "git: command not found"
Git non è installato. Nel terminale scrivi:
```bash
brew install git
```
Poi riprova dal PASSO 6.

### Errore: "Permission denied"
Username o token sbagliati. Riprova:
```bash
git push -u origin main
```
E inserisci username e token corretti.

### Errore: "Repository not found"
L'indirizzo è sbagliato. Controlla che sia esattamente:
```
https://github.com/TUO_USERNAME/refloop-bot.git
```

### Non Trovo la Cartella
Nel terminale, scrivi:
```bash
pwd
```
Ti dice dove sei. Poi usa `cd` per andare nella cartella giusta.

---

## 📝 Tutti i Comandi in Sequenza

```bash
cd Desktop/RefLoop
git init
git add .
git commit -m "RefLoop Bot v2.0"
git branch -M main
git remote add origin https://github.com/TUO_USERNAME/refloop-bot.git
git push -u origin main
```

Ricorda di sostituire `TUO_USERNAME` con il tuo vero username!

---

## 🎯 Fatto Questo, Cosa Faccio?

Vai su Render e segui la guida **DEPLOY_RENDER_GUIDA.md**!

Il codice è già online su GitHub, ora devi solo dire a Render di usarlo! 🚀
