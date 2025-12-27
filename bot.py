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

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USER_IDS = [int(id.strip()) for id in os.getenv('ADMIN_USER_IDS', '').split(',') if id.strip()]
CHANNEL_ID = -1003625306083

CATEGORIES = [
    "🎮 Games",
    "💰 Crypto", 
    "🏦 Banks",
    "📱 Telecom",
    "📦 Other"
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
    logger.info(f"START command received from user {update.effective_user.id}")
    
    user = update.effective_user
    
    if not user.username:
        logger.warning(f"User {user.id} has no username")
        await update.message.reply_text(
            "❌ Sorry! You need a public Telegram username to use this bot.\n\n"
            "Please set a username in Telegram Settings → Edit Profile → Username"
        )
        return
    
    try:
        db.create_user(user.id, user.username)
        logger.info(f"User {user.id} (@{user.username}) created/updated in database")
    except Exception as e:
        logger.error(f"Failed to create user {user.id}: {e}")
    
    if context.args and context.args[0] == 'submit':
        logger.info(f"Starting submission flow for user {user.id}")
        await start_submission_flow(update, context, user)
        return
    
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
        else:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=welcome_text,
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Failed to send welcome message: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again.")

async def menu_handler(update, context):
    try:
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        if not user.username:
            await query.message.reply_text("❌ You need a public username to use this bot.")
            return
        
        if query.data == "menu_submit":
            await submit_link_start(update, context)
        elif query.data == "menu_browse":
            await browse_links_callback(update, context)
    except Exception as e:
        logger.error(f"Error in menu_handler: {e}")
        try:
            await update.callback_query.answer("❌ An error occurred.")
        except:
            pass

async def submit_link_start(update, context):
    query = update.callback_query
    user = update.effective_user
    
    logger.info(f"submit_link_start called by user {user.id}")
    
    if not user.username:
        msg = "❌ You need a public Telegram username to use this bot."
        if query:
            await query.message.reply_text(msg)
        else:
            await update.message.reply_text(msg)
        return
    
    db.create_user(user.id, user.username)
    
    keyboard = [[InlineKeyboardButton("🔗 Continue in Private Chat", url=f"https://t.me/refloop_bot?start=submit")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
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
    except Exception as e:
        logger.error(f"Failed to send message to channel: {e}")

async def start_submission_flow(update, context, user):
    user_data = db.get_user(user.id)
    if not user_data:
        db.create_user(user.id, user.username)
    
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

async def submit_category(update, context):
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
    
    db.save_submission_state(user_id, state='SUBMIT_SERVICE', category=CATEGORIES[cat_index])
    
    await query.edit_message_text(
        f"✅ **Category:** {CATEGORIES[cat_index]}\n\n"
        "📝 **Step 2/4:** Enter the service name\n"
        "(e.g., 'Binance', 'Uber', 'Coursera')\n\n"
        "Just type the name and send it:",
        parse_mode='Markdown'
    )

async def submit_service(update, context):
    user_id = update.message.from_user.id
    
    db.save_submission_state(user_id, state='SUBMIT_URL', service_name=update.message.text.strip())
    
    await update.message.reply_text(
        f"✅ **Service:** {update.message.text.strip()}\n\n"
        "🔗 **Step 3/4:** Send your referral link URL\n"
        "(Must start with http:// or https://)",
        parse_mode='Markdown'
    )

async def submit_url(update, context):
    user_id = update.message.from_user.id
    url = update.message.text.strip()
    
    if not (url.startswith('http://') or url.startswith('https://')):
        await update.message.reply_text(
            "❌ Invalid URL! Please send a valid URL starting with http:// or https://"
        )
        return
    
    db.save_submission_state(user_id, state='SUBMIT_DESCRIPTION', url=url)
    
    await update.message.reply_text(
        f"✅ **URL:** {url}\n\n"
        "📝 **Step 4/4:** Enter a description\n"
        "(What should users do? Max 120 characters)\n\n"
        "Example: 'Sign up and verify your email'",
        parse_mode='Markdown'
    )

async def submit_description(update, context):
    user_id = update.message.from_user.id
    
    submission_state = db.get_submission_state(user_id)
    if not submission_state:
        await update.message.reply_text("❌ Session expired. Please start again with /start")
        return
    
    description = update.message.text.strip()
    
    if len(description) > 120:
        await update.message.reply_text(
            f"❌ Description too long! ({len(description)}/120 characters)\n\n"
            "Please send a shorter description (max 120 characters):"
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
    
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"🆕 **New link available!**\n\n"
             f"📂 {submission_state['category']}\n"
             f"📝 {submission_state['service_name']}\n"
             f"👤 Submitted by @{update.effective_user.username}\n\n"
             f"Use /start to browse and claim!"
    )
    
    db.clear_submission_state(user_id)

async def browse_links_callback(update, context):
    try:
        query = update.callback_query
        if query:
            await query.answer()
        
        user = update.effective_user
        
        if not user.username:
            msg = "❌ You need a public username to use this bot."
            if query:
                await query.message.reply_text(msg)
            else:
                await update.message.reply_text(msg)
            return
        
        categories = db.get_categories()
        
        if not categories:
            msg = "📭 No referral links available yet.\n\nBe the first to submit one!"
            if query:
                await query.message.reply_text(msg)
            else:
                await update.message.reply_text(msg)
            return
        
        keyboard = [[InlineKeyboardButton(cat, callback_data=f"browse_cat_{i}")] 
                    for i, cat in enumerate(categories)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        msg = "🔍 **Browse Referral Links**\n\nSelect a category:"
        if query:
            await query.message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in browse_links_callback: {e}")
        try:
            if update.callback_query:
                await update.callback_query.answer("❌ An error occurred.")
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
                f"📭 No available links in **{category}**\n\n"
                "Try another category or check back later!",
                parse_mode='Markdown'
            )
            return
        
        keyboard = []
        message = f"🔗 **Available Links in {category}:**\n\n"
        
        for i, link in enumerate(links[:10]):
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
            await update.callback_query.answer("❌ An error occurred.")
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
            await query.edit_message_text("❌ This link is no longer available.")
            return
        
        if link['current_claims'] >= link['max_claims']:
            await query.edit_message_text("❌ This link has already been used.")
            return
        
        if link['referrer_user_id'] == user_id:
            await query.edit_message_text("❌ You cannot use your own referral link!")
            return
        
        db.increment_link_claims(link_id)
        
        await query.edit_message_text(
            f"🎉 **Here's your referral link!**\n\n"
            f"🔗 **Service:** {link['service_name']}\n"
            f"📄 **Instructions:** {link['description']}\n\n"
            f"👆 **Click here to sign up:**\n{link['url']}\n\n"
            f"✅ This link has been marked as used and removed from the list.\n"
            f"Thanks for using RefLoop!",
            parse_mode='Markdown'
        )
        
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
            logger.error(f"Failed to notify link owner: {e}")
    except Exception as e:
        logger.error(f"Error in use_link: {e}")
        try:
            await update.callback_query.answer("❌ An error occurred.")
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
    await query.edit_message_text("❌ Submission cancelled.")

def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not found in environment variables")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(submit_category, pattern="^cat_"))
    application.add_handler(CallbackQueryHandler(cancel_submission, pattern="^submit_cancel$"))
    application.add_handler(CallbackQueryHandler(browse_category, pattern="^browse_cat_"))
    application.add_handler(CallbackQueryHandler(use_link, pattern="^use_link_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    
    try:
        db.init_database()
        logger.info("✅ Database initialization completed successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return
    
    logger.info("✅ All handlers registered")
    logger.info("Starting polling mode for maximum reliability")
    
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Polling error: {e}")
        raise

if __name__ == '__main__':
    main()
