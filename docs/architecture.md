# StudyPal Architecture Documentation

## 1. System Architecture Overview

StudyPal is implemented as a **modular monolith** combining a high-performance FastAPI backend with a modern React/TypeScript single-page application (SPA).

```
+-------------------------------------------------------------+
|                      React 19 SPA                           |
|       (Vite + TypeScript + Tailwind CSS + Recharts)         |
+------------------------------+------------------------------+
                               | HTTPS / JSON (REST API)
+------------------------------v------------------------------+
|                   FastAPI Modular Monolith                  |
|  - Auth & Security (/api/v1/auth)                           |
|  - Course Management (/api/v1/courses)                      |
|  - Ingestion Engine (/api/v1/courses/{id}/documents)        |
|  - Grounded Search Engine (/api/v1/courses/{id}/search)     |
|  - Dynamic Topic Discovery (/api/v1/courses/{id}/topics)    |
|  - Curated Quiz Engine (/api/v1/courses/{id}/quizzes)       |
|  - BKT Learning Progress (/api/v1/courses/{id}/progress)    |
|  - Explainable Recommender (/api/v1/courses/{id}/recs)      |
+------------------------------+------------------------------+
                               |
       +-----------------------+-----------------------+
       |                                               |
+------v---------------------+          +--------------v---------------+
|    ML & Content Engines    |          |   Relational Persistence     |
| - PyMuPDF Text Extractor   |          | - PostgreSQL / SQLite        |
| - Paragraph-aware Chunker  |          | - SQLAlchemy 2.0 ORM         |
| - TF-IDF Lexical Ranker    |          | - Alembic Database Schema    |
| - SentenceTransformer Dense|          +------------------------------+
| - Min-Max Hybrid Fusion    |
| - K-Means++ Topic Clusters |
| - Supervised Weakness Clf  |
| - Bayesian Knowledge Trace |
+----------------------------+
```

## 2. Dependency Direction and Clean Boundaries

The project enforces strict separation of concerns across tiers:
1. **API Routers (`app/api/v1/`)**: Expose validated HTTP contracts using Pydantic request/response schemas. Routers delegate directly to application services and ML engines, and perform no heavy compute inside the event loop.
2. **ML Modules (`app/ml/`)**: Completely decoupled from FastAPI request objects. Can be executed, evaluated, and unit-tested in isolation via command-line scripts or automated test runners.
3. **Database Repositories & Models (`app/db/`)**: Enforce data integrity, foreign keys, cascade deletes, and relational indexes.
4. **Security & Dependencies (`app/core/`, `app/dependencies.py`)**: Centralized password hashing, JWT generation, and course-level ownership verification.

## 3. Data Flow
1. **Upload**: User uploads `.pdf` or `.txt`.
2. **Extraction & Chunking**: PyMuPDF extracts clean text; paragraph-aware chunker produces bounded segments preserving source provenance and page numbers.
3. **Encoding**: Batched unit-normalized embeddings are generated via `all-MiniLM-L6-v2` alongside course-fitted TF-IDF matrices.
4. **Clustering**: K-Means with K-Means++ discovers topic groups and extracts high-weighted TF-IDF keywords for readable topic labels.
5. **Practice**: Student answers curated questions; server validates correctness and atomically computes Bayesian Knowledge Tracing updates.
6. **Recommendation**: Recommendation engine scores revision priority:
   $$\text{revision\_score} = w_m \cdot (1 - \text{mastery}) + w_w \cdot \text{weakness\_prob} + w_r \cdot \text{recency}$$
   and links each recommendation directly to supporting note passages.
