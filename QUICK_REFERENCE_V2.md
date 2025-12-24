# RefLoop Bot v2.0 - Quick Reference

## 🚀 Quick Start

### New Installation
```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your credentials

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run bot
python bot.py
# Migration happens automatically
```

### Upgrade from v1.0
```bash
# 1. Backup database
pg_dump $DATABASE_URL > backup.sql

# 2. Update code
git pull origin main

# 3. Restart bot
python bot.py
# Migration happens automatically

# Or run manual migration:
python migrate_v2.py
```

## 💰 Pricing Plans

| Plan | Referrals | Price | Per Referral |
|------|-----------|-------|--------------|
| A | 5 | 25 ⭐ | 5.00 ⭐ |
| B | 10 | 40 ⭐ | 4.00 ⭐ |
| C | 30 | 100 ⭐ | 3.33 ⭐ |

**Reward**: 3 ⭐ per verified claim (all claims)

## 📂 Categories

1. 🎮 Games
2. 💰 Crypto
3. 🏦 Banks
4. 📱 Telecom
5. 📦 Other

## 🎯 Key Features

### Tiered Plans
- Choose plan based on campaign size
- Better value for larger plans
- Clear, predictable pricing

### Higher Rewards
- 3 Stars per verified claim
- No complex rules
- Consistent for all claims

### Auto-Deletion
- Links auto-delete at limit
- Referrer notified
- Database stays clean

### Channel Interface
- Main menu in channel
- All functions via buttons
- Professional appearance

## 🔄 Workflows

### Submit Link
```
1. Click "Submit Link" button
2. Choose plan (A/B/C)
3. Pay Stars (25/40/100)
4. Select category
5. Enter service details
6. Link created
```

### Claim Reward
```
1. Click "Claim Reward" button
2. Select category
3. Select service
4. Upload screenshot
5. Wait for approval
6. Receive 3 Stars
```

### Admin Approval
```
1. /approve <claim_id>
2. User gets 3 Stars
3. Claims increment
4. Auto-delete if at limit
5. Referrer notified
```

## 🗄️ Database

### Schema
```sql
referral_links:
  - max_claims: 5, 10, or 30
  - current_claims: 0 to max_claims
  - Auto-deletes when current_claims == max_claims
```

### Migration
```sql
-- Automatic on startup
ALTER TABLE referral_links 
RENAME COLUMN used_claims TO current_claims;
```

## 📱 Channel Setup

### Channel ID
```python
CHANNEL_ID = -1003625306083  # RefLoop channel
```

### Menu Buttons
- 🔗 Submit Referral Link
- 🔍 Browse Links
- 🎁 Claim Reward
- 📊 My Status

## 🔧 Commands

### User Commands
- `/start` - Show main menu
- `/submit_link` - Submit link (also via button)
- `/browse` - Browse links (also via button)
- `/claim_reward` - Claim reward (also via button)

### Admin Commands
- `/approve <claim_id>` - Approve claim
- `/reject <claim_id>` - Reject claim

## 💻 Code Reference

### Key Constants
```python
CHANNEL_ID = -1003625306083

PLANS = {
    'A': {'max_claims': 5, 'price': 25},
    'B': {'max_claims': 10, 'price': 40},
    'C': {'max_claims': 30, 'price': 100}
}

CATEGORIES = [
    "🎮 Games",
    "💰 Crypto",
    "🏦 Banks",
    "📱 Telecom",
    "📦 Other"
]
```

### Key Functions
```python
# database.py
create_referral_link(..., max_claims)
increment_link_claims(link_id)  # Returns updated values
delete_referral_link(link_id)

# bot.py
submit_plan_choice()  # Handle plan selection
approve_claim()  # Includes auto-deletion
menu_handler()  # Channel button clicks
```

## 🔒 Safety Checks

### Before Claim
```python
# Check link exists
link = db.get_link_by_id(link_id)
if not link:
    return "Link no longer active"

# Check not at limit
if link['current_claims'] >= link['max_claims']:
    return "Link no longer active"

# Check no duplicate
if db.check_duplicate_claim(user_id, link_id):
    return "Already claimed"
```

### After Approval
```python
# Increment and check
link_update = db.increment_link_claims(link_id)

# Auto-delete if at limit
if link_update['current_claims'] >= link_update['max_claims']:
    db.delete_referral_link(link_id)
    notify_referrer()
```

## 📊 Comparison

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Price | 15 ⭐ | 25/40/100 ⭐ |
| Max Refs | 5 | 5/10/30 |
| Reward | 1 ⭐ | 3 ⭐ |
| Cleanup | Manual | Auto |
| Interface | Commands | Channel + Buttons |

## 🧪 Testing

### Quick Test
```bash
# 1. Start bot
python bot.py

# 2. In Telegram
/start  # Check menu appears

# 3. Test plan selection
Click "Submit Link"
Select Plan A
Verify price is 25 Stars

# 4. Test auto-deletion
Submit link with Plan A (5 refs)
Approve 5 claims
Verify link deleted
Verify referrer notified
```

### Full Test Checklist
- [ ] Plan selection works
- [ ] Payment works (25/40/100)
- [ ] Links created correctly
- [ ] Claims earn 3 Stars
- [ ] Auto-deletion works
- [ ] Notifications sent
- [ ] Channel menu works
- [ ] All buttons functional

## 🐛 Troubleshooting

### Migration Issues
```bash
# Check if migration needed
psql $DATABASE_URL -c "SELECT column_name FROM information_schema.columns WHERE table_name='referral_links';"

# Run manual migration
python migrate_v2.py

# Verify
psql $DATABASE_URL -c "SELECT * FROM referral_links LIMIT 1;"
```

### Channel Issues
```bash
# Verify channel ID
echo $CHANNEL_ID  # Should be -1003625306083

# Test posting
# Bot must be admin in channel
# Check bot has post permissions
```

### Payment Issues
```bash
# Verify Stars enabled
# Check BotFather settings
# Ensure currency="XTR"
# Ensure provider_token=""
```

## 📞 Support

### Documentation
- `UPDATE_NOTES.md` - Technical details
- `V2_SUMMARY.md` - Complete overview
- `QUICK_REFERENCE_V2.md` - This file
- `README.md` - General docs

### Scripts
- `bot.py` - Main application
- `database.py` - Database layer
- `migrate_v2.py` - Manual migration
- `test_setup.py` - Environment check

## 🎊 Quick Tips

1. **Choose Right Plan**: Plan C offers best value per referral
2. **Test First**: Use Plan A for testing (cheapest)
3. **Monitor Limits**: Links auto-delete at limit
4. **Check Channel**: Ensure bot is admin with post permissions
5. **Backup First**: Always backup before upgrading

## 📈 Best Practices

### For Referrers
- Start with Plan A to test
- Use Plan C for large campaigns
- Monitor claim progress
- Expect auto-deletion at limit

### For Admins
- Approve claims promptly
- Monitor auto-deletions
- Check referrer notifications
- Review logs regularly

### For Developers
- Test all plans
- Verify auto-deletion
- Check error handling
- Monitor database size

---

**Version**: 2.0.0  
**Updated**: December 24, 2024  
**Status**: ✅ Production Ready

**Need help?** Check the full documentation or run `python test_setup.py`
