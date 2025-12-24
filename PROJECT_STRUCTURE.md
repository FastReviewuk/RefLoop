# RefLoop Bot - Project Structure

## File Overview

```
refloop-bot/
├── bot.py                  # Main bot application
├── database.py             # Database operations and models
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .env                   # Your actual environment variables (not in git)
├── .gitignore            # Git ignore rules
├── README.md             # Main documentation
├── DEPLOYMENT.md         # Deployment guide
├── PROJECT_STRUCTURE.md  # This file
├── test_setup.py         # Setup verification script
├── start.sh              # Startup script
├── Procfile              # Heroku/Render process file
└── runtime.txt           # Python version specification
```

## Core Files

### bot.py
**Purpose**: Main Telegram bot application with all handlers and logic

**Key Components**:
- Command handlers: `/start`, `/submit_link`, `/browse`, `/claim_reward`, `/my_status`
- Admin commands: `/approve`, `/reject`
- Conversation handlers for multi-step flows
- Payment processing (Telegram Stars)
- Callback query handlers for inline keyboards

**Main Functions**:
- `start()` - Welcome message and user registration
- `submit_link_start()` - Begin link submission flow
- `claim_reward_start()` - Begin claim submission flow
- `approve_claim()` - Admin approval of claims
- `browse_links()` - Browse available referral links
- `my_status()` - Show user progress

### database.py
**Purpose**: Database operations and PostgreSQL connection management

**Key Components**:
- Connection management with context manager
- Table initialization
- CRUD operations for users, links, and claims

**Main Functions**:
- `init_database()` - Create all tables
- `create_user()` - Register new user
- `get_user()` - Fetch user data
- `update_user_claims()` - Increment verified claims
- `create_referral_link()` - Add new referral link
- `create_claim()` - Submit new claim
- `approve_claim()` - Mark claim as approved

## Configuration Files

### requirements.txt
Python package dependencies:
- `python-telegram-bot==20.7` - Telegram Bot API wrapper
- `psycopg2-binary==2.9.9` - PostgreSQL adapter
- `python-dotenv==1.0.0` - Environment variable loader

### .env.example
Template for environment variables. Copy to `.env` and fill in:
```env
BOT_TOKEN=your_bot_token_from_botfather
DATABASE_URL=postgresql://user:password@host:port/database
ADMIN_USER_IDS=comma,separated,user,ids
```

### .gitignore
Prevents sensitive files from being committed:
- `.env` (contains secrets)
- `__pycache__/` (Python cache)
- Virtual environment folders

## Documentation Files

### README.md
Main documentation covering:
- Features overview
- Setup instructions
- Deployment guides (Render, Heroku, Local)
- Database schema
- Commands reference
- Troubleshooting

### DEPLOYMENT.md
Step-by-step deployment guide for:
- Render (recommended)
- Heroku
- Local development
- Docker

### PROJECT_STRUCTURE.md
This file - explains project organization

## Utility Files

### test_setup.py
Verification script that tests:
- Environment variables
- Database connection
- Bot token validity
- Package installation
- Database schema creation

**Usage**:
```bash
python test_setup.py
```

### start.sh
Simple startup script that:
- Loads environment variables from `.env`
- Starts the bot

**Usage**:
```bash
chmod +x start.sh
./start.sh
```

### Procfile
Tells Render/Heroku how to run the bot:
```
worker: python bot.py
```

### runtime.txt
Specifies Python version for deployment:
```
python-3.11.0
```

## Database Schema

### Tables

#### users
Stores user information and progress
```sql
user_id                    BIGINT PRIMARY KEY
username                   VARCHAR(255)
free_submissions_available INTEGER DEFAULT 0
total_verified_claims      INTEGER DEFAULT 0
created_at                 TIMESTAMP
```

#### referral_links
Stores submitted referral links
```sql
id                 SERIAL PRIMARY KEY
referrer_user_id   BIGINT (FK to users)
category           VARCHAR(255)
service_name       VARCHAR(255)
url                TEXT
description        TEXT
max_claims         INTEGER DEFAULT 5
used_claims        INTEGER DEFAULT 0
created_at         TIMESTAMP
```

#### claims
Stores claim submissions and their status
```sql
id                  SERIAL PRIMARY KEY
referred_user_id    BIGINT (FK to users)
link_id             INTEGER (FK to referral_links)
screenshot_file_id  VARCHAR(255)
status              VARCHAR(50) DEFAULT 'pending'
rewarded            BOOLEAN DEFAULT FALSE
created_at          TIMESTAMP
UNIQUE(referred_user_id, link_id)
```

## Flow Diagrams

### Link Submission Flow
```
User: /submit_link
  ↓
Choose payment method (15 Stars OR Free)
  ↓
Select category
  ↓
Enter service name
  ↓
Enter URL
  ↓
Enter description
  ↓
[If paid] → Pay 15 Stars → Link created
[If free] → Use free slot → Link created
```

### Claim Submission Flow
```
User: /claim_reward
  ↓
Select category
  ↓
Select service
  ↓
View link details
  ↓
Upload screenshot
  ↓
Claim submitted (pending)
  ↓
Admin reviews
  ↓
[Approved] → Increment claims → Check count
  ├─ Claims 1-3: No reward, unlock free submission at 3
  └─ Claims 4+: Send 1 Star invoice
[Rejected] → Notify user
```

### Admin Approval Flow
```
User submits claim
  ↓
Bot sends notification to admins with screenshot
  ↓
Admin: /approve <claim_id>
  ↓
Update user's total_verified_claims
  ↓
Check claim count:
  ├─ If == 3: Grant free_submissions_available += 1
  └─ If > 3: Send 1 Star reward invoice
  ↓
Increment link's used_claims
  ↓
Notify user of approval
```

## Key Features Implementation

### Dual Submission Model
- **File**: `bot.py` → `submit_payment_choice()`
- **Logic**: Check `free_submissions_available` vs paid option
- **Payment**: Telegram Stars invoice for 15 XTR

### Claim Verification
- **File**: `bot.py` → `claim_screenshot()`
- **Process**: Screenshot → Admin notification → Manual review
- **Anti-duplicate**: Database constraint on (user_id, link_id)

### Reward System
- **File**: `bot.py` → `approve_claim()`
- **Logic**: 
  - Claims 1-3: No Stars, track progress
  - Claim 3: Unlock free submission
  - Claims 4+: Send 1 Star invoice

### Username Validation
- **File**: `bot.py` → `start()`, all handlers
- **Check**: `if not user.username` → Block access

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `BOT_TOKEN` | Telegram bot authentication | `123456:ABC-DEF...` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host:5432/db` |
| `ADMIN_USER_IDS` | Admin Telegram user IDs | `123456789,987654321` |

## Development Workflow

### Local Development
1. Set up PostgreSQL locally
2. Create `.env` with local database
3. Run `python test_setup.py`
4. Run `python bot.py`
5. Test with Telegram

### Making Changes
1. Edit `bot.py` or `database.py`
2. Test locally
3. Commit changes
4. Push to GitHub
5. Render auto-deploys

### Adding Features
1. Add database changes in `database.py`
2. Add handlers in `bot.py`
3. Update documentation
4. Test thoroughly
5. Deploy

## Security Considerations

### Implemented
- ✅ Parameterized SQL queries (prevents SQL injection)
- ✅ Username validation
- ✅ Admin-only commands
- ✅ Duplicate claim prevention
- ✅ Environment variable for secrets

### Best Practices
- Never commit `.env` file
- Use strong database passwords
- Regularly update dependencies
- Monitor admin actions
- Review claims carefully

## Monitoring & Maintenance

### Logs
- **Render**: Dashboard → Service → Logs
- **Heroku**: `heroku logs --tail`
- **Local**: Console output

### Database Maintenance
```sql
-- Check user stats
SELECT username, total_verified_claims, free_submissions_available 
FROM users ORDER BY total_verified_claims DESC;

-- Check pending claims
SELECT COUNT(*) FROM claims WHERE status = 'pending';

-- Check link usage
SELECT service_name, used_claims, max_claims 
FROM referral_links ORDER BY used_claims DESC;
```

### Performance
- Database indexes on foreign keys (auto-created)
- Connection pooling via context manager
- Efficient queries with proper WHERE clauses

## Troubleshooting Guide

### Bot not starting
1. Check `python test_setup.py`
2. Verify all environment variables
3. Check database connection
4. Review logs for errors

### Commands not working
1. Verify bot token is correct
2. Check BotFather settings
3. Ensure bot is running
4. Test with `/start` first

### Payment issues
1. Enable Telegram Stars in BotFather
2. Verify currency is "XTR"
3. Check provider_token is empty
4. Test with small amount first

## Future Enhancements

Potential features to add:
- [ ] User statistics dashboard
- [ ] Link expiration dates
- [ ] Category management by admins
- [ ] Automated claim verification (OCR)
- [ ] Referral leaderboard
- [ ] Multi-language support
- [ ] Link analytics
- [ ] Bulk admin actions

## Support & Resources

- **Telegram Bot API**: https://core.telegram.org/bots/api
- **python-telegram-bot**: https://docs.python-telegram-bot.org/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Render**: https://render.com/docs

---

**Last Updated**: December 2024
**Version**: 1.0.0
**Bot**: @refloop_bot
