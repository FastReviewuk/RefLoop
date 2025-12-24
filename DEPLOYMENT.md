# Quick Deployment Guide for RefLoop Bot

## Option 1: Deploy to Render (Recommended)

### Step-by-Step Instructions

#### 1. Prepare BotFather Setup
```
1. Open Telegram → Search @BotFather
2. Send: /newbot
3. Choose name: RefLoop Bot
4. Choose username: refloop_bot (or your choice)
5. Copy the token (looks like: 8384270899:AAHkMQ05e4SdCEUablOqYKc5LUXEUFfMsQg)
6. Send: /mybots → Select your bot → Bot Settings → Payments
7. Select: Telegram Stars
```

#### 2. Get Your Admin User ID
```
1. Open Telegram → Search @userinfobot
2. Send: /start
3. Copy your ID (e.g., 123456789)
```

#### 3. Create GitHub Repository
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/refloop-bot.git
git push -u origin main
```

#### 4. Deploy Database on Render
```
1. Go to: https://dashboard.render.com/
2. Click: New + → PostgreSQL
3. Settings:
   - Name: refloop-db
   - Database: refloop_db
   - Region: Oregon (or closest to you)
   - Plan: Free
4. Click: Create Database
5. Wait for deployment (2-3 minutes)
6. Copy: Internal Database URL (starts with postgresql://)
```

#### 5. Deploy Bot on Render
```
1. Click: New + → Web Service
2. Connect: Your GitHub repository
3. Settings:
   - Name: refloop-bot
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: python bot.py
   - Plan: Free
4. Environment Variables (click "Add Environment Variable"):
   
   BOT_TOKEN
   8384270899:AAHkMQ05e4SdCEUablOqYKc5LUXEUFfMsQg
   
   DATABASE_URL
   [paste the Internal Database URL from step 4]
   
   ADMIN_USER_IDS
   [your user ID from step 2]

5. Click: Create Web Service
6. Wait for deployment (3-5 minutes)
```

#### 6. Test Your Bot
```
1. Open Telegram
2. Search: @refloop_bot (or your bot username)
3. Send: /start
4. You should see the welcome message!
```

## Option 2: Deploy to Heroku

### Prerequisites
- Heroku account
- Heroku CLI installed

### Steps
```bash
# Login to Heroku
heroku login

# Create app
heroku create refloop-bot

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set BOT_TOKEN=your_bot_token_here
heroku config:set ADMIN_USER_IDS=your_user_id_here

# Deploy
git push heroku main

# Scale worker
heroku ps:scale worker=1

# Check logs
heroku logs --tail
```

## Option 3: Local Development

### Setup
```bash
# Install PostgreSQL (macOS)
brew install postgresql@14
brew services start postgresql@14

# Create database
createdb refloop_db

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your values
nano .env
```

### .env Configuration
```env
BOT_TOKEN=8384270899:AAHkMQ05e4SdCEUablOqYKc5LUXEUFfMsQg
DATABASE_URL=postgresql://localhost:5432/refloop_db
ADMIN_USER_IDS=your_user_id_here
```

### Run
```bash
python bot.py
```

## Option 4: Deploy with Docker

### Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

### Create docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: refloop_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  bot:
    build: .
    depends_on:
      - db
    environment:
      BOT_TOKEN: ${BOT_TOKEN}
      DATABASE_URL: postgresql://postgres:postgres@db:5432/refloop_db
      ADMIN_USER_IDS: ${ADMIN_USER_IDS}

volumes:
  postgres_data:
```

### Run with Docker
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f bot

# Stop
docker-compose down
```

## Troubleshooting

### Bot doesn't respond
- Check Render logs: Dashboard → Your Service → Logs
- Verify BOT_TOKEN is correct
- Ensure database is connected

### Database connection error
- Check DATABASE_URL format
- Verify database is running
- Try internal database URL (not external)

### Admin commands don't work
- Verify ADMIN_USER_IDS is your actual Telegram user ID
- Check for spaces or typos
- Restart the service after changing env vars

### Payment not working
- Ensure Telegram Stars is enabled in BotFather
- Check bot has payment permissions
- Verify you're using currency="XTR"

## Monitoring

### Render Dashboard
- View logs in real-time
- Check service health
- Monitor database usage

### Bot Commands for Testing
```
/start - Should show welcome message
/my_status - Should show 0/3 claims
/browse - Should show "no links" initially
/submit_link - Should show payment options
```

## Updating the Bot

### On Render
```bash
# Make changes locally
git add .
git commit -m "Update bot"
git push origin main

# Render auto-deploys from GitHub
# Check deployment status in dashboard
```

### Manual Restart
```
Render Dashboard → Your Service → Manual Deploy → Deploy latest commit
```

## Getting Help

1. Check logs first: `heroku logs --tail` or Render dashboard
2. Verify all environment variables are set
3. Test database connection
4. Ensure bot token is valid
5. Check BotFather settings

## Next Steps After Deployment

1. Test all features thoroughly
2. Submit a test referral link
3. Create a test claim
4. Approve it as admin
5. Verify Stars payment works
6. Share your bot with users!

---

**Your Bot**: @refloop_bot
**Support**: Check README.md for detailed documentation
