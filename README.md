# RefLoop Bot 🔗⭐

A fully functional Telegram bot that enables users to submit, browse, and claim rewards for referral links with integrated Telegram Stars payment system.

**Bot Username**: [@refloop_bot](https://t.me/refloop_bot)  
**Status**: ✅ Production Ready  
**Version**: 1.0.0

## 📚 Quick Navigation

- **New User?** Start with [QUICK_START.md](QUICK_START.md) (5 minutes to deploy!)
- **Admin?** Read [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
- **Developer?** Check [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **Deploying?** Follow [DEPLOYMENT.md](DEPLOYMENT.md)
- **Need Overview?** See [SUMMARY.md](SUMMARY.md)
- **All Docs?** Browse [INDEX.md](INDEX.md)

## Features

- 🔗 **Dual Submission Model**: Submit links by paying 15 Stars OR completing 3 verified sign-ups
- ⭐ **Telegram Stars Rewards**: Earn 1 Star for each verified claim after the first 3
- 📸 **Screenshot Verification**: All claims require screenshot proof and admin approval
- 🎯 **Category-Based Browsing**: Organized referral links across 10 categories
- 🔒 **Username Required**: Only users with public Telegram usernames can participate
- 📊 **Progress Tracking**: Users can check their status and progress anytime
- 🛡️ **Anti-Abuse**: Prevents duplicate claims and enforces claim limits per link

## How It Works

### For Users Claiming Rewards:
1. Complete sign-ups on existing referral links
2. Submit screenshot proof via the bot
3. Wait for admin approval
4. **First 3 verified claims**: No Stars earned, but unlocks 1 FREE link submission
5. **4th claim onwards**: Earn 1 Telegram Star per verified claim

### For Users Submitting Links:
1. Choose submission method:
   - **Pay 15 ⭐**: Immediate submission after payment
   - **Use Free Slot**: Available after completing 3 verified claims
2. Select category and provide link details
3. Link becomes available for others to claim (max 5 claims per link)

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### 1. Create Your Bot with BotFather

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Save your bot token (format: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
4. Send `/mybots` → Select your bot → **Bot Settings** → **Payments**
5. Select **Telegram Stars** as payment provider

### 2. Local Development Setup

```bash
# Clone or download the project
cd refloop-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials
# BOT_TOKEN=your_bot_token_here
# DATABASE_URL=postgresql://user:password@localhost:5432/refloop_db
# ADMIN_USER_IDS=your_telegram_user_id

# Set up PostgreSQL database
createdb refloop_db

# Run the bot
python bot.py
```

### 3. Deploy to Render

#### Step 1: Prepare Your Repository

1. Create a new GitHub repository
2. Push this code to your repository:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/refloop-bot.git
git push -u origin main
```

#### Step 2: Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **PostgreSQL**
3. Configure:
   - **Name**: `refloop-db`
   - **Database**: `refloop_db`
   - **User**: (auto-generated)
   - **Region**: Choose closest to your users
   - **Plan**: Free or paid
4. Click **Create Database**
5. Copy the **Internal Database URL** (starts with `postgresql://`)

#### Step 3: Deploy Bot as Web Service

1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `refloop-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Plan**: Free or paid
4. Add Environment Variables:
   - `BOT_TOKEN`: Your bot token from BotFather
   - `DATABASE_URL`: The Internal Database URL from Step 2
   - `ADMIN_USER_IDS`: Your Telegram user ID (comma-separated for multiple admins)
5. Click **Create Web Service**

#### Step 4: Get Your Telegram User ID

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot)
2. Send `/start` to get your user ID
3. Add this ID to the `ADMIN_USER_IDS` environment variable in Render

#### Step 5: Test Your Bot

1. Open Telegram and search for your bot: `@refloop_bot`
2. Send `/start` to begin
3. Test all features:
   - `/my_status` - Check your progress
   - `/browse` - Browse available links
   - `/claim_reward` - Claim a reward
   - `/submit_link` - Submit a referral link

## Bot Commands

### User Commands
- `/start` - Start the bot and register
- `/submit_link` - Submit a new referral link
- `/browse` - Browse available referral links
- `/claim_reward` - Claim a reward from a referral link
- `/my_status` - Check your progress and stats
- `/cancel` - Cancel current operation

### Admin Commands
- `/approve <claim_id>` - Approve a pending claim
- `/reject <claim_id>` - Reject a pending claim

## Database Schema

### Users Table
```sql
- user_id (BIGINT, PK)
- username (VARCHAR)
- free_submissions_available (INTEGER, default 0)
- total_verified_claims (INTEGER, default 0)
- created_at (TIMESTAMP)
```

### Referral Links Table
```sql
- id (SERIAL, PK)
- referrer_user_id (BIGINT, FK)
- category (VARCHAR)
- service_name (VARCHAR)
- url (TEXT)
- description (TEXT)
- max_claims (INTEGER, default 5)
- used_claims (INTEGER, default 0)
- created_at (TIMESTAMP)
```

### Claims Table
```sql
- id (SERIAL, PK)
- referred_user_id (BIGINT, FK)
- link_id (INTEGER, FK)
- screenshot_file_id (VARCHAR)
- status (VARCHAR, default 'pending')
- rewarded (BOOLEAN, default FALSE)
- created_at (TIMESTAMP)
- UNIQUE(referred_user_id, link_id)
```

## Categories

The bot supports 10 predefined categories:
- 💰 Finance & Banking
- 🛍️ E-commerce
- 🎮 Gaming
- 📱 Apps & Services
- 🎓 Education
- 🏨 Travel & Booking
- 🍔 Food Delivery
- 💼 Freelancing
- 📊 Crypto & Trading
- 🎬 Entertainment

## Telegram Stars Integration

### Payment Flow
1. **Link Submission (15 Stars)**: User pays → Invoice sent → Payment confirmed → Link created
2. **Claim Rewards (1 Star)**: Admin approves → Check claim count → If > 3, send 1 Star invoice

### Important Notes
- Telegram Stars use currency code `XTR`
- Empty `provider_token` for Telegram Stars
- Stars are virtual currency within Telegram
- Users need Telegram Premium or sufficient Stars balance

## Security Features

- ✅ Username validation (blocks users without public username)
- ✅ Duplicate claim prevention (same user can't claim same link twice)
- ✅ Claim limits (max 5 claims per referral link)
- ✅ Admin-only approval commands
- ✅ Screenshot verification required
- ✅ SQL injection prevention (parameterized queries)

## Troubleshooting

### Bot Not Responding
- Check if the bot is running: `ps aux | grep bot.py`
- Check logs for errors
- Verify BOT_TOKEN is correct
- Ensure database connection is working

### Database Connection Issues
- Verify DATABASE_URL format: `postgresql://user:password@host:port/database`
- Check if PostgreSQL is running
- Test connection: `psql $DATABASE_URL`

### Payment Issues
- Ensure Telegram Stars is enabled in BotFather settings
- Verify currency is set to "XTR"
- Check that provider_token is empty string

### Admin Commands Not Working
- Verify your user ID is in ADMIN_USER_IDS
- Check for typos in environment variable
- Restart bot after changing environment variables

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Your Telegram bot token from BotFather | `123456:ABC-DEF...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `ADMIN_USER_IDS` | Comma-separated admin user IDs | `123456789,987654321` |

## Development

### Running Tests
```bash
# Install dev dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Database Migrations
The bot automatically creates tables on first run. To reset:
```bash
# Connect to database
psql $DATABASE_URL

# Drop all tables
DROP TABLE claims, referral_links, users CASCADE;

# Restart bot to recreate tables
python bot.py
```

## License

MIT License - Feel free to use and modify for your needs.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Render logs for errors
3. Verify all environment variables are set correctly

## Credits

Built with:
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) v20.7
- PostgreSQL
- Telegram Stars API

---

**Bot Username**: [@refloop_bot](https://t.me/refloop_bot)

Happy referring! 🚀⭐
