# -*- coding: utf-8 -*-
"""Admin Dashboard for RefLoop Bot"""

import database as db

async def show_dashboard(update, context):
    """Show admin dashboard with all statistics"""
    user_id = update.effective_user.id
    
    # Get all statistics from database
    with db.get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        # Total links
        cursor.execute("SELECT COUNT(*) as count FROM referral_links")
        total_links = cursor.fetchone()['count']
        
        # Active links (not maxed out)
        cursor.execute("SELECT COUNT(*) as count FROM referral_links WHERE current_claims < max_claims")
        active_links = cursor.fetchone()['count']
        
        # Total claims
        cursor.execute("SELECT COUNT(*) as count FROM claims")
        total_claims = cursor.fetchone()['count']
        
        # Pending claims
        cursor.execute("SELECT COUNT(*) as count FROM claims WHERE status = 'pending'")
        pending_claims = cursor.fetchone()['count']
        
        # Approved claims
        cursor.execute("SELECT COUNT(*) as count FROM claims WHERE status = 'approved'")
        approved_claims = cursor.fetchone()['count']
        
        # Rejected claims
        cursor.execute("SELECT COUNT(*) as count FROM claims WHERE status = 'rejected'")
        rejected_claims = cursor.fetchone()['count']
        
        # Total Stars to be paid (3 per approved claim)
        stars_to_pay = approved_claims * 3
        
        # Total Stars received (estimate based on links created)
        cursor.execute("""
            SELECT 
                SUM(CASE 
                    WHEN max_claims = 5 THEN 25
                    WHEN max_claims = 10 THEN 40
                    WHEN max_claims = 30 THEN 100
                    ELSE 0
                END) as total
            FROM referral_links
        """)
        result = cursor.fetchone()
        stars_received = result['total'] if result['total'] else 0
        
        # Recent pending claims (last 5)
        cursor.execute("""
            SELECT c.id, c.referred_user_id, u.username, l.service_name, l.category
            FROM claims c
            JOIN users u ON c.referred_user_id = u.user_id
            JOIN referral_links l ON c.link_id = l.id
            WHERE c.status = 'pending'
            ORDER BY c.created_at DESC
            LIMIT 5
        """)
        pending_list = cursor.fetchall()
        
        cursor.close()
    
    # Build dashboard message
    dashboard_msg = (
        "📊 **ADMIN DASHBOARD**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 **Users:** {total_users}\n"
        f"🔗 **Total Links:** {total_links}\n"
        f"✅ **Active Links:** {active_links}\n"
        f"🗑️ **Completed Links:** {total_links - active_links}\n\n"
        f"📋 **Claims:**\n"
        f"  • Total: {total_claims}\n"
        f"  • ⏳ Pending: {pending_claims}\n"
        f"  • ✅ Approved: {approved_claims}\n"
        f"  • ❌ Rejected: {rejected_claims}\n\n"
        f"💰 **Stars:**\n"
        f"  • 💵 Received: ~{stars_received} ⭐\n"
        f"  • 💸 To Pay: {stars_to_pay} ⭐\n"
        f"  • 📈 Net: {stars_received - stars_to_pay} ⭐\n\n"
    )
    
    if pending_list:
        dashboard_msg += "⏳ **Pending Claims:**\n"
        for claim in pending_list:
            dashboard_msg += f"  • ID {claim['id']}: @{claim['username']} → {claim['service_name']} ({claim['category']})\n"
        dashboard_msg += f"\nUse `/approve <id>` or `/reject <id>` to process claims."
    else:
        dashboard_msg += "✅ No pending claims!"
    
    await update.message.reply_text(dashboard_msg, parse_mode='Markdown')
