# -*- coding: utf-8 -*-
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters
)
import database as db

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USER_IDS = [int(id.strip()) for id in os.getenv('ADMIN_USER_IDS', '').split(',') if id.strip()]
CHANNEL_ID = -1003625306083  # RefLoop channel

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
SUBMIT_PLAN, SUBMIT_CATEGORY, SUBMIT_SERVICE, SUBMIT_URL, SUBMIT_DESCRIPTION = range(5)
CLAIM_CATEGORY, CLAIM_SERVICE, CLAIM_SCREENSHOT = range(5, 8)

# Categories for referral links
CATEGORIES = [
    "🎮 Games",
    "💰 Crypto",
    "🏦 Banks",
    "📱 Telecom",
    "📦 Other"
]

# Pricing plans
PLANS = {
    'A': {'max_claims': 5, 'price': 25, 'name': 'Plan A - 5 Referrals'},
    'B': {'max_claims': 10, 'price': 40, 'name': 'Plan B - 10 Referrals'},
    'C': {'max_claims': 30, 'price': 100, 'name': 'Plan C - 30 Referrals'}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler - Register user and show menu in channel"""
    user = update.effective_user
    
    # Check if user has a public username
    if not user.username:
        await update.message.reply_text(
            "❌ Sorry! You need a public Telegram username to use this bot.\n\n"
            "Please set a username in Telegram Settings → Edit Profile → Username"
        )
        return
    
    # Create user in database (auto-registration)
    db.create_user(user.id, user.username)
    
    # Get user data to show current status
    user_data = db.get_user(user.id)
    verified_claims = user_data['total_verified_claims']
    
    # Create main menu keyboard
    keyboard = [
        [InlineKeyboardButton("📊 My Status", callback_data="menu_status")],
        [InlineKeyboardButton("🔍 Browse Available Links", callback_data="menu_browse")],
        [InlineKeyboardButton("🔗 Submit Referral Link", callback_data="menu_submit")],
        [InlineKeyboardButton("🎁 Claim Reward", callback_data="menu_claim")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"👋 Welcome to RefLoop, @{user.username}!\n\n"
        "🔗 Share referral links and earn Telegram Stars!\n\n"
        "📋 How it works:\n"
        "• Complete 3 verified sign-ups to unlock FREE link submission\n"
        "• OR pay Stars to submit immediately (25/40/100 ⭐)\n"
        "• Earn 3 ⭐ for each verified claim you complete\n\n"
        "💰 Pricing Plans:\n"
        "• Plan A: 5 referrals → 25 ⭐\n"
        "• Plan B: 10 referrals → 40 ⭐\n"
        "• Plan C: 30 referrals → 100 ⭐\n\n"
        f"📊 Your Status: {verified_claims}/3 claims completed\n\n"
        "Choose an option below:"
    )
    
    # Post to channel
    try:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=welcome_text,
            reply_markup=reply_markup
        )
        await update.message.reply_text(
            "✅ Welcome! Check the RefLoop channel for the main menu."
        )
    except Exception as e:
        logger.error(f"Failed to post to channel: {e}")
        # Fallback: send to user directly
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu button clicks"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    if not user.username:
        await query.message.reply_text("❌ You need a public username to use this bot.")
        return
    
    if query.data == "menu_submit":
        # Start submit link flow
        await submit_link_start(update, context)
    elif query.data == "menu_browse":
        # Start browse flow
        await browse_links_callback(update, context)
    elif query.data == "menu_claim":
        # Start claim flow
        await claim_reward_start_callback(update, context)
    elif query.data == "menu_status":
        # Show status
        await my_status_callback(update, context)

async def my_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's current status (callback version)"""
    query = update.callback_query
    user = query.from_user
    
    user_data = db.get_user(user.id)
    
    if not user_data:
        await query.message.reply_text("❌ User not found. Please use /start first.")
        return
    
    total_claims = user_data['total_verified_claims']
    
    status_msg = (
        f"📊 Your Status:\n\n"
        f"✅ Verified claims: {total_claims}\n"
        f"⭐ You earn 3 Stars per verified claim!\n\n"
        f"💡 Keep claiming to earn more Stars!"
    )
    
    await query.message.reply_text(status_msg)

async def submit_link_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start link submission process - Show payment or free option"""
    query = update.callback_query if update.callback_query else None
    user = update.effective_user
    
    if not user.username:
        msg = "❌ You need a public Telegram username to use this bot."
        if query:
            await query.message.reply_text(msg)
        else:
            await update.message.reply_text(msg)
        return ConversationHandler.END
    
    user_data = db.get_user(user.id)
    if not user_data:
        # Auto-register user
        db.create_user(user.id, user.username)
        user_data = db.get_user(user.id)
    
    verified_claims = user_data['total_verified_claims']
    free_available = user_data['free_submissions_available']
    
    # Check if user has completed 3 claims or has free submissions
    if verified_claims >= 3 or free_available > 0:
        # Show both options: pay or use free
        keyboard = [
            [InlineKeyboardButton("💎 Plan A - 5 Referrals (25 ⭐)", callback_data="plan_A")],
            [InlineKeyboardButton("💎 Plan B - 10 Referrals (40 ⭐)", callback_data="plan_B")],
            [InlineKeyboardButton("💎 Plan C - 30 Referrals (100 ⭐)", callback_data="plan_C")],
            [InlineKeyboardButton("🎁 Use Free Submission", callback_data="plan_FREE")],
            [InlineKeyboardButton("❌ Cancel", callback_data="submit_cancel")]
        ]
        msg_text = (
            "🔗 Submit Your Referral Link\n\n"
            f"✅ You have {free_available} free submission(s) available!\n\n"
            "Choose an option:\n\n"
            "💎 Paid Plans:\n"
            "• Plan A: 5 referrals → 25 ⭐\n"
            "• Plan B: 10 referrals → 40 ⭐\n"
            "• Plan C: 30 referrals → 100 ⭐\n\n"
            "🎁 Or use your free submission!\n\n"
            "Each verified claim earns users 3 ⭐\n"
            "Links auto-delete when limit is reached."
        )
    else:
        # Only show paid options
        keyboard = [
            [InlineKeyboardButton("💎 Plan A - 5 Referrals (25 ⭐)", callback_data="plan_A")],
            [InlineKeyboardButton("💎 Plan B - 10 Referrals (40 ⭐)", callback_data="plan_B")],
            [InlineKeyboardButton("💎 Plan C - 30 Referrals (100 ⭐)", callback_data="plan_C")],
            [InlineKeyboardButton("❌ Cancel", callback_data="submit_cancel")]
        ]
        remaining = 3 - verified_claims
        msg_text = (
            "🔗 Submit Your Referral Link\n\n"
            f"📊 Your progress: {verified_claims}/3 verified claims\n\n"
            f"💡 Complete {remaining} more claim(s) to unlock FREE submission!\n\n"
            "Or choose a paid plan:\n\n"
            "💎 Plan A: 5 referrals → 25 ⭐\n"
            "💎 Plan B: 10 referrals → 40 ⭐\n"
            "💎 Plan C: 30 referrals → 100 ⭐\n\n"
            "Each verified claim earns users 3 ⭐\n"
            "Links auto-delete when limit is reached."
        )
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=msg_text,
            reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=msg_text,
            reply_markup=reply_markup
        )
    
    return SUBMIT_PLAN

async def submit_plan_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plan selection including FREE option"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "submit_cancel":
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text="❌ Submission cancelled."
        )
        return ConversationHandler.END
    
    # Check if FREE plan
    if query.data == "plan_FREE":
        user_data = db.get_user(query.from_user.id)
        if user_data['free_submissions_available'] <= 0:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text="❌ You don't have any free submissions available.\n"
                     "Complete 3 verified claims to unlock free submission!"
            )
            return ConversationHandler.END
        
        context.user_data['plan'] = 'FREE'
        context.user_data['max_claims'] = 5  # Default for free
        context.user_data['price'] = 0
        context.user_data['payment_method'] = 'free'
        plan_name = "Free Submission (5 referrals)"
    else:
        # Extract plan (A, B, or C)
        plan = query.data.split('_')[1]
        context.user_data['plan'] = plan
        context.user_data['max_claims'] = PLANS[plan]['max_claims']
        context.user_data['price'] = PLANS[plan]['price']
        context.user_data['payment_method'] = 'paid'
        plan_name = PLANS[plan]['name']
    
    # Show categories
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat_{i}")] 
                for i, cat in enumerate(CATEGORIES)]
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="submit_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"✅ Selected: {plan_name}\n\n"
             "📂 Select a category for your referral link:",
        reply_markup=reply_markup
    )
    
    return SUBMIT_CATEGORY

async def submit_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "submit_cancel":
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text="❌ Submission cancelled."
        )
        return ConversationHandler.END
    
    cat_index = int(query.data.split('_')[1])
    context.user_data['category'] = CATEGORIES[cat_index]
    
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"📂 Category: {CATEGORIES[cat_index]}\n\n"
             "📝 Now, enter the service name (e.g., 'Binance', 'Uber', 'Coursera'):"
    )
    
    return SUBMIT_SERVICE

async def submit_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle service name input"""
    context.user_data['service_name'] = update.message.text.strip()
    
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"✅ Service: {context.user_data['service_name']}\n\n"
             "🔗 Now, send your referral link URL:"
    )
    
    return SUBMIT_URL

async def submit_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL input"""
    url = update.message.text.strip()
    
    if not url.startswith(('http://', 'https://')):
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text="❌ Please enter a valid URL starting with http:// or https://"
        )
        return SUBMIT_URL
    
    context.user_data['url'] = url
    
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text="📄 Finally, add a brief description (max 120 characters - what users need to do):"
    )
    
    return SUBMIT_DESCRIPTION

async def submit_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle description and send payment invoice or create free submission"""
    description = update.message.text.strip()
    
    # Validate description length (max 120 characters)
    if len(description) > 120:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"❌ Description too long! ({len(description)}/120 characters)\n\n"
                 "Please send a shorter description (max 120 characters):"
        )
        return SUBMIT_DESCRIPTION
    
    context.user_data['description'] = description
    
    # Check if this is a free submission
    payment_method = context.user_data.get('payment_method', 'paid')
    
    if payment_method == 'free':
        # Free submission - create link directly without payment
        max_claims = 5  # Free submissions get 5 referrals
        
        # Use the free submission slot
        db.use_free_submission(update.effective_user.id)
        
        # Create the referral link
        link_id = db.create_referral_link(
            update.effective_user.id,
            context.user_data['category'],
            context.user_data['service_name'],
            context.user_data['url'],
            context.user_data['description'],
            max_claims
        )
        
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"✅ Free submission successful! Link created! (ID: {link_id})\n\n"
                 f"📂 {context.user_data['category']}\n"
                 f"📝 {context.user_data['service_name']}\n"
                 f"🔗 {context.user_data['url']}\n"
                 f"📄 {context.user_data['description']}\n"
                 f"📊 Max referrals: {max_claims}\n\n"
                 "Your link is now available for users to claim! 🎉\n"
                 "It will auto-delete when the limit is reached.\n\n"
                 "💡 Complete 3 more verified claims to unlock another free submission!"
        )
        
        context.user_data.clear()
        return ConversationHandler.END
    
    else:
        # Paid submission - send invoice to user in private chat
        plan = context.user_data['plan']
        price = context.user_data['price']
        max_claims = context.user_data['max_claims']
        
        # Send invoice to user's private chat
        await context.bot.send_invoice(
            chat_id=update.effective_user.id,
            title=f"Submit Referral Link - {PLANS[plan]['name']}",
            description=f"Pay {price} Telegram Stars to submit your referral link with up to {max_claims} referrals",
            payload=f"submit_link_{update.effective_user.id}_{plan}",
            provider_token="",  # Empty for Telegram Stars
            currency="XTR",
            prices=[LabeledPrice(f"Plan {plan}", price)]
        )
        
        # Notify in channel
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"💳 Payment invoice sent to your private chat @{update.effective_user.username}!\n"
                 f"Please complete the payment to submit your link."
        )
        
        return SUBMIT_DESCRIPTION


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pre-checkout query"""
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle successful payment"""
    payment = update.message.successful_payment
    
    if payment.invoice_payload.startswith("submit_link_"):
        # Extract plan from payload
        parts = payment.invoice_payload.split('_')
        plan = parts[-1] if len(parts) > 2 else 'A'
        max_claims = context.user_data.get('max_claims', PLANS[plan]['max_claims'])
        
        # Create the referral link after payment
        link_id = db.create_referral_link(
            update.effective_user.id,
            context.user_data['category'],
            context.user_data['service_name'],
            context.user_data['url'],
            context.user_data['description'],
            max_claims
        )
        
        await update.message.reply_text(
            f"✅ Payment received! Link submitted successfully! (ID: {link_id})\n\n"
            f"📂 {context.user_data['category']}\n"
            f"📝 {context.user_data['service_name']}\n"
            f"🔗 {context.user_data['url']}\n"
            f"📊 Max referrals: {max_claims}\n\n"
            "Your link is now available for users to claim! 🎉\n"
            "It will auto-delete when the limit is reached."
        )
        
        context.user_data.clear()
    
    elif payment.invoice_payload.startswith("reward_"):
        # Reward payment completed (3 Stars)
        claim_id = int(payment.invoice_payload.split('_')[1])
        db.mark_claim_rewarded(claim_id)
        
        await update.message.reply_text(
            "⭐ Congratulations! You've received 3 Telegram Stars!\n\n"
            "Keep claiming more rewards to earn more Stars! 💰"
        )

async def browse_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Browse available referral links"""
    user = update.effective_user
    
    if not user.username:
        await update.message.reply_text("❌ You need a public username to use this bot.")
        return
    
    # Get all categories with available links
    categories = db.get_categories()
    
    if not categories:
        await update.message.reply_text(
            "📭 No referral links available yet.\n\n"
            "Be the first to submit one with /submit_link!"
        )
        return
    
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"browse_cat_{i}")] 
                for i, cat in enumerate(categories)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔍 Browse Referral Links\n\n"
        "Select a category:",
        reply_markup=reply_markup
    )

async def browse_links_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Browse available referral links (callback version)"""
    query = update.callback_query
    user = query.from_user
    
    if not user.username:
        await query.message.reply_text("❌ You need a public username to use this bot.")
        return
    
    # Get all categories with available links
    categories = db.get_categories()
    
    if not categories:
        await query.message.reply_text(
            "📭 No referral links available yet.\n\n"
            "Be the first to submit one!"
        )
        return
    
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"browse_cat_{i}")] 
                for i, cat in enumerate(categories)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "🔍 Browse Referral Links\n\n"
        "Select a category:",
        reply_markup=reply_markup
    )

async def browse_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show links in selected category"""
    query = update.callback_query
    await query.answer()
    
    categories = db.get_categories()
    cat_index = int(query.data.split('_')[-1])
    category = categories[cat_index]
    
    # Safety check: only show links with current_claims < max_claims
    links = db.get_available_links(category)
    
    if not links:
        await query.edit_message_text(
            f"📭 No available links in {category}\n\n"
            "Try another category or check back later!"
        )
        return
    
    message = f"🔗 Available Links in {category}:\n\n"
    
    for link in links[:10]:  # Show max 10 links
        remaining = link['max_claims'] - link['current_claims']
        message += (
            f"🆔 ID: {link['id']}\n"
            f"📝 {link['service_name']}\n"
            f"📄 {link['description']}\n"
            f"📊 {remaining}/{link['max_claims']} claims remaining\n"
            f"🔗 {link['url']}\n\n"
        )
    
    message += "Use /claim_reward to claim a reward!"
    
    await query.edit_message_text(message)

async def claim_reward_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start claim reward process"""
    user = update.effective_user
    
    if not user.username:
        await update.message.reply_text("❌ You need a public username to use this bot.")
        return ConversationHandler.END
    
    user_data = db.get_user(user.id)
    if not user_data:
        await update.message.reply_text("❌ Please use /start first.")
        return ConversationHandler.END
    
    # Get all categories with available links
    categories = db.get_categories()
    
    if not categories:
        await update.message.reply_text(
            "📭 No referral links available to claim.\n\n"
            "Check back later!"
        )
        return ConversationHandler.END
    
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"claim_cat_{i}")] 
                for i, cat in enumerate(categories)]
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="claim_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎁 Claim a Reward\n\n"
        "Select a category:",
        reply_markup=reply_markup
    )
    
    return CLAIM_CATEGORY

async def claim_reward_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start claim reward process (callback version)"""
    query = update.callback_query
    user = query.from_user
    
    if not user.username:
        await query.message.reply_text("❌ You need a public username to use this bot.")
        return ConversationHandler.END
    
    user_data = db.get_user(user.id)
    if not user_data:
        await query.message.reply_text("❌ Please use /start first.")
        return ConversationHandler.END
    
    # Get all categories with available links
    categories = db.get_categories()
    
    if not categories:
        await query.message.reply_text(
            "📭 No referral links available to claim.\n\n"
            "Check back later!"
        )
        return ConversationHandler.END
    
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"claim_cat_{i}")] 
                for i, cat in enumerate(categories)]
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="claim_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "🎁 Claim a Reward\n\n"
        "Select a category:",
        reply_markup=reply_markup
    )
    
    return CLAIM_CATEGORY

async def claim_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection for claim"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "claim_cancel":
        await query.edit_message_text("❌ Claim cancelled.")
        return ConversationHandler.END
    
    categories = db.get_categories()
    cat_index = int(query.data.split('_')[-1])
    category = categories[cat_index]
    
    links = db.get_available_links(category)
    
    if not links:
        await query.edit_message_text(
            f"📭 No available links in {category}\n\n"
            "Try another category!"
        )
        return ConversationHandler.END
    
    context.user_data['claim_category'] = category
    
    # Show available services
    keyboard = []
    for link in links[:20]:  # Max 20 links
        remaining = link['max_claims'] - link['used_claims']
        keyboard.append([InlineKeyboardButton(
            f"{link['service_name']} ({remaining} left)",
            callback_data=f"claim_link_{link['id']}"
        )])
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="claim_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📂 {category}\n\n"
        "Select a service to claim:",
        reply_markup=reply_markup
    )
    
    return CLAIM_SERVICE

async def claim_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle service selection for claim"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "claim_cancel":
        await query.edit_message_text("❌ Claim cancelled.")
        return ConversationHandler.END
    
    link_id = int(query.data.split('_')[-1])
    link = db.get_link_by_id(link_id)
    
    if not link:
        await query.edit_message_text("❌ This referral link is no longer active.")
        return ConversationHandler.END
    
    # Safety check: verify link still has available claims
    if link['current_claims'] >= link['max_claims']:
        await query.edit_message_text("❌ This referral link is no longer active.")
        return ConversationHandler.END
    
    # Check for duplicate claim
    if db.check_duplicate_claim(query.from_user.id, link_id):
        await query.edit_message_text("❌ You've already claimed this link!")
        return ConversationHandler.END
    
    context.user_data['claim_link_id'] = link_id
    
    await query.edit_message_text(
        f"🔗 {link['service_name']}\n\n"
        f"📄 Instructions: {link['description']}\n"
        f"🌐 Link: {link['url']}\n"
        f"📊 {link['max_claims'] - link['current_claims']} claims remaining\n\n"
        "📸 Please complete the sign-up and send a screenshot as proof.\n\n"
        "⚠️ Your claim will be reviewed by an admin before approval.\n"
        "✅ You'll earn 3 ⭐ when approved!"
    )
    
    return CLAIM_SCREENSHOT

async def claim_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle screenshot submission"""
    if not update.message.photo:
        await update.message.reply_text("❌ Please send a screenshot (photo).")
        return CLAIM_SCREENSHOT
    
    # Get the largest photo
    photo = update.message.photo[-1]
    screenshot_file_id = photo.file_id
    
    link_id = context.user_data['claim_link_id']
    
    # Create claim
    claim_id = db.create_claim(
        update.effective_user.id,
        link_id,
        screenshot_file_id
    )
    
    # Notify admins
    link = db.get_link_by_id(link_id)
    admin_message = (
        f"🔔 New Claim Pending Review\n\n"
        f"🆔 Claim ID: {claim_id}\n"
        f"👤 User: @{update.effective_user.username} (ID: {update.effective_user.id})\n"
        f"🔗 Link: {link['service_name']} (ID: {link_id})\n"
        f"📂 Category: {link['category']}\n\n"
        f"Use /approve {claim_id} or /reject {claim_id}"
    )
    
    for admin_id in ADMIN_USER_IDS:
        try:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=screenshot_file_id,
                caption=admin_message
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")
    
    await update.message.reply_text(
        f"✅ Claim submitted! (ID: {claim_id})\n\n"
        "⏳ Your claim is pending admin review.\n"
        "You'll be notified once it's approved!"
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def approve_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to approve a claim"""
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
    
    # Safety check: ensure link hasn't reached max claims
    if link['current_claims'] >= link['max_claims']:
        await update.message.reply_text("❌ This link has already reached its maximum claims.")
        db.reject_claim(claim_id)
        return
    
    # Approve the claim
    db.approve_claim(claim_id)
    
    # Update user's verified claims count
    total_claims = db.update_user_claims(claim['referred_user_id'])
    
    # Increment link's current claims and get updated values
    link_update = db.increment_link_claims(claim['link_id'])
    
    # Check if link reached its limit and delete if so
    link_deleted = False
    if link_update and link_update['current_claims'] >= link_update['max_claims']:
        # Link reached limit - delete it
        db.delete_referral_link(claim['link_id'])
        link_deleted = True
        
        # Notify the referrer
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
    
    # Send 3 Stars reward to the referred user
    # Build user message based on claim milestone
    if total_claims < 3:
        user_message = (
            f"✅ Your claim has been approved!\n\n"
            f"📊 Progress: {total_claims}/3 verified claims\n\n"
            f"⭐ You've earned 3 Telegram Stars!\n\n"
            f"💡 Complete {3 - total_claims} more claim(s) to unlock a FREE link submission!"
        )
    elif total_claims == 3:
        user_message = (
            f"🎉 Congratulations! Your claim has been approved!\n\n"
            f"📊 Total verified claims: {total_claims}\n\n"
            f"⭐ You've earned 3 Telegram Stars!\n\n"
            f"🎁 MILESTONE REACHED! You've unlocked 1 FREE link submission!\n"
            f"Use /submit_link and choose the FREE option to submit your referral link without paying Stars!"
        )
    else:
        user_message = (
            f"✅ Your claim has been approved!\n\n"
            f"📊 Total verified claims: {total_claims}\n\n"
            f"⭐ You've earned 3 Telegram Stars!\n\n"
            f"Keep claiming to unlock more free submissions! (Every 3 claims = 1 free submission)"
        )
    
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
    
    if link_deleted:
        admin_msg += f"\n🗑️ Link {claim['link_id']} auto-deleted (limit reached)"
    
    await update.message.reply_text(admin_msg)

async def reject_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to reject a claim"""
    if update.effective_user.id not in ADMIN_USER_IDS:
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Usage: /reject <claim_id>")
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
    
    # Reject the claim
    db.reject_claim(claim_id)
    
    # Notify user
    try:
        await context.bot.send_message(
            chat_id=claim['referred_user_id'],
            text="❌ Your claim has been rejected.\n\n"
                 "Please make sure to follow the instructions correctly and submit valid proof."
        )
    except Exception as e:
        logger.error(f"Failed to notify user: {e}")
    
    await update.message.reply_text(f"✅ Claim {claim_id} rejected.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text("❌ Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

def main():
    """Start the bot"""
    # Initialize database
    db.init_database()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("browse", browse_links))
    application.add_handler(CommandHandler("approve", approve_claim))
    application.add_handler(CommandHandler("reject", reject_claim))
    
    # Menu handlers
    application.add_handler(CallbackQueryHandler(menu_handler, pattern="^menu_"))
    
    # Submit link conversation
    submit_conv = ConversationHandler(
        entry_points=[
            CommandHandler("submit_link", submit_link_start),
            CallbackQueryHandler(submit_link_start, pattern="^menu_submit$")
        ],
        states={
            SUBMIT_PLAN: [CallbackQueryHandler(submit_plan_choice, pattern="^(plan_A|plan_B|plan_C|plan_FREE|submit_cancel)")],
            SUBMIT_CATEGORY: [CallbackQueryHandler(submit_category, pattern="^(cat_|submit_cancel)")],
            SUBMIT_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, submit_service)],
            SUBMIT_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, submit_url)],
            SUBMIT_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, submit_description)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(cancel, pattern="^submit_cancel$")
        ],
        per_chat=False,
        per_user=True,
        per_message=False,
    )
    application.add_handler(submit_conv)
    
    # Claim reward conversation
    claim_conv = ConversationHandler(
        entry_points=[
            CommandHandler("claim_reward", claim_reward_start),
            CallbackQueryHandler(claim_reward_start_callback, pattern="^menu_claim$")
        ],
        states={
            CLAIM_CATEGORY: [CallbackQueryHandler(claim_category, pattern="^(claim_cat_|claim_cancel)")],
            CLAIM_SERVICE: [CallbackQueryHandler(claim_service, pattern="^(claim_link_|claim_cancel)")],
            CLAIM_SCREENSHOT: [MessageHandler(filters.PHOTO, claim_screenshot)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(cancel, pattern="^claim_cancel$")
        ],
        per_chat=False,
        per_user=True,
        per_message=False,
    )
    application.add_handler(claim_conv)
    
    # Browse callback
    application.add_handler(CallbackQueryHandler(browse_category, pattern="^browse_cat_"))
    
    # Payment handlers
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    
    # Start health check server for Render in a separate thread
    import threading
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Bot is running')
        
        def log_message(self, format, *args):
            pass  # Suppress HTTP logs
    
    def run_health_server():
        port = int(os.getenv('PORT', 10000))
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"Health check server running on port {port}")
        server.serve_forever()
    
    # Start health check server in background thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Start bot
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
