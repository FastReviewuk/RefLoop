# RefLoop Bot - System Flow Diagrams

## 🔄 Complete System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      REFLOOP BOT SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐      ┌──────────┐      ┌──────────────┐      │
│  │  Users   │◄────►│   Bot    │◄────►│  PostgreSQL  │      │
│  │ (Telegram)│      │ (Python) │      │  Database    │      │
│  └──────────┘      └──────────┘      └──────────────┘      │
│       │                  │                                    │
│       │                  │                                    │
│       ▼                  ▼                                    │
│  ┌──────────┐      ┌──────────┐                             │
│  │ Telegram │      │  Admin   │                             │
│  │  Stars   │      │  Users   │                             │
│  └──────────┘      └──────────┘                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 📝 User Registration Flow

```
User Opens Bot
      │
      ▼
  /start command
      │
      ▼
Check Username ──► No Username? ──► Block & Show Error
      │                                     │
      │ Has Username                        │
      ▼                                     │
Create User Record                          │
      │                                     │
      ▼                                     │
Show Welcome Message ◄──────────────────────┘
      │
      ▼
User Registered ✅
```

## 🔗 Link Submission Flow

```
User: /submit_link
      │
      ▼
┌─────────────────────┐
│ Choose Payment:     │
│ 1. Pay 15 ⭐        │
│ 2. Use Free Slot    │
└─────────────────────┘
      │
      ├──────────────────┬──────────────────┐
      │                  │                  │
      ▼                  ▼                  ▼
  Pay 15 ⭐        Use Free Slot      Cancel
      │                  │
      │                  ▼
      │         Check Free Slots
      │                  │
      │                  ├──► No Slots? ──► Error
      │                  │
      │                  ▼
      │         Decrement Counter
      │                  │
      └──────────────────┘
                │
                ▼
        Select Category
                │
                ▼
        Enter Service Name
                │
                ▼
           Enter URL
                │
                ▼
        Enter Description
                │
                ├──────────────┬──────────────┐
                │              │              │
                ▼              ▼              ▼
         Paid Method    Free Method      Cancel
                │              │
                ▼              │
        Send Invoice           │
                │              │
                ▼              │
        User Pays              │
                │              │
                └──────────────┘
                        │
                        ▼
                Create Link Record
                        │
                        ▼
                Show Confirmation
                        │
                        ▼
                Link Active ✅
```

## 🎁 Claim Submission Flow

```
User: /claim_reward
      │
      ▼
Browse Categories
      │
      ▼
Select Category
      │
      ▼
Get Available Links ──► No Links? ──► Show Error
      │
      ▼
Show Services List
      │
      ▼
User Selects Service
      │
      ▼
Check Availability
      │
      ├──► Max Claims Reached? ──► Error
      │
      ├──► Already Claimed? ──► Error
      │
      ▼
Show Link Details
      │
      ▼
User Uploads Screenshot
      │
      ▼
Create Claim Record
(status: pending)
      │
      ├──────────────────┬──────────────────┐
      │                  │                  │
      ▼                  ▼                  ▼
Notify Admins    Save Screenshot    Notify User
      │                                     │
      │                                     ▼
      │                          "Pending Review"
      │
      ▼
Admin Reviews
```

## 👨‍💼 Admin Approval Flow

```
Admin Receives Notification
      │
      ▼
┌─────────────────────────┐
│ Claim Details:          │
│ - User                  │
│ - Service               │
│ - Screenshot            │
└─────────────────────────┘
      │
      ▼
Admin Decision
      │
      ├──────────────────┬──────────────────┐
      │                  │                  │
      ▼                  ▼                  ▼
  /approve          /reject            Ignore
      │                  │
      │                  ▼
      │         Update Status: rejected
      │                  │
      │                  ▼
      │         Notify User: Rejected
      │                  │
      │                  ▼
      │              [END]
      │
      ▼
Update Status: approved
      │
      ▼
Increment User Claims
      │
      ▼
Increment Link Used Claims
      │
      ▼
Check Total Claims
      │
      ├──────────────┬──────────────┬──────────────┐
      │              │              │              │
      ▼              ▼              ▼              ▼
  Claims 1-2    Claim 3      Claims 4+       Error
      │              │              │
      ▼              ▼              ▼
Show Progress  Grant Free    Send 1 ⭐
   "X/3"       Submission     Invoice
      │              │              │
      │              ▼              ▼
      │      "Unlocked!"    User Receives
      │                         Star
      │              │              │
      └──────────────┴──────────────┘
                     │
                     ▼
              Notify User
                     │
                     ▼
              Claim Complete ✅
```

## 💰 Payment Flow (Link Submission)

```
User Chooses "Pay 15 ⭐"
      │
      ▼
Bot Creates Invoice
      │
      ├─────────────────────────┐
      │                         │
      │  Title: Submit Link     │
      │  Amount: 15 Stars       │
      │  Currency: XTR          │
      │  Provider: (empty)      │
      │                         │
      └─────────────────────────┘
      │
      ▼
Send Invoice to User
      │
      ▼
User Sees Payment Screen
      │
      ├──────────────┬──────────────┐
      │              │              │
      ▼              ▼              ▼
   Pay          Cancel         Timeout
      │              │              │
      │              └──────────────┘
      │                     │
      ▼                     ▼
Pre-Checkout Query      [END]
      │
      ▼
Validate Payment
      │
      ▼
User Confirms
      │
      ▼
Payment Successful
      │
      ▼
Create Link Record
      │
      ▼
Notify User: Success ✅
```

## ⭐ Reward Flow (Claim Approval)

```
Admin Approves Claim
      │
      ▼
Check User's Total Claims
      │
      ├──────────────┬──────────────┬──────────────┐
      │              │              │              │
      ▼              ▼              ▼              ▼
  Claim 1       Claim 2       Claim 3      Claim 4+
      │              │              │              │
      ▼              ▼              ▼              ▼
No Reward      No Reward    Grant Free    Send 1 ⭐
                            Submission     Invoice
      │              │              │              │
      ▼              ▼              ▼              ▼
"1/3 claims"  "2/3 claims"  "3/3 - Free   Bot Creates
                            Unlocked!"     Invoice
      │              │              │              │
      │              │              │              ▼
      │              │              │      User Receives
      │              │              │      Payment Screen
      │              │              │              │
      │              │              │              ▼
      │              │              │      User Accepts
      │              │              │              │
      │              │              │              ▼
      │              │              │      Payment to User
      │              │              │              │
      │              │              │              ▼
      │              │              │      Mark Rewarded
      │              │              │              │
      └──────────────┴──────────────┴──────────────┘
                                    │
                                    ▼
                            Notify User ✅
```

## 🔄 Complete User Journey

```
DAY 1: Registration & First Claim
┌────────────────────────────────────────┐
│ 1. User: /start                        │
│    Bot: Welcome! (0/3 claims)          │
│                                        │
│ 2. User: /browse                       │
│    Bot: Shows categories               │
│                                        │
│ 3. User: Selects service               │
│    Bot: Shows link details             │
│                                        │
│ 4. User: Completes sign-up             │
│    User: /claim_reward                 │
│    User: Uploads screenshot            │
│    Bot: Claim pending                  │
│                                        │
│ 5. Admin: /approve 1                   │
│    Bot: Claim approved! (1/3)          │
└────────────────────────────────────────┘

DAY 2-3: More Claims
┌────────────────────────────────────────┐
│ 6. User: /claim_reward (2nd time)      │
│    Admin: /approve 2                   │
│    Bot: Claim approved! (2/3)          │
│                                        │
│ 7. User: /claim_reward (3rd time)      │
│    Admin: /approve 3                   │
│    Bot: 3/3 - Free submission! 🎉      │
└────────────────────────────────────────┘

DAY 4: Free Submission
┌────────────────────────────────────────┐
│ 8. User: /my_status                    │
│    Bot: 3/3 claims, 1 free submission  │
│                                        │
│ 9. User: /submit_link                  │
│    User: Selects "Use Free Slot"       │
│    User: Enters link details           │
│    Bot: Link submitted! ✅             │
└────────────────────────────────────────┘

DAY 5+: Earning Stars
┌────────────────────────────────────────┐
│ 10. User: /claim_reward (4th time)     │
│     Admin: /approve 4                  │
│     Bot: You earned 1 ⭐!              │
│     User: Accepts payment              │
│     Bot: Star received! ✅             │
│                                        │
│ 11. User: /claim_reward (5th time)     │
│     Admin: /approve 5                  │
│     Bot: You earned 1 ⭐!              │
│     [Repeat...]                        │
└────────────────────────────────────────┘
```

## 🗄️ Database Interaction Flow

```
User Action
      │
      ▼
Bot Handler
      │
      ▼
Database Function
      │
      ├──────────────────┬──────────────────┬──────────────────┐
      │                  │                  │                  │
      ▼                  ▼                  ▼                  ▼
  users table    referral_links    claims table    Transaction
                     table
      │                  │                  │                  │
      ▼                  ▼                  ▼                  ▼
  SELECT/           INSERT/           INSERT/              COMMIT/
  UPDATE            UPDATE            UPDATE               ROLLBACK
      │                  │                  │                  │
      └──────────────────┴──────────────────┴──────────────────┘
                                    │
                                    ▼
                            Return Result
                                    │
                                    ▼
                            Bot Handler
                                    │
                                    ▼
                            User Response
```

## 🔐 Security Flow

```
User Request
      │
      ▼
Check Username ──► No Username? ──► Block
      │
      ▼ Has Username
Check Command Type
      │
      ├──────────────────┬──────────────────┐
      │                  │                  │
      ▼                  ▼                  ▼
User Command      Admin Command      Unknown
      │                  │                  │
      ▼                  ▼                  ▼
Process           Check Admin ID     Ignore
                        │
                        ├──► Not Admin? ──► Deny
                        │
                        ▼ Is Admin
                  Process Command
                        │
                        ▼
                  Execute Action
                        │
                        ▼
                Database Query
                (Parameterized)
                        │
                        ▼
                  Return Result
```

## 📊 State Management Flow

```
User Starts Conversation
      │
      ▼
ConversationHandler
      │
      ├──────────────────┬──────────────────┬──────────────────┐
      │                  │                  │                  │
      ▼                  ▼                  ▼                  ▼
Submit Link Flow   Claim Flow      Browse Flow      Status Check
      │                  │                  │                  │
      ▼                  ▼                  ▼                  ▼
State: PAYMENT    State: CATEGORY   No State      No State
      │                  │           (One-shot)   (One-shot)
      ▼                  ▼
State: CATEGORY   State: SERVICE
      │                  │
      ▼                  ▼
State: SERVICE    State: SCREENSHOT
      │                  │
      ▼                  ▼
State: URL        End Conversation
      │
      ▼
State: DESCRIPTION
      │
      ▼
End Conversation
      │
      ▼
Clear User Data
```

## 🎯 Error Handling Flow

```
User Action
      │
      ▼
Try Execute
      │
      ├──────────────────┬──────────────────┐
      │                  │                  │
      ▼                  ▼                  ▼
  Success          Exception          Validation Error
      │                  │                  │
      ▼                  ▼                  ▼
Return Result     Log Error         Show Error Message
      │                  │                  │
      ▼                  ▼                  ▼
Show Success      Rollback DB       Retry/Cancel
      │                  │                  │
      │                  ▼                  │
      │         Show Error Message          │
      │                  │                  │
      └──────────────────┴──────────────────┘
                         │
                         ▼
                  Continue/End
```

## 🔄 Claim Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                    CLAIM LIFECYCLE                       │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Created ──► Pending ──► Approved ──► Rewarded          │
│                  │                                        │
│                  └──────► Rejected                       │
│                                                           │
└─────────────────────────────────────────────────────────┘

Details:

1. CREATED
   - User submits claim
   - Screenshot uploaded
   - Status: pending
   - Rewarded: false

2. PENDING
   - Admin notified
   - Awaiting review
   - Can be approved or rejected

3. APPROVED
   - Admin approves
   - User claims incremented
   - Link claims incremented
   - Status: approved

4. REWARDED (if applicable)
   - Stars sent (if 4+ claims)
   - Rewarded: true
   - Complete

5. REJECTED
   - Admin rejects
   - User notified
   - Status: rejected
   - No rewards
```

## 📈 Link Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                    LINK LIFECYCLE                        │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Submitted ──► Active ──► Partial ──► Full              │
│                                                           │
└─────────────────────────────────────────────────────────┘

Details:

1. SUBMITTED
   - User pays or uses free slot
   - Link created
   - used_claims: 0
   - max_claims: 5

2. ACTIVE
   - Available for claims
   - Shown in browse
   - used_claims < max_claims

3. PARTIAL
   - Some claims used
   - Still accepting claims
   - 0 < used_claims < max_claims

4. FULL
   - Max claims reached
   - No longer shown
   - used_claims = max_claims
```

## 🎊 Summary Flow

```
┌─────────────────────────────────────────────────────────┐
│                  REFLOOP BOT FLOW                        │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Users ──► Register ──► Browse/Claim ──► Submit Links   │
│              │              │                │            │
│              │              ▼                │            │
│              │         Screenshot            │            │
│              │              │                │            │
│              │              ▼                │            │
│              │         Admin Review          │            │
│              │              │                │            │
│              │              ▼                │            │
│              │         Approve/Reject        │            │
│              │              │                │            │
│              │              ▼                │            │
│              │         Update Stats          │            │
│              │              │                │            │
│              │              ▼                │            │
│              │         Send Rewards          │            │
│              │              │                │            │
│              └──────────────┴────────────────┘            │
│                             │                             │
│                             ▼                             │
│                      Repeat Cycle                         │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

**Visual Guide Complete!** 📊

These diagrams show the complete flow of the RefLoop bot system. Use them to understand how all components work together.

For implementation details, see the code in `bot.py` and `database.py`.
