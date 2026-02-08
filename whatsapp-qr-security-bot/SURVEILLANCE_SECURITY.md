# Professional Surveillance Security System

## What Changed

### ❌ Removed:
- Funny "Mat Kar Lala" meme
- Casual voice alerts
- Humorous elements

### ✅ Added:
- Professional security system
- Failed attempt tracking
- Photo capture and logging
- Surveillance warning
- Automatic lockout

---

## How It Works Now

### Attempt 1-2 (Warning Phase):
```
User tries face verification
   ↓
Face doesn't match
   ↓
🔊 Voice: "Unauthorized access attempt detected."
   ↓
❌ Status: "Face not matched (Attempt 1/3)"
   ↓
Can try again
```

### Attempt 3 (Lockout Phase):
```
User tries 3rd time
   ↓
Face doesn't match
   ↓
📸 PHOTO CAPTURED automatically
   ↓
💾 Saved to: data/unauthorized_attempts/
   ↓
🚨 BIG WARNING appears:
   "YOU ARE UNDER SURVEILLANCE"
   ↓
🔒 Login disabled for 5 seconds
   ↓
↩️ Auto-redirect to login page
```

---

## Surveillance Warning Screen

### What User Sees:
```
🚨
SECURITY ALERT

⚠️ YOU ARE UNDER SURVEILLANCE ⚠️

Multiple unauthorized access attempts detected
Your photo has been captured and logged

⚡ Security Measures Activated:
✓ Photo captured and saved
✓ Timestamp recorded
✓ Admin will be notified
✓ IP address logged

Redirecting in 5 seconds...
```

### Voice Alert:
```
"Security alert. You are under surveillance. 
Multiple unauthorized access attempts detected."
```

---

## What Gets Logged

### Photo Storage:
```
data/unauthorized_attempts/
├── unauthorized_20260207_115230.jpg
├── unauthorized_20260207_120145.jpg
└── attempts_log.json
```

### Log File (attempts_log.json):
```json
[
  {
    "timestamp": "2026-02-07T11:52:30.123456",
    "photo": "unauthorized_20260207_115230.jpg",
    "ip_address": "127.0.0.1",
    "user_agent": "Mozilla/5.0..."
  }
]
```

---

## Security Features

| Feature | Status | Details |
|---------|--------|---------|
| **Attempt Tracking** | ✅ Active | Counts 1, 2, 3 attempts |
| **Photo Capture** | ✅ Active | After 3rd failed attempt |
| **Timestamp Logging** | ✅ Active | ISO format with milliseconds |
| **IP Logging** | ✅ Active | Records requester IP |
| **User Agent** | ✅ Active | Browser/device info |
| **Auto Lockout** | ✅ Active | 5-second delay + redirect |
| **Voice Warning** | ✅ Active | Professional alert |
| **Visual Warning** | ✅ Active | Full-screen surveillance notice |

---

## Testing Instructions

### Test 1: Your Face (Should Work)
1. Go to: `http://localhost:5001/admin/login`
2. Enter: `piyush69` / `admin123`
3. Verify your face
4. **Expected:**
   - Voice: "You are authorized. Welcome admin."
   - Login successful ✅

### Test 2: Wrong Face (Should Trigger Security)
1. Ask someone else to try
2. They enter credentials
3. They try face verification 3 times
4. **Expected:**
   - Attempt 1: "Unauthorized... (Attempt 1/3)"
   - Attempt 2: "Unauthorized... (Attempt 2/3)"
   - Attempt 3: 
     - 📸 Photo captured
     - 🚨 "YOU ARE UNDER SURVEILLANCE" screen
     - 🔊 Voice warning
     - 🔒 Lockout for 5 seconds
     - ↩️ Redirect to login

---

## Check Logged Attempts

### View Photos:
```bash
cd whatsapp-qr-security-bot
ls -lh data/unauthorized_attempts/
```

### View Log:
```bash
cat data/unauthorized_attempts/attempts_log.json
```

### Example Output:
```json
[
  {
    "timestamp": "2026-02-07T11:52:30.456789",
    "photo": "unauthorized_20260207_115230.jpg",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
  }
]
```

---

## Admin Dashboard Integration

The logged attempts can be viewed in admin dashboard:
- Total unauthorized attempts
- Photos of intruders
- Timestamps
- IP addresses

(Future enhancement: Add to admin dashboard UI)

---

## Security Flow Diagram

```
┌─────────────────────────────────────┐
│  User Tries Face Verification      │
└──────────────┬──────────────────────┘
               │
               ▼
        ┌──────────────┐
        │ Face Match?  │
        └──────┬───────┘
               │
       ┌───────┴────────┐
       │                │
    YES│                │NO
       │                │
       ▼                ▼
  ┌─────────┐    ┌──────────────┐
  │ SUCCESS │    │ Attempt++    │
  │ Login   │    │ Show Warning │
  └─────────┘    └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Attempt >= 3?│
                 └──────┬───────┘
                        │
                ┌───────┴────────┐
                │                │
             YES│                │NO
                │                │
                ▼                ▼
         ┌──────────────┐  ┌─────────┐
         │ 📸 Capture   │  │ Try     │
         │ 💾 Log       │  │ Again   │
         │ 🚨 Warning   │  └─────────┘
         │ 🔒 Lockout   │
         └──────────────┘
```

---

## Current Status

✅ **COMPLETE** - Professional surveillance system active
✅ **SECURE** - 3-attempt limit with photo capture
✅ **LOGGED** - All unauthorized attempts recorded
✅ **WARNING** - Big surveillance alert after 3 attempts

**Test at:** `http://localhost:5001/admin/login`
