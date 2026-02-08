# UPI QR Code Detection Logic - FIXED ✅

## Problem Statement
Previous logic was incorrectly flagging ALL UPI QR codes with embedded amounts as "PAYMENT REQUEST" (dangerous), even normal receive QR codes.

## Correct Logic (Now Implemented)

### Case 1: Payment REQUEST - 🚨 HIGH RISK (Dangerous)
**Indicators:**
- `mode=02` (collect request mode)
- `intent=collect` 
- `type=collect`

**Example:**
```
upi://pay?pa=scammer@paytm&pn=Scammer&am=5000&mode=02
```

**Risk Score:** +5 (HIGH RISK)

**Message:**
- "🚨 PAYMENT REQUEST: ₹5000 मांगा जा रहा है!"
- "⚠️ यह खतरनाक है! Agar pay karenge to ₹5000 aapke account se jayega!"

---

### Case 2: Normal Receive QR with EMBEDDED AMOUNT - ⚠️ MEDIUM RISK (Suspicious)
**Indicators:**
- Has `pa=` and `pn=` (normal UPI)
- Has `am=` (amount pre-filled)
- NO `mode=02` or collect indicators

**Example:**
```
upi://pay?pa=merchant@paytm&pn=Shop&am=500
```

**Risk Score:** +2 (MEDIUM RISK)

**Message:**
- "⚠️ Amount pre-filled: ₹500"
- "💡 Dhyan se check karein - Amount pehle se set hai!"
- "✅ Agar aap jaante ho ki yeh kitna hona chahiye, to safe hai"

**Why Suspicious?**
- Amount already set - user cannot change it
- Could be legitimate (merchant QR) or scam (fake amount)
- User should verify the amount is correct

---

### Case 3: Normal Receive QR WITHOUT Amount - ✅ SAFE (No Risk)
**Indicators:**
- Has `pa=` and `pn=` (normal UPI)
- NO `am=` (no amount)
- NO `mode=02` or collect indicators

**Example:**
```
upi://pay?pa=merchant@paytm&pn=MyShop
```

**Risk Score:** 0 (SAFE)

**Message:**
- "✅ Normal UPI receive QR - Safe for collecting payments"
- "💚 Koi amount pre-filled nahi hai - Aap khud amount enter kar sakte ho"

**Why Safe?**
- User enters amount themselves
- Standard merchant/personal receive QR
- No pre-filled amount to trick user

---

## Code Changes Made

### 1. Updated `detect_upi_payment_direction()` function
**File:** `app_simple.py`

**Key Changes:**
- Separated payment REQUEST detection (mode=02) from amount detection
- Normal receive QR with amount → NOT flagged as payment request
- Only `mode=02`, `intent=collect`, `type=collect` → flagged as payment request

### 2. Updated Risk Scoring Logic
**Files:** `app_simple.py` (2 endpoints)

**Risk Scores:**
- Payment REQUEST: +5 (HIGH RISK)
- Receive QR with amount: +2 (MEDIUM RISK)
- Receive QR without amount: 0 (SAFE)

---

## Examples

### ✅ SAFE - Normal Merchant QR
```
upi://pay?pa=shop@paytm&pn=MyShop
```
→ User enters amount → SAFE

### ⚠️ SUSPICIOUS - Pre-filled Amount
```
upi://pay?pa=shop@paytm&pn=MyShop&am=500
```
→ Amount already set → Check if correct

### 🚨 DANGEROUS - Payment Request
```
upi://pay?pa=scammer@paytm&pn=Scammer&am=5000&mode=02
```
→ Requesting money → DANGEROUS!

---

## Testing

Test with these QR codes:

1. **Safe:** `upi://pay?pa=test@paytm&pn=TestShop`
2. **Suspicious:** `upi://pay?pa=test@paytm&pn=TestShop&am=100`
3. **Dangerous:** `upi://pay?pa=test@paytm&pn=TestShop&am=100&mode=02`

---

## User Education

**Key Message:**
- Normal UPI receive QR (without amount) = SAFE ✅
- UPI receive QR with amount = Check amount carefully ⚠️
- Payment REQUEST (mode=02) = NEVER pay! 🚨

---

**Date:** February 7, 2026
**Status:** ✅ FIXED AND TESTED
