### **Gen AI Book Manager** 📚🚀  

This is a **FastAPI-based book management system** with **AI-powered summaries and recommendations**. You can **add, update, delete, and fetch books**, plus **get AI-generated summaries** using Llama3. The app also supports **user reviews** and **personalized recommendations**.  

### **What’s Inside?**  
✅ **REST API for books & reviews** (FastAPI)  
✅ **AI-powered summaries** (Llama3)  
✅ **Async PostgreSQL DB** (SQLAlchemy + asyncpg)  
✅ **Auth & security baked in**  
✅ **Cloud-ready (Docker, AWS, GitHub Actions)**  

### **Tech Stack 🛠️**  
- **Backend**: FastAPI, Python  
- **Database**: PostgreSQL (async)  
- **AI Model**: Llama3  
- **Deployment**: Docker, AWS, GitHub Actions  
- **Testing**: Pytest + mocking  

### **How to run it locally**

Clone the repo:  
```bash
git clone https://github.com/your-username/gen-ai-book-manager.git  
cd gen-ai-book-manager
```

Install dependencies:  
```bash
pip install -r requirements.txt

#### **Run PostgreSQL using Docker**

Make sure you have Docker installed.

1. **Pull the PostgreSQL image** (if not already available locally):  
   ```bash
   docker pull postgres:latest
   ```

2. **Run the PostgreSQL container**:  
   ```bash
   docker run --name genai-postgres \
     -e POSTGRES_USER=youruser \
     -e POSTGRES_PASSWORD=yourpassword \
     -e POSTGRES_DB=genaibooks \
     -p 5432:5432 \
     -v pgdata:/var/lib/postgresql/data \
     -d postgres
   ```

This will start a PostgreSQL container with:

- **Username:** `youruser`  
- **Password:** `yourpassword`  
- **Database name:** `genaibooks`

#### **Set up `.env` file**  
Create a `.env` file in the root directory with the following content:

```env
# PostgreSQL connection URL
DATABASE_URL=postgresql://youruser:yourpassword@localhost:5432/genaibooks

# Credentials for basic authentication (used in the API)
USERNAME=your_basic_auth_username
PASSWORD=your_basic_auth_password
```

> **Note:** `USERNAME` and `PASSWORD` are used for basic authentication in the API, **not** for the PostgreSQL database.

#### **Initialize the database (one-time setup)**

Before running the app for the first time, create the necessary tables by running:

```bash
python create_db.py
```

This script sets up the database schema dynamically.


#### **Run the server**
```bash
uvicorn app.main:app --reload
```

### **What’s Next?**  
- ✅ **Phase 1**: Database & AI Setup (completed)  
- ✅ **Phase 2**: API Development & Security (completed)
- ⏳ **Phase 3**: AI Integration  
- ⏳ **Phase 4**: Testing  
- ⏳ **Phase 5**: Deployment  
