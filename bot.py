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
import admin_dashboard
import admin_claims
import admin_delete_links
import admin_menu
from keep_alive import KeepAlive

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USER_IDS = [int(id.strip()) for id in os.getenv('ADMIN_USER_IDS', '').split(',') if id.strip()]
CHANNEL_ID = -1003625306083  # RefLoop channel

# Enable free submissions for promotion (set to False to re-enable payments)
FREE_PROMOTION_MODE = True

# Categories for referral links
CATEGORIES = [
    "🎮 Games",
    "💰 Crypto", 
    "🏦 Banks",
    "📱 Telecom",
    "📦 Other"
]

# Pricing plans (all FREE in promotion mode)
PLANS = {
    'A': {'max_claims': 10, 'price': 0, 'name': 'FREE Plan A - 10 Referrals'},
    'B': {'max_claims': 10, 'price': 0, 'name': 'FREE Plan B - 10 Referrals'}, 
    'C': {'max_claims': 10, 'price': 0, 'name': 'FREE Plan C - 10 Referrals'}
}

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_user_data(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Get user data from bot context"""
    if 'users' not in context.bot_data:
        context.bot_data['users'] = {}
    if user_id not in context.bot_data['users']:
        context.bot_data['users'][user_id] = {}
    return context.bot_data['users'][user_id]

# Conversation states
SUBMIT_PLAN, SUBMIT_CATEGORY, SUBMIT_SERVICE, SUBMIT_URL, SUBMIT_DESCRIPTION = range(5)
CLAIM_CATEGORY, CLAIM_SERVICE, CLAIM_SCREENSHOT = range(5, 8)

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
    
    # Handle deep links
    if context.args:
        arg = context.args[0]
        
        # Handle claim deep links
        if arg.startswith('claim_'):
            link_id = int(arg.split('_')[1])
            link = db.get_link_by_id(link_id)
            
            if not link:
                await update.message.reply_text("❌ This referral link is no longer active.")
                return
            
            await update.message.reply_text(
                f"📸 **Submit Screenshot for Claim**\n\n"
                f"🔗 **Service:** {link['service_name']}\n"
                f"📄 **Task:** {link['description']}\n\n"
                "Please send a screenshot showing you completed the sign-up.\n\n"
                "📋 **Instructions:**\n"
                "• Screenshot must show confirmation email or welcome screen\n"
                "• Make sure your username/email is visible\n"
                "• Send the image directly to this chat\n\n"
                "⏳ Your claim will be reviewed by an admin.",
                parse_mode='Markdown'
            )
            
            # Store claim info for screenshot handler
            user_data = get_user_data(context, user.id)
            user_data['claim_link_id'] = link_id
            return
        
        # Handle complete submission flow in private chat
        if arg == 'submit_flow':
            await start_private_submission_flow(update, context, user)
            return
    
    # Show main menu in channel
    keyboard = [
        [InlineKeyboardButton("📊 My Status", callback_data="menu_status")],
        [InlineKeyboardButton("📋 Browse Links", callback_data="menu_browse")],
        [InlineKeyboardButton("🔗 Submit Link", callback_data="menu_submit")],
        [InlineKeyboardButton("🎁 Claim Reward", callback_data="menu_claim")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"🎉 Welcome to RefLoop, @{user.username}!\n\n"
        "🔗 **Submit** your referral links\n"
        "🎁 **Claim** rewards from others\n"
        "⭐ **Earn** Telegram Stars\n\n"
        "Choose an option below:"
    )
    
    if update.message.chat.type == 'private':
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    else:
        # In channel, send to channel
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=welcome_text,
            reply_markup=reply_markup
        )

async def start_private_submission_flow(update, context, user):
    """Start complete submission flow in private chat"""
    # Get user data to check free submissions
    user_data = db.get_user(user.id)
    if not user_data:
        db.create_user(user.id, user.username)
        user_data = db.get_user(user.id)
    
    # In promotional mode, show only free options
    keyboard = [
        [InlineKeyboardButton("🎁 FREE Plan A - 10 Referrals", callback_data="plan_A")],
        [InlineKeyboardButton("🎁 FREE Plan B - 10 Referrals", callback_data="plan_B")],
        [InlineKeyboardButton("🎁 FREE Plan C - 10 Referrals", callback_data="plan_C")],
        [InlineKeyboardButton("❌ Cancel", callback_data="submit_cancel")]
    ]
    
    msg_text = (
        "🔗 **Submit Your Referral Link**\n\n"
        "🎉 **ALL SUBMISSIONS ARE FREE!**\n"
        "Choose your plan (all include 10 referrals):\n\n"
        "💡 Each verified claim earns users 3 ⭐\n\n"
        "Click below to continue:"
    )
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msg_text, parse_mode='Markdown', reply_markup=reply_markup)

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
    """Show user status (callback version)"""
    query = update.callback_query
    user = query.from_user
    
    user_data = db.get_user(user.id)
    if not user_data:
        await query.message.reply_text("❌ Please use /start first.")
        return
    
    verified_claims = user_data['total_verified_claims']
    free_available = user_data['free_submissions_available']
    
    # Count user's active links
    user_links = db.get_user_links(user.id)
    active_links = len([link for link in user_links if link['current_claims'] < link['max_claims']])
    
    status_msg = (
        f"📊 **Status for @{user.username}**\n\n"
        f"✅ **Verified Claims:** {verified_claims}\n"
        f"🎁 **Free Submissions Available:** {free_available}\n"
        f"🔗 **Active Links:** {active_links}\n\n"
        f"💡 **Progress to next free submission:** {verified_claims % 3}/3\n\n"
        "🎯 **How it works:**\n"
        "• Complete 3 verified claims = 1 free submission\n"
        "• Each verified claim earns you 3 ⭐\n"
        "• Submit links to earn more claims!"
    )
    
    await query.message.reply_text(status_msg, parse_mode='Markdown')

async def submit_link_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redirect user to private chat for complete submission flow"""
    query = update.callback_query if update.callback_query else None
    user = update.effective_user
    
    logger.info(f"submit_link_start called by user {user.id} (@{user.username})")
    
    if not user.username:
        msg = "❌ You need a public Telegram username to use this bot."
        if query:
            await query.message.reply_text(msg)
        else:
            await update.message.reply_text(msg)
        return
    
    # Create user in database
    db.create_user(user.id, user.username)
    
    # Create button to redirect to private chat
    keyboard = [[InlineKeyboardButton("🔗 Continue in Private Chat", url=f"https://t.me/refloop_bot?start=submit_flow")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"✅ @{user.username}, click the button below to submit your referral link:\n\n"
             "📝 You'll be guided through:\n"
             "1️⃣ Choose your plan (A/B/C - all FREE!)\n"
             "2️⃣ Select category\n"
             "3️⃣ Enter service details\n"
             "4️⃣ Link created automatically!",
        reply_markup=reply_markup
    )

async def submit_plan_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plan selection - now works entirely in private chat"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = get_user_data(context, user_id)
    
    logger.info(f"submit_plan_choice called by user {user_id} with data: {query.data}")
    
    if query.data == "submit_cancel":
        await query.edit_message_text("❌ Submission cancelled.")
        user_data.clear()
        return
    
    # Extract plan (A, B, or C) - all are free in promotional mode
    plan = query.data.split('_')[1]
    user_data['plan'] = plan
    user_data['max_claims'] = PLANS[plan]['max_claims']
    user_data['price'] = PLANS[plan]['price']
    user_data['payment_method'] = 'free'
    plan_name = PLANS[plan]['name']
    
    # Save to database
    db.save_submission_state(user_id, plan=plan, max_claims=PLANS[plan]['max_claims'])
    
    logger.info(f"Plan selected: {plan_name}, moving to category selection")
    
    # Show categories in private chat
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat_{i}")] 
                for i, cat in enumerate(CATEGORIES)]
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="submit_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ **Plan Selected:** {plan_name}\n\n"
        "📂 **Step 2/4:** Select a category for your referral link:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def submit_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection - now works entirely in private chat"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = get_user_data(context, user_id)
    
    if query.data == "submit_cancel":
        await query.edit_message_text("❌ Submission cancelled.")
        user_data.clear()
        return
    
    cat_index = int(query.data.split('_')[1])
    user_data['category'] = CATEGORIES[cat_index]
    user_data['state'] = 'SUBMIT_SERVICE'
    
    # Save to database
    db.save_submission_state(user_id, state='SUBMIT_SERVICE', category=CATEGORIES[cat_index])
    
    await query.edit_message_text(
        f"✅ **Category:** {CATEGORIES[cat_index]}\n\n"
        "📝 **Step 3/4:** Enter the service name\n"
        "(e.g., 'Binance', 'Uber', 'Coursera')\n\n"
        "Just type the name and send it:",
        parse_mode='Markdown'
    )

async def submit_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle service name input"""
    user_id = update.message.from_user.id if update.message and update.message.from_user else update.effective_user.id
    user_data = get_user_data(context, user_id)
    
    user_data['service_name'] = update.message.text.strip()
    user_data['state'] = 'SUBMIT_URL'
    
    # Save to database
    db.save_submission_state(user_id, state='SUBMIT_URL', service_name=update.message.text.strip())
    
    await update.message.reply_text(
        f"✅ Service: {user_data['service_name']}\n\n"
        "🔗 **Step 3/4:** Send your referral link URL\n"
        "(Must start with http:// or https://)"
    )

async def submit_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL input"""
    user_id = update.message.from_user.id if update.message and update.message.from_user else update.effective_user.id
    user_data = get_user_data(context, user_id)
    
    url = update.message.text.strip()
    
    # Validate URL
    if not (url.startswith('http://') or url.startswith('https://')):
        await update.message.reply_text(
            "❌ Invalid URL! Please send a valid URL starting with http:// or https://"
        )
        return
    
    user_data['url'] = url
    user_data['state'] = 'SUBMIT_DESCRIPTION'
    
    # Save to database
    db.save_submission_state(user_id, state='SUBMIT_DESCRIPTION', url=url)
    
    await update.message.reply_text(
        f"✅ URL: {url}\n\n"
        "📝 **Step 4/4:** Enter a description\n"
        "(What should users do? Max 120 characters)\n\n"
        "Example: 'Sign up and verify your email'"
    )

async def submit_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle description and create free submission"""
    user_id = update.message.from_user.id if update.message and update.message.from_user else update.effective_user.id
    
    # Get submission state from database
    submission_state = db.get_submission_state(user_id)
    if not submission_state:
        await update.message.reply_text("❌ Session expired. Please start again with /start")
        return
    
    description = update.message.text.strip()
    
    # Validate description length (max 120 characters)
    if len(description) > 120:
        await update.message.reply_text(
            f"❌ Description too long! ({len(description)}/120 characters)\n\n"
            "Please send a shorter description (max 120 characters):"
        )
        return
    
    # Save description to database
    db.save_submission_state(user_id, state=None, description=description)
    
    # Get updated submission state
    submission_state = db.get_submission_state(user_id)
    plan = submission_state['plan']
    max_claims = submission_state['max_claims']
    
    # In promotional mode, all submissions are free
    link_id = db.create_referral_link(
        user_id,
        submission_state['category'],
        submission_state['service_name'],
        submission_state['url'],
        description,
        max_claims
    )
    
    # Send success message in private chat
    await update.message.reply_text(
        f"✅ **FREE**: Link submitted successfully! (ID: {link_id})\n\n"
        f"📂 {submission_state['category']}\n"
        f"📝 {submission_state['service_name']}\n"
        f"🔗 {submission_state['url']}\n"
        f"📄 {description}\n"
        f"📊 Max referrals: {max_claims}\n\n"
        "🎉 Your link is now available for users to claim!\n"
        "It will auto-delete when the limit is reached.",
        parse_mode='Markdown'
    )
    
    # Also notify in channel
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"✅ New link submitted by @{update.effective_user.username}!\n\n"
             f"📂 {submission_state['category']}\n"
             f"📝 {submission_state['service_name']}\n"
             f"📊 Max referrals: {max_claims}"
    )
    
    # Clear submission state
    db.clear_submission_state(user_id)

# Add other essential functions here...
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
    
    message += "Use the Claim Reward button to claim a reward!"
    
    await query.edit_message_text(message)

async def claim_reward_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start claim reward process (callback version)"""
    query = update.callback_query
    user = query.from_user
    
    if not user.username:
        await query.message.reply_text("❌ You need a public username to use this bot.")
        return
    
    user_data = db.get_user(user.id)
    if not user_data:
        await query.message.reply_text("❌ Please use /start first.")
        return
    
    # Get all categories with available links
    categories = db.get_categories()
    
    if not categories:
        await query.message.reply_text(
            "📭 No referral links available to claim.\n\n"
            "Check back later!"
        )
        return
    
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"claim_cat_{i}")] 
                for i, cat in enumerate(categories)]
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="claim_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "🎁 Claim a Reward\n\n"
        "Select a category:",
        reply_markup=reply_markup
    )

async def claim_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection for claim"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = get_user_data(context, user_id)
    
    if query.data == "claim_cancel":
        await query.edit_message_text("❌ Claim cancelled.")
        user_data.clear()
        return
    
    categories = db.get_categories()
    cat_index = int(query.data.split('_')[-1])
    category = categories[cat_index]
    
    links = db.get_available_links(category)
    
    if not links:
        await query.edit_message_text(
            f"📭 No available links in {category}\n\n"
            "Try another category!"
        )
        user_data.clear()
        return
    
    user_data['claim_category'] = category
    
    # Show available services
    keyboard = []
    for link in links[:20]:  # Max 20 links
        remaining = link['max_claims'] - link['current_claims']
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

async def claim_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle service selection for claim"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = get_user_data(context, user_id)
    
    if query.data == "claim_cancel":
        await query.edit_message_text("❌ Claim cancelled.")
        user_data.clear()
        return
    
    link_id = int(query.data.split('_')[-1])
    link = db.get_link_by_id(link_id)
    
    if not link:
        await query.edit_message_text("❌ This referral link is no longer active.")
        user_data.clear()
        return
    
    # Safety check: verify link still has available claims
    if link['current_claims'] >= link['max_claims']:
        await query.edit_message_text("❌ This referral link is no longer active.")
        user_data.clear()
        return
    
    # Check for duplicate claim
    if db.check_duplicate_claim(query.from_user.id, link_id):
        await query.edit_message_text("❌ You've already claimed this link!")
        user_data.clear()
        return
    
    user_data['claim_link_id'] = link_id
    
    # Create button to continue in private chat
    keyboard = [[InlineKeyboardButton("📸 Send Screenshot in Private Chat", url=f"https://t.me/refloop_bot?start=claim_{link_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🔗 **{link['service_name']}**\n\n"
        f"📄 **What to do:** {link['description']}\n\n"
        f"🌐 **Referral Link:**\n{link['url']}\n\n"
        f"📊 {link['max_claims'] - link['current_claims']} claims remaining\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📸 **NEXT STEPS:**\n"
        "1️⃣ Click the referral link above\n"
        "2️⃣ Complete the sign-up\n"
        "3️⃣ Take a screenshot of the confirmation\n"
        "4️⃣ Click the button below to send screenshot\n\n"
        "⚠️ Your claim will be reviewed by an admin\n"
        "✅ You'll earn 3 ⭐ when approved!",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def claim_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle screenshot submission"""
    user_id = update.effective_user.id
    user_data = get_user_data(context, user_id)
    
    if not update.message.photo:
        await update.message.reply_text("❌ Please send a screenshot (photo).")
        return
    
    # Get the largest photo
    photo = update.message.photo[-1]
    screenshot_file_id = photo.file_id
    
    link_id = user_data.get('claim_link_id')
    
    if not link_id:
        await update.message.reply_text("❌ Session expired. Please start again with /start")
        user_data.clear()
        return
    
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
    
    user_data.clear()

async def test_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to simulate a payment for testing"""
    if update.effective_user.id not in ADMIN_USER_IDS:
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    user_id = update.effective_user.id
    
    # Get submission state from database
    submission_state = db.get_submission_state(user_id)
    
    if not submission_state or not submission_state.get('plan'):
        await update.message.reply_text("❌ No pending submission found. Start with Submit Link first.")
        return
    
    # Simulate successful payment
    plan = submission_state['plan']
    max_claims = submission_state.get('max_claims', PLANS[plan]['max_claims'])
    
    # Create the referral link
    link_id = db.create_referral_link(
        user_id,
        submission_state['category'],
        submission_state['service_name'],
        submission_state['url'],
        submission_state['description'],
        max_claims
    )
    
    # Send success message in private chat
    await update.message.reply_text(
        f"✅ TEST: Payment simulated! Link submitted successfully! (ID: {link_id})\n\n"
        f"📂 {submission_state['category']}\n"
        f"📝 {submission_state['service_name']}\n"
        f"🔗 {submission_state['url']}\n"
        f"📊 Max referrals: {max_claims}\n\n"
        "Your link is now available for users to claim! 🎉\n"
        "It will auto-delete when the limit is reached."
    )
    
    # Also notify in channel
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"✅ New link submitted by @{update.effective_user.username}!\n\n"
             f"📂 {submission_state['category']}\n"
             f"📝 {submission_state['service_name']}\n"
             f"📊 Max referrals: {max_claims}"
    )
    
    # Clear submission state from database
    db.clear_submission_state(user_id)

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
        await update.message.reply_text("❌ Invalid claim ID. Please provide a number.")
        return
    
    # Get claim details
    claim = db.get_claim_by_id(claim_id)
    if not claim:
        await update.message.reply_text(f"❌ Claim {claim_id} not found.")
        return
    
    if claim['status'] != 'pending':
        await update.message.reply_text(f"❌ Claim {claim_id} is already {claim['status']}.")
        return
    
    # Approve the claim
    db.approve_claim(claim_id)
    
    # Update link claims count
    db.increment_link_claims(claim['link_id'])
    
    # Update user's verified claims count
    db.increment_user_verified_claims(claim['referred_user_id'])
    
    # Check if user reached milestone (every 3 claims = 1 free submission)
    user_data = db.get_user(claim['referred_user_id'])
    verified_claims = user_data['total_verified_claims']
    
    if verified_claims % 3 == 0:
        # Grant free submission
        db.add_free_submission(claim['referred_user_id'])
        
        # Notify user about milestone
        try:
            await context.bot.send_message(
                chat_id=claim['referred_user_id'],
                text=f"🎉 **Milestone Reached!**\n\n"
                     f"You've completed {verified_claims} verified claims!\n"
                     f"🎁 You've unlocked 1 FREE submission (5 referrals)\n\n"
                     f"Use the Submit Link button to use your free submission!"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {claim['referred_user_id']}: {e}")
    
    # Notify user about approval
    try:
        await context.bot.send_message(
            chat_id=claim['referred_user_id'],
            text=f"✅ Your claim has been approved!\n\n"
                 f"🎁 You earned 3 ⭐ Telegram Stars!\n"
                 f"📊 Total verified claims: {verified_claims}\n\n"
                 f"Keep claiming to unlock free submissions!"
        )
    except Exception as e:
        logger.error(f"Failed to notify user {claim['referred_user_id']}: {e}")
    
    await update.message.reply_text(f"✅ Claim {claim_id} approved.")

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
        await update.message.reply_text("❌ Invalid claim ID. Please provide a number.")
        return
    
    # Get claim details
    claim = db.get_claim_by_id(claim_id)
    if not claim:
        await update.message.reply_text(f"❌ Claim {claim_id} not found.")
        return
    
    if claim['status'] != 'pending':
        await update.message.reply_text(f"❌ Claim {claim_id} is already {claim['status']}.")
        return
    
    # Reject the claim
    db.reject_claim(claim_id)
    
    # Notify user about rejection
    try:
        await context.bot.send_message(
            chat_id=claim['referred_user_id'],
            text=f"❌ Your claim has been rejected.\n\n"
                 f"Please make sure to follow the instructions correctly and submit valid proof.\n\n"
                 f"You can try claiming other referral links!"
        )
    except Exception as e:
        logger.error(f"Failed to notify user {claim['referred_user_id']}: {e}")
    
    await update.message.reply_text(f"✅ Claim {claim_id} rejected.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text="❌ Operation cancelled."
    )
    context.user_data.clear()

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input based on current state"""
    # Get user from message (could be from channel or private chat)
    if update.message and update.message.from_user:
        user_id = update.message.from_user.id
    elif update.effective_user:
        user_id = update.effective_user.id
    else:
        logger.warning("No user found in update, ignoring")
        return
    
    # Get submission state from database
    submission_state = db.get_submission_state(user_id)
    
    if not submission_state:
        # No active submission, check if it's a screenshot for claim
        user_data = get_user_data(context, user_id)
        if user_data.get('claim_link_id') and update.message.photo:
            await claim_screenshot(update, context)
        return
    
    state = submission_state.get('state')
    
    if state == 'SUBMIT_SERVICE':
        await submit_service(update, context)
    elif state == 'SUBMIT_URL':
        await submit_url(update, context)
    elif state == 'SUBMIT_DESCRIPTION':
        await submit_description(update, context)

def main():
    """Main function to run the bot"""
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not found in environment variables")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", approve_claim))
    application.add_handler(CommandHandler("reject", reject_claim))
    application.add_handler(CommandHandler("test_payment", test_payment))
    application.add_handler(CommandHandler("admin", admin_menu.show_admin_menu))
    application.add_handler(CommandHandler("dashboard", admin_dashboard.show_dashboard))
    application.add_handler(CommandHandler("claims", admin_claims.list_claims))
    application.add_handler(CommandHandler("screenshot", admin_claims.view_screenshot))
    application.add_handler(CommandHandler("deletelinks", admin_delete_links.list_links_for_deletion))
    
    # Menu handlers
    application.add_handler(CallbackQueryHandler(menu_handler, pattern="^menu_"))
    
    # Admin menu handler
    application.add_handler(CallbackQueryHandler(admin_menu.handle_admin_menu, pattern="^admin_"))
    
    # Delete links handler (admin)
    application.add_handler(CallbackQueryHandler(admin_delete_links.handle_delete_link, pattern="^dellink_"))
    
    # Submit link handlers (without ConversationHandler)
    application.add_handler(CallbackQueryHandler(submit_plan_choice, pattern="^plan_"))
    application.add_handler(CallbackQueryHandler(submit_category, pattern="^cat_"))
    application.add_handler(CallbackQueryHandler(cancel, pattern="^submit_cancel$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    
    # Claim reward handlers (without ConversationHandler)  
    application.add_handler(CallbackQueryHandler(claim_category, pattern="^claim_cat_"))
    application.add_handler(CallbackQueryHandler(claim_service, pattern="^claim_link_"))
    application.add_handler(CallbackQueryHandler(cancel, pattern="^claim_cancel$"))
    
    # Browse callback
    application.add_handler(CallbackQueryHandler(browse_category, pattern="^browse_cat_"))
    
    # Initialize database
    db.init_database()
    
    # Check if running on Render (webhook mode) or locally (polling mode)
    render_url = os.getenv('RENDER_EXTERNAL_URL')
    
    if render_url:
        # Webhook mode for Render
        webhook_url = f"{render_url}/webhook"
        logger.info(f"Starting webhook mode with URL: {webhook_url}")
        
        # Start keep-alive system
        keep_alive = KeepAlive(render_url)
        application.post_start = keep_alive.start
        
        application.run_webhook(
            listen="0.0.0.0",
            port=int(os.getenv('PORT', 8000)),
            webhook_url=webhook_url,
            secret_token=os.getenv('WEBHOOK_SECRET', 'your-secret-token')
        )
    else:
        # Polling mode for local development
        logger.info("Starting polling mode for local development")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()