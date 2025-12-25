# Test Payment Command - Quick Guide

## ✅ Implementation Complete

The `/test_payment` command has been successfully added to the bot for testing purposes.

## How to Use

### Step 1: Start a Link Submission
1. In the channel or private chat, use the menu or type `/start`
2. Click "📤 Submit Link"
3. Select a plan (A, B, or C)
4. Select a category
5. Continue in private chat with @refloop_bot
6. Enter service name
7. Enter URL
8. Enter description

### Step 2: Simulate Payment
Instead of paying with Stars, use the test command:
```
/test_payment
```

This will:
- ✅ Skip the payment invoice
- ✅ Create the referral link immediately
- ✅ Show success message with link details
- ✅ Make the link available for claiming

## Admin Access

The command is restricted to admin users only (configured in ADMIN_USER_IDS environment variable).

Current admin ID in .env: `123456789`

**Important**: Make sure your Telegram user ID matches the ADMIN_USER_IDS in your environment variables (both locally and on Render).

## Testing Workflow

1. **Local Testing**: Use the external database URL in .env
2. **Test the full flow**: Submit → Plan → Category → Service → URL → Description
3. **Use `/test_payment`**: Instead of paying, simulate the payment
4. **Verify**: Check that the link appears in "📋 Available Links"

## Production Note

After testing is complete, you can:
- Keep the command for future testing (recommended)
- Remove it by deleting the handler line from main() function

## Troubleshooting

If you get "❌ You don't have permission":
- Check your Telegram user ID (send a message to @userinfobot)
- Update ADMIN_USER_IDS in .env and on Render
- Restart the bot

If you get "❌ No pending submission found":
- Start the submission flow first with "Submit Link"
- Complete all steps up to the payment
- Then use `/test_payment`
