# Questo file contiene le modifiche principali da applicare a bot.py
# Copia queste funzioni nel file bot.py originale

# MODIFICA 1: Aggiorna la funzione submit_plan_choice per gestire FREE
async def submit_plan_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plan selection including FREE option"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "submit_cancel":
        await query.edit_message_text("❌ Submission cancelled.")
        return ConversationHandler.END
    
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
        context.user_data['max_claims'] = 5  # Default for free
        context.user_data['price'] = 0
        context.user_data['payment_method'] = 'free'
    else:
        # Extract plan (A, B, or C)
        plan = query.data.split('_')[1]
        context.user_data['plan'] = plan
        context.user_data['max_claims'] = PLANS[plan]['max_claims']
        context.user_data['price'] = PLANS[plan]['price']
        context.user_data['payment_method'] = 'paid'
    
    # Show categories
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat_{i}")] 
                for i, cat in enumerate(CATEGORIES)]
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="submit_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    plan_name = "Free Submission" if context.user_data['plan'] == 'FREE' else PLANS[context.user_data['plan']]['name']
    
    await query.edit_message_text(
        f"✅ Selected: {plan_name}\n\n"
        "📂 Select a category for your referral link:",
        reply_markup=reply_markup
    )
    
    return SUBMIT_CATEGORY


# MODIFICA 2: Aggiorna submit_description per validare lunghezza
async def submit_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle description with 120 char limit and finalize submission"""
    description = update.message.text.strip()
    
    # Validate description length
    if len(description) > 120:
        await update.message.reply_text(
            f"❌ Description too long! ({len(description)}/120 characters)\n\n"
            "Please send a shorter description (max 120 characters):"
        )
        return SUBMIT_DESCRIPTION
    
    context.user_data['description'] = description
    
    # Check if free or paid
    if context.user_data.get('payment_method') == 'free':
        # Use free slot
        db.use_free_submission(update.effective_user.id)
        
        # Create link
        link_id = db.create_referral_link(
            update.effective_user.id,
            context.user_data['category'],
            context.user_data['service_name'],
            context.user_data['url'],
            context.user_data['description'],
            context.user_data['max_claims']
        )
        
        await update.message.reply_text(
            f"✅ Link submitted successfully! (ID: {link_id})\n\n"
            f"📂 {context.user_data['category']}\n"
            f"📝 {context.user_data['service_name']}\n"
            f"🔗 {context.user_data['url']}\n"
            f"📄 {context.user_data['description']}\n"
            f"📊 Max referrals: {context.user_data['max_claims']}\n\n"
            "Your link is now available for users to claim! 🎉"
        )
        
        context.user_data.clear()
        return ConversationHandler.END
    else:
        # Send invoice for paid plan
        plan = context.user_data['plan']
        price = context.user_data['price']
        max_claims = context.user_data['max_claims']
        
        await update.message.reply_invoice(
            title=f"Submit Referral Link - {PLANS[plan]['name']}",
            description=f"Pay {price} Telegram Stars to submit your referral link with up to {max_claims} referrals",
            payload=f"submit_link_{update.effective_user.id}_{plan}",
            provider_token="",  # Empty for Telegram Stars
            currency="XTR",
            prices=[LabeledPrice(f"Plan {plan}", price)]
        )
        
        return SUBMIT_DESCRIPTION


# MODIFICA 3: Aggiorna approve_claim per gestire free submissions
async def approve_claim_UPDATED(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to approve a claim - UPDATED VERSION"""
    if update.effective_user.id not in ADMIN_USER_IDS:
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Usage: /approve <claim_id>")
        return
    
    try:
        claim_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid claim ID.")
        return
    
    claim = db.get_claim(claim_id)
    
    if not claim:
        await update.message.reply_text("❌ Claim not found.")
        return
    
    if claim['status'] != 'pending':
        await update.message.reply_text(f"❌ Claim is already {claim['status']}.")
        return
    
    # Verify the linked referral still exists
    link = db.get_link_by_id(claim['link_id'])
    if not link:
        await update.message.reply_text("❌ The referral link no longer exists.")
        db.reject_claim(claim_id)
        return
    
    # Safety check
    if link['current_claims'] >= link['max_claims']:
        await update.message.reply_text("❌ This link has already reached its maximum claims.")
        db.reject_claim(claim_id)
        return
    
    # Approve the claim
    db.approve_claim(claim_id)
    
    # Update user's verified claims count
    total_claims = db.update_user_claims(claim['referred_user_id'])
    
    # Check if user reached 3 claims - grant free submission
    if total_claims == 3:
        # Grant free submission
        user_data = db.get_user(claim['referred_user_id'])
        # This is already handled in update_user_claims, but we notify
        pass
    
    # Increment link's current claims
    link_update = db.increment_link_claims(claim['link_id'])
    
    # Check if link reached limit and delete
    link_deleted = False
    if link_update and link_update['current_claims'] >= link_update['max_claims']:
        db.delete_referral_link(claim['link_id'])
        link_deleted = True
        
        # Notify referrer
        try:
            await context.bot.send_message(
                chat_id=link_update['referrer_user_id'],
                text=(
                    f"✅ Your link for {link_update['service_name']} has reached its limit "
                    f"of {link_update['max_claims']} referrals and has been removed.\n\n"
                    "Thank you for using RefLoop! 🎉"
                )
            )
        except Exception as e:
            logger.error(f"Failed to notify referrer: {e}")
    
    # Send 3 Stars reward to user
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
    
    try:
        # Send reward invoice (3 Stars)
        await context.bot.send_invoice(
            chat_id=claim['referred_user_id'],
            title="Claim Reward",
            description="You've earned 3 Telegram Stars for your verified claim!",
            payload=f"reward_{claim_id}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice("Claim Reward", 3)]
        )
        
        await context.bot.send_message(
            chat_id=claim['referred_user_id'],
            text=user_message
        )
    except Exception as e:
        logger.error(f"Failed to send reward or notify user: {e}")
    
    # Notify admin
    admin_msg = (
        f"✅ Claim {claim_id} approved!\n"
        f"User now has {total_claims} verified claims.\n"
        f"Link claims: {link_update['current_claims']}/{link_update['max_claims']}"
    )
    
    if total_claims == 3:
        admin_msg += f"\n🎁 User unlocked FREE submission!"
    
    if link_deleted:
        admin_msg += f"\n🗑️ Link {claim['link_id']} auto-deleted (limit reached)"
    
    await update.message.reply_text(admin_msg)
