# StudyPal REST API Documentation

The StudyPal API is versioned under `/api/v1` and provides interactive OpenAPI documentation at `/docs` and ReDoc at `/redoc`.

## Base URLs
- Local Development: `http://localhost:8000/api/v1`
- OpenAPI Specification: `http://localhost:8000/openapi.json`
- Health Liveness: `http://localhost:8000/health/live`
- Health Readiness: `http://localhost:8000/health/ready`

---

## 1. Authentication (`/auth`)

### `POST /auth/register`
Create a new student account.
- **Request Body**:
  ```json
  {
    "email": "student@example.edu",
    "password": "securepassword123",
    "display_name": "Student Name"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": "uuid-string",
      "email": "student@example.edu",
      "display_name": "Student Name",
      "is_active": true,
      "created_at": "2026-10-26T00:00:00Z"
    }
  }
  ```

### `POST /auth/login`
Authenticate with OAuth2 password flow (`application/x-www-form-urlencoded`).
- **Form Fields**: `username` (email), `password`.
- **Response (200 OK)**: Returns JWT bearer token and user profile.

### `GET /auth/me`
Retrieve currently authenticated student profile using `Authorization: Bearer <token>`.

---

## 2. Courses (`/courses`)

### `POST /courses`
Create a new study course.
- **Request Body**:
  ```json
  {
    "name": "Machine Learning Fundamentals",
    "description": "Supervised and unsupervised study material."
  }
  ```

### `GET /courses`
List all courses owned by authenticated user.

### `GET /courses/{course_id}`
Retrieve course details, document counts, and topic counts.

### `PATCH /courses/{course_id}`
Update course name or description.

### `DELETE /courses/{course_id}`
Delete course and all cascading documents, chunks, topics, and quiz attempts.

---

## 3. Documents (`/courses/{course_id}/documents`)

### `POST /courses/{course_id}/documents`
Upload `.pdf` or `.txt` lecture notes (`multipart/form-data`).
- Maximum upload size: 25 MB.
- Background worker extracts text, chunks with paragraph awareness, and generates embeddings.

### `GET /courses/{course_id}/documents`
List uploaded documents and their processing status (`pending`, `processing`, `completed`, `failed`).

### `DELETE /documents/{document_id}`
Delete document, storage file, and indexed chunks.

---

## 4. Topics (`/courses/{course_id}/topics`)

### `GET /courses/{course_id}/topics`
List discovered K-Means clusters and representative keywords.

### `PATCH /topics/{topic_id}`
Rename a topic label.
- **Request Body**: `{"label": "New Topic Title"}`

### `GET /topics/{topic_id}/related-content`
Retrieve representative note chunks and contributing source documents.

---

## 5. Search (`/courses/{course_id}/search`)

### `POST /courses/{course_id}/search`
Execute query retrieval across indexed course chunks without generative hallucination.
- **Request Body**:
  ```json
  {
    "query": "How does gradient descent minimize loss?",
    "retrieval_method": "hybrid",
    "top_k": 5
  }
  ```
- **Response**: Top ranked passages with source document names, page numbers, and similarity scores.

---

## 6. Quizzes (`/courses/{course_id}/quizzes`)

### `POST /courses/{course_id}/quizzes/sessions`
Start a diagnostic quiz session randomly selecting questions without replacement.
- **Request Body**: `{"question_count": 5, "topic_id": null}`

### `POST /quiz-sessions/{session_id}/answers`
Submit an answer. Evaluates correctness on server and updates Bayesian Knowledge Tracing state.
- **Request Body**:
  ```json
  {
    "question_id": "uuid-string",
    "selected_option_index": 1,
    "response_time_ms": 12000
  }
  ```

### `POST /quiz-sessions/{session_id}/submit`
Complete quiz session and receive score summary.

---

## 7. Progress & Recommendations

### `GET /courses/{course_id}/progress`
Returns overall course mastery, question accuracy, and mastery timeline points.

### `GET /courses/{course_id}/recommendations`
Returns ranked revision topics combining BKT mastery, weakness classifier predictions, and time since last practice, linked directly to source passages.
