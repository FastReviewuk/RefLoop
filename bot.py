# -*- coding: utf-8 -*-
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import database as db

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USER_IDS = [int(id.strip()) for id in os.getenv('ADMIN_USER_IDS', '').split(',') if id.strip()]
CHANNEL_ID = -1003625306083  # RefLoop channel

# Categories for referral links
CATEGORIES = [
    "🎮 Games",
    "💰 Crypto", 
    "🏦 Banks",
    "📱 Telecom",
    "📦 Other"
]

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler - Register user and show menu"""
    logger.info(f"START command received from user {update.effective_user.id} (@{update.effective_user.username})")
    
    user = update.effective_user
    
    # Check if user has a public username
    if not user.username:
        logger.warning(f"User {user.id} has no username")
        await update.message.reply_text(
            "❌ Sorry! You need a public Telegram username to use this bot.\n\n"
            "Please set a username in Telegram Settings → Edit Profile → Username"
        )
        return
    
    # Create user in database (auto-registration)
    try:
        db.create_user(user.id, user.username)
        logger.info(f"User {user.id} (@{user.username}) created/updated in database")
    except Exception as e:
        logger.error(f"Failed to create user {user.id}: {e}")
    
    # Handle deep links for direct submission
    if context.args and context.args[0] == 'submit':
        logger.info(f"Starting submission flow for user {user.id}")
        await start_submission_flow(update, context, user)
        return
    
    # Show main menu
    keyboard = [
        [InlineKeyboardButton("📋 Browse Links", callback_data="menu_browse")],
        [InlineKeyboardButton("🔗 Submit Link", callback_data="menu_submit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"🎉 Welcome to RefLoop, @{user.username}!\n\n"
        "🔗 **Submit** your referral links (FREE!)\n"
        "📋 **Browse** and use others' links\n\n"
        "✨ **How it works:**\n"
        "• Submit your referral link for free\n"
        "• Others can use it (one time only)\n"
        "• Link gets removed after use\n"
        "• You can resubmit anytime!\n\n"
        "Choose an option below:"
    )
    
    try:
        if update.message.chat.type == 'private':
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)
            logger.info(f"Welcome message sent to private chat for user {user.id}")
        else:
            # In channel, send to channel
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=welcome_text,
                reply_markup=reply_markup
            )
            logger.info(f"Welcome message sent to channel for user {user.id}")
    except Exception as e:
        logger.error(f"Failed to send welcome message to user {user.id}: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again.")

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu button clicks"""
    try:
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
    except Exception as e:
        logger.error(f"Error in menu_handler: {e}")
        try:
            await update.callback_query.answer("❌ An error occurred. Please try again.")
        except:
            pass

async def submit_link_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start link submission flow"""
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
    keyboard = [[InlineKeyboardButton("🔗 Continue in Private Chat", url=f"https://t.me/refloop_bot?start=submit")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"✅ @{user.username}, click the button below to submit your referral link:\n\n"
             "📝 You'll be guided through:\n"
             "1️⃣ Select category\n"
             "2️⃣ Enter service name\n"
             "3️⃣ Enter your referral URL\n"
             "4️⃣ Add description\n\n"
             "🎉 **Completely FREE!**",
        reply_markup=reply_markup
    )

async def start_submission_flow(update, context, user):
    """Start submission flow in private chat"""
    # Get user data
    user_data = db.get_user(user.id)
    if not user_data:
        db.create_user(user.id, user.username)
    
    # Show categories
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat_{i}")] 
                for i, cat in enumerate(CATEGORIES)]
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="submit_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg_text = (
        "🔗 **Submit Your Referral Link**\n\n"
        "🎉 **Completely FREE!**\n\n"
        "📂 **Step 1/4:** Select a category for your referral link:"
    )
    
    await update.message.reply_text(msg_text, parse_mode='Markdown', reply_markup=reply_markup)

async def submit_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection"""
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
        "📝 **Step 2/4:** Enter the service name\n"
        "(e.g., 'Binance', 'Uber', 'Coursera')\n\n"
        "Just type the name and send it:",
        parse_mode='Markdown'
    )

async def submit_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle service name input"""
    user_id = update.message.from_user.id
    
    # Save to database
    db.save_submission_state(user_id, state='SUBMIT_URL', service_name=update.message.text.strip())
    
    await update.message.reply_text(
        f"✅ **Service:** {update.message.text.strip()}\n\n"
        "🔗 **Step 3/4:** Send your referral link URL\n"
        "(Must start with http:// or https://)",
        parse_mode='Markdown'
    )

async def submit_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL input"""
    user_id = update.message.from_user.id
    url = update.message.text.strip()
    
    # Validate URL
    if not (url.startswith('http://') or url.startswith('https://')):
        await update.message.reply_text(
            "❌ Invalid URL! Please send a valid URL starting with http:// or https://"
        )
        return
    
    # Save to database
    db.save_submission_state(user_id, state='SUBMIT_DESCRIPTION', url=url)
    
    await update.message.reply_text(
        f"✅ **URL:** {url}\n\n"
        "📝 **Step 4/4:** Enter a description\n"
        "(What should users do? Max 120 characters)\n\n"
        "Example: 'Sign up and verify your email'",
        parse_mode='Markdown'
    )

async def submit_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle description and create link"""
    user_id = update.message.from_user.id
    
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
    
    # Create the referral link (max_claims = 1, single use)
    link_id = db.create_referral_link(
        user_id,
        submission_state['category'],
        submission_state['service_name'],
        submission_state['url'],
        description,
        1  # Single use only
    )
    
    # Send success message in private chat
    await update.message.reply_text(
        f"✅ **Link submitted successfully!** (ID: {link_id})\n\n"
        f"📂 **Category:** {submission_state['category']}\n"
        f"📝 **Service:** {submission_state['service_name']}\n"
        f"🔗 **URL:** {submission_state['url']}\n"
        f"📄 **Description:** {description}\n\n"
        "🎉 Your link is now available for others to use!\n"
        "It will be removed after someone uses it.\n"
        "You can resubmit anytime!",
        parse_mode='Markdown'
    )
    
    # Also notify in channel
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"🆕 **New link available!**\n\n"
             f"📂 {submission_state['category']}\n"
             f"📝 {submission_state['service_name']}\n"
             f"👤 Submitted by @{update.effective_user.username}\n\n"
             f"Use /start to browse and claim!"
    )
    
    # Clear submission state
    db.clear_submission_state(user_id)

async def browse_links_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Browse available referral links"""
    try:
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
            "🔍 **Browse Referral Links**\n\n"
            "Select a category:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in browse_links_callback: {e}")
        try:
            await update.callback_query.answer("❌ An error occurred. Please try again.")
        except:
            pass

async def browse_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show links in selected category"""
    try:
        query = update.callback_query
        await query.answer()
        
        categories = db.get_categories()
        cat_index = int(query.data.split('_')[-1])
        category = categories[cat_index]
        
        # Get available links (not used yet)
        links = db.get_available_links(category)
        
        if not links:
            await query.edit_message_text(
                f"📭 No available links in **{category}**\n\n"
                "Try another category or check back later!",
                parse_mode='Markdown'
            )
            return
        
        # Show links with use buttons
        keyboard = []
        message = f"🔗 **Available Links in {category}:**\n\n"
        
        for i, link in enumerate(links[:10]):  # Show max 10 links
            referrer = db.get_user_by_id(link['referrer_user_id'])
            username = referrer['username'] if referrer else "Unknown"
            message += (
                f"**{i+1}. {link['service_name']}**\n"
                f"📄 {link['description']}\n"
                f"👤 By @{username}\n\n"
            )
            keyboard.append([InlineKeyboardButton(f"🔗 Use {link['service_name']}", callback_data=f"use_link_{link['id']}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Categories", callback_data="menu_browse")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in browse_category: {e}")
        try:
            await update.callback_query.answer("❌ An error occurred. Please try again.")
        except:
            pass

async def use_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle link usage"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        link_id = int(query.data.split('_')[-1])
        
        # Get link details
        link = db.get_link_by_id(link_id)
        
        if not link:
            await query.edit_message_text("❌ This link is no longer available.")
            return
        
        # Check if link is still available
        if link['current_claims'] >= link['max_claims']:
            await query.edit_message_text("❌ This link has already been used.")
            return
        
        # Check if user is trying to use their own link
        if link['referrer_user_id'] == user_id:
            await query.edit_message_text("❌ You cannot use your own referral link!")
            return
        
        # Mark link as used (increment claims)
        db.increment_link_claims(link_id)
        
        # Show the referral link to user
        await query.edit_message_text(
            f"🎉 **Here's your referral link!**\n\n"
            f"🔗 **Service:** {link['service_name']}\n"
            f"📄 **Instructions:** {link['description']}\n\n"
            f"👆 **Click here to sign up:**\n{link['url']}\n\n"
            f"✅ This link has been marked as used and removed from the list.\n"
            f"Thanks for using RefLoop!",
            parse_mode='Markdown'
        )
        
        # Notify the link owner
        try:
            await context.bot.send_message(
                chat_id=link['referrer_user_id'],
                text=f"🎉 **Great news!**\n\n"
                     f"Someone used your referral link for **{link['service_name']}**!\n"
                     f"👤 Used by: @{query.from_user.username}\n\n"
                     f"Your link has been removed as planned.\n"
                     f"You can submit it again anytime! 🔄",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to notify link owner {link['referrer_user_id']}: {e}")
    except Exception as e:
        logger.error(f"Error in use_link: {e}")
        try:
            await update.callback_query.answer("❌ An error occurred. Please try again.")
        except:
            pass

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input based on current state"""
    if not update.message or not update.message.from_user:
        return
    
    user_id = update.message.from_user.id
    
    # Get submission state from database
    submission_state = db.get_submission_state(user_id)
    
    if not submission_state:
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
    
    # Menu handlers
    application.add_handler(CallbackQueryHandler(menu_handler, pattern="^menu_"))
    
    # Submit link handlers
    application.add_handler(CallbackQueryHandler(submit_category, pattern="^cat_"))
    application.add_handler(CallbackQueryHandler(lambda u, c: get_user_data(c, u.callback_query.from_user.id).clear() or u.callback_query.edit_message_text("❌ Cancelled."), pattern="^submit_cancel$"))
    
    # Browse handlers
    application.add_handler(CallbackQueryHandler(browse_category, pattern="^browse_cat_"))
    application.add_handler(CallbackQueryHandler(use_link, pattern="^use_link_"))
    
    # Text input handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    
    # Initialize database
    try:
        db.init_database()
        logger.info("✅ Database initialization completed successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return
    
    logger.info("✅ All handlers registered")
    
    # Force polling mode for reliability
    logger.info("Starting polling mode for maximum reliability")
    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            poll_interval=0.0,
            timeout=30,
            read_timeout=15,
            write_timeout=15,
            connect_timeout=15
        )
    except Exception as e:
        logger.error(f"Polling error: {e}")
        raise

if __name__ == '__main__':
    main()