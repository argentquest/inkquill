# Google Analytics Integration Guide

This document explains how to set up and use Google Analytics 4 (GA4) with GDPR-compliant Consent Mode for the AI Storytelling Assistant application.

## Setup Instructions

### 1. Create Google Analytics Property

1. Go to [Google Analytics](https://analytics.google.com/)
2. Create a new GA4 property for your website
3. Get your Measurement ID (format: `G-XXXXXXXXXX`)

### 2. Configure Environment Variable

Add your Google Analytics Measurement ID to your environment configuration:

#### For Development (.env file):
```bash
GOOGLE_ANALYTICS_ID="G-XXXXXXXXXX"
GOOGLE_ANALYTICS_CONSENT_MODE=true
COOKIE_CONSENT_REQUIRED=true
```

#### For Production (Azure App Service):
Set the environment variables in your App Service configuration:
- `GOOGLE_ANALYTICS_ID`: `G-XXXXXXXXXX`
- `GOOGLE_ANALYTICS_CONSENT_MODE`: `true`
- `COOKIE_CONSENT_REQUIRED`: `true`

### 3. Restart Application

After setting the environment variable, restart your application for the changes to take effect.

## Features Included

### GDPR-Compliant Consent Mode
- **Cookie Consent Banner**: Appears for new users, respects previous choices
- **Google Consent Mode**: Properly configured for EU privacy compliance
- **Granular Controls**: Users can accept all, necessary only, or custom preferences
- **Persistent Choices**: Consent preferences saved in browser localStorage
- **Privacy-First**: Analytics denied by default until user consent

### Automatic Page Tracking
- All page views are automatically tracked (with user consent)
- Page titles and URLs are captured
- User sessions and engagement metrics are recorded
- IP anonymization enabled when consent mode is active

### Custom Event Tracking
The integration includes predefined custom events for key user actions:

#### Authentication Events
- `login_modal_click` - User clicks login from auth required modal
- `register_modal_click` - User clicks register from auth required modal

#### Feature Usage Events
- `worlds.auth_required` - User tries to access world features without login
- `stories.auth_required` - User tries to create stories without login
- `story_list.auth_required` - User tries to access story list without login

#### AI Interaction Events
- Custom tracking for AI feature usage (ready for implementation)

### JavaScript Functions Available

The following global functions are available for custom tracking:

```javascript
// Track authentication-related events (consent-aware)
trackAuthEvent('login', 'modal_click');
trackAuthEvent('register', 'homepage_button');

// Track feature usage (consent-aware)
trackFeatureUse('world_creation', 'started');
trackFeatureUse('story_generation', 'completed');

// Track AI interactions (consent-aware)
trackAIInteraction('act_generation', 'gpt-4o');
trackAIInteraction('world_import', 'text-embedding-3-large');

// Cookie consent management
showCookiePreferences();           // Show consent modal
resetCookieConsent();             // Reset consent for testing
getCookieConsentStatus();         // Get current consent status
grantAnalyticsConsent();          // Programmatically grant consent
denyAnalyticsConsent();           // Programmatically deny consent
```

**Note**: All tracking functions automatically check for user consent before sending data to Google Analytics.

## Implementation Details

### Template Integration
- Google Analytics code is automatically included in `layouts/base.html`
- Only loads when `GOOGLE_ANALYTICS_ID` is configured
- No impact on performance if not configured

### Configuration
- Settings managed in `app/core/config.py`
- Environment variable: `GOOGLE_ANALYTICS_ID`
- Supports both development and production environments

### Privacy Considerations
- **GDPR Compliant**: Full Google Consent Mode v2 implementation
- **Privacy by Design**: Analytics denied by default until user consent
- **Transparent**: Clear cookie consent banner with detailed explanations
- **User Control**: Granular consent options (necessary vs analytics cookies)
- **Persistent**: User choices remembered across sessions
- **Revocable**: Users can change preferences at any time via footer link
- **No Personal Data**: Custom events don't track personal information
- **IP Anonymization**: Enabled when consent mode is active

## Verification

### 1. Check Configuration
Look for this log message during application startup:
```
Google Analytics: Enabled, Consent Mode: Enabled
```

### 2. Test Cookie Consent Banner
1. Open your application in incognito/private browsing mode
2. Cookie consent banner should appear after 1 second
3. Test both "Accept All" and "Necessary Only" options
4. Verify preferences are saved (banner doesn't reappear on refresh)

### 3. Browser Developer Tools
1. Open browser developer tools
2. Go to Network tab
3. Visit your application
4. Look for requests to `googletagmanager.com`
5. Check Console for consent-related messages

### 4. Test Consent Mode
1. Deny analytics cookies
2. Check Console - tracking functions should log "Analytics consent required"
3. Accept analytics cookies
4. Tracking should work normally

### 5. Google Analytics Dashboard
1. Go to your GA4 property
2. Check "Realtime" reports
3. Visit your application to see live traffic

## Troubleshooting

### Google Analytics Not Loading
1. Verify `GOOGLE_ANALYTICS_ID` is set correctly
2. Check application logs for configuration errors
3. Ensure the Measurement ID format is correct (`G-XXXXXXXXXX`)

### Events Not Appearing
1. Events may take 24-48 hours to appear in reports
2. Use "Realtime" reports for immediate verification
3. Check browser console for JavaScript errors

### Development vs Production
- Use separate GA4 properties for development and production
- Set different `GOOGLE_ANALYTICS_ID` values for each environment
- Consider filtering out internal traffic in production

## Configuration Options

### Environment Variables
```bash
# Required: Your Google Analytics 4 Measurement ID
GOOGLE_ANALYTICS_ID="G-XXXXXXXXXX"

# Optional: Enable Google Consent Mode (default: true)
GOOGLE_ANALYTICS_CONSENT_MODE=true

# Optional: Show cookie consent banner (default: true)
COOKIE_CONSENT_REQUIRED=true
```

### Consent Mode Behavior
- **`GOOGLE_ANALYTICS_CONSENT_MODE=true`**: Full GDPR compliance, consent required
- **`GOOGLE_ANALYTICS_CONSENT_MODE=false`**: Analytics always enabled (not recommended for EU)
- **`COOKIE_CONSENT_REQUIRED=false`**: No consent banner, respects consent mode setting

### Recommended Configurations

#### Production (EU/GDPR Required)
```bash
GOOGLE_ANALYTICS_ID="G-PROD12345"
GOOGLE_ANALYTICS_CONSENT_MODE=true
COOKIE_CONSENT_REQUIRED=true
```

#### Development/Testing
```bash
GOOGLE_ANALYTICS_ID="G-DEV12345"
GOOGLE_ANALYTICS_CONSENT_MODE=true
COOKIE_CONSENT_REQUIRED=true
```

#### Internal/Admin Use (No Consent Required)
```bash
GOOGLE_ANALYTICS_ID="G-INTERNAL12345"
GOOGLE_ANALYTICS_CONSENT_MODE=false
COOKIE_CONSENT_REQUIRED=false
```

## Best Practices

1. **Separate Properties**: Use different GA4 properties for dev/staging/production
2. **Consent Mode**: Always enable for public-facing applications
3. **Privacy**: Respect user privacy and comply with applicable regulations
4. **Performance**: GA4 loads asynchronously and won't block page rendering
5. **Testing**: Use GA4's real-time reports to verify tracking implementation
6. **Transparency**: Clearly explain what data you collect and why

## Future Enhancements

Consider adding tracking for:
- AI feature usage (story generation, world building)
- User engagement metrics (time on features, completion rates)
- Conversion funnels (signup → first story → continued usage)
- Error tracking and user experience issues

---

For technical support, check the application logs and Google Analytics documentation.