### **Gen AI Book Manager** 📚🚀  

This is a **FastAPI-based book management system** with **AI-powered summaries and recommendations**. You can **add, update, delete, and fetch books**, plus **get AI-generated summaries** using Llama3. The app also supports **user reviews** and **personalized recommendations**.  

### **What’s Inside?**  
✅ **REST API for books & reviews** (FastAPI)  
✅ **AI-powered summaries** (Llama3)  
✅ **Async PostgreSQL DB** (SQLAlchemy + asyncpg)  
✅ **Auth & security baked in**  
✅ **Cloud-ready** (Docker, AWS, GitHub Actions)  

### **Tech Stack 🛠️**  
- **Backend**: FastAPI, Python  
- **Database**: PostgreSQL (async)  
- **AI Model**: Llama3  
- **Deployment**: Docker, AWS, GitHub Actions  
- **Testing**: Pytest, Pytest-Asyncio, httpx.AsyncClient

### **How to run it locally**

Clone the repo:  
```bash
git clone https://github.com/your-username/gen-ai-book-manager.git  
cd gen-ai-book-manager
```

Install dependencies:  
```bash
pip install -r requirements.txt
```

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

### **Run Llama3 Locally with Ollama**  
To enable AI summaries and recommendations, make sure Llama3 is running via Ollama.

#### **Steps to install and run Ollama with Llama3**

1. **Pull the Ollama image**  
   ```bash
   docker pull ollama/ollama
   ```

2. **Run the Ollama container**  
   ```bash
   docker run -d -p 11434:11434 --name ollama ollama/ollama
   ```

3. **Shell into the container**  
   ```bash
   docker exec -it ollama bash
   ```

4. **Pull the Llama3 model**  
   ```bash
   ollama pull llama3
   ```

5. **Done!**  
   The model will be available at:  
   `http://localhost:11434`

> The FastAPI app connects to this endpoint using the environment variable `MODEL_BASE_URL`.

#### **Update your `.env` file**

Add the following line to your `.env` file:

```env
MODEL_BASE_URL=http://localhost:11434
```

This ensures the app knows where to send requests for AI-generated summaries and recommendations.

### **Running the Tests**

We’ve built a fully **async-powered test suite** using `pytest`, `pytest-asyncio`, and `httpx.AsyncClient`. These tests hit real API endpoints and run against a real PostgreSQL test database.

To run **all tests**:

```bash
pytest
```

Want to run just one specific test?

```bash
pytest -k test_create_book
```

The test database is automatically set up using `create_db.py`, and each test gets its own fresh database session.

### Deployment

The infrastructure setup for deploying this project is managed in a separate repository using Terraform and AWS services.

**Check out the deployment setup here**: [gen-ai-book-manager-cloud-infrastructure](https://github.com/ashu8894/gen-ai-book-manager-cloud-infrastructure)


### **What’s Next?**  
- ✅ **Phase 1**: Database & AI Setup (completed)  
- ✅ **Phase 2**: API Development & Security (completed)  
- ✅ **Phase 3**: AI Integration (completed) 
- ✅ **Phase 4**: Testing (Completed)
- ✅ **Phase 5**: Deployment (Completed)