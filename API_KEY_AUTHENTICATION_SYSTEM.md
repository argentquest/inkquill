# API Key Authentication System

**Project**: External API Access for Ink And Quill Storytelling Platform  
**Status**: Specification Complete - Ready for Implementation  
**Date**: August 2025

---

## 📋 Project Overview

This document outlines the design and implementation plan for adding API key authentication to expose selected FastAPI endpoints to external systems. The system provides secure, read-only access to story and user data through dedicated external API endpoints.

### Goals
- Enable trusted external systems to access story data
- Maintain security through API key authentication
- Provide admin-controlled key management
- Support integration with third-party services

---

## 🔧 Requirements Summary

Based on comprehensive requirements gathering, the system will have the following characteristics:

| **Aspect** | **Decision** | **Rationale** |
|------------|--------------|---------------|
| **Endpoint Scope** | Dedicated external endpoints (`/api/v1/external/*`) with read operations | Clean separation from internal UI endpoints |
| **Access Level** | System-wide (access to all stories/users) | Simplified for trusted integrations |
| **Key Management** | Admin-generated only through web interface | Controlled access and security oversight |
| **Key Format** | Random string with prefix (`ak_[32_chars]`) | Recognizable and secure |
| **Rate Limiting** | None (unlimited for trusted systems) | Simple implementation for known partners |
| **Expiration** | Never expire (permanent until revoked) | Low maintenance for stable integrations |
| **Authentication** | Authorization Bearer header | Industry standard approach |
| **Storage** | New dedicated database table | Clean data separation and auditability |

---

## 🌐 External API Endpoints

The following 8 endpoints will be exposed for external access:

### **Story Operations**
1. **Get Story Details**
   - `GET /api/v1/external/stories/basic/{story_id}`
   - Returns story metadata (title, author, creation date, etc.)
   - Excludes content for performance

2. **Get Story Content**
   - `GET /api/v1/external/stories/basic/{story_id}/content`  
   - Returns the actual story content (HTML from editor)
   - Separate endpoint for content-heavy operations

3. **List All Basic Stories**
   - `GET /api/v1/external/stories/basic`
   - Returns paginated list of all basic stories in system
   - Includes basic metadata for each story

4. **List User's Stories**
   - `GET /api/v1/external/users/{user_id}/stories/basic`
   - Returns all basic stories belonging to specific user
   - Filtered by user ownership

### **Published Story Operations**
5. **List Published Stories**
   - `GET /api/v1/external/stories/published`
   - Returns all publicly published stories
   - Includes publication metadata

6. **Get Published Story Details**
   - `GET /api/v1/external/stories/published/{story_id}`
   - Returns full details and content of published story
   - Optimized for public consumption

### **User Operations**
7. **Get User Information**
   - `GET /api/v1/external/users/{user_id}`
   - Returns basic user info (username, display name, creation date)
   - For story attribution and user identification

8. **List All Users**
   - `GET /api/v1/external/users`
   - Returns paginated list of all users
   - Basic information only (no sensitive data)

---

## 🏗️ Technical Specifications

### **Database Schema**

```sql
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);
```

### **API Key Format**
- **Pattern**: `ak_[32_random_characters]`
- **Example**: `ak_abcd1234efgh5678ijkl9012mnop3456`
- **Generation**: Cryptographically secure random characters
- **Storage**: SHA-256 hash only (never store plain text)

### **Authentication Flow**
1. External system includes header: `Authorization: Bearer ak_abcd1234efgh5678ijkl9012mnop3456`
2. API extracts Bearer token from header
3. System hashes received key and looks up in database
4. If valid and active, updates `last_used_at` timestamp
5. Request proceeds with full system access
6. If invalid, returns 401 Unauthorized

### **Response Format**
All external endpoints return JSON-only responses:

```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2025-08-10T17:30:00Z",
    "api_version": "1.0"
  }
}
```

---

## 🔒 Security Features

### **Key Security**
- ✅ **Hashed Storage**: Keys stored as SHA-256 hashes with salt
- ✅ **Secure Generation**: Cryptographically secure random generation
- ✅ **No Expiration**: Keys remain valid until manually revoked
- ✅ **Usage Tracking**: Last used timestamps for audit trails

### **Access Control**
- ✅ **Admin Only**: Key creation restricted to administrators
- ✅ **System Wide**: Keys provide access to all stories/users
- ✅ **Read Only**: No create/update/delete operations exposed
- ✅ **Audit Trail**: Track key creation, usage, and revocation

### **API Security**
- ✅ **Bearer Token**: Industry standard authentication method
- ✅ **HTTPS Only**: Production deployment requires SSL/TLS
- ✅ **Rate Monitoring**: Log usage for abuse detection
- ✅ **Error Handling**: Secure error responses (no data leakage)

---

## 📋 Implementation Plan

### **Phase 1: Database Foundation**
- [ ] Create Alembic migration for `api_keys` table
- [ ] Create `APIKey` SQLAlchemy model
- [ ] Add database indexes for performance

### **Phase 2: Core Authentication**
- [ ] Implement `APIKeyService` for key management
- [ ] Create authentication dependency for FastAPI
- [ ] Add key hashing and validation utilities

### **Phase 3: External API Endpoints**
- [ ] Create `external_api.py` router
- [ ] Implement all 8 approved endpoints
- [ ] Add JSON response formatting
- [ ] Include comprehensive error handling

### **Phase 4: Admin Interface**
- [ ] Design API key management page
- [ ] Create key creation form
- [ ] Add key listing and status management
- [ ] Integrate with existing admin dashboard

### **Phase 5: Documentation & Testing**
- [ ] Update OpenAPI/Swagger documentation
- [ ] Create integration examples
- [ ] Add comprehensive test coverage
- [ ] Performance testing for key lookup

---

## 👨‍💻 Usage Examples

### **Authentication**
All requests must include the API key in the Authorization header:

```bash
curl -H "Authorization: Bearer ak_abcd1234efgh5678ijkl9012mnop3456" \
     http://localhost:8000/api/v1/external/stories/basic/201
```

### **Common Operations**

**Get story metadata:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:8000/api/v1/external/stories/basic/201
```

**Get story content:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:8000/api/v1/external/stories/basic/201/content
```

**List all stories:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:8000/api/v1/external/stories/basic
```

**List user's stories:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:8000/api/v1/external/users/123/stories/basic
```

### **Integration Examples**

**Python with requests:**
```python
import requests

API_KEY = "ak_abcd1234efgh5678ijkl9012mnop3456"
BASE_URL = "http://localhost:8000/api/v1/external"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Get story
response = requests.get(f"{BASE_URL}/stories/basic/201", headers=headers)
story = response.json()

# Get content  
content_response = requests.get(f"{BASE_URL}/stories/basic/201/content", headers=headers)
content = content_response.json()
```

**JavaScript/Node.js:**
```javascript
const API_KEY = 'ak_abcd1234efgh5678ijkl9012mnop3456';
const BASE_URL = 'http://localhost:8000/api/v1/external';

const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json'
};

// Get story
const response = await fetch(`${BASE_URL}/stories/basic/201`, { headers });
const story = await response.json();
```

---

## 🔧 Admin Interface

### **Key Management Dashboard**
The admin interface will provide comprehensive key management:

**Features:**
- **Create New Keys**: Form with name and description fields
- **List All Keys**: Table showing key details, creation info, last used
- **Key Status**: Toggle active/inactive status
- **Usage Statistics**: Last used timestamps and usage frequency
- **Revocation**: Permanently disable compromised keys

**Admin Page Layout:**
```
┌─────────────────────────────────────────┐
│ API Key Management                      │
├─────────────────────────────────────────┤
│ [+ Create New API Key]                  │
├─────────────────────────────────────────┤
│ Key Name    | Created    | Last Used    │
│ Integration | 2025-08-01 | 2025-08-10  │
│ Mobile App  | 2025-08-05 | Never       │
│ Analytics   | 2025-08-08 | 2025-08-09  │
└─────────────────────────────────────────┘
```

---

## 📁 File Structure

### **New Files to Create:**
```
app/
├── models/
│   └── api_key.py                 # SQLAlchemy model
├── services/
│   └── api_key_service.py         # Key generation and management
├── routers/
│   └── external_api.py            # External API endpoints
└── templates/pages/
    └── admin_api_keys.html        # Admin management interface

alembic/versions/
└── xxx_create_api_keys_table.py   # Database migration
```

### **Files to Modify:**
```
app/
├── core/
│   └── deps.py                    # Add API key authentication
├── routers/
│   └── views_admin.py             # Add admin routes
└── main.py                        # Include external router
```

---

## 🚀 Next Steps

1. **Review and Approve** this specification
2. **Assign Development Resources** for implementation
3. **Set Timeline** for each phase
4. **Begin Phase 1** with database foundation
5. **Iterate and Test** each phase before proceeding

---

## 📞 Integration Support

Once implemented, external systems will have secure, reliable access to story data through these standardized endpoints. The system is designed for:

- **Third-party integrations**
- **Mobile applications** 
- **Analytics platforms**
- **Content management systems**
- **Automated workflows**

For technical support and integration assistance, contact the development team with your API key requirements and use case details.

---

*This document serves as the complete specification for implementing external API access to the Ink And Quill storytelling platform.*