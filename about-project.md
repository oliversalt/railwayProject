# 🧠 Word Vector API – Embedding-Based Semantic Word Math

This is a backend API built with **FastAPI** and **Gensim**, designed to run on **Railway**. It loads 100-dimensional word embeddings into memory at startup and exposes endpoints for semantic word vector operations (e.g. `king - man + woman → queen`).

## ✅ Features

- Cosine similarity between any two words  
- Word vector arithmetic (e.g. a - b + c = ?)  
- Find top-N most similar words to a given word  
- GloVe model loaded into **server RAM**, not sent to the client  
- Simple REST API with JSON responses

---

## 🧠 Key Design Notes

- Uses `glove-wiki-gigaword-100` via `gensim.downloader` (about ~100MB)
- Model is loaded once at **server startup** and stays in memory for fast access
- No database required — all word vectors live in RAM
- Not suitable for **serverless** platforms like Vercel (which can't retain RAM state between requests)
- Instead, we deploy the API to **Railway**, which maintains a persistent process

---

## 🖥️ How Users Interact

- Users do **not** download or store vectors — they only send requests to the backend
- The backend processes these using in-memory vector math and returns results
- A frontend **can** be built separately and connected via API

---

## 📦 API Endpoints

| Endpoint                        | Functionality                               |
|--------------------------------|---------------------------------------------|
| `/similarity?word1=...&word2=...` | Returns cosine similarity between two words |
| `/analogy?a=...&b=...&c=...`      | Solves word vector math a - b + c           |
| `/neighbors?word=...&topn=10`     | Returns top N most similar words            |

---

## 🛠️ Deployment

- **Backend only (for now)** is hosted on [Railway](https://railway.app)
- The API is accessible via browser/HTTP (returns JSON)
- A frontend can later be added and hosted separately

---

## 🚧 Project Roadmap

**Step-by-step development plan**:

### ✅ Step 1 – Backend API with Preloaded Model
- [x] Build FastAPI app (`main.py`)
- [x] Load GloVe model into RAM on startup
- [x] Expose `/similarity`, `/analogy`, `/neighbors` endpoints
- [x] Add vocabulary endpoint for model info
- [x] Create requirements.txt and README.md
- [x] Add test script and startup script

### 🟡 Step 2 – Local testing
- [ ] Run with Uvicorn locally
- [ ] Test accuracy and performance of endpoints
- [ ] Handle edge cases (missing words, bad input)

### 🟢 Step 3 – Host API on Railway
- [ ] Create Railway project
- [ ] Deploy FastAPI app
- [ ] Confirm model loads on server and endpoints respond

### 🟢 Step 4 – Optional Frontend (future)
- [ ] Build a React or static HTML interface
- [ ] Host it on Vercel or inside FastAPI `/static`
- [ ] Connect UI to backend API

---

## 🧠 Copilot Notes

- All word vectors are normalized on load → cosine similarity is a dot product
- No database is used — vectors are stored in memory as a Gensim model
- The model should not be reloaded per request — keep it global

---

Let me know if you want setup scripts, `.env` examples, or deployment commands included.

