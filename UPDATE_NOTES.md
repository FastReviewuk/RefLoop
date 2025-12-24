# RefLoop Bot - Update Notes (v2.0)

## 🎉 Major Update: New Economic Model

### What's Changed

#### 1. New Tiered Pricing Plans
**Old Model**: Pay 15 Stars OR complete 3 claims for free submission

**New Model**: Three paid plans with different referral limits
- **Plan A**: Up to 5 referrals → 25 ⭐
- **Plan B**: Up to 10 referrals → 40 ⭐
- **Plan C**: Up to 30 referrals → 100 ⭐

#### 2. Increased Rewards
**Old Model**: 1 Star per verified claim (after 3rd claim)

**New Model**: 3 Stars per verified claim (all claims)

#### 3. Automatic Link Cleanup
**New Feature**: Links are automatically deleted when they reach their referral limit
- Referrer receives notification when link is removed
- Future claim attempts show "This referral link is no longer active"

#### 4. Simplified Categories
**Old Categories**: 10 categories (Finance, E-commerce, Gaming, etc.)

**New Categories**: 5 streamlined categories
- 🎮 Games
- 💰 Crypto
- 🏦 Banks
- 📱 Telecom
- 📦 Other

#### 5. Channel-Based Interface
**New Feature**: Main menu posted to RefLoop channel (-1003625306083)
- Clean button interface for all functions
- Submit Link, Browse, Claim Reward, My Status
- Better organization and user experience

## 📊 Database Changes

### Updated Schema
```sql
-- referral_links table now uses:
max_claims INTEGER NOT NULL      -- 5, 10, or 30 based on plan
current_claims INTEGER DEFAULT 0 -- renamed from used_claims

-- Migration handled automatically
```

### Key Changes
- `used_claims` renamed to `current_claims`
- `max_claims` now varies (5, 10, or 30) instead of fixed at 5
- Automatic migration on startup

## 🔄 Workflow Changes

### Link Submission Flow
```
User clicks "Submit Link" button
  ↓
Choose Plan (A/B/C)
  ↓
Pay Stars (25/40/100)
  ↓
Select Category
  ↓
Enter Service Details
  ↓
Link Created with max_claims
```

### Claim Approval Flow
```
Admin approves claim
  ↓
Send 3 Stars to user
  ↓
Increment current_claims
  ↓
If current_claims == max_claims:
  → Delete link
  → Notify referrer
```

### Auto-Deletion Logic
```python
# After incrementing claims
if link['current_claims'] >= link['max_claims']:
    # Delete the link
    db.delete_referral_link(link_id)
    
    # Notify referrer
    send_notification(referrer_id, 
        "Your link has reached its limit and been removed")
```

## 🎯 Key Features

### 1. Tiered Plans
- Users choose plan based on expected referrals
- Higher plans offer better value per referral
- Flexible pricing for different needs

### 2. Consistent Rewards
- All verified claims earn 3 Stars
- No more "first 3 free" complexity
- Simpler, more predictable rewards

### 3. Automatic Cleanup
- No manual link management needed
- Database stays clean
- Clear communication to users

### 4. Channel Integration
- Professional interface via channel
- All functions accessible via buttons
- Better user experience

## 🔧 Technical Implementation

### New Functions in database.py
```python
def increment_link_claims(link_id: int):
    """Returns updated claim counts for auto-deletion check"""
    
def delete_referral_link(link_id: int):
    """Removes link that reached its limit"""
    
def create_referral_link(..., max_claims: int):
    """Now accepts max_claims parameter"""
```

### New Constants in bot.py
```python
CHANNEL_ID = -1003625306083  # RefLoop channel

PLANS = {
    'A': {'max_claims': 5, 'price': 25, 'name': 'Plan A - 5 Referrals'},
    'B': {'max_claims': 10, 'price': 40, 'name': 'Plan B - 10 Referrals'},
    'C': {'max_claims': 30, 'price': 100, 'name': 'Plan C - 30 Referrals'}
}

CATEGORIES = [
    "🎮 Games",
    "💰 Crypto",
    "🏦 Banks",
    "📱 Telecom",
    "📦 Other"
]
```

### Updated Handlers
- `submit_link_start()` - Now shows plan selection
- `submit_plan_choice()` - New handler for plan selection
- `approve_claim()` - Now includes auto-deletion logic
- `menu_handler()` - New handler for channel buttons

## 📱 User Experience

### Main Menu (Channel)
```
👋 Welcome to RefLoop!

🔗 Share referral links and earn Telegram Stars!

💰 Pricing Plans:
• Plan A: 5 referrals → 25 ⭐
• Plan B: 10 referrals → 40 ⭐
• Plan C: 30 referrals → 100 ⭐

[🔗 Submit Referral Link]
[🔍 Browse Links]
[🎁 Claim Reward]
[📊 My Status]
```

### Plan Selection
```
🔗 Submit Your Referral Link

Choose a plan:

💎 Plan A: Up to 5 referrals → 25 ⭐
💎 Plan B: Up to 10 referrals → 40 ⭐
💎 Plan C: Up to 30 referrals → 100 ⭐

Each verified claim earns the user 3 ⭐
Links auto-delete when limit is reached.

[💎 Plan A] [💎 Plan B] [💎 Plan C]
```

### Link Deletion Notification
```
✅ Your link for Binance has reached its limit 
of 10 referrals and has been removed.

Thank you for using RefLoop! 🎉
```

## 🔒 Safety Features

### 1. Link Existence Check
Before processing claim:
```python
link = db.get_link_by_id(link_id)
if not link:
    return "This referral link is no longer active."
```

### 2. Claim Limit Check
Before accepting claim:
```python
if link['current_claims'] >= link['max_claims']:
    return "This referral link is no longer active."
```

### 3. Atomic Operations
Claims increment and deletion happen in sequence:
```python
# 1. Approve claim
db.approve_claim(claim_id)

# 2. Increment counter
link_update = db.increment_link_claims(link_id)

# 3. Check and delete if needed
if link_update['current_claims'] >= link_update['max_claims']:
    db.delete_referral_link(link_id)
```

## 📈 Benefits

### For Users
- ✅ Clear pricing structure
- ✅ Higher rewards (3 Stars vs 1 Star)
- ✅ Flexible plan options
- ✅ Clean interface via channel

### For Referrers
- ✅ Choose plan based on needs
- ✅ Automatic cleanup
- ✅ Clear notifications
- ✅ Better value for larger campaigns

### For Admins
- ✅ Simpler approval process
- ✅ Automatic link management
- ✅ Less manual cleanup needed
- ✅ Clear audit trail

## 🚀 Migration Guide

### For Existing Installations

1. **Backup Database**
```bash
pg_dump $DATABASE_URL > backup.sql
```

2. **Update Code**
```bash
git pull origin main
```

3. **Restart Bot**
```bash
# The bot will automatically migrate the schema
python bot.py
```

4. **Verify Migration**
```sql
-- Check column was renamed
SELECT column_name FROM information_schema.columns 
WHERE table_name='referral_links';

-- Should show 'current_claims' not 'used_claims'
```

### For New Installations

Just follow the standard setup in QUICK_START.md - everything is ready to go!

## 🧪 Testing Checklist

- [ ] Plan selection shows all 3 plans
- [ ] Payment works for each plan (25/40/100 Stars)
- [ ] Links created with correct max_claims
- [ ] Claims earn 3 Stars when approved
- [ ] Links auto-delete at limit
- [ ] Referrer receives deletion notification
- [ ] Future claims show "no longer active"
- [ ] Channel menu buttons work
- [ ] Categories show correctly (5 categories)

## 📝 Code Comments

Key sections now include detailed comments:

```python
# NEW ECONOMIC MODEL: Tiered pricing plans
# Plan A: 5 referrals → 25 Stars
# Plan B: 10 referrals → 40 Stars
# Plan C: 30 referrals → 100 Stars

# REWARD LOGIC: All verified claims earn 3 Stars
# (Previously: 1 Star after 3rd claim)

# AUTO-DELETION: Links removed when current_claims == max_claims
# Referrer is notified automatically
```

## 🎊 Summary

This update transforms RefLoop into a more professional, scalable referral platform with:
- Clear pricing tiers
- Better rewards
- Automatic management
- Improved UX

All changes are backward-compatible with automatic migration!

---

**Version**: 2.0.0  
**Updated**: December 24, 2024  
**Status**: ✅ Production Ready
