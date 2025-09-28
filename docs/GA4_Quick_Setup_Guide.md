# GA4 Quick Setup Guide - Essential Steps

This is a condensed version focusing on the most important setup steps to get your enhanced tracking working in GA4.

## 🚀 Quick Start (15 minutes)

### 1️⃣ Enable User-ID (2 minutes)
```
Admin → Data Streams → Your Web Stream → Configure tag settings → User-ID → Toggle ON
```

### 2️⃣ Create Essential Custom Dimensions (5 minutes)

Go to: **Admin → Custom definitions → Create custom dimension**

| Dimension Name | Scope | Parameter Name |
|----------------|-------|----------------|
| User Type | User | user_type |
| Story ID | Event | story_id |
| AI Model Used | Event | ai_model |
| Action Type | Event | action_type |

### 3️⃣ Create Key Custom Metrics (3 minutes)

Go to: **Admin → Custom definitions → Create custom metric**

| Metric Name | Scope | Parameter Name | Unit |
|-------------|-------|----------------|------|
| AI Token Count | Event | token_count | Standard |
| AI Estimated Cost | Event | estimated_cost | Currency |

### 4️⃣ Mark Conversions (2 minutes)

Go to: **Admin → Events**

Toggle "Mark as conversion" for:
- `signup`
- `story_publish`
- `world_create`

### 5️⃣ Test with DebugView (3 minutes)

1. Add `?_dbg=1` to your site URL
2. Open **Admin → DebugView** in GA4
3. Perform actions on your site
4. Verify events appear with parameters

---

## 📊 Essential Reports to Create

### Report 1: User Activity Overview
```
Dimensions: User ID, User Type, Date
Metrics: Active users, Event count, Engagement time
```

### Report 2: AI Usage Summary
```
Dimensions: AI Model Used, User Type
Metrics: Event count, AI Token Count (sum), AI Estimated Cost (sum)
```

### Report 3: Content Creation
```
Dimensions: Event name (filtered: story_create, story_publish)
Metrics: Event count, Users
```

---

## ✅ Verification Checklist

After setup, verify these work:

1. **User Tracking**
   - Login to your app
   - Check DebugView shows your user_id
   - Check user_type appears in user properties

2. **Event Tracking**
   - Create a story
   - Check `story_create` event appears
   - Verify story_id parameter is included

3. **AI Tracking**
   - Use any AI feature
   - Check `ai_interaction` event appears
   - Verify token_count and ai_model parameters

---

## 🎯 What You Can Now Track

### User Insights
- Which users are most active
- Admin vs regular user behavior
- User retention by account age

### Content Analytics
- Most created story types
- Publishing rate
- Average story word count

### AI Usage
- Cost per user
- Most used AI models
- Token usage patterns

### Feature Adoption
- Which features are discovered
- Feature usage frequency
- User journey through features

---

## 🚨 Common Issues & Fixes

### "I don't see my custom dimensions"
→ **Fix**: Wait 24-48 hours after creation, GA4 needs time to process

### "User ID isn't showing"
→ **Fix**: Ensure you're logged in when testing, anonymous users won't have user_id

### "Events aren't appearing"
→ **Fix**: Check browser console for errors, disable ad blockers, verify measurement ID

### "DebugView is empty"
→ **Fix**: Add `?_dbg=1` to URL or use Chrome GA Debugger extension

---

## 📈 Next Steps

1. **Create Dashboards**: Build custom dashboards for different stakeholders
2. **Set Up Alerts**: Configure alerts for errors or unusual activity
3. **Export to BigQuery**: For advanced analysis and long-term storage
4. **Build Audiences**: Create remarketing audiences based on behavior

---

## 🔗 Useful Links

- [GA4 DebugView](https://support.google.com/analytics/answer/7201382)
- [Custom Dimensions Guide](https://support.google.com/analytics/answer/10075209)
- [User-ID Feature](https://support.google.com/analytics/answer/9213390)
- [GA4 Limits](https://support.google.com/analytics/answer/9267744)

---

## 💡 Pro Tips

1. **Test First**: Always test new tracking in DebugView before going live
2. **Document Everything**: Keep a spreadsheet of all custom events and parameters
3. **Stay Under Limits**: GA4 allows 50 custom event-scoped dimensions
4. **Use Consistent Naming**: Stick to snake_case for all parameters
5. **Monitor Data Quality**: Set up regular checks for data accuracy