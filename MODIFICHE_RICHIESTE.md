# Modifiche Richieste per RefLoop Bot

## 📋 Cosa Modificare

### 1. ✅ Ordine Bottoni Menu (FATTO)
```
Prima: Submit, Browse, Claim, Status
Dopo: Status, Browse, Submit, Claim
```

### 2. ✅ Registrazione Automatica (FATTO)
- Quando utente entra nel canale viene registrato automaticamente
- Non serve più "Please use /start first"

### 3. ⚠️ Sistema "3 Claim per Free Submission" (DA COMPLETARE)
- Utente completa 3 claim verificati
- Sblocca 1 submission gratuita
- Può scegliere tra pagare o usare free

### 4. ✅ Descrizione Obbligatoria Max 120 Caratteri (FATTO)
- Validazione lunghezza descrizione
- Messaggio errore se troppo lunga

### 5. ⚠️ Gestione Free Submissions nel Database (DA AGGIUNGERE)
- Colonna `free_submissions_available` già esiste
- Serve aggiornare logica in `update_user_claims()`

## 🔧 Modifiche da Applicare

### File: database.py

Aggiorna la funzione `update_user_claims`:

```python
def update_user_claims(user_id: int):
    """Increment user's verified claims and handle free submission unlock"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            UPDATE users 
            SET total_verified_claims = total_verified_claims + 1
            WHERE user_id = %s
            RETURNING total_verified_claims
        """, (user_id,))
        result = cursor.fetchone()
        total_claims = result['total_verified_claims']
        
        # Grant free submission after 3rd claim
        if total_claims == 3:
            cursor.execute("""
                UPDATE users 
                SET free_submissions_available = free_submissions_available + 1
                WHERE user_id = %s
            """, (user_id,))
        
        cursor.close()
        return total_claims
```

### File: bot.py

#### 1. Aggiorna `submit_plan_choice` per gestire opzione FREE:

Aggiungi dopo la riga dove gestisci `submit_cancel`:

```python
# Check if FREE plan
if query.data == "plan_FREE":
    user_data = db.get_user(query.from_user.id)
    if user_data['free_submissions_available'] <= 0:
        await query.edit_message_text(
            "❌ You don't have any free submissions available.\n"
            "Complete 3 verified claims to unlock free submission!"
        )
        return ConversationHandler.END
    
    context.user_data['plan'] = 'FREE'
    context.user_data['max_claims'] = 5
    context.user_data['price'] = 0
    context.user_data['payment_method'] = 'free'
else:
    # Codice esistente per plan A/B/C
    ...
```

#### 2. Aggiorna `submit_description` per validare lunghezza:

All'inizio della funzione aggiungi:

```python
# Validate description length
if len(description) > 120:
    await update.message.reply_text(
        f"❌ Description too long! ({len(description)}/120 characters)\n\n"
        "Please send a shorter description (max 120 characters):"
    )
    return SUBMIT_DESCRIPTION
```

#### 3. Aggiorna `submit_description` per gestire free submissions:

Sostituisci la parte del pagamento con:

```python
# Check if free or paid
if context.user_data.get('payment_method') == 'free':
    # Use free slot
    db.use_free_submission(update.effective_user.id)
    
    # Create link
    link_id = db.create_referral_link(...)
    
    await update.message.reply_text("✅ Link submitted successfully!")
    context.user_data.clear()
    return ConversationHandler.END
else:
    # Send invoice for paid plan
    ...
```

#### 4. Aggiorna `approve_claim` per notificare free submission:

Dopo `total_claims = db.update_user_claims(...)` aggiungi:

```python
# Check if user reached 3 claims
if total_claims == 3:
    user_message = (
        f"✅ Your claim has been approved!\n\n"
        f"🎉 Congratulations! You've completed 3 verified claims!\n"
        f"🎁 You've unlocked 1 FREE link submission!\n\n"
        f"⭐ You've also earned 3 Telegram Stars!"
    )
else:
    user_message = (
        f"✅ Your claim has been approved!\n\n"
        f"📊 Total verified claims: {total_claims}\n\n"
        f"⭐ You've earned 3 Telegram Stars!"
    )
    
    if total_claims < 3:
        user_message += f"\n\n💡 Complete {3 - total_claims} more claim(s) to unlock FREE submission!"
```

## 🧪 Test da Fare

1. ✅ Utente entra nel canale → vede menu
2. ✅ Bottoni in ordine: Status, Browse, Submit, Claim
3. ⚠️ Utente con 0 claim → vede solo piani a pagamento
4. ⚠️ Utente completa 3 claim → riceve notifica free submission
5. ⚠️ Utente con 3+ claim → vede opzione "Use Free Submission"
6. ✅ Descrizione > 120 caratteri → errore
7. ✅ Descrizione ≤ 120 caratteri → accettata

## 📝 Note

- La colonna `free_submissions_available` esiste già nel database
- La funzione `use_free_submission()` esiste già in database.py
- Serve solo collegare tutto insieme nel flusso

## 🚀 Prossimi Passi

1. Applica modifiche a database.py
2. Applica modifiche a bot.py
3. Testa il flusso completo
4. Deploy su Render

Vuoi che applichi queste modifiche automaticamente?
