# RefLoop Bot - Admin Guide

## 👨‍💼 Admin Overview

As an admin, you're responsible for reviewing and approving/rejecting claim submissions. This ensures quality control and prevents abuse.

## 🔐 Admin Setup

### Getting Admin Access
Your Telegram user ID must be in the `ADMIN_USER_IDS` environment variable.

**Find your User ID:**
1. Open Telegram
2. Search for `@userinfobot`
3. Send `/start`
4. Copy your ID (e.g., `123456789`)

**Add to Environment:**
- **Render**: Dashboard → Service → Environment → Add `ADMIN_USER_IDS`
- **Heroku**: `heroku config:set ADMIN_USER_IDS=123456789`
- **Local**: Add to `.env` file

**Multiple Admins:**
```env
ADMIN_USER_IDS=123456789,987654321,555666777
```

## 📋 Admin Commands

### /approve <claim_id>
Approve a pending claim submission.

**What happens:**
1. Claim status changes to "approved"
2. User's `total_verified_claims` increments
3. Link's `used_claims` increments
4. User receives notification
5. **If claim #3**: User unlocks free submission
6. **If claim #4+**: User receives 1 Star invoice

**Example:**
```
/approve 42
```

**Response:**
```
✅ Claim 42 approved!
User now has 3 verified claims.
```

### /reject <claim_id>
Reject a pending claim submission.

**What happens:**
1. Claim status changes to "rejected"
2. User receives rejection notification
3. No rewards given
4. User can submit another claim

**Example:**
```
/reject 42
```

**Response:**
```
✅ Claim 42 rejected.
```

## 🔔 Claim Notifications

When a user submits a claim, you'll receive:

**Notification Format:**
```
🔔 New Claim Pending Review

🆔 Claim ID: 42
👤 User: @username (ID: 123456789)
🔗 Link: Binance (ID: 15)
📂 Category: 💰 Finance & Banking

[Screenshot attached]

Use /approve 42 or /reject 42
```

## ✅ Approval Checklist

Before approving a claim, verify:

### 1. Screenshot Quality
- [ ] Screenshot is clear and readable
- [ ] Shows the correct service/website
- [ ] Contains proof of sign-up (confirmation email, welcome screen, etc.)
- [ ] Not obviously fake or edited

### 2. Sign-Up Verification
- [ ] User actually completed the sign-up
- [ ] Used the correct referral link
- [ ] Followed the instructions in the link description
- [ ] Account appears legitimate (not spam)

### 3. User History
- [ ] Check if user has suspicious patterns
- [ ] Verify they're not submitting multiple fake claims
- [ ] Ensure they haven't claimed this link before (bot prevents this, but double-check)

### 4. Link Status
- [ ] Link hasn't reached max claims (5)
- [ ] Link is still active and valid
- [ ] Service is legitimate

## ❌ Rejection Reasons

Common reasons to reject a claim:

### Invalid Screenshot
- Blurry or unreadable
- Wrong service/website
- Doesn't show sign-up proof
- Obviously edited or fake

### Incomplete Sign-Up
- User didn't complete the process
- Didn't use the referral link
- Didn't follow instructions

### Suspicious Activity
- Multiple claims from same IP/device
- Fake accounts
- Spam behavior
- Abuse of system

### Technical Issues
- Link expired or invalid
- Service no longer available
- Referral link broken

## 📊 Admin Dashboard Queries

Use these SQL queries to monitor the system:

### Check Pending Claims
```sql
SELECT c.id, u.username, rl.service_name, c.created_at
FROM claims c
JOIN users u ON c.referred_user_id = u.user_id
JOIN referral_links rl ON c.link_id = rl.id
WHERE c.status = 'pending'
ORDER BY c.created_at DESC;
```

### Top Users by Claims
```sql
SELECT username, total_verified_claims, free_submissions_available
FROM users
ORDER BY total_verified_claims DESC
LIMIT 10;
```

### Most Popular Links
```sql
SELECT service_name, category, used_claims, max_claims
FROM referral_links
ORDER BY used_claims DESC
LIMIT 10;
```

### Recent Activity
```sql
SELECT 
    u.username,
    rl.service_name,
    c.status,
    c.created_at
FROM claims c
JOIN users u ON c.referred_user_id = u.user_id
JOIN referral_links rl ON c.link_id = rl.id
ORDER BY c.created_at DESC
LIMIT 20;
```

## 🚨 Handling Issues

### Spam/Abuse
If you notice spam or abuse:

1. **Reject all suspicious claims**
2. **Document the user ID**
3. **Consider blocking** (requires code modification)
4. **Monitor for patterns**

### Disputed Claims
If a user disputes a rejection:

1. **Review the screenshot again**
2. **Check claim details in database**
3. **Ask for additional proof if needed**
4. **Make final decision**

### Technical Problems
If claims aren't processing:

1. **Check bot logs** (Render Dashboard → Logs)
2. **Verify database connection**
3. **Test with a simple claim**
4. **Restart service if needed**

## 📈 Best Practices

### Response Time
- ⏱️ Review claims within 24 hours
- 🔔 Enable Telegram notifications
- 📱 Check regularly throughout the day

### Consistency
- 📋 Use the same criteria for all claims
- 📝 Document your decisions
- 🤝 Coordinate with other admins

### Communication
- 💬 Be clear in rejection reasons (if you message users)
- 🎯 Set expectations for approval time
- 📢 Announce any policy changes

### Security
- 🔒 Keep your admin credentials secure
- 🚫 Don't share your user ID publicly
- ⚠️ Watch for social engineering attempts

## 🎯 Approval Guidelines

### Quick Approve ✅
Clear screenshot showing:
- Welcome email from service
- Account confirmation page
- Dashboard with new account
- Referral bonus confirmation

### Needs Review 🤔
- Partial screenshot
- Unclear proof
- First-time user
- High-value service

### Quick Reject ❌
- No screenshot
- Wrong service
- Obviously fake
- Spam account

## 📞 Admin Communication

### With Users
When rejecting, you can optionally message users:

```
❌ Your claim #42 was rejected.

Reason: Screenshot doesn't show sign-up confirmation.

Please submit a new claim with:
- Clear screenshot
- Proof of account creation
- Visible confirmation email or welcome screen

Use /claim_reward to try again.
```

### With Other Admins
Coordinate on:
- Difficult decisions
- Policy changes
- Suspicious patterns
- System improvements

## 🔧 Admin Tools

### View Screenshot
When you receive a claim notification, the screenshot is attached. You can:
- Download it for closer inspection
- Forward to other admins for review
- Save for records

### Check User Stats
To see a user's history:
```sql
SELECT * FROM users WHERE user_id = 123456789;
SELECT * FROM claims WHERE referred_user_id = 123456789;
```

### Check Link Details
To see link information:
```sql
SELECT * FROM referral_links WHERE id = 15;
SELECT * FROM claims WHERE link_id = 15;
```

## 📊 Weekly Admin Tasks

### Monday
- [ ] Review weekend claims
- [ ] Check for spam patterns
- [ ] Clear pending queue

### Wednesday
- [ ] Mid-week review
- [ ] Check system health
- [ ] Monitor popular links

### Friday
- [ ] Week summary
- [ ] Identify trends
- [ ] Plan improvements

## 🎓 Training New Admins

When adding new admins:

1. **Share this guide**
2. **Add their user ID** to `ADMIN_USER_IDS`
3. **Do a test approval** together
4. **Review guidelines**
5. **Set expectations**

## 📈 Success Metrics

Track these metrics:

- **Approval Rate**: % of claims approved
- **Response Time**: Average time to review
- **User Satisfaction**: Feedback from users
- **Fraud Prevention**: Rejected spam claims

**Target Goals:**
- ✅ 90%+ approval rate (indicates quality submissions)
- ✅ <24 hour response time
- ✅ <5% fraud/spam rate

## 🆘 Emergency Procedures

### Bot Down
1. Check Render/Heroku status
2. Review error logs
3. Restart service
4. Notify users if extended downtime

### Database Issues
1. Check connection
2. Verify credentials
3. Contact hosting support
4. Restore from backup if needed

### Spam Attack
1. Reject all suspicious claims
2. Document user IDs
3. Consider temporary shutdown
4. Implement additional checks

## 📝 Admin Changelog

Keep track of important decisions:

```
2024-12-24: Initial launch
- Set approval criteria
- Defined rejection reasons
- Established response time goal

[Add your entries here]
```

## 🎉 Tips for Success

1. **Be Fair**: Treat all users equally
2. **Be Fast**: Quick reviews improve user experience
3. **Be Thorough**: Don't rush important decisions
4. **Be Consistent**: Use same standards for everyone
5. **Be Communicative**: Keep users informed

## 📚 Additional Resources

- **Main Documentation**: `README.md`
- **Technical Details**: `PROJECT_STRUCTURE.md`
- **Deployment**: `DEPLOYMENT.md`
- **Quick Start**: `QUICK_START.md`

---

**Remember**: You're the quality gatekeeper. Your careful review ensures the system works fairly for everyone! 🛡️

**Questions?** Review the documentation or check the bot logs for insights.

**Happy Moderating!** 🎯
