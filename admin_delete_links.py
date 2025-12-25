# -*- coding: utf-8 -*-
"""Admin Delete Links Management for RefLoop Bot"""

import database as db
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def list_links_for_deletion(update, context):
    """Show all referral links with delete buttons"""
    user_id = update.effective_user.id
    
    # Check admin permission
    from bot import ADMIN_USER_IDS
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    # Get all referral links
    with db.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                l.id,
                l.referrer_user_id,
                u.username,
                l.category,
                l.service_name,
                l.url,
                l.description,
                l.max_claims,
                l.current_claims,
                l.created_at
            FROM referral_links l
            JOIN users u ON l.referrer_user_id = u.user_id
            ORDER BY l.id ASC
        """)
        links = cursor.fetchall()
        cursor.close()
    
    if not links:
        await update.message.reply_text("📭 No referral links in database.")
        return
    
    # Create message with links list
    msg = "🗑️ **DELETE REFERRAL LINKS**\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"Total links: {len(links)}\n\n"
    
    # Create buttons (max 8 per row, Telegram limit)
    keyboard = []
    row = []
    
    for idx, link in enumerate(links, 1):
        status = "✅ Active" if link['current_claims'] < link['max_claims'] else "🔴 Full"
        
        msg += f"**{idx}.** {link['service_name']}\n"
        msg += f"   📂 {link['category']}\n"
        msg += f"   👤 @{link['username']}\n"
        msg += f"   📊 {link['current_claims']}/{link['max_claims']} claims - {status}\n"
        msg += f"   🆔 ID: {link['id']}\n\n"
        
        # Add button
        row.append(InlineKeyboardButton(f"🗑️ {idx}", callback_data=f"dellink_{link['id']}"))
        
        # Create new row every 4 buttons
        if len(row) == 4:
            keyboard.append(row)
            row = []
    
    # Add remaining buttons
    if row:
        keyboard.append(row)
    
    # Add cancel button
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="dellink_cancel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Split message if too long
    if len(msg) > 4000:
        # Send message without buttons first
        chunks = [msg[i:i+4000] for i in range(0, len(msg), 4000)]
        for chunk in chunks[:-1]:
            await update.message.reply_text(chunk, parse_mode='Markdown')
        # Send last chunk with buttons
        await update.message.reply_text(chunks[-1], parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_delete_link(update, context):
    """Handle link deletion button press"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Check admin permission
    from bot import ADMIN_USER_IDS
    if user_id not in ADMIN_USER_IDS:
        await query.edit_message_text("❌ You don't have permission to use this command.")
        return
    
    # Handle cancel
    if query.data == "dellink_cancel":
        await query.edit_message_text("❌ Link deletion cancelled.")
        return
    
    # Extract link ID
    link_id = int(query.data.split('_')[1])
    
    # Get link details before deletion
    link = db.get_link_by_id(link_id)
    
    if not link:
        await query.edit_message_text(f"❌ Link {link_id} not found (already deleted?).")
        return
    
    # Check for associated claims
    with db.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM claims WHERE link_id = %s", (link_id,))
        result = cursor.fetchone()
        claims_count = result['count']
        cursor.close()
    
    # Delete associated claims first (if any)
    if claims_count > 0:
        with db.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM claims WHERE link_id = %s", (link_id,))
            cursor.close()
    
    # Now delete the link
    db.delete_referral_link(link_id)
    
    # Send confirmation
    warning = f"\n⚠️ Also deleted {claims_count} associated claim(s)." if claims_count > 0 else ""
    
    await query.edit_message_text(
        f"✅ **Link Deleted Successfully!**\n\n"
        f"🆔 ID: {link_id}\n"
        f"📝 Service: {link['service_name']}\n"
        f"📂 Category: {link['category']}\n"
        f"📊 Claims: {link['current_claims']}/{link['max_claims']}\n"
        f"{warning}\n\n"
        f"The link has been permanently removed from the database.",
        parse_mode='Markdown'
    )
    
    # Log the deletion
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Admin {user_id} deleted link {link_id} ({link['service_name']}) with {claims_count} claims")
