# 🧪 Testing Guide - Unauthorized Surveillance System

## ✅ Server Status: RUNNING
- URL: http://localhost:5001
- All endpoints active and working

---

## 🎯 Test 1: Unauthorized Access Flow (5 Attempts)

### Steps:
1. **Open Login Page**:
   ```
   http://localhost:5001/admin/login
   ```

2. **Attempt 1-2** (Normal Failures):
   - Username: `wrong_user`
   - Password: `wrong_pass`
   - Click "Next: Face Recognition →"
   - **Expected**: Error message + voice alert "Unauthorized access attempt detected."

3. **Attempt 3** (Warning Triggered):
   - Try again with wrong credentials
   - **Expected**: 
     - Error message: "❌ Invalid credentials (Attempt 3/5)"
     - Voice alert: "Warning! Multiple unauthorized attempts detected. You are being monitored."

4. **Attempt 4** (Continue):
   - Try again
   - **Expected**: Warning continues

5. **Attempt 5** (Photo Capture + Surveillance):
   - Try again with wrong credentials
   - **Expected**:
     - ✅ Photo automatically captured from webcam
     - ✅ Full-screen surveillance warning appears
     - ✅ Voice alert: "Security alert. You are under surveillance..."
     - ✅ Auto-redirect after 5 seconds
     - ✅ Verify button disabled

6. **Check Logs**:
   ```bash
   # Check if photo was saved
   ls -la whatsapp-qr-security-bot/data/unauthorized_attempts/
   
   # Check log file
   cat whatsapp-qr-security-bot/data/unauthorized_attempts/attempts_log.json
   ```
   
   **Expected Log Entry**:
   ```json
   {
     "timestamp": "2026-02-07T...",
     "photo": "unauthorized_20260207_HHMMSS.jpg",
     "ip_address": "127.0.0.1",
     "user_agent": "Mozilla/5.0...",
     "total_attempts": 5,
     "status": "BLOCKED",
     "severity": "HIGH",
     "action_taken": "Photo captured, access denied, session terminated"
   }
   ```

---

## 🎯 Test 2: Admin Dashboard Display

### Steps:
1. **Login as Admin**:
   - Go to: http://localhost:5001/admin/login
   - Username: `piyush69`
   - Password: `admin123`
   - Complete face recognition (Step 2)

2. **View Dashboard**:
   - Go to: http://localhost:5001/admin
   - Scroll down to "🚨 Unauthorized Access Attempts" section

3. **Verify Display**:
   - ✅ Photo is displayed (160px height)
   - ✅ Full timestamp with date, time, seconds
   - ✅ IP address shown
   - ✅ Total attempts: **5**
   - ✅ Status badge: **BLOCKED** (gray)
   - ✅ Severity badge: **HIGH** (red)
   - ✅ Action taken description displayed
   - ✅ Card design is compact and neat (280px width)
   - ✅ Hover effect works (elevation + shadow)

---

## 🎯 Test 3: Case 2 Update (Impact Section)

### Steps:
1. **Open Homepage**:
   ```
   http://localhost:5001/
   ```

2. **Scroll to Impact Section**:
   - Find "असली घटनाएं - जो आपके साथ भी हो सकती हैं"
   - Locate **Case 2**: "सुनीता देवी - ₹4.8 Lakh Phone Scam"

3. **Verify Content**:
   - ✅ Title: "Phone Scam" (NOT "Digital Arrest")
   - ✅ Description mentions:
     - "phone call" (not video call)
     - "AI-generated voice" (not deepfake video)
     - "Voice deepfake था"
   - ✅ Solution mentions:
     - "Voice Fraud Detector"
     - "AI-generated voice पकड़ ली होती"
     - "Deepfake voice detected"
   - ✅ Source: "📰 Dainik Jagran, March 2024"

4. **Test Language Switching**:
   - Click language selector (top-right)
   - Test all 8 languages:
     - Hindi ✅
     - English ✅
     - Hinglish ✅
     - Gujarati ✅
     - Tamil ✅
     - Telugu ✅
     - Bengali ✅
     - Marathi ✅
   - Verify Case 2 is correctly translated in each language

---

## 🎯 Test 4: Complete Integration Test

### Full Flow:
1. **Trigger Unauthorized Attempts** (5 times)
2. **Verify Photo Capture** (check file system)
3. **Verify Complete Logging** (check JSON file)
4. **Login as Admin**
5. **View Dashboard**
6. **Verify All Details Displayed**
7. **Check Homepage Case 2**
8. **Test All Languages**

---

## ✅ Expected Results Summary

### Unauthorized Access System:
- ✅ Attempt tracking (1-5)
- ✅ Warning on 3rd attempt
- ✅ Photo capture on 5th attempt
- ✅ Complete logging with all details
- ✅ Admin dashboard displays everything
- ✅ Compact, neat, professional design

### Case 2 Update:
- ✅ Changed from "Digital Arrest" to "Phone Scam"
- ✅ Changed from video call to phone call
- ✅ Changed from deepfake video to AI-generated voice
- ✅ Solution mentions Voice Fraud Detector
- ✅ All 8 languages updated

---

## 🚨 Troubleshooting

### If Photo Not Captured:
- Check browser camera permissions
- Ensure webcam is connected
- Check browser console for errors

### If Log Not Saved:
- Check `data/unauthorized_attempts/` folder exists
- Check file permissions
- Check Flask server logs

### If Admin Dashboard Not Showing:
- Verify you're logged in as admin
- Check browser console for errors
- Refresh the page
- Check `/api/admin/unauthorized-attempts` endpoint

---

## 📊 Success Criteria

All tests pass when:
1. ✅ 5 failed attempts trigger photo capture
2. ✅ Complete log entry saved with all details
3. ✅ Admin dashboard shows all information
4. ✅ Card design is compact and neat
5. ✅ Case 2 mentions Phone Scam (not Digital Arrest)
6. ✅ Case 2 mentions AI voice (not video)
7. ✅ All 8 languages work correctly

---

## 🎉 Ready for Testing!

Server is running at: **http://localhost:5001**

Start with Test 1 (Unauthorized Access Flow) to see the complete system in action!
