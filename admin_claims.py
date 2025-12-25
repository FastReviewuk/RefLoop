# -*- coding: utf-8 -*-
"""Admin Claims Management for RefLoop Bot"""

import database as db

async def list_claims(update, context):
    """Show all pending claims with details"""
    user_id = update.effective_user.id
    
    # Check admin permission (import from bot.py)
    from bot import ADMIN_USER_IDS
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    # Get all pending claims
    with db.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                c.id,
                c.referred_user_id,
                u.username,
                c.link_id,
                l.service_name,
                l.category,
                l.url,
                c.screenshot_file_id,
                c.status,
                c.created_at
            FROM claims c
            JOIN users u ON c.referred_user_id = u.user_id
            JOIN referral_links l ON c.link_id = l.id
            WHERE c.status = 'pending'
            ORDER BY c.created_at ASC
        """)
        pending_claims = cursor.fetchall()
        cursor.close()
    
    if not pending_claims:
        await update.message.reply_text("✅ No pending claims!")
        return
    
    # Send message with list of claims
    claims_msg = "⏳ **PENDING CLAIMS**\n"
    claims_msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for claim in pending_claims:
        claims_msg += f"🆔 **Claim ID:** {claim['id']}\n"
        claims_msg += f"👤 User: @{claim['username']} (ID: {claim['referred_user_id']})\n"
        claims_msg += f"🔗 Service: {claim['service_name']}\n"
        claims_msg += f"📂 Category: {claim['category']}\n"
        claims_msg += f"🌐 Link: {claim['url']}\n"
        claims_msg += f"📅 Date: {claim['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
        claims_msg += f"📸 Screenshot: {'✅ Uploaded' if claim['screenshot_file_id'] else '❌ Missing'}\n"
        claims_msg += "\n"
        claims_msg += f"**Actions:**\n"
        claims_msg += f"`/approve {claim['id']}` or `/reject {claim['id']}`\n"
        claims_msg += f"`/screenshot {claim['id']}` to view screenshot\n"
        claims_msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Split message if too long
    if len(claims_msg) > 4000:
        # Send in chunks
        chunks = [claims_msg[i:i+4000] for i in range(0, len(claims_msg), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk, parse_mode='Markdown')
    else:
        await update.message.reply_text(claims_msg, parse_mode='Markdown')

async def view_screenshot(update, context):
    """View screenshot for a specific claim"""
    user_id = update.effective_user.id
    
    # Check admin permission
    from bot import ADMIN_USER_IDS
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Usage: /screenshot <claim_id>")
        return
    
    try:
        claim_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid claim ID. Must be a number.")
        return
    
    # Get claim
    claim = db.get_claim(claim_id)
    
    if not claim:
        await update.message.reply_text(f"❌ Claim {claim_id} not found.")
        return
    
    # Get link details
    link = db.get_link_by_id(claim['link_id'])
    
    # Send screenshot with details
    caption = (
        f"📸 **Claim #{claim_id}**\n\n"
        f"👤 User: ID {claim['referred_user_id']}\n"
        f"🔗 Service: {link['service_name']}\n"
        f"📂 Category: {link['category']}\n"
        f"🌐 Link: {link['url']}\n"
        f"📄 Description: {link['description']}\n\n"
        f"**Actions:**\n"
        f"`/approve {claim_id}` or `/reject {claim_id}`"
    )
    
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=claim['screenshot_file_id'],
        caption=caption,
        parse_mode='Markdown'
    )
