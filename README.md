# 🧠 RAG Evaluation Service (FastAPI)

A **production-ready, reusable Evaluation Microservice** for **RAG / Chatbot systems**, designed to be shared across **multiple projects** without requiring **ground-truth reference answers**.

This service evaluates:
- Retriever quality
- Hallucination risk
- Answer relevance
- Cost & latency (optional)

All evaluations run **asynchronously**, without blocking user responses.

---

## 🚀 Key Features

- ✅ Production-safe (no reference answers required)
- ✅ Asynchronous, non-blocking evaluation
- ✅ Multi-project & multi-environment support
- ✅ RAGAS-based metrics
- ✅ LLM-as-Judge (pluggable)
- ✅ Alerting with thresholds
- ✅ Scalable & extensible
- ✅ Kafka-ready (can be added later without API changes)

---

## 🏗️ Architecture Overview
```text
RAG Application
|
| POST /v1/evaluate (fire & forget)
v
Evaluation Service (FastAPI)
|
| Background Task
v
Evaluation Engine
├── RAGAS Metrics
├── LLM-as-Judge
├── Rules Engine
|
v
Metrics Database
|
v
Alerts / Dashboards
```


---

## 📁 Project Structure
```
.
├─ Dockerfile
├─ README.md
├─ requirements.txt
├─ .env
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ api/
│  │  └─ routes/
│  │     ├─ __init__.py
│  │     ├─ eval.py
│  │     └─ health.py
│  ├─ config/
│  │  ├─ __init__.py
│  │  └─ config.py
│  ├─ evaluators/
│  │  ├─ __init__.py
│  │  └─ ragas_eval.py
│  ├─ schemas/
│  │  ├─ __init__.py
│  │  ├─ evaluation_event.py
│  │  ├─ evaluation_metric.py
│  │  ├─ evaluation_request.py
│  │  └─ health_response.py
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ db_service.py
│  │  ├─ evaluation_service.py
│  │  └─ notifier_service.py
│  └─ utils/
│     ├─ __init__.py
│     └─ logger.py
├─ configs/
│  └─ thresholds.yaml
└─ db/



---

## 📦 Tech Stack

- **FastAPI** – API layer
- **RAGAS** – RAG evaluation metrics
- **PostgreSQL** – Metrics storage
- **SQLAlchemy** – ORM
- **FastAPI BackgroundTasks** – Async execution
- **YAML** – Project-level configuration

---

## 🚀 Quickstart

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## 🧪 Metrics Supported

### Production (No Reference Required)

| Metric | Purpose |
|------|--------|
| Context Precision | Retriever relevance |
| Faithfulness | Hallucination detection |
| Answer Relevancy | Answer quality |
| Latency | Performance monitoring |
| Cost | Budget control |

### Offline / Benchmarking

| Metric | Purpose |
|------|--------|
| Context Recall | Retriever coverage (requires reference data) |

---

## 🔌 API Contract

### `POST /v1/evaluate`

```json
{
  "project_id": "rbac_chatbot",
  "environment": "prod",
  "request_id": "uuid",
  "question": "How do I assign a role?",
  "answer": "You can assign a role by...",
  "contexts": [
    "Roles are assigned via...",
    "Admins can manage permissions..."
  ],
  "metadata": {
    "retriever": "hybrid",
    "k": 5,
    "model": "gpt-4o-mini",
    "latency_ms": 1820,
    "cost_usd": 0.0041
  }
}

```bash
curl -X POST "http://localhost:8000/v1/evaluate" -H "Content-Type: application/json" -d '{
  "project_id": "rbac_chatbot",
  "environment": "prod",
  "request_id": "uuid",
  "question": "How do I assign a role?",
  "answer": "You can assign a role by...",
  "contexts": [
    "Roles are assigned via...",
    "Admins can manage permissions..."
  ],
  "metadata": {
    "retriever": "hybrid",
    "k": 5,
    "model": "gpt-4o-mini",
    "latency_ms": 1820,
    "cost_usd": 0.0041
  }
}'
```

---
### Response
```json
{
  "status": "accepted",
  "event_id": "uuid"
}
```

---

## Contributing

Contributions are welcome! Please open issues for bugs or feature requests and submit pull requests with tests and clear descriptions. Follow the repository style and run the test suite where applicable.

## License

This project is available under the MIT License. Replace with your preferred license if different.


