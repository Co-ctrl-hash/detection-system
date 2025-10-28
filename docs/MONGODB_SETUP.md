# MongoDB Setup Guide

This project supports MongoDB as an alternative NoSQL database option.

## Why MongoDB?

**Advantages:**
- ✅ Flexible schema - no migrations needed for schema changes
- ✅ Excellent for unstructured/semi-structured data
- ✅ Horizontal scalability
- ✅ Fast writes and queries with proper indexing
- ✅ JSON-like documents match API responses naturally

**Trade-offs:**
- ⚠️ No built-in relationships (vs SQL foreign keys)
- ⚠️ Requires different query patterns than SQL
- ⚠️ Larger storage footprint

## Quick Start

### Option 1: Local MongoDB

**Windows:**
1. Download MongoDB Community Server: https://www.mongodb.com/try/download/community
2. Install with default settings
3. MongoDB will run as a Windows service

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0
```

**Linux (Ubuntu/Debian):**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
```

### Option 2: MongoDB Atlas (Cloud - Free Tier)

**Recommended for Production**

1. Sign up at https://www.mongodb.com/cloud/atlas
2. Create a free cluster (M0 tier)
3. Create database user and password
4. Whitelist your IP address (or use 0.0.0.0/0 for testing)
5. Get connection string from "Connect" button

## Installation

MongoDB drivers are already installed:
```bash
pip install pymongo flask-pymongo
```

## Configuration

### 1. Switch to MongoDB App

Use `app_mongodb.py` instead of `app.py`:

**Method A: Rename files**
```bash
mv backend/app.py backend/app_sql.py
mv backend/app_mongodb.py backend/app.py
```

**Method B: Update imports (recommended)**
Keep both files and run MongoDB version:
```bash
python backend/app_mongodb.py
```

### 2. Set MongoDB Connection String

Create or update `.env`:

**Local:**
```bash
MONGO_URI=mongodb://localhost:27017/plates_db
```

**With authentication:**
```bash
MONGO_URI=mongodb://username:password@localhost:27017/plates_db
```

**MongoDB Atlas (Cloud):**
```bash
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/plates_db?retryWrites=true&w=majority
```

### 3. Run the Application

```bash
python backend/app_mongodb.py
```

The database and collections will be created automatically on first use!

## MongoDB vs SQL Differences

### Data Structure

**SQL (app.py):**
```python
Detection(
    id=1,
    plate_number="ABC123",
    confidence=0.95,
    bbox_x1=10, bbox_y1=20, bbox_x2=100, bbox_y2=80
)
```

**MongoDB (app_mongodb.py):**
```json
{
    "_id": ObjectId("..."),
    "plate_number": "ABC123",
    "confidence": 0.95,
    "bbox": {"x1": 10, "y1": 20, "x2": 100, "y2": 80},
    "created_at": ISODate("2025-10-28T10:30:00Z")
}
```

### Queries

**SQL:**
```python
Detection.query.filter_by(camera_id="cam1").all()
```

**MongoDB:**
```python
mongo.db.detections.find({"camera_id": "cam1"})
```

## Testing MongoDB Connection

```bash
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017/'); print('Connected:', client.server_info()['version'])"
```

## Creating Indexes (Performance)

Add to your `app_mongodb.py` startup:

```python
# Create indexes for better performance
with app.app_context():
    mongo.db.detections.create_index([('camera_id', 1)])
    mongo.db.detections.create_index([('plate_number', 1)])
    mongo.db.detections.create_index([('created_at', -1)])
```

## MongoDB GUI Tools

**Recommended:**
- **MongoDB Compass** (Official) - https://www.mongodb.com/products/compass
- **Studio 3T** - https://studio3t.com/
- **Robo 3T** - https://robomongo.org/

## Migration from SQL to MongoDB

No automatic migration available. Options:

**Option 1: Fresh Start**
- Use MongoDB from the beginning
- Old SQL data stays in `plates.db`

**Option 2: Export/Import**
```python
# Export from SQLite
from backend.app import app, Detection
import json

with app.app_context():
    detections = Detection.query.all()
    data = [d.to_dict() for d in detections]
    
with open('export.json', 'w') as f:
    json.dump(data, f)

# Import to MongoDB
from backend.app_mongodb import app, mongo
import json

with app.app_context():
    with open('export.json', 'r') as f:
        data = json.load(f)
    mongo.db.detections.insert_many(data)
```

## Troubleshooting

**Connection refused:**
```bash
# Check if MongoDB is running
# Windows:
net start MongoDB

# macOS/Linux:
brew services list  # macOS
sudo systemctl status mongod  # Linux
```

**Authentication failed:**
- Verify username/password in connection string
- Ensure user has read/write permissions on database

**Atlas IP whitelist:**
- Add your current IP in Atlas dashboard → Network Access
- Or use `0.0.0.0/0` for testing (not recommended for production)

## Performance Tips

1. **Create indexes** on frequently queried fields
2. **Limit fields** in queries: `.find({}, {'plate_number': 1})`
3. **Use aggregation** for complex queries
4. **Enable compression** in connection string: `?compressors=snappy`

## Switching Back to SQL

Simply run the original `app.py`:
```bash
python backend/app.py
```

Both versions can coexist - use environment variables to switch.

## Production Checklist

- [ ] Use MongoDB Atlas or managed MongoDB service
- [ ] Enable authentication
- [ ] Create database indexes
- [ ] Set up automated backups
- [ ] Enable SSL/TLS connection
- [ ] Monitor with MongoDB Cloud Manager
- [ ] Set connection pool size appropriately
