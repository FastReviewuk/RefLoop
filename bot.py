# -*- coding: utf-8 -*-
import os
import logging
import sys
import signal
import time
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

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USER_IDS = [int(id.strip()) for id in os.getenv('ADMIN_USER_IDS', '').split(',') if id.strip()]

CATEGORIES = [
    "Games",
    "Crypto", 
    "Banks",
    "Telecom",
    "Other"
]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_user_data(context, user_id):
    if 'users' not in context.bot_data:
        context.bot_data['users'] = {}
    if user_id not in context.bot_data['users']:
        context.bot_data['users'][user_id] = {}
    return context.bot_data['users'][user_id]

async def start(update, context):
    logger.info("START command from user %d" % update.effective_user.id)
    
    user = update.effective_user
    
    if not user.username:
        logger.warning("User %d has no username" % user.id)
        await update.message.reply_text(
            "Sorry! You need a public Telegram username to use this bot.\n\n"
            "Please set a username in Telegram Settings"
        )
        return
    
    try:
        db.create_user(user.id, user.username)
        logger.info("User %d created/updated" % user.id)
    except Exception as e:
        logger.error("Failed to create user: %s" % str(e))
    
    if context.args and context.args[0] == 'submit':
        logger.info("Starting submission flow for user %d" % user.id)
        await start_submission_flow(update, context, user)
        return
    
    keyboard = [
        [InlineKeyboardButton("Browse Links", callback_data="menu_browse")],
        [InlineKeyboardButton("Submit Link", callback_data="menu_submit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "Welcome to RefLoop!\n"
        "A 100% free & open referral exchange — no payments, no rewards, just real links that work.\n\n"
        "Submit your referral link (games, crypto, banks, telecom, etc.)\n"
        "Browse active links shared by others\n"
        "Use a link → get your bonus from the service (not from us!)\n"
        "Each link is automatically removed after one use — fair for everyone\n"
        "You can submit a new link anytime\n\n"
        "No tricks. Just smart sharing.\n\n"
        "Use /submit_link to share yours\n"
        "Use /browse to find active referrals\n\n"
        "Let's help each other — one referral at a time."
    )
    
    try:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        logger.info("Welcome message sent to user %d" % user.id)
    except Exception as e:
        logger.error("Failed to send welcome message: %s" % str(e))
        await update.message.reply_text("Something went wrong. Please try again.")

async def menu_handler(update, context):
    try:
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        if not user.username:
            await query.message.reply_text("You need a public username to use this bot.")
            return
        
        if query.data == "menu_submit":
            await submit_link_start(update, context)
        elif query.data == "menu_browse":
            await browse_links_callback(update, context)
    except Exception as e:
        logger.error("Error in menu_handler: %s" % str(e))
        try:
            await update.callback_query.answer("An error occurred.")
        except:
            pass

async def submit_link_start(update, context):
    query = update.callback_query
    user = update.effective_user
    
    logger.info("submit_link_start called by user %d" % user.id)
    
    if not user.username:
        msg = "You need a public Telegram username to use this bot."
        if query:
            await query.message.reply_text(msg)
        else:
            await update.message.reply_text(msg)
        return
    
    db.create_user(user.id, user.username)
    
    await start_submission_flow(update, context, user)

async def start_submission_flow(update, context, user):
    keyboard = [[InlineKeyboardButton(cat, callback_data="cat_%d" % i)] 
                for i, cat in enumerate(CATEGORIES)]
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="submit_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg_text = (
        "Submit Your Referral Link\n\n"
        "Completely FREE!\n\n"
        "Step 1/4: Select a category for your referral link:"
    )
    
    await update.message.reply_text(msg_text, reply_markup=reply_markup)

async def submit_category(update, context):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = get_user_data(context, user_id)
    
    if query.data == "submit_cancel":
        await query.edit_message_text("Submission cancelled.")
        user_data.clear()
        return
    
    cat_index = int(query.data.split('_')[1])
    user_data['category'] = CATEGORIES[cat_index]
    user_data['state'] = 'SUBMIT_SERVICE'
    
    db.save_submission_state(user_id, state='SUBMIT_SERVICE', category=CATEGORIES[cat_index])
    
    await query.edit_message_text(
        "Category: %s\n\n"
        "Step 2/4: Enter the service name\n"
        "(e.g., 'Binance', 'Uber', 'Coursera')\n\n"
        "Just type the name and send it:" % CATEGORIES[cat_index]
    )

async def submit_service(update, context):
    user_id = update.message.from_user.id
    
    db.save_submission_state(user_id, state='SUBMIT_URL', service_name=update.message.text.strip())
    
    await update.message.reply_text(
        "Service: %s\n\n"
        "Step 3/4: Send your referral link URL\n"
        "(Must start with http:// or https://)" % update.message.text.strip()
    )

async def submit_url(update, context):
    user_id = update.message.from_user.id
    url = update.message.text.strip()
    
    if not (url.startswith('http://') or url.startswith('https://')):
        await update.message.reply_text(
            "Invalid URL! Please send a valid URL starting with http:// or https://"
        )
        return
    
    db.save_submission_state(user_id, state='SUBMIT_DESCRIPTION', url=url)
    
    await update.message.reply_text(
        "URL: %s\n\n"
        "Step 4/4: Enter a description\n"
        "(What should users do? Max 120 characters)\n\n"
        "Example: 'Sign up and verify your email'" % url
    )

async def submit_description(update, context):
    user_id = update.message.from_user.id
    
    submission_state = db.get_submission_state(user_id)
    if not submission_state:
        await update.message.reply_text("Session expired. Please start again with /start")
        return
    
    description = update.message.text.strip()
    
    if len(description) > 120:
        await update.message.reply_text(
            "Description too long! (%d/120 characters)\n\n"
            "Please send a shorter description (max 120 characters):" % len(description)
        )
        return
    
    link_id = db.create_referral_link(
        user_id,
        submission_state['category'],
        submission_state['service_name'],
        submission_state['url'],
        description,
        1
    )
    
    await update.message.reply_text(
        "Link submitted successfully! (ID: %d)\n\n"
        "Category: %s\n"
        "Service: %s\n"
        "URL: %s\n"
        "Description: %s\n\n"
        "Your link is now available for others to use!\n"
        "It will be removed after someone uses it.\n"
        "You can resubmit anytime!" % (
            link_id,
            submission_state['category'],
            submission_state['service_name'],
            submission_state['url'],
            description
        )
    )
    
    db.clear_submission_state(user_id)

async def browse_links_callback(update, context):
    try:
        query = update.callback_query
        if query:
            await query.answer()
        
        user = update.effective_user
        
        if not user.username:
            msg = "You need a public username to use this bot."
            if query:
                await query.message.reply_text(msg)
            else:
                await update.message.reply_text(msg)
            return
        
        categories = db.get_categories()
        
        if not categories:
            msg = "No referral links available yet.\n\nBe the first to submit one!"
            if query:
                await query.message.reply_text(msg)
            else:
                await update.message.reply_text(msg)
            return
        
        keyboard = [[InlineKeyboardButton(cat, callback_data="browse_cat_%d" % i)] 
                    for i, cat in enumerate(categories)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        msg = "Browse Referral Links\n\nSelect a category:"
        if query:
            await query.message.reply_text(msg, reply_markup=reply_markup)
        else:
            await update.message.reply_text(msg, reply_markup=reply_markup)
    except Exception as e:
        logger.error("Error in browse_links_callback: %s" % str(e))
        try:
            if update.callback_query:
                await update.callback_query.answer("An error occurred.")
        except:
            pass

async def browse_category(update, context):
    try:
        query = update.callback_query
        await query.answer()
        
        categories = db.get_categories()
        cat_index = int(query.data.split('_')[-1])
        category = categories[cat_index]
        
        links = db.get_available_links(category)
        
        if not links:
            await query.edit_message_text(
                "No available links in %s\n\n"
                "Try another category or check back later!" % category
            )
            return
        
        keyboard = []
        message = "Available Links in %s:\n\n" % category
        
        for i, link in enumerate(links[:10]):
            referrer = db.get_user_by_id(link['referrer_user_id'])
            username = referrer['username'] if referrer else "Unknown"
            message += (
                "%d. %s\n"
                "%s\n"
                "By @%s\n\n" % (
                    i+1,
                    link['service_name'],
                    link['description'],
                    username
                )
            )
            keyboard.append([InlineKeyboardButton("Use %s" % link['service_name'], callback_data="use_link_%d" % link['id'])])
        
        keyboard.append([InlineKeyboardButton("Back to Categories", callback_data="menu_browse")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
    except Exception as e:
        logger.error("Error in browse_category: %s" % str(e))
        try:
            await update.callback_query.answer("An error occurred.")
        except:
            pass

async def use_link(update, context):
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        link_id = int(query.data.split('_')[-1])
        
        link = db.get_link_by_id(link_id)
        
        if not link:
            await query.edit_message_text("This link is no longer available.")
            return
        
        if link['current_claims'] >= link['max_claims']:
            await query.edit_message_text("This link has already been used.")
            return
        
        if link['referrer_user_id'] == user_id:
            await query.edit_message_text("You cannot use your own referral link!")
            return
        
        db.increment_link_claims(link_id)
        
        await query.edit_message_text(
            "Here's your referral link!\n\n"
            "Service: %s\n"
            "Instructions: %s\n\n"
            "Click here to sign up:\n%s\n\n"
            "This link has been marked as used and removed from the list.\n"
            "Thanks for using RefLoop!" % (
                link['service_name'],
                link['description'],
                link['url']
            )
        )
        
        try:
            await context.bot.send_message(
                chat_id=link['referrer_user_id'],
                text="Great news!\n\n"
                     "Someone used your referral link for %s!\n"
                     "Used by: @%s\n\n"
                     "Your link has been removed as planned.\n"
                     "You can submit it again anytime!" % (
                         link['service_name'],
                         query.from_user.username
                     )
            )
        except Exception as e:
            logger.error("Failed to notify link owner: %s" % str(e))
    except Exception as e:
        logger.error("Error in use_link: %s" % str(e))
        try:
            await update.callback_query.answer("An error occurred.")
        except:
            pass

async def handle_text_input(update, context):
    if not update.message or not update.message.from_user:
        return
    
    user_id = update.message.from_user.id
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

async def cancel_submission(update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data = get_user_data(context, user_id)
    user_data.clear()
    await query.edit_message_text("Submission cancelled.")

async def admin_command(update, context):
    """Admin menu command"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("You don't have permission to use this command.")
        return
    
    keyboard = [
        [InlineKeyboardButton("View Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("Close", callback_data="admin_close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    admin_msg = (
        "ADMIN PANEL\n"
        "============\n\n"
        "Select an option:"
    )
    
    await update.message.reply_text(admin_msg, reply_markup=reply_markup)

async def admin_handler(update, context):
    """Handle admin menu button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id not in ADMIN_USER_IDS:
        await query.edit_message_text("You don't have permission to use this.")
        return
    
    if query.data == "admin_stats":
        try:
            total_users = db.get_total_users()
            total_links = db.get_total_links()
            available_links = db.get_available_links_count()
            
            stats_msg = (
                "BOT STATISTICS\n"
                "===============\n\n"
                "Total Users: %d\n"
                "Total Links Submitted: %d\n"
                "Available Links: %d" % (
                    total_users if total_users else 0,
                    total_links if total_links else 0,
                    available_links if available_links else 0
                )
            )
            await query.edit_message_text(stats_msg)
        except Exception as e:
            logger.error("Error getting stats: %s" % str(e))
            await query.edit_message_text("Error getting statistics.")
    
    elif query.data == "admin_close":
        await query.edit_message_text("Admin menu closed.")

def handle_signal(signum, frame):
    logger.info("Received signal %d, shutting down gracefully..." % signum)
    sys.exit(0)

async def error_handler(update, context):
    """Handle errors in the bot"""
    logger.error("Update %s caused error %s" % (update, context.error))
    
    # If it's a Conflict error, exit to let watchdog restart
    if "Conflict" in str(context.error):
        logger.error("Conflict detected - exiting for watchdog restart")
        sys.exit(1)

def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not found in environment variables")
        logger.error("BOT_TOKEN not found")
        return
    
    logger.info("BOT_TOKEN found: %s..." % BOT_TOKEN[:20])
    
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    logger.info("Creating application...")
    application = Application.builder().token(BOT_TOKEN).build()
    logger.info("Application created")
    
    # Add a small delay to allow old instance to shut down
    import time
    time.sleep(2)
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("submit_link", submit_link_start))
    application.add_handler(CommandHandler("browse", browse_links_callback))
    application.add_handler(CallbackQueryHandler(menu_handler, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(submit_category, pattern="^cat_"))
    application.add_handler(CallbackQueryHandler(cancel_submission, pattern="^submit_cancel$"))
    application.add_handler(CallbackQueryHandler(browse_category, pattern="^browse_cat_"))
    application.add_handler(CallbackQueryHandler(use_link, pattern="^use_link_"))
    application.add_handler(CallbackQueryHandler(admin_handler, pattern="^admin_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    try:
        db.init_database()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error("Database initialization failed: %s" % str(e))
        return
    
    logger.info("All handlers registered")
    logger.info("Starting polling mode for maximum reliability")
    logger.info("Watchdog monitoring active - bot will auto-restart on crash")
    
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error("Polling error: %s" % str(e), exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
