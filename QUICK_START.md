# RefLoop Bot - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Get Your Bot Token (2 minutes)
1. Open Telegram
2. Search for `@BotFather`
3. Send: `/newbot`
4. Follow prompts to create your bot
5. **Copy the token** (looks like: `8384270899:AAHkMQ05e4SdCEUablOqYKc5LUXEUFfMsQg`)
6. Send: `/mybots` → Select your bot → **Bot Settings** → **Payments** → Select **Telegram Stars**

### Step 2: Get Your User ID (30 seconds)
1. Search for `@userinfobot` in Telegram
2. Send: `/start`
3. **Copy your ID** (e.g., `123456789`)

### Step 3: Deploy to Render (3 minutes)

#### A. Create Database
1. Go to [render.com](https://dashboard.render.com/)
2. Click **New +** → **PostgreSQL**
3. Name: `refloop-db`
4. Click **Create Database**
5. **Copy the Internal Database URL**

#### B. Deploy Bot
1. Click **New +** → **Web Service**
2. Connect your GitHub repo (or use "Public Git Repository" with this repo URL)
3. Settings:
   - **Name**: `refloop-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
4. Add Environment Variables:
   ```
   BOT_TOKEN = [your token from Step 1]
   DATABASE_URL = [your database URL from Step 3A]
   ADMIN_USER_IDS = [your user ID from Step 2]
   ```
5. Click **Create Web Service**
6. Wait 2-3 minutes for deployment

### Step 4: Test Your Bot (1 minute)
1. Open Telegram
2. Search for your bot (e.g., `@refloop_bot`)
3. Send: `/start`
4. You should see the welcome message! 🎉

## 📱 Basic Commands

### For Users
- `/start` - Register and see welcome message
- `/my_status` - Check your progress (claims completed, free submissions)
- `/browse` - Browse available referral links by category
- `/claim_reward` - Claim a reward from a referral link
- `/submit_link` - Submit your own referral link (pay 15 ⭐ or use free slot)

### For Admins
- `/approve <claim_id>` - Approve a pending claim
- `/reject <claim_id>` - Reject a pending claim

## 🎯 How It Works

### For Users Claiming Rewards:
1. **Browse** available referral links (`/browse`)
2. **Claim** a reward (`/claim_reward`)
3. **Complete** the sign-up on the referral link
4. **Upload** screenshot proof
5. **Wait** for admin approval

**Rewards:**
- Claims 1-3: No Stars, but unlocks 1 FREE link submission after 3rd claim
- Claims 4+: Earn 1 ⭐ per verified claim

### For Users Submitting Links:
1. **Choose** payment method:
   - Pay 15 ⭐ (immediate)
   - Use free slot (after completing 3 claims)
2. **Select** category
3. **Enter** service name, URL, and description
4. **Submit** and wait for users to claim!

## 🔧 Local Development (Optional)

### Prerequisites
- Python 3.8+
- PostgreSQL

### Setup
```bash
# Clone repository
git clone <your-repo-url>
cd refloop-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
createdb refloop_db

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Test setup
python test_setup.py

# Run bot
python bot.py
```

## 🐛 Troubleshooting

### Bot doesn't respond
- ✅ Check Render logs (Dashboard → Your Service → Logs)
- ✅ Verify `BOT_TOKEN` is correct
- ✅ Ensure service is running (not crashed)

### Database error
- ✅ Use **Internal Database URL** (not External)
- ✅ Check DATABASE_URL format: `postgresql://user:pass@host:port/db`
- ✅ Verify database is running

### Admin commands don't work
- ✅ Verify `ADMIN_USER_IDS` is YOUR Telegram user ID
- ✅ No spaces in the ID
- ✅ Restart service after changing environment variables

### Payment not working
- ✅ Enable Telegram Stars in BotFather settings
- ✅ Go to: `/mybots` → Your Bot → Bot Settings → Payments → Telegram Stars

## 📊 Testing Checklist

After deployment, test these features:

- [ ] `/start` - Shows welcome message
- [ ] `/my_status` - Shows 0/3 claims
- [ ] `/browse` - Shows "no links" (initially)
- [ ] `/submit_link` - Shows payment options
- [ ] Submit a test link (pay 15 ⭐)
- [ ] `/browse` - Now shows your link
- [ ] `/claim_reward` - Can select your link
- [ ] Upload screenshot
- [ ] `/approve <id>` - Approve as admin
- [ ] Check user receives notification
- [ ] Verify claim counter increases

## 🎓 Example Workflow

### Scenario: New User Journey

**Day 1:**
```
User: /start
Bot: Welcome message

User: /my_status
Bot: 0/3 claims, 0 free submissions

User: /browse
Bot: Shows available links

User: /claim_reward
Bot: Select category → service → upload screenshot
User: [uploads screenshot]
Bot: Claim submitted, pending review

Admin: /approve 1
Bot: Claim approved! (1/3 claims)
```

**Day 2:**
```
User: /claim_reward
[completes 2nd claim]
Admin: /approve 2
Bot: Claim approved! (2/3 claims)
```

**Day 3:**
```
User: /claim_reward
[completes 3rd claim]
Admin: /approve 3
Bot: Claim approved! (3/3 claims) - FREE submission unlocked! 🎉

User: /my_status
Bot: 3/3 claims, 1 free submission available

User: /submit_link
Bot: Pay 15 ⭐ OR Use free slot
User: [selects free slot]
Bot: [guides through submission]
Bot: Link submitted successfully!
```

**Day 4:**
```
User: /claim_reward
[completes 4th claim]
Admin: /approve 4
Bot: Claim approved! You've earned 1 ⭐
[Bot sends 1 Star invoice]
User: [accepts payment]
Bot: Congratulations! You've received 1 Telegram Star!
```

## 📚 Additional Resources

- **Full Documentation**: See `README.md`
- **Deployment Guide**: See `DEPLOYMENT.md`
- **Project Structure**: See `PROJECT_STRUCTURE.md`
- **Test Setup**: Run `python test_setup.py`

## 🆘 Need Help?

1. Check the logs first
2. Run `python test_setup.py` to verify configuration
3. Review `README.md` for detailed troubleshooting
4. Check environment variables are set correctly
5. Verify database connection

## 🎉 Success!

If you can:
- ✅ Send `/start` and get a response
- ✅ See your bot online in Telegram
- ✅ Submit and approve a test claim

**Your bot is working perfectly!** 🚀

Now share it with users and start building your referral network!

---

**Bot Token**: `8384270899:AAHkMQ05e4SdCEUablOqYKc5LUXEUFfMsQg`
**Bot Username**: `@refloop_bot`
**Ready to launch!** 🎊
