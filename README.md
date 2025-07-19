# 🚀 InnovateX Backend API

Complete API documentation for **Team Management** and **Attendance Tracking** system for hackathons and bootcamps.

## 🌐 API Base URLs

### **Production**: `https://innovatex-backend-r6ie.onrender.com`
### **Local Development**: `http://localhost:8000`

## 📋 Table of Contents

- [🔥 Quick Start](#-quick-start)
- [📖 API Endpoints](#-api-endpoints)
- [🧪 Complete Testing Guide](#-complete-testing-guide)
- [💻 Frontend Integration](#-frontend-integration)
- [🛠️ Local Development Setup](#️-local-development-setup)
- [❌ Error Handling](#-error-handling)
- [📊 Data Validation Rules](#-data-validation-rules)
- [🔍 Troubleshooting](#-troubleshooting)

---

## 🔥 Quick Start

### **For Frontend Developers** - Ready to Use!

**Production API**: `https://innovatex-backend-r6ie.onrender.com`

**Available Endpoints**:
- `GET /` - API documentation
- `GET /teams` - Fetch team data
- `POST /attendance` - Save attendance records
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

### **Test the API Right Now**:

```bash
# Get API info
curl https://innovatex-backend-r6ie.onrender.com/

# Fetch teams data
curl https://innovatex-backend-r6ie.onrender.com/teams

# Save bootcamp attendance (category required)
curl -X POST "https://innovatex-backend-r6ie.onrender.com/attendance" \
  -H "Content-Type: application/json" \
  -d '{"regno": "21ITR001", "day": "1", "event_type": "bootcamp", "category": "AI/ML"}'

# Save hackathon attendance (no category needed)
curl -X POST "https://innovatex-backend-r6ie.onrender.com/attendance" \
  -H "Content-Type: application/json" \
  -d '{"regno": "21ITR002", "day": "1", "event_type": "hackathon"}'
```

---

## 📖 API Endpoints

### 1. 🏠 **Home/API Information**
- **URL**: `/`
- **Method**: `GET`
- **Description**: Returns API information and usage examples

#### Example Request:
```bash
# Production
curl https://innovatex-backend-r6ie.onrender.com/

# Local
curl http://localhost:8000/
```

#### Example Response:
```json
{
  "message": "Team Domains API",
  "endpoints": {
    "/teams": "GET - Fetch all team names and domains",
    "/attendance": "POST - Save attendance data to Google Sheets",
    "/": "GET - API information",
    "/docs": "GET - Interactive API documentation",
    "/redoc": "GET - Alternative API documentation"
  },
  "attendance_usage": {
    "method": "POST",
    "endpoint": "/attendance",
    "body": {
      "regno": "Registration number (string)",
      "day": "Day number (1-5 for bootcamp, 1-2 for hackathon)",
      "event_type": "bootcamp or hackathon",
      "category": "AI/ML, Cyber, Full Stack (for bootcamp only)"
    }
  }
}
```

### 2. 👥 **Get Teams Data**
- **URL**: `/teams`
- **Method**: `GET`
- **Description**: Fetches team names, domains, and team leader information from Google Sheets

#### Example Request:
```bash
# Production
curl https://innovatex-backend-r6ie.onrender.com/teams

# Local
curl http://localhost:8000/teams
```

#### Example Response:
```json
{
  "success": true,
  "count": 3,
  "teams": [
    {
      "team_name": "Tech Innovators",
      "domains": "techinnovators.com",
      "team_leader": "John Doe (21ITR001)"
    },
    {
      "team_name": "AI Masters",
      "domains": "aimasters.io",
      "team_leader": "Jane Smith (21ITR002)"
    },
    {
      "team_name": "Cyber Warriors",
      "domains": "cyberwarriors.net",
      "team_leader": "Bob Johnson (21ITR003)"
    }
  ]
}
```

### 3. ✅ **Save Attendance** ⭐ **Main Feature**
- **URL**: `/attendance`
- **Method**: `POST`
- **Description**: Saves attendance data to appropriate Google Sheets based on event type

#### Request Body Structure:
```json
{
  "regno": "string (required)",
  "day": "string (required)", 
  "event_type": "string (required)",
  "category": "string (required for bootcamp only)"
}
```

#### Parameters:
- **regno**: Registration number (required)
- **day**: Day number
  - For bootcamp: `"1"`, `"2"`, `"3"`, `"4"`, `"5"`
  - For hackathon: `"1"`, `"2"`
- **event_type**: `"bootcamp"` or `"hackathon"` (required)
- **category**: 
  - For bootcamp: `"AI/ML"`, `"Cyber"`, `"Full Stack"` (**required**)
  - For hackathon: **Not required** (ignored if provided)

#### Example Requests:

**🎓 Bootcamp Attendance (category required):**
```bash
# Production
curl -X POST "https://innovatex-backend-r6ie.onrender.com/attendance" \
  -H "Content-Type: application/json" \
  -d '{
    "regno": "21ITR001",
    "day": "1",
    "event_type": "bootcamp",
    "category": "AI/ML"
  }'

# Local
curl -X POST "http://localhost:8000/attendance" \
  -H "Content-Type: application/json" \
  -d '{
    "regno": "21ITR001",
    "day": "1",
    "event_type": "bootcamp",
    "category": "AI/ML"
  }'
```

**🏆 Hackathon Attendance (no category needed):**
```bash
# Production
curl -X POST "https://innovatex-backend-r6ie.onrender.com/attendance" \
  -H "Content-Type: application/json" \
  -d '{
    "regno": "21ITR002",
    "day": "1",
    "event_type": "hackathon"
  }'

# Local
curl -X POST "http://localhost:8000/attendance" \
  -H "Content-Type: application/json" \
  -d '{
    "regno": "21ITR002",
    "day": "1",
    "event_type": "hackathon"
  }'
```

#### Example Success Response:
```json
{
  "success": true,
  "message": "Attendance recorded successfully for 21ITR001",
  "data": {
    "regno": "21ITR001",
    "day": "1",
    "event_type": "bootcamp",
    "category": "AI/ML",
    "timestamp": "2025-07-19 14:30:25",
    "worksheet": "AI/ML Bootcamp"
  }
}
```

### 4. 📚 **Interactive Documentation**
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

```bash
# Production
https://innovatex-backend-r6ie.onrender.com/docs
https://innovatex-backend-r6ie.onrender.com/redoc

# Local
http://localhost:8000/docs
http://localhost:8000/redoc
```

---

## 🧪 Complete Testing Guide

### **1. Using cURL (Recommended for Quick Testing)**

```bash
# Test API Info
curl https://innovatex-backend-r6ie.onrender.com/

# Test Teams Endpoint
curl https://innovatex-backend-r6ie.onrender.com/teams

# Test All Bootcamp Categories
curl -X POST "https://innovatex-backend-r6ie.onrender.com/attendance" \
  -H "Content-Type: application/json" \
  -d '{"regno": "TEST001", "day": "1", "event_type": "bootcamp", "category": "AI/ML"}'

curl -X POST "https://innovatex-backend-r6ie.onrender.com/attendance" \
  -H "Content-Type: application/json" \
  -d '{"regno": "TEST002", "day": "2", "event_type": "bootcamp", "category": "Cyber"}'

curl -X POST "https://innovatex-backend-r6ie.onrender.com/attendance" \
  -H "Content-Type: application/json" \
  -d '{"regno": "TEST003", "day": "3", "event_type": "bootcamp", "category": "Full Stack"}'

# Test Hackathon Days
curl -X POST "https://innovatex-backend-r6ie.onrender.com/attendance" \
  -H "Content-Type: application/json" \
  -d '{"regno": "TEST004", "day": "1", "event_type": "hackathon"}'

curl -X POST "https://innovatex-backend-r6ie.onrender.com/attendance" \
  -H "Content-Type: application/json" \
  -d '{"regno": "TEST005", "day": "2", "event_type": "hackathon"}'
```

### **2. Using JavaScript/Fetch (Frontend Integration)**

```javascript
const API_BASE = 'https://innovatex-backend-r6ie.onrender.com';

// Get teams data
async function getTeams() {
  try {
    const response = await fetch(`${API_BASE}/teams`);
    const data = await response.json();
    console.log('Teams:', data);
    return data;
  } catch (error) {
    console.error('Error fetching teams:', error);
  }
}

// Save bootcamp attendance
async function saveBootcampAttendance(regno, day, category) {
  try {
    const response = await fetch(`${API_BASE}/attendance`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        regno: regno,
        day: day,
        event_type: 'bootcamp',
        category: category
      })
    });
    
    const data = await response.json();
    if (response.ok) {
      console.log('Bootcamp attendance saved:', data);
      return data;
    } else {
      console.error('Error:', data);
      throw new Error(data.detail?.error || 'Failed to save attendance');
    }
  } catch (error) {
    console.error('Error saving bootcamp attendance:', error);
    throw error;
  }
}

// Save hackathon attendance
async function saveHackathonAttendance(regno, day) {
  try {
    const response = await fetch(`${API_BASE}/attendance`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        regno: regno,
        day: day,
        event_type: 'hackathon'
      })
    });
    
    const data = await response.json();
    if (response.ok) {
      console.log('Hackathon attendance saved:', data);
      return data;
    } else {
      console.error('Error:', data);
      throw new Error(data.detail?.error || 'Failed to save attendance');
    }
  } catch (error) {
    console.error('Error saving hackathon attendance:', error);
    throw error;
  }
}

// Example usage
getTeams();
saveBootcampAttendance('21ITR001', '1', 'AI/ML');
saveHackathonAttendance('21ITR002', '1');
```

### **3. Using Python requests**

```python
import requests
import json

API_BASE = 'https://innovatex-backend-r6ie.onrender.com'

def get_teams():
    """Fetch all teams data"""
    try:
        response = requests.get(f"{API_BASE}/teams")
        response.raise_for_status()
        data = response.json()
        print(f"Found {data['count']} teams")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching teams: {e}")
        return None

def save_bootcamp_attendance(regno, day, category):
    """Save bootcamp attendance"""
    try:
        payload = {
            "regno": regno,
            "day": day,
            "event_type": "bootcamp",
            "category": category
        }
        
        response = requests.post(
            f"{API_BASE}/attendance",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bootcamp attendance saved: {data['message']}")
            return data
        else:
            error_data = response.json()
            print(f"❌ Error: {error_data}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

def save_hackathon_attendance(regno, day):
    """Save hackathon attendance"""
    try:
        payload = {
            "regno": regno,
            "day": day,
            "event_type": "hackathon"
        }
        
        response = requests.post(
            f"{API_BASE}/attendance",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Hackathon attendance saved: {data['message']}")
            return data
        else:
            error_data = response.json()
            print(f"❌ Error: {error_data}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Test teams endpoint
    teams = get_teams()
    
    # Test bootcamp attendance
    save_bootcamp_attendance("21ITR001", "1", "AI/ML")
    save_bootcamp_attendance("21ITR002", "2", "Cyber")
    save_bootcamp_attendance("21ITR003", "3", "Full Stack")
    
    # Test hackathon attendance
    save_hackathon_attendance("21ITR004", "1")
    save_hackathon_attendance("21ITR005", "2")
```

### **4. Using Postman**

1. **Import Collection**: Create a new Postman collection
2. **Set Base URL**: `https://innovatex-backend-r6ie.onrender.com`

**Requests to create:**

**GET Teams:**
- Method: `GET`
- URL: `{{base_url}}/teams`

**POST Bootcamp Attendance:**
- Method: `POST`
- URL: `{{base_url}}/attendance`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "regno": "21ITR001",
  "day": "1",
  "event_type": "bootcamp",
  "category": "AI/ML"
}
```

**POST Hackathon Attendance:**
- Method: `POST`
- URL: `{{base_url}}/attendance`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "regno": "21ITR002",
  "day": "1",
  "event_type": "hackathon"
}
```

---

## 💻 Frontend Integration

### **React Example**

```jsx
import React, { useState, useEffect } from 'react';

const API_BASE = 'https://innovatex-backend-r6ie.onrender.com';

function AttendanceForm() {
  const [teams, setTeams] = useState([]);
  const [formData, setFormData] = useState({
    regno: '',
    day: '',
    event_type: '',
    category: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // Fetch teams on component mount
  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      const response = await fetch(`${API_BASE}/teams`);
      const data = await response.json();
      setTeams(data.teams || []);
    } catch (error) {
      console.error('Error fetching teams:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const payload = {
        regno: formData.regno,
        day: formData.day,
        event_type: formData.event_type
      };

      // Add category only for bootcamp
      if (formData.event_type === 'bootcamp') {
        payload.category = formData.category;
      }

      const response = await fetch(`${API_BASE}/attendance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(`✅ ${data.message}`);
        setFormData({ regno: '', day: '', event_type: '', category: '' });
      } else {
        setMessage(`❌ ${data.detail?.error || 'Error saving attendance'}`);
      }
    } catch (error) {
      setMessage(`❌ Network error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="attendance-form">
      <h2>InnovateX Attendance System</h2>
      
      {/* Teams Display */}
      <div className="teams-section">
        <h3>Registered Teams ({teams.length})</h3>
        {teams.map((team, index) => (
          <div key={index} className="team-card">
            <strong>{team.team_name}</strong>
            <p>Domain: {team.domains}</p>
            <p>Leader: {team.team_leader}</p>
          </div>
        ))}
      </div>

      {/* Attendance Form */}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Registration Number:</label>
          <input
            type="text"
            value={formData.regno}
            onChange={(e) => setFormData({...formData, regno: e.target.value})}
            required
          />
        </div>

        <div>
          <label>Event Type:</label>
          <select
            value={formData.event_type}
            onChange={(e) => setFormData({...formData, event_type: e.target.value})}
            required
          >
            <option value="">Select Event Type</option>
            <option value="bootcamp">Bootcamp</option>
            <option value="hackathon">Hackathon</option>
          </select>
        </div>

        <div>
          <label>Day:</label>
          <select
            value={formData.day}
            onChange={(e) => setFormData({...formData, day: e.target.value})}
            required
          >
            <option value="">Select Day</option>
            {formData.event_type === 'bootcamp' && (
              <>
                <option value="1">Day 1</option>
                <option value="2">Day 2</option>
                <option value="3">Day 3</option>
                <option value="4">Day 4</option>
                <option value="5">Day 5</option>
              </>
            )}
            {formData.event_type === 'hackathon' && (
              <>
                <option value="1">Day 1</option>
                <option value="2">Day 2</option>
              </>
            )}
          </select>
        </div>

        {formData.event_type === 'bootcamp' && (
          <div>
            <label>Category:</label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({...formData, category: e.target.value})}
              required
            >
              <option value="">Select Category</option>
              <option value="AI/ML">AI/ML</option>
              <option value="Cyber">Cyber</option>
              <option value="Full Stack">Full Stack</option>
            </select>
          </div>
        )}

        <button type="submit" disabled={loading}>
          {loading ? 'Saving...' : 'Save Attendance'}
        </button>
      </form>

      {message && <div className="message">{message}</div>}
    </div>
  );
}

export default AttendanceForm;
```

### **Vue.js Example**

```vue
<template>
  <div class="attendance-app">
    <h2>InnovateX Attendance System</h2>
    
    <!-- Teams Display -->
    <div class="teams-section">
      <h3>Registered Teams ({{ teams.length }})</h3>
      <div v-for="team in teams" :key="team.team_name" class="team-card">
        <strong>{{ team.team_name }}</strong>
        <p>Domain: {{ team.domains }}</p>
        <p>Leader: {{ team.team_leader }}</p>
      </div>
    </div>

    <!-- Attendance Form -->
    <form @submit.prevent="saveAttendance">
      <div>
        <label>Registration Number:</label>
        <input v-model="formData.regno" type="text" required />
      </div>

      <div>
        <label>Event Type:</label>
        <select v-model="formData.event_type" required>
          <option value="">Select Event Type</option>
          <option value="bootcamp">Bootcamp</option>
          <option value="hackathon">Hackathon</option>
        </select>
      </div>

      <div>
        <label>Day:</label>
        <select v-model="formData.day" required>
          <option value="">Select Day</option>
          <option v-if="formData.event_type === 'bootcamp'" value="1">Day 1</option>
          <option v-if="formData.event_type === 'bootcamp'" value="2">Day 2</option>
          <option v-if="formData.event_type === 'bootcamp'" value="3">Day 3</option>
          <option v-if="formData.event_type === 'bootcamp'" value="4">Day 4</option>
          <option v-if="formData.event_type === 'bootcamp'" value="5">Day 5</option>
          <option v-if="formData.event_type === 'hackathon'" value="1">Day 1</option>
          <option v-if="formData.event_type === 'hackathon'" value="2">Day 2</option>
        </select>
      </div>

      <div v-if="formData.event_type === 'bootcamp'">
        <label>Category:</label>
        <select v-model="formData.category" required>
          <option value="">Select Category</option>
          <option value="AI/ML">AI/ML</option>
          <option value="Cyber">Cyber</option>
          <option value="Full Stack">Full Stack</option>
        </select>
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? 'Saving...' : 'Save Attendance' }}
      </button>
    </form>

    <div v-if="message" class="message">{{ message }}</div>
  </div>
</template>

<script>
const API_BASE = 'https://innovatex-backend-r6ie.onrender.com';

export default {
  name: 'AttendanceApp',
  data() {
    return {
      teams: [],
      formData: {
        regno: '',
        day: '',
        event_type: '',
        category: ''
      },
      loading: false,
      message: ''
    };
  },
  mounted() {
    this.fetchTeams();
  },
  methods: {
    async fetchTeams() {
      try {
        const response = await fetch(`${API_BASE}/teams`);
        const data = await response.json();
        this.teams = data.teams || [];
      } catch (error) {
        console.error('Error fetching teams:', error);
      }
    },
    
    async saveAttendance() {
      this.loading = true;
      this.message = '';

      try {
        const payload = {
          regno: this.formData.regno,
          day: this.formData.day,
          event_type: this.formData.event_type
        };

        // Add category only for bootcamp
        if (this.formData.event_type === 'bootcamp') {
          payload.category = this.formData.category;
        }

        const response = await fetch(`${API_BASE}/attendance`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
          this.message = `✅ ${data.message}`;
          this.formData = { regno: '', day: '', event_type: '', category: '' };
        } else {
          this.message = `❌ ${data.detail?.error || 'Error saving attendance'}`;
        }
      } catch (error) {
        this.message = `❌ Network error: ${error.message}`;
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

---

## 🛠️ Local Development Setup

### **Prerequisites**
- Python 3.8+
- pip (Python package manager)

### **Installation Steps**

1. **Clone the repository:**
```bash
git clone https://github.com/dharshan-kumarj/InnovateX_Backend.git
cd InnovateX_Backend
```

2. **Create virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up Google Sheets credentials:**
   - Place `credentials.json` in the project root
   - Or set environment variables (see below)

5. **Run the application:**
```bash
python sheets_scanner.py
```

The API will be available at `http://localhost:8000`

### **Environment Variables (Optional)**
```bash
export GOOGLE_CREDENTIALS_TYPE=service_account
export GOOGLE_PROJECT_ID=your-project-id
export GOOGLE_PRIVATE_KEY_ID=your-private-key-id
export GOOGLE_PRIVATE_KEY="your-private-key"
export GOOGLE_CLIENT_EMAIL=your-service-account-email
export GOOGLE_CLIENT_ID=your-client-id
export GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
export GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
export GOOGLE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
export GOOGLE_CLIENT_X509_CERT_URL=your-cert-url
export GOOGLE_UNIVERSE_DOMAIN=googleapis.com
export PORT=8000
```

---

## ❌ Error Handling

### **Common Error Responses**

#### **400 Bad Request - Missing Required Fields**
```json
{
  "detail": {
    "error": "Registration number is required"
  }
}
```

#### **400 Bad Request - Invalid Event Type**
```json
{
  "detail": {
    "error": "Event type must be 'bootcamp' or 'hackathon'"
  }
}
```

#### **400 Bad Request - Invalid Day**
```json
{
  "detail": {
    "error": "For bootcamp, day must be between 1-5"
  }
}
```

#### **400 Bad Request - Missing Category for Bootcamp**
```json
{
  "detail": {
    "error": "Category is required for bootcamp events"
  }
}
```

#### **400 Bad Request - Invalid Bootcamp Category**
```json
{
  "detail": {
    "error": "Invalid bootcamp category: Data Science. Use 'AI/ML', 'Cyber', or 'Full Stack'"
  }
}
```

#### **400 Bad Request - Duplicate Entry**
```json
{
  "detail": {
    "error": "Duplicate entry",
    "message": "Attendance for regno 21ITR001 on day 1 already recorded"
  }
}
```

#### **500 Internal Server Error**
```json
{
  "detail": {
    "error": "Internal server error",
    "message": "Database connection failed"
  }
}
```

### **Frontend Error Handling Example**

```javascript
async function saveAttendance(attendanceData) {
  try {
    const response = await fetch(`${API_BASE}/attendance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(attendanceData)
    });

    const data = await response.json();

    if (!response.ok) {
      // Handle different error types
      if (response.status === 400) {
        const error = data.detail?.error || 'Validation error';
        alert(`Error: ${error}`);
      } else if (response.status === 500) {
        alert('Server error. Please try again later.');
      } else {
        alert('Unknown error occurred.');
      }
      return null;
    }

    return data;
  } catch (error) {
    alert(`Network error: ${error.message}`);
    return null;
  }
}
```

---

## 📊 Data Validation Rules

### **✅ Valid Combinations**

| Event Type | Day | Category | Result |
|------------|-----|----------|--------|
| bootcamp | 1-5 | AI/ML | ✅ Saved to "AI/ML Bootcamp" sheet |
| bootcamp | 1-5 | Cyber | ✅ Saved to "Cyber Bootcamp" sheet |
| bootcamp | 1-5 | Full Stack | ✅ Saved to "Full Stack Development" sheet |
| hackathon | 1-2 | (any/none) | ✅ Saved to "Hackathon Day X" sheet |

### **❌ Invalid Combinations**

| Event Type | Day | Category | Error |
|------------|-----|----------|--------|
| bootcamp | 6 | AI/ML | ❌ Invalid day for bootcamp |
| bootcamp | 1 | (missing) | ❌ Category required for bootcamp |
| bootcamp | 1 | Data Science | ❌ Invalid bootcamp category |
| hackathon | 3 | (any) | ❌ Invalid day for hackathon |
| workshop | 1 | AI/ML | ❌ Invalid event type |

### **🔄 Google Sheets Structure**

**Created Worksheets:**
- `AI/ML Bootcamp` - For AI/ML bootcamp attendance
- `Cyber Bootcamp` - For Cyber bootcamp attendance
- `Full Stack Development` - For Full Stack bootcamp attendance
- `Hackathon Day 1` - For hackathon day 1 attendance
- `Hackathon Day 2` - For hackathon day 2 attendance

**Each sheet contains:**
| Column | Description | Example |
|--------|-------------|---------|
| Registration Number | Student reg number | 21ITR001 |
| Day | Event day | 1 |
| Timestamp | When recorded | 2025-07-19 14:30:25 |
| Event Type | bootcamp/hackathon | bootcamp |
| Category | Event category | AI/ML |

---

## 🔍 Troubleshooting

### **Common Issues & Solutions**

#### **1. CORS Errors in Browser**
**Problem**: Cross-origin requests blocked
**Solution**: The API has CORS enabled for all origins. If you still get CORS errors:
```javascript
// Make sure you're using the correct URL
const API_BASE = 'https://innovatex-backend-r6ie.onrender.com'; // ✅ Correct
const API_BASE = 'http://innovatex-backend-r6ie.onrender.com'; // ❌ Wrong (no HTTPS)
```

#### **2. Network/Connection Errors**
**Problem**: Request fails to reach server
**Solutions**:
- Check internet connection
- Verify the API URL is correct
- Try the request in a new browser tab
- Check if the server is running (for localhost)

#### **3. 403 Permission Denied**
**Problem**: Google Sheets permission error
**Solution**: This is a backend configuration issue. The API should handle this gracefully.

#### **4. Invalid JSON Response**
**Problem**: Response is not valid JSON
**Solution**:
```javascript
try {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  const data = await response.json();
  return data;
} catch (error) {
  if (error instanceof SyntaxError) {
    console.error('Invalid JSON response');
  } else {
    console.error('Request error:', error.message);
  }
}
```

#### **5. Slow Response Times**
**Problem**: API takes too long to respond
**Cause**: Server cold start on free hosting
**Solution**: 
- First request may take 30-60 seconds (server wake up)
- Subsequent requests will be faster
- Consider implementing loading states in your frontend

### **Testing Checklist**

Before reporting issues, please test:

1. ✅ API base URL is correct
2. ✅ Request headers include `Content-Type: application/json`
3. ✅ Request body is valid JSON
4. ✅ Required fields are provided
5. ✅ Event type is either "bootcamp" or "hackathon"
6. ✅ Day is valid for the event type
7. ✅ Category is provided for bootcamp events
8. ✅ Network connection is working

### **Debug Mode**

For debugging, add console logging:

```javascript
console.log('Request URL:', `${API_BASE}/attendance`);
console.log('Request payload:', JSON.stringify(payload, null, 2));

const response = await fetch(url, options);
console.log('Response status:', response.status);
console.log('Response headers:', [...response.headers.entries()]);

const data = await response.json();
console.log('Response data:', data);
```

---

## 🎯 Summary

**InnovateX Backend API** provides:

1. **Team Management**: Fetch team data from Google Sheets
2. **Attendance Tracking**: Save attendance for bootcamps and hackathons
3. **Automatic Organization**: Data is saved to appropriate sheets based on event type
4. **Duplicate Prevention**: Prevents multiple attendance entries for same day
5. **Flexible Categories**: Required for bootcamps, optional for hackathons

**Ready to use**: `https://innovatex-backend-r6ie.onrender.com`

**Interactive docs**: `https://innovatex-backend-r6ie.onrender.com/docs`

For any issues or questions, check the troubleshooting section or open an issue in the repository.

---

**Happy coding! 🚀**
