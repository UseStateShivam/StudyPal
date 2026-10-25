# StudyPal Security and Privacy Documentation

## 1. Authentication & Session Management
- **Password Security**: Passwords hashed using `bcrypt` (work factor 12) with salt. Plaintext passwords are never logged or stored.
- **Tokens**: Stateless signed JSON Web Tokens (JWT) using HMAC-SHA256 (`HS256`).
- **Token Claims**: Subject (`sub`), issued-at (`iat`), and expiration (`exp`, configurable, defaults to 24 hours).

## 2. Authorization & Data Isolation
- **Course-Scoped Isolation**: All document, search, topic, quiz, and learner state queries strictly enforce user ownership checks (`get_user_course` dependency).
- **Cross-User Protection**: Attempting to query, mutate, or search content in a course owned by another student immediately raises `HTTP 403 Forbidden`.

## 3. Input Validation & File Handling
- **File Types**: Whitelist validation restricted strictly to `.pdf` and `.txt`.
- **Upload Size Limit**: 25 MB default ceiling.
- **Path Traversal Protection**: Files are assigned unique internal UUID filenames and stored in configured storage directories; raw user filenames are never used as filesystem paths.
- **Execution Prevention**: Uploaded files are strictly processed as static text or PDF streams; script execution and active macros are disabled.
- **SQL Injection Prevention**: All queries use SQLAlchemy 2.0 ORM parameterization.

## 4. Groundedness & Model Safety
- **Zero Generative Hallucination**: StudyPal does not send student notes to remote third-party generative AI endpoints or commercial LLMs. Retrieval produces exact, traceable quotations from local student materials.
- **Fair Assessment**: Bayesian Knowledge Tracing is documented as a probabilistic estimate of practice mastery, not a measurement of general intelligence.
