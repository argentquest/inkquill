# Google Analytics 4 (GA4) Setup Instructions

This guide walks you through setting up GA4 to use the enhanced tracking implementation with user IDs and custom dimensions.

## Table of Contents
1. [Enable User-ID Reporting](#1-enable-user-id-reporting)
2. [Create Custom Dimensions](#2-create-custom-dimensions)
3. [Create Custom Metrics](#3-create-custom-metrics)
4. [Set Up Custom Events](#4-set-up-custom-events)
5. [Create Custom Reports](#5-create-custom-reports)
6. [Set Up Audiences](#6-set-up-audiences)
7. [Configure DebugView](#7-configure-debugview)
8. [Verify Implementation](#8-verify-implementation)

---

## 1. Enable User-ID Reporting

### Steps:
1. Go to your GA4 property
2. Click **Admin** (gear icon in bottom left)
3. Under **Property**, click **Data Streams**
4. Click on your web data stream
5. Click **Configure tag settings** (at the bottom)
6. Click **Show all** to see all settings
7. Click **User-ID**
8. Toggle **ON** the User-ID collection
9. Click **Save**

### Create User-ID Based Reporting Identity:
1. In Admin, under **Property**, click **Reporting Identity**
2. Select **Blended** (uses User-ID when available, then device-based)
3. Click **Save**

---

## 2. Create Custom Dimensions

### Navigate to Custom Definitions:
1. In GA4, go to **Admin**
2. Under **Property**, click **Custom definitions**

### User-Scoped Dimensions:
Create these dimensions for user properties:

#### Dimension 1: User Type
- Click **Create custom dimensions**
- **Dimension name**: User Type
- **Scope**: User
- **Description**: Whether user is admin or regular
- **User property**: user_type

#### Dimension 2: Account Created Date
- **Dimension name**: Account Created
- **Scope**: User
- **Description**: Date when user account was created
- **User property**: account_created

#### Dimension 3: Is Active
- **Dimension name**: User Active Status
- **Scope**: User
- **Description**: Whether user account is active
- **User property**: is_active

### Event-Scoped Dimensions:
Create these dimensions for event parameters:

#### Dimension 4: Story ID
- **Dimension name**: Story ID
- **Scope**: Event
- **Description**: Unique identifier for stories
- **Event parameter**: story_id

#### Dimension 5: World ID
- **Dimension name**: World ID
- **Scope**: Event
- **Description**: Unique identifier for worlds
- **Event parameter**: world_id

#### Dimension 6: AI Model
- **Dimension name**: AI Model Used
- **Scope**: Event
- **Description**: Which AI model was used
- **Event parameter**: ai_model

#### Dimension 7: Element Type
- **Dimension name**: Element Type
- **Scope**: Event
- **Description**: Type of element (character, location, etc.)
- **Event parameter**: element_type

#### Dimension 8: Action Type
- **Dimension name**: Action Type
- **Scope**: Event
- **Description**: Type of action performed
- **Event parameter**: action_type

#### Dimension 9: Page URL
- **Dimension name**: Page URL Path
- **Scope**: Event
- **Description**: URL path where event occurred
- **Event parameter**: page_url

#### Dimension 10: Error Source
- **Dimension name**: Error Source
- **Scope**: Event
- **Description**: Source of application errors
- **Event parameter**: error_source

---

## 3. Create Custom Metrics

### Navigate to Custom Definitions:
1. In **Admin** > **Custom definitions**
2. Click **Create custom metrics**

### Metric 1: Token Count
- **Metric name**: AI Token Count
- **Scope**: Event
- **Description**: Number of tokens used in AI interaction
- **Event parameter**: token_count
- **Unit of measurement**: Standard

### Metric 2: Estimated Cost
- **Metric name**: AI Estimated Cost
- **Scope**: Event
- **Description**: Estimated cost of AI interaction
- **Event parameter**: estimated_cost
- **Unit of measurement**: Currency

### Metric 3: Word Count
- **Metric name**: Story Word Count
- **Scope**: Event
- **Description**: Word count of published stories
- **Event parameter**: word_count
- **Unit of measurement**: Standard

### Metric 4: Generation Time
- **Metric name**: Generation Time (ms)
- **Scope**: Event
- **Description**: Time taken for generation in milliseconds
- **Event parameter**: generation_time_ms
- **Unit of measurement**: Milliseconds

---

## 4. Set Up Custom Events

### Mark Events as Conversions:
1. Go to **Admin** > **Events**
2. Find these events and toggle **Mark as conversion**:
   - `signup` (user registration)
   - `story_publish` (story publishing)
   - `world_create` (world creation)
   - `purchase` (if you track purchases)

### Create Event Modifications (if needed):
1. Go to **Admin** > **Events** > **Modify events**
2. Click **Create**

Example: Standardize login events
- **Modification name**: Standardize Login
- **Matching conditions**: Event name equals `login`
- **Parameter modifications**: Add parameter `method` with value from `event_label`

---

## 5. Create Custom Reports

### Report 1: User Engagement by Type
1. Go to **Reports** > **Library**
2. Click **Create new report** > **Blank**
3. Add dimensions:
   - User Type
   - User ID
4. Add metrics:
   - Active users
   - Engagement time
   - Event count
5. Save as "User Engagement by Type"

### Report 2: AI Usage Analytics
1. Create new blank report
2. Add dimensions:
   - AI Model Used
   - Event name
   - User Type
3. Add metrics:
   - Event count
   - AI Token Count (sum)
   - AI Estimated Cost (sum)
4. Save as "AI Usage Analytics"

### Report 3: Content Creation Funnel
1. Create new blank report
2. Add dimensions:
   - Event name
   - Element Type
3. Add metrics:
   - Event count
   - Users
4. Filter by events: `world_create`, `story_create`, `story_publish`
5. Save as "Content Creation Funnel"

### Report 4: Error Tracking
1. Create new blank report
2. Add dimensions:
   - Error Source
   - Page URL Path
   - Event name
3. Add metrics:
   - Event count
   - Users affected
4. Filter by event name: `exception`
5. Save as "Error Tracking Report"

---

## 6. Set Up Audiences

### Audience 1: Power Users
1. Go to **Admin** > **Audiences**
2. Click **New audience** > **Create a custom audience**
3. **Audience name**: Power Users
4. **Description**: Users who actively create content
5. Add condition:
   - Include users when: Event count > 50 in last 30 days
   - AND User Type = regular
6. Save

### Audience 2: AI Heavy Users
1. Create new custom audience
2. **Audience name**: AI Heavy Users
3. Add condition:
   - Include users when: AI Token Count (sum) > 10000 in last 30 days
4. Save

### Audience 3: Story Publishers
1. Create new custom audience
2. **Audience name**: Story Publishers
3. Add condition:
   - Include users when: Event name = story_publish (at least once)
4. Save

---

## 7. Configure DebugView

### Enable Debug Mode:
1. Install [Google Analytics Debugger](https://chrome.google.com/webstore/detail/google-analytics-debugger/jnkmfdileelhofjcijamephohjechhna) Chrome extension
2. Or add to your site URL: `?_dbg=1`
3. Or in console: `window.gtag('config', 'GA_MEASUREMENT_ID', { 'debug_mode': true });`

### Use DebugView:
1. In GA4, go to **Admin** > **DebugView**
2. Trigger events on your site
3. Watch events appear in real-time
4. Click on events to see all parameters
5. Verify custom dimensions are captured

---

## 8. Verify Implementation

### Step 1: Check User Properties
1. Go to **Reports** > **User** > **User attributes**
2. Look for:
   - user_type
   - account_created
   - is_active

### Step 2: Check Events
1. Go to **Reports** > **Engagement** > **Events**
2. Look for custom events:
   - story_create, story_publish, story_delete
   - world_create, world_import_from_book
   - ai_interaction
   - feature_use
   - image_generation

### Step 3: Check Real-Time
1. Go to **Reports** > **Realtime**
2. Perform actions on your site
3. Verify events appear within seconds
4. Click on events to see parameters

### Step 4: Create Test Dashboard
1. Go to **Reports** > **Library**
2. Create a new detail report
3. Add cards:
   - User ID count
   - Events by User Type
   - AI Model usage distribution
   - Top features used
   - Error count by source

---

## Additional Configuration

### Set Up Data Retention:
1. Go to **Admin** > **Data Settings** > **Data Retention**
2. Set **Event data retention** to 14 months (maximum)
3. Toggle ON **Reset user data on new activity**

### Configure Data Filters:
1. Go to **Admin** > **Data Settings** > **Data Filters**
2. Create filter to exclude internal traffic:
   - **Filter name**: Exclude Internal Traffic
   - **Filter type**: Internal traffic
   - **IP address**: Your office IP

### Set Up BigQuery Export (Optional):
1. Go to **Admin** > **BigQuery Links**
2. Click **Link**
3. Choose your BigQuery project
4. Configure daily export
5. Include advertising identifiers

---

## Testing Checklist

- [ ] User ID appears in DebugView
- [ ] User properties are set correctly
- [ ] Custom events fire with correct parameters
- [ ] Custom dimensions appear in reports
- [ ] Conversions are tracked
- [ ] Real-time reports show data
- [ ] No duplicate events
- [ ] Error tracking works
- [ ] Audiences populate correctly

---

## Troubleshooting

### Events not appearing:
1. Check browser console for errors
2. Verify GA4 measurement ID is correct
3. Check if ad blockers are interfering
4. Use DebugView to see if events are sent

### Custom dimensions not showing:
1. Wait 24-48 hours after creation
2. Ensure parameter names match exactly
3. Check parameter value types (string, number)
4. Verify events are sending parameters

### User ID not working:
1. Ensure User-ID is enabled in data stream
2. Check that user_id is sent with config
3. Verify user is authenticated
4. Use DebugView to confirm user_id parameter

---

## Best Practices

1. **Naming Convention**: Use consistent naming (snake_case for parameters)
2. **Documentation**: Document all custom events and parameters
3. **Testing**: Always test in DebugView first
4. **Validation**: Set up data quality alerts
5. **Privacy**: Ensure PII is never sent to GA4
6. **Limits**: Stay within GA4 limits (500 events per app, 50 custom dimensions)