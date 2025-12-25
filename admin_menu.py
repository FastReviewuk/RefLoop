# -*- coding: utf-8 -*-
"""Admin Menu for RefLoop Bot"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def show_admin_menu(update, context):
    """Show admin menu with buttons"""
    user_id = update.effective_user.id
    
    # Check admin permission
    from bot import ADMIN_USER_IDS
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    # Create admin menu keyboard
    keyboard = [
        [InlineKeyboardButton("📊 Dashboard", callback_data="admin_dashboard")],
        [InlineKeyboardButton("⏳ Pending Claims", callback_data="admin_claims")],
        [InlineKeyboardButton("🗑️ Delete Links", callback_data="admin_deletelinks")],
        [InlineKeyboardButton("💳 Test Payment", callback_data="admin_testpayment")],
        [InlineKeyboardButton("🎉 Toggle Promo Mode", callback_data="admin_togglepromo")],
        [InlineKeyboardButton("❌ Close Menu", callback_data="admin_close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    admin_msg = (
        "🔐 **ADMIN PANEL**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select an option:\n\n"
        "📊 **Dashboard** - View bot statistics\n"
        "⏳ **Pending Claims** - Review claims\n"
        "🗑️ **Delete Links** - Remove referral links\n"
        "💳 **Test Payment** - Test submission flow\n"
        "🎉 **Toggle Promo Mode** - Enable/disable free submissions\n\n"
        "**Quick Commands:**\n"
        "`/approve <id>` - Approve a claim\n"
        "`/reject <id>` - Reject a claim\n"
        "`/screenshot <id>` - View claim screenshot"
    )
    
    await update.message.reply_text(admin_msg, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_admin_menu(update, context):
    """Handle admin menu button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Check admin permission
    from bot import ADMIN_USER_IDS
    if user_id not in ADMIN_USER_IDS:
        await query.edit_message_text("❌ You don't have permission to use this.")
        return
    
    # Handle menu actions
    if query.data == "admin_dashboard":
        # Import and call dashboard
        import admin_dashboard
        # Create a fake update object for the dashboard
        class FakeUpdate:
            def __init__(self, query):
                self.message = query.message
                self.effective_user = query.from_user
        
        fake_update = FakeUpdate(query)
        await admin_dashboard.show_dashboard(fake_update, context)
        
    elif query.data == "admin_claims":
        # Import and call claims list
        import admin_claims
        class FakeUpdate:
            def __init__(self, query):
                self.message = query.message
                self.effective_user = query.from_user
        
        fake_update = FakeUpdate(query)
        await admin_claims.list_claims(fake_update, context)
        
    elif query.data == "admin_deletelinks":
        # Import and call delete links
        import admin_delete_links
        class FakeUpdate:
            def __init__(self, query):
                self.message = query.message
                self.effective_user = query.from_user
        
        fake_update = FakeUpdate(query)
        await admin_delete_links.list_links_for_deletion(fake_update, context)
        
    elif query.data == "admin_testpayment":
        await query.edit_message_text(
            "💳 **Test Payment Mode**\n\n"
            "To test the payment flow:\n\n"
            "1️⃣ Start a link submission (Submit Link)\n"
            "2️⃣ Complete all steps (plan, category, service, URL, description)\n"
            "3️⃣ When you receive the payment invoice, use:\n"
            "   `/test_payment`\n\n"
            "This will create the link without actual payment.",
            parse_mode='Markdown'
        )
        
    elif query.data == "admin_togglepromo":
        # Import and call toggle promo mode
        from bot import toggle_promo_mode
        class FakeUpdate:
            def __init__(self, query):
                self.message = query.message
                self.effective_user = query.from_user
        
        fake_update = FakeUpdate(query)
        await toggle_promo_mode(fake_update, context)
        
    elif query.data == "admin_close":
        await query.edit_message_text("✅ Admin menu closed.")
