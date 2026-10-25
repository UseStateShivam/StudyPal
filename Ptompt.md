# MASTER ENGINEERING PROMPT — STUDYPAL
## Build a Production-Quality, ML-Powered Personalised Study Recommendation Platform

You are acting as a **senior software engineer, machine learning engineer, ML researcher, backend architect, frontend engineer, QA engineer, and technical documentation writer**.

Your task is to design, implement, test, document, and package a complete software project named **StudyPal**.

This is an undergraduate engineering capstone and a serious resume project. The final result must demonstrate real machine learning, sound software architecture, full-stack development, reproducible experimentation, responsible data handling, and professional engineering practices.

Do not produce a toy demonstration, a static UI, a collection of disconnected Jupyter notebooks, or a simple CRUD application with superficial ML features. Build a coherent, working, end-to-end application.

You are expected to write the code, create the project files, run the application where possible, execute tests, resolve errors, and produce a polished README and final technical documentation.

---

# 1. Project overview

## 1.1 Project name

**StudyPal — Personalised Learning and Intelligent Study Recommendation Platform**

## 1.2 Core problem

Students accumulate lecture notes, PDFs, slides, reference material, and other course resources. However, these materials are fragmented and difficult to navigate.

Students frequently struggle with five problems:

1. Finding relevant explanations of a concept across multiple documents.
2. Identifying which chapters and concepts are related.
3. Determining which topics they understand poorly.
4. Deciding what they should revise next.
5. Tracking whether their understanding of a topic improves over time.

Traditional file search finds keywords but does not necessarily identify semantically related passages. Generic question-answering tools may not be restricted to a student's own course material. Ordinary quiz applications do not necessarily maintain topic-level mastery estimates or personalise revision based on learning history.

StudyPal must combine document retrieval, unsupervised learning, supervised machine learning, knowledge tracing, and recommendation logic into one integrated platform.

## 1.3 Product vision

Build a web application in which a student can:

- Create an account and manage a course.
- Upload PDF and plain-text study materials.
- Extract, clean, chunk, and index document content.
- Automatically discover groups of related content.
- Browse topic groups and the source documents behind them.
- Ask a topic-based question and retrieve relevant passages from their own uploaded material.
- Take short quizzes associated with specific topics.
- View quiz history, mastery estimates, and predicted weak areas.
- Receive a ranked, personalised revision plan.
- Open the original document and inspect the source passage supporting each recommendation.
- Track progress over multiple study sessions.

The platform must remain useful for students who have no quiz history. In this cold-start situation, it should offer content-based recommendations and clearly explain that personalised learner predictions are not yet available.

## 1.4 Primary engineering objective

Implement a reproducible ML pipeline that transforms:

**Uploaded course material + student questions + quiz history → structured content representations + topic groups + learner mastery estimates → ranked, explainable revision recommendations.**

Every major stage must have an identifiable input, output, implementation, validation strategy, and documented limitations.

## 1.5 Scope boundaries

The initial release is a working prototype for a limited course domain and a small student pilot.

The core project must not depend on:

- Paid external APIs.
- Proprietary LLMs.
- An always-on cloud GPU.
- Third-party hosted embedding APIs.
- External generative AI for answering questions.
- Hardcoded model predictions.
- Fake evaluation results.
- Pretrained recommendation models that replace the project's own modelling work.

Open-source libraries are permitted as implementation tools. For example, sentence-transformer models may be used as pretrained text encoders, but the project must independently implement, configure, evaluate, and compare its retrieval, clustering, supervised classification, knowledge-tracing, and recommendation components.

Do not claim to have trained a transformer from scratch. That is not a requirement of this project.

---

# 2. Mandatory working principles

Follow these rules throughout implementation.

## 2.1 Build working software, not just a plan

Inspect the existing repository first. Determine whether it is empty, partially implemented, or already contains useful work.

If a repository already exists, preserve useful components and avoid destructive rewrites without a clear reason.

If it is empty, create the complete repository structure and all required files.

Do not stop after generating architecture diagrams, pseudocode, schemas, or implementation plans. Continue through implementation, integration, testing, and documentation.

## 2.2 No fake functionality

Every user-facing feature must connect to real backend logic.

Examples:

- Uploading a file must persist the file metadata and process its contents.
- Searching must use the implemented retrieval engine.
- Topic discovery must execute the actual clustering pipeline.
- Quiz submissions must be recorded in the database.
- Knowledge tracing must update mastery estimates.
- Recommendations must be computed from actual content and learner-engine outputs.
- Progress charts must use stored quiz and mastery data.
- Model evaluation must run against identifiable datasets and produce real metrics.

Do not hardcode sample recommendations and present them as model-generated results.

Demo fixtures are acceptable only when clearly labelled as sample or synthetic data.

## 2.3 No fabricated results

Do not invent accuracy, F1-score, Precision@5, Recall@5, clustering quality, latency, dataset size, or other experimental findings.

If a dataset has not been collected or an experiment has not been executed, describe the result as pending.

Separate:

- Implemented functionality.
- Tests that have passed.
- Tests that have failed.
- Experiments that have actually run.
- Planned experiments.
- Synthetic demonstrations.
- Known limitations.

## 2.4 Keep the implementation appropriately scoped

This is a five-week undergraduate project, not an enterprise SaaS platform requiring a large infrastructure team.

Use modular, maintainable architecture without unnecessary microservices, Kubernetes, distributed training, elaborate event streaming, or multiple independent deployments.

Prefer a **modular monolith**: one FastAPI application with clearly separated domain modules and background processing that can run locally.

Keep abstractions justified by actual requirements.

## 2.5 Make reasonable decisions independently

Do not repeatedly ask the user to choose between routine implementation details.

Use the technical decisions in this prompt as the default specification.

If an external dependency, model download, dataset, or service is unavailable, implement a documented fallback where feasible. Record the limitation rather than silently substituting a different algorithm.

## 2.6 Work in verifiable stages

After each major implementation stage:

1. Summarise what was implemented.
2. List the important files created or modified.
3. Run the relevant tests.
4. Report failures accurately.
5. Fix failures before progressing when practical.
6. Update documentation to reflect the actual implementation.

Do not claim that a command or test passed unless you actually ran it and observed the result.

---

# 3. Technology stack

Use the following stack unless an existing repository has a compelling, documented reason to differ.

## 3.1 Backend

- Python 3.12 or a compatible, supported Python 3.x version.
- FastAPI.
- Uvicorn.
- Pydantic v2 and pydantic-settings.
- SQLAlchemy 2.x.
- Alembic for database migrations.
- PostgreSQL as the primary database.
- SQLite as an optional lightweight development and testing backend where supported.
- pytest for automated testing.
- HTTPX for API testing.
- Ruff for linting and formatting.
- mypy or appropriately strict type checks for critical modules.

Pin compatible dependency versions in the dependency-management files.

Do not blindly use the newest version of every package if doing so creates incompatibilities.

## 3.2 Machine learning and data processing

Use:

- NumPy.
- pandas.
- scikit-learn.
- sentence-transformers or a compatible open-source sentence-embedding library.
- PyTorch as required by the embedding library.
- SciPy where useful for sparse matrices and scientific operations.
- joblib for supported model persistence.
- Matplotlib for offline evaluation plots where appropriate.

The embedding model must be configurable. Select a compact, locally executable sentence encoder suitable for semantic similarity on a CPU.

Use a specific, documented model identifier and revision where practical. Do not download a model on every application startup.

Support model caching and offline operation after the required model assets have been downloaded.

If the preferred model cannot be downloaded, allow a clearly identified lexical-retrieval-only mode. Do not pretend that semantic retrieval is operating when embeddings are unavailable.

## 3.3 Document processing

Use suitable libraries for:

- PDF text extraction.
- Plain-text ingestion.
- Text normalization.
- Chunking.
- Metadata extraction.

PyMuPDF is a reasonable PDF extraction choice.

Do not implement OCR in the initial scope. Detect scanned or image-only PDFs where feasible and return a clear message explaining that OCR is unsupported.

Preserve source document names and available page numbers throughout the ingestion pipeline.

## 3.4 Frontend

Use:

- React.
- TypeScript.
- Vite.
- A consistent component system, preferably Tailwind CSS with a suitable accessible component library.
- A charting library such as Recharts.
- A typed API client.
- React Router or an equivalent routing solution.
- A lightweight, justified state-management approach.

Use the current stable versions that work together and lock dependencies.

The frontend must be a real application with functional forms, loading states, error states, navigation, data fetching, and meaningful visualisations.

Do not build a static HTML mockup or a collection of nonfunctional screens.

## 3.5 Persistence and indexing

Use PostgreSQL for structured data.

Store:

- Users.
- Courses.
- Documents and ingestion status.
- Document chunks.
- Topic assignments.
- Quiz questions.
- Quiz attempts.
- Per-topic mastery state.
- Recommendation snapshots if useful.
- Model and evaluation metadata where appropriate.

For the initial scope, store embedding vectors as serialised arrays or a suitable local vector representation and use a lightweight exact cosine-similarity index.

Keep the retrieval interface independent of its storage implementation so that a more scalable vector database can be introduced later.

Do not add a separate vector database unless the implemented requirements justify it.

Avoid repeatedly serialising and deserialising all embeddings on every request. Load and cache appropriate indices, and define an explicit invalidation or rebuild strategy when documents change.

## 3.6 Development and deployment

Include:

- Docker.
- Docker Compose.
- A multi-stage or otherwise sensibly structured Dockerfile where appropriate.
- A `.env.example` file.
- `.gitignore`.
- Database migrations.
- A health endpoint.
- CI through GitHub Actions.
- Structured logging.
- Reproducible development and test instructions.

The complete system should be runnable locally with documented commands.

The default development environment must not require paid services or a GPU.

---

# 4. Repository architecture

Create a clean monorepo with a structure broadly equivalent to the following. Adapt individual filenames when needed, but preserve the separation of responsibilities.

```text
studypal/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── pyproject.toml
├── Makefile
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   ├── dependencies.py
│   │   │
│   │   ├── api/
│   │   │   ├── router.py
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── courses.py
│   │   │       ├── documents.py
│   │   │       ├── topics.py
│   │   │       ├── search.py
│   │   │       ├── quizzes.py
│   │   │       ├── learning.py
│   │   │       ├── recommendations.py
│   │   │       └── health.py
│   │   │
│   │   ├── core/
│   │   │   ├── security.py
│   │   │   ├── exceptions.py
│   │   │   └── middleware.py
│   │   │
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── models/
│   │   │
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── workers/
│   │   │
│   │   └── ml/
│   │       ├── common/
│   │       ├── ingestion/
│   │       ├── content/
│   │       ├── learner/
│   │       ├── recommender/
│   │       └── evaluation/
│   │
│   ├── alembic/
│   │   └── versions/
│   └── tests/
│       ├── unit/
│       ├── integration/
│       ├── api/
│       ├── ml/
│       ├── security/
│       └── conftest.py
│
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── courses/
│   │   │   ├── documents/
│   │   │   ├── topics/
│   │   │   ├── search/
│   │   │   ├── quizzes/
│   │   │   ├── progress/
│   │   │   └── recommendations/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── routes/
│   │   ├── types/
│   │   └── main.tsx
│   └── tests/
│
├── data/
│   ├── README.md
│   ├── sample/
│   └── generated/
│
├── scripts/
│   ├── seed_demo_data.py
│   ├── run_evaluation.py
│   ├── train_models.py
│   ├── rebuild_indices.py
│   └── validate_environment.py
│
├── models/
│   ├── README.md
│   └── .gitkeep
│
├── reports/
│   ├── README.md
│   └── .gitkeep
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── ml_methodology.md
│   ├── evaluation.md
│   ├── database.md
│   ├── security.md
│   └── development.md
│
└── .github/
    └── workflows/
        └── ci.yml
```

This is a target structure, not an instruction to create empty directories indiscriminately.

Only create files that have a purpose. All important modules must contain implemented logic rather than placeholder functions.

## 4.1 Architectural rules

Use the following dependency direction:

**API routes → application services → domain/ML components and repositories → persistence or model artefacts.**

Enforce these rules:

- API routes must not contain substantial ML algorithms.
- ML modules must not depend on FastAPI request objects.
- Database repositories must not contain recommendation-ranking logic.
- Frontend components must not implement ML calculations.
- Configuration must be centralised.
- Shared request and response schemas must be explicit.
- Business logic must be testable without running the entire web application.
- External dependencies must be injectable where practical.
- Avoid circular imports.
- Avoid global mutable state.
- Avoid a single enormous service file containing the entire application.
- Avoid needless abstraction layers that merely forward function calls.

The system must remain a modular monolith. A separate process for long-running document ingestion is acceptable, but a distributed microservice architecture is not required.

---

# 5. Database design

Design a normalised relational schema with SQLAlchemy models, foreign keys, indexes, uniqueness constraints, timestamps, and Alembic migrations.

Document all important entities and relationships.

## 5.1 User

Required fields:

- ID.
- Email, unique and normalised.
- Secure password hash.
- Display name, where appropriate.
- Created timestamp.
- Updated timestamp.
- Active or disabled status.

Never store plaintext passwords.

## 5.2 Course

Required fields:

- ID.
- Owner ID.
- Course name.
- Optional description.
- Created timestamp.
- Updated timestamp.

A user must only be able to access their own courses unless an explicit sharing feature is implemented.

## 5.3 Document

Required fields:

- ID.
- Course ID.
- Original filename.
- Safe internal storage identifier.
- File type.
- File size.
- Content checksum.
- Processing status.
- Error details suitable for display without leaking internal paths.
- Number of pages where available.
- Number of chunks created.
- Upload timestamp.
- Processing completion timestamp.
- Relevant model or pipeline version.

Suggested statuses:

- `pending`
- `processing`
- `completed`
- `failed`

Prevent accidental duplicate ingestion where appropriate using checksums and course-level uniqueness rules. Do not silently discard a document when the UI expects a new upload; explain duplicate handling.

## 5.4 Document chunk

Required fields:

- ID.
- Document ID.
- Course ID or another safe way to enforce course-scoped access.
- Chunk index.
- Text content.
- Start and end character offsets where available.
- Page number or source location where available.
- Token or word count where useful.
- Topic assignment, nullable initially.
- Creation timestamp.
- Embedding reference or storage representation.
- Content-index version where useful.

Add indexes for course-level retrieval and document-level lookup.

Avoid embedding large vector blobs inside API responses.

## 5.5 Topic

Required fields:

- ID.
- Course ID.
- Stable cluster or topic identifier within the relevant model version.
- Human-readable label.
- Optional descriptive keywords.
- Number of assigned chunks.
- Model version.
- Created and updated timestamps.

Allow a user to edit a topic label without altering the underlying cluster assignments.

Do not assume cluster IDs are globally stable between retraining runs.

## 5.6 Quiz question

Required fields:

- ID.
- Course ID.
- Topic ID.
- Question text.
- Answer options.
- Correct answer.
- Optional explanation.
- Difficulty label, if available.
- Source or provenance.
- Active status.
- Creation timestamp.

For the initial version, support multiple-choice questions.

Use deterministic validation for answer options and correct-answer references.

Do not generate questions from arbitrary text and then claim their correctness has been validated. A small curated question bank is preferable.

## 5.7 Quiz attempt

Required fields:

- ID.
- User ID.
- Course ID.
- Question ID.
- Topic ID.
- Submitted answer.
- Correctness.
- Response time in milliseconds, where collected.
- Attempt timestamp.
- Relevant model or knowledge-state version if needed.

Keep attempt records immutable after submission. Corrections to quiz content must not rewrite historical student answers.

## 5.8 Learner topic state

Required fields:

- ID.
- User ID.
- Course ID.
- Topic ID.
- Current mastery probability.
- Number of attempts.
- Number of correct answers.
- Last practice timestamp.
- Last updated timestamp.
- Knowledge-tracing parameter version.

Enforce uniqueness for each user/course/topic combination.

## 5.9 Model and evaluation metadata

Where useful, track:

- Model type.
- Model version.
- Training or fitting dataset identifier.
- Configuration.
- Training timestamp.
- Artifact path or artifact identifier.
- Evaluation results.
- Active status.

Do not store secrets or sensitive training data in model metadata.

## 5.10 Migration and transaction requirements

- Create migrations for all schema changes.
- Never rely exclusively on `create_all()` for production-style schema management.
- Ensure quiz submission and learner-state updates behave consistently.
- Use transactions where a failed operation must not leave partial state.
- Enforce access control at the service or repository boundary.
- Include tests for foreign keys, uniqueness, rollback behaviour, and ownership restrictions.

---

# 6. User authentication and security

Implement authentication appropriate for a local multi-user web application.

The application must support:

- User registration.
- Login.
- Logout.
- Authenticated API requests.
- Current-user retrieval.
- Ownership-based authorisation.
- Secure password hashing using a maintained password-hashing library.
- Configurable token expiration.
- Appropriate credential handling.

Use a well-established authentication mechanism and document its trade-offs. If using JWTs, validate signatures, expiration, and expected claims. If using cookies, configure appropriate `HttpOnly`, `SameSite`, and `Secure` settings for the deployment environment and handle CSRF risks appropriately.

Do not place sensitive tokens in ordinary browser local storage without carefully considering the security implications.

Implement:

- Input validation.
- File upload limits.
- Allowed file extensions and content-type checks.
- Safe internal filenames.
- Protection against path traversal.
- Database parameterisation through the ORM.
- CORS restrictions based on configuration.
- Request-size limits.
- Safe error responses.
- Rate limiting or a documented local-prototype alternative for sensitive endpoints.
- Protection against cross-user data access.
- Secret management through environment variables.

Uploaded content must be treated as untrusted input.

Do not execute uploaded files, embedded scripts, or document instructions.

Do not expose raw stack traces, credentials, filesystem paths, or internal configuration in public API responses.

Provide a clear security limitations section. Do not claim that a prototype has undergone a professional penetration test unless that has actually occurred.

---

# 7. Content ingestion engine

Implement a complete document-processing pipeline.

## 7.1 Supported formats

Initial supported formats:

- PDF documents containing extractable text.
- Plain-text `.txt` documents.

Unsupported formats must be rejected with a useful message.

Do not pretend that scanned PDFs or handwritten notes are processed successfully.

## 7.2 Ingestion pipeline

Implement the following sequence:

1. Validate the upload.
2. Verify file size and supported format.
3. Generate a safe internal filename.
4. Compute a content checksum.
5. Store the document and metadata.
6. Create a processing job or mark the document as processing.
7. Extract the document text.
8. Detect empty or unusable extracted text.
9. Normalise whitespace and common extraction artefacts.
10. Preserve paragraph boundaries and page-level source information where possible.
11. Split the content into manageable chunks.
12. Remove unusable chunks according to documented rules.
13. Generate TF-IDF-compatible text representations.
14. Generate semantic embeddings when the configured embedding model is available.
15. Store chunk metadata and vector representations.
16. Fit or update the topic-clustering pipeline at the appropriate course scope.
17. Save topic assignments and topic labels.
18. Update document processing status.
19. Make the document searchable only after the required indexing steps succeed.
20. Record useful processing metrics and errors.

Do not silently mark failed ingestion as successful.

## 7.3 Chunking strategy

Use paragraph-aware chunking rather than splitting blindly at arbitrary character counts.

Use a configurable target of approximately 150–300 words per chunk, with a reasonable maximum length and optional overlap.

The exact limits must be configurable.

Requirements:

- Avoid empty chunks.
- Avoid duplicating large amounts of text.
- Preserve source document IDs.
- Preserve page numbers where possible.
- Preserve chunk order.
- Handle short documents.
- Handle unusually long paragraphs.
- Prevent a single document from exhausting memory.
- Keep the original extracted text available where practical.
- Make chunking deterministic for the same input and configuration.

Document why the selected chunk size is appropriate and evaluate alternatives if time permits.

## 7.4 Idempotency and reprocessing

The same file must not accidentally create duplicate chunks every time a user retries an upload.

Provide an explicit reprocessing mechanism.

If the embedding model or chunking configuration changes, track the relevant index version and rebuild derived data consistently.

A failed reprocessing operation must not leave the course in an inconsistent partially indexed state.

## 7.5 Processing status

The frontend must display:

- Pending.
- Processing.
- Completed.
- Failed.

Show a useful error message for failures.

Long-running extraction, embedding, or clustering work should not block an HTTP request indefinitely. Use a simple background-processing approach suitable for a single-machine application.

If using a worker process, document how it is started and monitored.

---

# 8. Content engine: TF-IDF, semantic embeddings, and hybrid retrieval

This is one of the core research components. Implement all three retrieval approaches and compare them.

## 8.1 TF-IDF retrieval

Implement TF-IDF using scikit-learn.

Requirements:

- Fit the vectoriser on the indexed corpus for the relevant course.
- Configure tokenisation and n-gram handling sensibly.
- Handle English technical terms, abbreviations, and sparse documents.
- Store or persist the fitted vectoriser.
- Represent each chunk as a sparse vector.
- Transform queries using the same fitted vectoriser.
- Compute cosine similarity between the query and candidate chunks.
- Return the top-k ranked results.
- Exclude empty or unusable results.
- Handle unknown terms and zero-vector queries gracefully.

Do not refit the TF-IDF vectoriser independently for each query.

## 8.2 Sentence-embedding retrieval

Use a compact, locally runnable open-source sentence encoder.

Requirements:

- Keep model configuration separate from business logic.
- Load the model once per worker where practical.
- Generate embeddings in batches.
- Use deterministic inference settings.
- Normalise embeddings where appropriate.
- Compute cosine similarity efficiently.
- Handle missing models gracefully.
- Cache model assets.
- Store embeddings in a consistent numeric format.
- Avoid loading a full embedding corpus into memory for every request.

The embedding model is an encoder, not a pretrained StudyPal recommender. StudyPal must still implement the retrieval, ranking, evaluation, and personalisation logic itself.

Explain this distinction in the README and ML methodology documentation.

## 8.3 Hybrid retrieval

Implement a configurable hybrid ranker.

A simple initial formulation is:

`hybrid_score = alpha * normalised_tfidf_score + (1 - alpha) * normalised_embedding_score`

where `alpha` is configurable.

Important requirements:

- Do not assume raw TF-IDF cosine scores and embedding cosine scores have identical distributions.
- Choose and document a sensible score-normalisation strategy.
- Handle zero vectors and missing retrieval channels.
- Do not assign a fixed arbitrary score to a missing model output.
- Record the retrieval method used for each search.
- Allow the evaluation script to compare all retrieval variants.

Use a sensible default weighting and expose it through configuration.

If one retrieval channel is unavailable, return a clearly identified fallback ranking rather than pretending the hybrid model ran normally.

## 8.4 Query-based retrieval

The student must be able to enter a question or concept.

For example:

“What is the working principle of a synchronous motor?”

StudyPal should retrieve relevant passages from the user's own course material.

The response must include:

- Source document title.
- Relevant passage.
- Page number when available.
- Similarity or ranking score where appropriate.
- Retrieval method.
- A link or action to open the source document or its relevant excerpt.

The application must not fabricate explanations, citations, page numbers, or passages.

## 8.5 Topic-to-topic retrieval

Allow a student to inspect a topic and discover related chunks or chapters.

Use the topic's representative chunks, centroid representation, or another documented approach to generate related-content results.

Exclude the same chunk from its own related-content list when appropriate.

## 8.6 Relevance and provenance

Every returned result must preserve a traceable relationship to its original document and chunk.

Do not return chunks belonging to another user's course.

Avoid duplicate or near-identical passages dominating the top results. Where appropriate, implement a simple deduplication or diversity mechanism and evaluate its effect.

---

# 9. Unsupervised topic discovery

Implement topic discovery with K-means and K-means++ initialisation.

## 9.1 Feature representation

Use a documented representation for clustering.

The initial implementation may cluster TF-IDF vectors or dense sentence embeddings. Select the default based on practicality and justify the choice.

Keep the clustering input representation configurable enough to support a comparison.

## 9.2 Cluster-count selection

Do not arbitrarily claim that one cluster count is optimal.

Implement:

- A configurable cluster count.
- Validation against the number of available chunks.
- A minimum corpus-size rule.
- A fallback for very small corpora.
- An optional experiment across several candidate cluster counts.
- Silhouette-score evaluation where mathematically appropriate.
- A documented manual-inspection procedure.

If the dataset is too small for meaningful clustering, explain that fact and use a simple fallback grouping strategy. Do not fabricate clustering scores.

## 9.3 Cluster labels

Generate readable labels using high-weighted TF-IDF terms or another explainable approach.

Each topic should expose:

- A topic identifier.
- A human-readable label.
- Representative keywords.
- The number of assigned chunks.
- Representative source passages.
- The list of documents contributing content.
- A model version or cluster-run identifier.

Allow a student to rename a topic.

Clearly distinguish automatically generated labels from user-edited labels.

## 9.4 Topic stability and retraining

Cluster IDs can change after refitting. Do not assume that topic number 2 means the same concept forever.

Store the clustering run or model version.

When a new document arrives, use an explicit policy:

- Rebuild the course topic model; or
- Assign new chunks using a compatible fitted model.

Choose the simpler reliable strategy for the initial implementation and document its consequences.

Ensure old learner states do not become silently attached to unrelated topics after reclustering.

Provide a safe strategy for handling changed topic assignments. For example, archive the old topic-model version and initialise or migrate learner states only when a defensible topic mapping exists.

---

# 10. Learner engine: supervised weakness prediction

The learner engine must estimate which topics a student is likely to struggle with.

This must be a genuine supervised-learning pipeline, not a collection of hand-written thresholds presented as a trained classifier.

## 10.1 Training data

Use labelled quiz-attempt data.

The target is:

`will_answer_next_question_incorrectly`

Construct features from information available before the prediction target.

Potential features:

- Recent accuracy for the topic.
- Total attempts.
- Recent number of incorrect answers.
- Recent streak of correct or incorrect responses.
- Time since last practice.
- Average response time.
- Change in recent performance.
- Number of distinct questions attempted.
- Historical topic mastery, if calculated without target leakage.

Do not include the target question's correctness, answer, or future performance in the features.

Do not use information that would only become available after the prediction being made.

## 10.2 Baseline

Implement a simple baseline classifier.

A majority-class or simple recent-performance baseline is acceptable.

The baseline must be evaluated on the same held-out data as the trained model.

## 10.3 Candidate models

Implement and compare:

1. Logistic regression.
2. A tree-based ensemble such as Random Forest.

Use scikit-learn pipelines where useful.

Requirements:

- Reproducible random seeds.
- Explicit feature definitions.
- Missing-value handling.
- Appropriate categorical encoding if categorical features are used.
- Training and evaluation separation.
- Saved model artefacts.
- Saved feature metadata.
- Versioned model configuration.
- Clear error handling for insufficient training data.

Do not fit the classifier on all available data and then report training-set accuracy as generalisation performance.

## 10.4 Train/test separation

Prefer a student-wise split so that records from the same student do not leak across training and evaluation sets.

Where chronological prediction is being evaluated, use a temporal split that respects the order of events.

If the pilot dataset is too small to support these splits reliably, report that limitation.

Do not quietly substitute a random row split that overstates performance.

## 10.5 Class imbalance

Report the class distribution.

Use suitable metrics such as:

- Precision.
- Recall.
- F1-score.
- Balanced accuracy where appropriate.
- Confusion matrix.

If probability estimates are used to rank topics, assess calibration when sufficient data is available.

Do not optimise solely for accuracy when the target class is imbalanced.

## 10.6 Training-data limitations

A small undergraduate pilot may not contain enough student histories to train a useful predictive model.

Implement a minimum-data policy.

When insufficient valid training data exists:

- Do not claim that a reliable classifier has been trained.
- Mark the classifier as unavailable or in a fallback state.
- Use knowledge tracing and content-based recommendations.
- Explain why personalised classifier-based predictions are unavailable.
- Keep the rest of the application functional.

Synthetic data may be used for pipeline testing and demonstrations, but must be explicitly identified as synthetic. Do not present results on synthetic data as evidence of real-world student prediction accuracy.

## 10.7 Inference

For a particular student and topic, the model should return a structured result containing:

- Topic ID.
- Predicted probability of an incorrect response, if the classifier is available.
- Model identifier.
- Timestamp or relevant learner-state version.
- Whether the result is a trained-model prediction or a fallback.
- A user-friendly explanation of the prediction's limitations.

The interface must avoid presenting uncertain estimates as definitive facts about a student's ability.

---

# 11. Learner engine: Bayesian Knowledge Tracing

Implement Bayesian Knowledge Tracing (BKT) as a separate, explicit component.

This component must maintain a mastery estimate for each student and topic.

## 11.1 Model parameters

Use the standard BKT parameters:

- `P(L0)`: initial probability that the student already knows the skill.
- `P(T)`: probability of learning the skill after an opportunity.
- `P(G)`: probability of guessing correctly despite not knowing the skill.
- `P(S)`: probability of slipping and answering incorrectly despite knowing the skill.

Keep parameter values configurable and validate that they fall within valid ranges.

For the initial version, use documented, configurable parameter values rather than claiming that the parameters have been statistically estimated from a large dataset.

Parameter fitting may be added as an optional extension if sufficient data exists.

## 11.2 Update equations

Let `p` be the current mastery probability before the answer.

For a correct response:

`p_correct = p * (1 - P(S)) / [p * (1 - P(S)) + (1 - p) * P(G)]`

For an incorrect response:

`p_incorrect = p * P(S) / [p * P(S) + (1 - p) * (1 - P(G))]`

Then update mastery after the learning opportunity:

`p_next = p_observed + (1 - p_observed) * P(T)`

Here, `p_observed` is the posterior probability after observing the answer.

Implement numerical safety for near-zero denominators and validate parameter constraints.

Write unit tests for correct answers, incorrect answers, edge cases, and repeated sequences.

## 11.3 State management

For every quiz submission:

1. Retrieve the existing mastery state or initialise the topic state.
2. Compute the posterior mastery probability.
3. Apply the learning transition.
4. Persist the updated mastery.
5. Record the quiz attempt.
6. Update relevant learner features.
7. Make the new state available to recommendation logic.

Use a transaction so that a failed state update does not leave a partially recorded quiz attempt.

The system must not update mastery simply because a quiz page was opened.

## 11.4 Progress tracking

Store a historical sequence of mastery updates or enough immutable quiz-attempt data to reconstruct the trend.

The frontend must show mastery estimates over time.

Explain that BKT mastery is a model-based estimate, not a direct measurement of intelligence, overall academic ability, or a guaranteed examination score.

## 11.5 Relationship to deep knowledge tracing

Deep Knowledge Tracing may be discussed in future scope.

Do not implement an unnecessarily complex recurrent neural network simply to make the project appear more advanced. The initial version must focus on a correctly implemented and tested BKT model.

---

# 12. Recommendation engine

This component combines the outputs of the content engine and learner engine.

Its responsibility is to decide **what the student should revise and which specific material they should review**.

## 12.1 Inputs

The recommender should use:

- Per-topic BKT mastery estimates.
- Supervised weakness probabilities, when available.
- Quiz-attempt recency.
- Number of attempts.
- Topic availability.
- Related-content retrieval results.
- Course topic metadata.
- Whether the student has any quiz history.

## 12.2 Topic scoring

Implement a configurable scoring formula.

A reasonable initial formulation is:

`revision_score = w_m * (1 - mastery) + w_w * weakness_probability + w_r * recency_factor`

where:

- `mastery` is the BKT mastery probability.
- `weakness_probability` is the trained classifier's predicted probability of an incorrect answer.
- `recency_factor` reflects how long the topic has gone without practice.
- `w_m`, `w_w`, and `w_r` are configurable weights.

Normalise or constrain inputs where needed.

Document the score range and weight interpretation.

The recency factor should not automatically dominate mastery and weakness. Choose a bounded, interpretable formulation.

When a trained classifier is unavailable, explicitly renormalise the available weights or use a documented fallback formula. Do not silently substitute an arbitrary weakness probability.

## 12.3 Cold-start behaviour

For a student with no quiz history:

- Do not invent mastery probabilities based on nonexistent observations.
- Clearly identify learner-state values as uninitialised or based on prior assumptions.
- Recommend content using the content engine.
- Suggest starting with a short topic quiz.
- Label the revision list as content-based rather than fully personalised.

After quiz history becomes available, combine content recommendations with learner-state information.

## 12.4 Recommendation output

Each recommended topic should contain:

- Topic ID and label.
- Rank.
- Revision priority score.
- Mastery estimate and availability status.
- Weakness probability and model status.
- A concise reason for the recommendation.
- Related source documents.
- Relevant note passages.
- Recommended next action, such as reviewing a passage or taking a quiz.

Provide transparent explanations such as:

- “Mastery estimate is currently low.”
- “Recent quiz attempts indicate difficulty with this topic.”
- “This topic has not been practised recently.”
- “You have not completed a quiz for this topic yet.”

Only show an explanation when the underlying data supports it.

## 12.5 Diversity and usefulness

Avoid returning ten nearly identical passages for one topic.

Where practical:

- Deduplicate repeated chunks.
- Limit excessive representation from one document.
- Include related content from more than one source when genuinely relevant.
- Return fewer than the requested number of results if too few useful results exist.

Do not manufacture content to fill the list.

## 12.6 Explainability

The recommendation engine must expose enough intermediate information for debugging and evaluation.

Provide a developer-facing breakdown of the contributing scores.

Do not expose unnecessary sensitive learner history to other users.

---

# 13. Question answering without generative AI

Implement topic-based question retrieval, not unrestricted free-form answer generation.

When a student asks a question:

1. Validate the question.
2. Determine the relevant course scope.
3. Retrieve relevant chunks using the configured retrieval strategy.
4. Rank the results.
5. Return the most relevant passages.
6. Preserve document titles, page numbers, and source identifiers.
7. Provide links to the source material.

The interface may label the results as “Relevant passages from your notes.”

Do not use an LLM to invent answers, fabricate references, or summarise information that does not exist in the indexed documents.

If an optional extractive summary is later introduced, it must be clearly distinguished from direct source text and validated separately.

If no relevant passage is found above a configured relevance threshold, display an honest no-results message and suggest a broader search query.

Do not present low-similarity passages as confidently relevant answers.

---

# 14. Quiz system

Implement a functional quiz workflow.

## 14.1 Quiz experience

The student should be able to:

- Select a course.
- Select a topic or begin a mixed-topic quiz.
- Choose the number of questions.
- Answer multiple-choice questions.
- Submit responses.
- Receive a score and review.
- See explanations where available.
- View topic-level performance.
- Receive next-step revision suggestions.

## 14.2 Question selection

Select questions from the actual stored question bank.

Support random selection without replacement within a quiz session when enough eligible questions exist.

Avoid repeatedly showing the same question within a single quiz.

If a topic has too few questions, communicate that limitation instead of failing silently.

## 14.3 Answer submission

On submission:

- Validate the question and selected option.
- Determine correctness on the server.
- Record the attempt.
- Update BKT state.
- Update features used by the weakness classifier.
- Recalculate or invalidate relevant recommendation results.
- Return the outcome.

Never trust a correctness flag sent by the browser.

Do not expose correct answers through an endpoint that is available before submission.

## 14.4 Question-bank provenance

Allow the application to identify whether a question is:

- Curated by the project team.
- Imported from a permitted source.
- Generated for a synthetic test fixture.

Do not misrepresent automatically generated or synthetic questions as validated educational content.

---

# 15. REST API design

Use a versioned API prefix, such as `/api/v1`.

Use consistent request validation, response schemas, status codes, pagination, and error formatting.

Create an OpenAPI specification through FastAPI and document the principal endpoints.

At minimum, implement the following logical endpoints. Exact paths may be refined consistently.

## Authentication

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

## Courses

- `GET /api/v1/courses`
- `POST /api/v1/courses`
- `GET /api/v1/courses/{course_id}`
- `PATCH /api/v1/courses/{course_id}`
- `DELETE /api/v1/courses/{course_id}`

## Documents

- `POST /api/v1/courses/{course_id}/documents`
- `GET /api/v1/courses/{course_id}/documents`
- `GET /api/v1/documents/{document_id}`
- `GET /api/v1/documents/{document_id}/status`
- `DELETE /api/v1/documents/{document_id}`
- `POST /api/v1/documents/{document_id}/reprocess`

## Topics

- `GET /api/v1/courses/{course_id}/topics`
- `GET /api/v1/topics/{topic_id}`
- `PATCH /api/v1/topics/{topic_id}`
- `GET /api/v1/topics/{topic_id}/related-content`

## Search

- `POST /api/v1/courses/{course_id}/search`
- `GET /api/v1/courses/{course_id}/search/config`

## Quizzes

- `GET /api/v1/courses/{course_id}/quizzes`
- `POST /api/v1/courses/{course_id}/quizzes/sessions`
- `GET /api/v1/quiz-sessions/{session_id}`
- `POST /api/v1/quiz-sessions/{session_id}/answers`
- `POST /api/v1/quiz-sessions/{session_id}/submit`
- `GET /api/v1/courses/{course_id}/quiz-history`

## Learning and progress

- `GET /api/v1/courses/{course_id}/mastery`
- `GET /api/v1/courses/{course_id}/progress`
- `GET /api/v1/topics/{topic_id}/mastery-history`

## Recommendations

- `GET /api/v1/courses/{course_id}/recommendations`
- `GET /api/v1/courses/{course_id}/recommendations/{topic_id}`

## Health

- `GET /health/live`
- `GET /health/ready`

The endpoints listed here are a functional contract, not a requirement to create unnecessary endpoints.

## API requirements

- Use Pydantic request and response models.
- Return suitable HTTP status codes.
- Distinguish validation errors, missing resources, unauthorised access, conflicts, and internal failures.
- Paginate potentially large result sets.
- Enforce course ownership on every relevant endpoint.
- Validate all IDs and references.
- Avoid exposing database models directly.
- Ensure file responses do not leak internal storage paths.
- Keep endpoint documentation accurate.
- Add integration tests for critical workflows.

Use consistent error objects, for example:

```json
{
  "error": {
    "code": "DOCUMENT_PROCESSING_FAILED",
    "message": "The document could not be processed.",
    "details": null,
    "request_id": "example-request-id"
  }
}
```

This is an example response shape; implement a consistent schema throughout the application.

---

# 16. Frontend and user experience

Build a polished, responsive, accessible interface suitable for a public GitHub portfolio and a live project demonstration.

The design should be clean and professional. Avoid excessive gradients, decorative animations, unnecessary cards, oversized empty areas, and generic dashboard clutter.

Use a consistent visual system, typography scale, spacing, colour palette, and component library.

The interface should be understandable without reading the source code.

## 16.1 Required pages

### A. Authentication

Include:

- Registration.
- Login.
- Validation errors.
- Loading states.
- Helpful authentication failure messages.

### B. Dashboard

Display:

- Number of courses.
- Number of indexed documents.
- Topics discovered.
- Recent study activity.
- Current mastery overview where data exists.
- Recommended revision topics.
- A clear path to upload material or take a quiz.

Do not show fake metrics for a new account.

For an empty account, provide an attractive, useful empty state with a clear next action.

### C. Course management

Allow students to:

- Create courses.
- View courses.
- Open a course.
- Rename or edit course details.
- Delete a course with confirmation.

### D. Document library

Include:

- File upload.
- File type and size validation.
- Upload progress where feasible.
- Processing status.
- Document metadata.
- Error states.
- Reprocessing controls.
- Delete controls with confirmation.

Do not show “Indexed successfully” until the backend confirms successful indexing.

### E. Topic explorer

Display:

- Topic labels.
- Representative keywords.
- Chunk counts.
- Associated documents.
- Representative passages.
- Topic details.
- Editable topic labels.

Provide sensible filtering and search.

### F. Search and related content

Include:

- Search input.
- Retrieval-method selection if appropriate.
- Loading indicator.
- Ranked results.
- Source-document labels.
- Page references where available.
- Relevant passage excerpts.
- A link to inspect source content.
- A no-results state.
- An honest indication of the retrieval mode.

### G. Quiz interface

Include:

- Topic selection.
- Quiz length selection.
- Question and answer choices.
- Submission flow.
- Correctness feedback.
- Explanations.
- Results summary.
- Next-step recommendations.

Avoid showing the correct answer before submission.

### H. Learning progress

Show:

- Mastery estimates by topic.
- Changes over time.
- Quiz accuracy.
- Attempt counts.
- Recent practice.
- Topics needing revision.

Use real API data.

When there is insufficient history for a chart, display a useful empty state rather than misleading zero-valued trends.

### I. Recommendations

For each recommended topic, show:

- Priority rank.
- Topic label.
- Reason for the recommendation.
- Relevant mastery or weakness information when available.
- Suggested source passages.
- A direct action to review the material or take a quiz.

Make the difference between content-based recommendations and fully personalised recommendations visible.

## 16.2 Frontend engineering quality

Requirements:

- Strong TypeScript typing.
- Reusable components.
- Feature-based organisation.
- Centralised API client.
- Typed API responses.
- Environment-based API URL configuration.
- Error boundaries where appropriate.
- Loading and empty states.
- Form validation.
- Accessible labels and keyboard navigation.
- Responsive layouts.
- Avoid duplicated API logic.
- Avoid giant components.
- Avoid `any` unless justified.
- No API secrets in frontend code.
- No hardcoded user data masquerading as live results.

Write frontend tests for important interactions and error states.

---

# 17. ML experimentation and evaluation framework

This project must demonstrate measured evaluation rather than merely having algorithms in the codebase.

Create a reproducible evaluation pipeline with scripts, configuration, metrics, and machine-readable output.

## 17.1 Data sources

Use:

1. Course notes owned by the project team or obtained from an appropriate open source.
2. A hand-labelled query-to-relevant-chunk reference set for retrieval evaluation.
3. A curated quiz bank mapped to topics.
4. A small voluntary pilot group for real learner-history evaluation where feasible.
5. Clearly labelled synthetic data for testing edge cases and exercising the pipeline.

Document dataset origins, licences where applicable, collection procedures, and limitations.

Do not commit copyrighted course materials or personal student records without permission.

## 17.2 Retrieval evaluation

Create a hand-labelled evaluation set containing queries and relevant chunks.

Compare:

- TF-IDF cosine retrieval.
- Sentence-embedding cosine retrieval.
- Hybrid retrieval.

Calculate:

- Precision@5.
- Recall@5.
- Mean Reciprocal Rank where feasible.
- Optionally nDCG@5 if relevance labels support it.

Define each metric in the documentation.

Handle cases with fewer than five eligible chunks correctly.

Do not count irrelevant or unavailable chunks as relevant.

Save results in CSV or JSON format and generate a concise comparison report.

The comparison must use the same query set for all retrieval methods.

## 17.3 Clustering evaluation

Evaluate:

- Silhouette score where valid.
- Cluster-size distribution.
- Number of unassigned chunks, if applicable.
- Topic-label coherence through documented manual inspection.
- Representative chunks for each cluster.

Compare a small, reasonable range of cluster counts where the dataset permits.

Do not treat a higher silhouette score as proof that the topics are educationally meaningful.

Report when a score cannot be calculated because the corpus is too small or clustering produces degenerate groups.

## 17.4 Weakness classifier evaluation

Compare:

- Majority-class baseline.
- Logistic regression.
- Random Forest or the selected tree ensemble.

Report:

- Accuracy.
- Precision.
- Recall.
- F1-score.
- Balanced accuracy where appropriate.
- Confusion matrix.
- Class distribution.

Use appropriate train/test separation.

Where data volume permits, include cross-validation or a separate validation set.

Do not report a test result when no independent test data exists.

If no adequate real pilot dataset is available, report that the real-world model evaluation is incomplete.

## 17.5 BKT validation

Validate the implementation using:

- Unit tests of update equations.
- Known edge cases.
- Synthetic response sequences.
- Replay of recorded quiz sequences where available.
- Comparison of predicted correctness probabilities against observed outcomes where the dataset supports it.

Track whether mastery estimates remain within valid probability bounds.

Do not claim that a rising mastery estimate necessarily proves that the student has learned the underlying topic.

## 17.6 End-to-end validation

Test:

- Registration and login.
- Course creation.
- Document upload.
- Text extraction.
- Chunk creation.
- Retrieval.
- Topic discovery.
- Quiz creation and submission.
- Mastery updates.
- Recommendation generation.
- Progress display.
- Cross-user access restrictions.
- Error handling.
- Data deletion and cleanup.

Record results in a final evaluation report.

## 17.7 Evaluation output

The evaluation script should generate reproducible outputs, such as:

```text
reports/
├── retrieval_metrics.csv
├── clustering_metrics.csv
├── classifier_metrics.json
├── bkt_validation.json
├── evaluation_summary.md
└── plots/
```

Only create output files that correspond to actual executed experiments.

Include the dataset identifier, configuration, random seed, and timestamp in the experiment metadata.

Separate results generated from synthetic fixtures from results generated from real data.

---

# 18. Automated testing requirements

Create a meaningful test suite covering the entire system.

Use pytest for backend testing and an appropriate frontend testing framework.

## 18.1 Unit tests

Test:

- Text normalisation.
- Chunking.
- PDF extraction failure cases.
- TF-IDF retrieval.
- Embedding similarity.
- Hybrid score calculation.
- Cluster-count validation.
- Cluster-label generation.
- Classifier feature construction.
- Leakage prevention.
- BKT update equations.
- Recommendation scoring.
- Score normalisation.
- Empty-data handling.
- Configuration validation.

## 18.2 Integration tests

Test:

- Database persistence.
- Alembic migrations.
- Document-processing pipeline.
- Index persistence and reload.
- Model artifact loading.
- Quiz submission transactions.
- Learner-state updates.
- Recommendation generation from actual stored data.

## 18.3 API tests

Test all core user workflows.

Include:

- Valid requests.
- Invalid inputs.
- Missing resources.
- Unauthorised access.
- Cross-user access attempts.
- Duplicate uploads.
- Unsupported formats.
- Empty PDFs.
- Oversized files.
- Failed ingestion.
- Empty search results.
- Empty quiz banks.
- Insufficient training data.
- Model unavailability.

## 18.4 Frontend tests

Test:

- Registration and login forms.
- Course creation.
- Upload feedback.
- Document status display.
- Search-result rendering.
- Quiz answer submission.
- Progress empty states.
- Recommendation navigation.
- API failure handling.

## 18.5 Coverage

Aim for strong coverage of critical backend logic, particularly the ML algorithms, scoring functions, security boundaries, and quiz-state transitions.

A target of approximately 80% coverage for core backend modules is reasonable if achievable without writing low-value tests solely to inflate the percentage.

Report actual coverage. Never claim the target has been met without measuring it.

## 18.6 Continuous integration

Configure GitHub Actions to run, where practical:

1. Dependency installation.
2. Formatting and lint checks.
3. Type checks.
4. Backend unit tests.
5. Integration/API tests.
6. Frontend lint checks.
7. Frontend tests.
8. Frontend production build.

Do not require downloading large embedding models in every CI job. Use dependency injection and test doubles for unit tests, and reserve model-backed integration tests for a controlled test configuration.

---

# 19. Configuration and reproducibility

Centralise configuration using environment variables and validated settings.

Include a comprehensive `.env.example` with non-secret development defaults.

Potential configuration categories include:

- Application environment.
- API host and port.
- Database URL.
- Authentication secrets.
- Access-token lifetime.
- Upload directory.
- Maximum upload size.
- Allowed file extensions.
- Chunk size and overlap.
- Embedding model identifier.
- Embedding device.
- Model cache directory.
- TF-IDF settings.
- Retrieval method.
- Hybrid retrieval weights.
- Clustering configuration.
- BKT parameters.
- Recommendation weights.
- Logging level.
- CORS origins.

Never commit production secrets.

Provide a reproducible way to:

- Install dependencies.
- Run database migrations.
- Create demo data.
- Download or initialise the embedding model.
- Process sample documents.
- Train or fit the relevant models.
- Run evaluation.
- Start the backend.
- Start the frontend.
- Run tests.
- Rebuild indices.

Where randomness is involved, make random seeds configurable.

Document the difference between fitting unsupervised models, training supervised models, and performing inference.

Do not claim that every component is “trained” in the same sense. For example, TF-IDF vectorisation and K-means fitting are unsupervised corpus-fitting procedures, while logistic regression and Random Forest require labelled training data.

---

# 20. Logging, observability, and error handling

Implement structured logging using a maintained Python logging configuration or suitable structured-logging library.

Log useful events such as:

- Application startup and shutdown.
- Database connection failures.
- Document-processing start and completion.
- Processing failures.
- Model loading.
- Model availability.
- Index rebuilds.
- Quiz submissions.
- Recommendation generation.
- Unexpected exceptions.

Include a request identifier where practical.

Do not log passwords, authentication tokens, complete sensitive documents, or unnecessary personal data.

Create separate liveness and readiness health checks.

- Liveness should indicate that the application process is responsive.
- Readiness should verify the dependencies necessary to serve requests.

Do not make readiness depend on downloading a model every time the health endpoint is called.

Return useful, sanitised errors to clients and preserve detailed diagnostic context in server logs.

---

# 21. Privacy and ethical considerations

StudyPal handles uploaded documents and student performance data.

Implement and document:

- Course ownership.
- Per-user data isolation.
- Minimal data collection.
- Anonymous identifiers in research exports.
- Voluntary pilot participation.
- Safe handling of uploaded files.
- Configurable local storage.
- Data deletion behaviour.
- Protection of quiz history.
- Appropriate access controls.
- Separation between demo data and real user data.

Do not upload student documents to external APIs.

Do not use real student data for model training without appropriate consent and a documented purpose.

Provide a mechanism to delete a course and its associated documents, chunks, quiz history, and learner state according to the application's retention policy.

Ensure that deletion also addresses stored files and derived indices. If model artefacts contain information that cannot be cleanly separated, document the limitation and define a safe rebuild procedure.

The application must not describe students as unintelligent or incapable. Recommendations should focus on observed quiz performance and study actions.

---

# 22. Demo data and reproducible demonstration

Create a reliable demonstration workflow so that the project can be evaluated without first recruiting a group of students.

Provide a small, clearly labelled synthetic demo course with:

- A few short sample educational documents written specifically for the project or otherwise appropriately licensed.
- Multiple paragraphs covering several related topics.
- Curated multiple-choice quiz questions.
- Correct answers and explanations.
- Example search queries.
- A reproducible script for creating demo data.
- A documented demo account workflow that does not require a pre-existing private account.

The demo must exercise actual application functionality.

The script should use the real ingestion pipeline, content retrieval, topic discovery, quiz workflow, BKT update logic, and recommendation engine.

Do not hardcode the expected recommendation list.

If the supervised classifier has insufficient real training data, show the documented fallback state instead of manufacturing classifier performance.

Do not automatically seed synthetic demo data into production deployments.

Make seeding an explicit development action.

---

# 23. README.md — mandatory portfolio-quality documentation

The root `README.md` is one of the most important deliverables.

Treat it as the primary technical presentation of the project to recruiters, software engineers, ML engineers, and interviewers.

It must be exceptionally clear, professional, technically accurate, visually organised, and sufficiently detailed that a reviewer can understand the project without browsing the entire repository.

Do not write a generic README containing only an installation command and a list of features.

Write the actual README based on the implemented code. Do not claim that future features already exist.

Include the following sections.

## 23.1 Project title and introduction

Include:

- StudyPal's full name.
- A concise one-line description.
- A compelling project overview.
- The problem being addressed.
- The main technical approach.
- The intended users.
- The scope of the current implementation.

Use a polished opening paragraph suitable for a resume project.

## 23.2 Feature overview

Clearly explain:

- Course and document management.
- PDF and text ingestion.
- Content chunking and indexing.
- TF-IDF retrieval.
- Sentence-embedding retrieval.
- Hybrid ranking.
- Topic clustering.
- Supervised weakness prediction.
- Bayesian Knowledge Tracing.
- Personalised revision recommendations.
- Quiz management.
- Progress visualisation.
- Evaluation tooling.

Mark incomplete or optional features honestly.

## 23.3 Screenshots and demo

Create a dedicated section for:

- Dashboard.
- Document library.
- Topic explorer.
- Search results.
- Quiz interface.
- Progress dashboard.
- Recommendation interface.

If the environment supports browser-based testing or screenshots, capture real screenshots of the implemented application.

Do not create fake screenshots that imply functionality the application does not possess.

If screenshots cannot yet be captured, include clearly labelled placeholders or instructions for adding them later.

Provide a demo workflow and demo-data setup instructions.

## 23.4 Architecture diagram

Include a Mermaid diagram showing the major layers and how data moves through the system.

It should depict:

- React frontend.
- FastAPI REST API.
- Authentication and application services.
- Document-ingestion pipeline.
- Content engine.
- Learner engine.
- Recommendation engine.
- PostgreSQL.
- Embedding/index storage.
- Evaluation pipeline.

The diagram must reflect the actual code architecture, not an aspirational architecture that was never implemented.

## 23.5 End-to-end workflow

Explain the entire data flow:

1. Upload course documents.
2. Extract and clean text.
3. Split text into chunks.
4. Generate lexical and semantic representations.
5. Discover topic groups.
6. Ask a question or retrieve related material.
7. Take a topic-based quiz.
8. Update BKT mastery.
9. Construct learner features.
10. Predict weakness where a trained classifier is available.
11. Rank revision topics.
12. Retrieve supporting source passages.
13. Display a personalised revision plan.
14. Evaluate model behaviour using the evaluation framework.

Include a second diagram showing the core study workflow.

## 23.6 Technology stack

Use a table describing each major technology and why it is used.

Include backend, frontend, database, ML, document processing, testing, packaging, and CI tools.

Explain the role of sentence embeddings accurately.

Do not describe a pretrained sentence encoder as a model trained from scratch by the project.

## 23.7 Machine learning methodology

Provide an in-depth explanation of:

### TF-IDF

- Mathematical intuition.
- Representation of chunks.
- Cosine similarity.
- Strengths and limitations.

### Sentence embeddings

- How a sentence encoder represents text.
- How query and chunk vectors are compared.
- Why semantic similarity may retrieve paraphrases.
- Model size and local execution considerations.

### Hybrid retrieval

- Scoring formula.
- Score normalisation.
- Weight configuration.
- Fallback behaviour.
- Evaluation approach.

### K-means clustering

- Vector representation.
- K-means++ initialisation.
- Cluster-count selection.
- Cluster labels.
- Silhouette-score interpretation.
- Topic stability limitations.

### Supervised weakness prediction

- Target variable.
- Feature engineering.
- Baseline.
- Logistic regression.
- Tree ensemble.
- Data splitting.
- Leakage prevention.
- Evaluation metrics.
- Insufficient-data fallback.

### Bayesian Knowledge Tracing

- The four model parameters.
- Correct-answer update.
- Incorrect-answer update.
- Learning transition.
- Topic-level state persistence.
- Assumptions and limitations.

### Recommendation ranking

- Mastery score.
- Weakness probability.
- Recency.
- Weighting.
- Cold-start handling.
- Source-passage retrieval.
- Recommendation explanations.

Use readable equations where useful. Ensure equations match the implemented code.

## 23.8 Repository structure

Explain the purpose of each important directory and module.

Do not paste the entire directory tree without explanation.

## 23.9 Installation and setup

Provide tested instructions for the supported operating system environments.

Cover:

- Prerequisites.
- Repository cloning.
- Python environment creation.
- Backend dependency installation.
- Frontend dependency installation.
- Environment configuration.
- PostgreSQL setup.
- Database migrations.
- Embedding model initialisation.
- Demo-data seeding.
- Backend startup.
- Frontend startup.
- Accessing the application.
- Running tests.

Provide both a local-development setup and a Docker Compose setup.

Where commands differ between Windows PowerShell and Linux/macOS, show the relevant differences.

Do not assume that users have a pre-existing `.env` file.

## 23.10 API documentation

Document the key endpoints, methods, authentication requirements, request bodies, response shapes, and error cases.

Provide realistic examples.

Point readers to FastAPI's generated OpenAPI documentation.

Do not document endpoints that do not exist.

## 23.11 Database schema

Include an entity-relationship diagram or Mermaid ER diagram.

Explain:

- User-course relationships.
- Course-document relationships.
- Document-chunk relationships.
- Topic assignments.
- Quiz questions and attempts.
- Learner topic states.
- Model and evaluation metadata where implemented.

Explain ownership and integrity constraints.

## 23.12 Model training and evaluation

Provide exact commands for:

- Preparing or validating data.
- Building content indices.
- Fitting clustering models.
- Training the weakness classifier when sufficient data exists.
- Evaluating retrieval.
- Evaluating clustering.
- Evaluating the classifier.
- Validating BKT.
- Generating evaluation reports.

Explain how to interpret each metric.

Include a results table containing only real, executed experimental results.

If experiments have not been run, mark results as pending. If synthetic data was used, label the associated results as synthetic.

## 23.13 Testing and quality

Document:

- Unit tests.
- Integration tests.
- API tests.
- ML tests.
- Frontend tests.
- Linting.
- Type checking.
- Coverage commands.
- CI workflow.

Report the actual status of tests when writing the final documentation.

## 23.14 Security and privacy

Explain:

- Authentication.
- Password hashing.
- Authorisation.
- File-upload validation.
- Data ownership.
- Secret configuration.
- Data deletion.
- Local document processing.
- Limitations of the current security posture.

## 23.15 Performance and resource requirements

Document realistic resource requirements.

The application should be designed for a normal laptop with approximately 8 GB RAM and a multi-core CPU, although actual requirements will depend on the embedding model, corpus size, and concurrent workloads.

Explain:

- CPU inference.
- Model caching.
- Batch embedding.
- Index rebuilding.
- Expected scaling limitations.
- The absence of GPU requirements for the default workflow.

Do not publish invented latency or throughput numbers.

If performance benchmarks are implemented, describe the hardware, dataset, configuration, and measurement procedure.

## 23.16 Limitations and future work

Include the actual limitations of the implemented system.

Potential future directions include:

- OCR for scanned documents.
- Spaced repetition.
- Deep Knowledge Tracing.
- Collaborative filtering.
- Better topic modelling.
- Instructor analytics.
- Mobile applications.
- Larger real-world student datasets.
- More advanced ranking methods.
- Improved vector indexing for larger corpora.

Separate current limitations from features that have already been implemented.

## 23.17 Resume-ready project summary

Include a concise, technically accurate summary suitable for a resume.

Provide a template with placeholders for metrics that must be measured, such as:

- Retrieval Precision@5.
- Retrieval Recall@5.
- Classifier F1-score.
- Number of documents or chunks evaluated.
- End-to-end latency.

Do not fill these placeholders with invented values.

## 23.18 References

Include credible references for the implemented algorithms and tools.

At minimum, cite the relevant foundational literature:

- Salton and Buckley — term-weighting approaches in information retrieval.
- Manning, Raghavan, and Schütze — *Introduction to Information Retrieval*.
- Reimers and Gurevych — Sentence-BERT.
- Corbett and Anderson — Bayesian Knowledge Tracing.
- Arthur and Vassilvitskii — K-means++.
- Pedregosa et al. — scikit-learn.

Piech et al.'s Deep Knowledge Tracing may be included in the future-work discussion.

Add links to the official documentation for FastAPI, React, SQLAlchemy, scikit-learn, and other major dependencies.

Do not cite a paper as evidence that StudyPal itself achieved a particular result.

---

# 24. Additional project documentation

Create concise, accurate technical documents that supplement the README.

## `docs/architecture.md`

Include:

- System architecture.
- Component responsibilities.
- Dependency direction.
- Data flow.
- Error-handling boundaries.
- Model lifecycle.
- Index lifecycle.
- Major architectural decisions and their rationale.

## `docs/ml_methodology.md`

Include:

- Model definitions.
- Feature engineering.
- Training procedures.
- Retrieval algorithms.
- BKT equations.
- Recommendation formula.
- Model versioning.
- Data leakage safeguards.
- Fallback behaviour.

## `docs/evaluation.md`

Include:

- Dataset requirements.
- Evaluation methodology.
- Metric definitions.
- Experimental setup.
- Reproducibility instructions.
- Results tables based on actual runs.
- Known evaluation limitations.

## `docs/api.md`

Document API routes, authentication, request and response schemas, errors, and examples.

## `docs/database.md`

Document schema entities, relationships, constraints, migrations, and deletion behaviour.

## `docs/security.md`

Document the threat model, authentication, authorisation, file validation, data isolation, secret handling, and known limitations.

## `docs/development.md`

Document environment setup, coding standards, testing, debugging, adding a new ML component, and the development workflow.

Avoid duplicating the entire README verbatim. Use the README as the entry point and these documents for implementation-level detail.

---

# 25. Docker and deployment

Provide a complete local Docker Compose workflow.

The default configuration should include:

- PostgreSQL.
- FastAPI backend.
- React frontend, or a documented development-server setup.
- A persistent database volume.
- Appropriate health checks.
- Environment-variable configuration.
- A writable location for uploaded files and local model artefacts.

Requirements:

- Do not bake secrets into images.
- Do not run application containers as root unnecessarily.
- Use reproducible dependency installation.
- Handle database readiness correctly.
- Apply migrations through an explicit and documented startup or deployment step.
- Avoid repeatedly downloading model files at container startup.
- Configure reasonable resource limits where appropriate.
- Document persistent storage and backup considerations.
- Provide a clean local shutdown procedure.

Do not claim the application is production-deployed merely because a Dockerfile exists.

The goal is production-quality engineering practices in a locally runnable capstone application, not a claim of production-scale hosting.

---

# 26. Performance and resource management

Optimise for a modest development machine without compromising correctness.

Implement:

- Batch embedding generation.
- Reuse of loaded models.
- Reuse of fitted vectorisers and indices.
- Pagination.
- Bounded document sizes.
- Efficient similarity calculations.
- Reasonable database indexes.
- Lazy loading of large result sets.
- Background processing for expensive ingestion.
- Avoidance of repeated model fitting on ordinary requests.

Define explicit invalidation rules when documents, chunks, or model configurations change.

Avoid unbounded in-memory caches.

Make concurrency assumptions explicit.

Do not use asynchronous syntax merely for appearance. CPU-heavy ML work must not block the event loop indefinitely.

Use a thread pool, worker, or other appropriate execution mechanism where necessary, and document the trade-offs.

Include an optional benchmark script that measures ingestion time, query latency, and memory usage on a specified dataset. Results must be measured, not estimated and presented as facts.

---

# 27. Five-week implementation plan

Implement the project in five phases, prioritising a working end-to-end product over optional complexity.

## Week 1 — Foundation and data pipeline

Implement:

- Repository structure.
- Backend configuration.
- Database models.
- Initial migrations.
- Authentication foundation.
- Course management.
- Document upload.
- PDF/text extraction.
- Cleaning and chunking.
- Basic test setup.
- Initial README and architecture documentation.

**Deliverable:** A user can create a course, upload a supported document, and inspect its processing status and stored chunks.

## Week 2 — Content engine

Implement:

- TF-IDF retrieval.
- Sentence embeddings.
- Hybrid ranking.
- Local index persistence.
- K-means clustering.
- Topic labels.
- Related-content endpoints.
- Topic explorer.
- Retrieval evaluation dataset and script.

**Deliverable:** Uploaded documents can be searched and grouped into topics, and retrieval methods can be compared.

## Week 3 — Learner engine

Implement:

- Curated quiz bank.
- Quiz sessions and answer submission.
- Attempt persistence.
- Learner-feature construction.
- Logistic regression baseline and candidate model.
- Random Forest comparison.
- BKT implementation.
- Mastery history.
- Classifier evaluation.

**Deliverable:** Quiz performance updates topic-level mastery, and a trained weakness classifier can operate when adequate training data exists.

## Week 4 — Recommendation and integration

Implement:

- Recommendation score fusion.
- Cold-start behaviour.
- Source-passage attachment.
- Dashboard.
- Progress visualisation.
- Recommendation interface.
- End-to-end API integration.
- Security checks.
- Docker Compose workflow.

**Deliverable:** The user can move from uploaded notes to a quiz and then receive a revision plan grounded in their own material and available learner data.

## Week 5 — Validation and final delivery

Implement and complete:

- Unit and integration tests.
- Frontend tests.
- Security tests.
- Retrieval evaluation.
- Clustering evaluation.
- Classifier evaluation where data permits.
- BKT validation.
- Bug fixing.
- Performance checks.
- Documentation.
- README screenshots where feasible.
- Final demonstration workflow.
- Final project report and presentation material if requested by the repository's deliverables.

**Deliverable:** A reproducible, documented, testable application with honest evaluation results and a polished GitHub repository.

## Prioritisation rule

If time becomes limited, prioritise in this order:

1. Correct document ingestion and retrieval.
2. Correct quiz submission and BKT updates.
3. Working recommendation logic.
4. Reliable persistence and authentication.
5. Functional frontend.
6. Evaluation and automated tests.
7. Docker, CI, and complete documentation.
8. Optional refinements and future-scope features.

Do not sacrifice core correctness to implement optional features.

---

# 28. Acceptance criteria

The project is complete only when the following criteria have been addressed and the actual status documented.

## 28.1 Application functionality

- [ ] A user can register and log in.
- [ ] A user can create and manage courses.
- [ ] A user can upload a PDF or text file.
- [ ] Supported documents are extracted and chunked.
- [ ] Unsupported or invalid documents fail clearly.
- [ ] Chunks retain source metadata.
- [ ] The application builds a usable content index.
- [ ] TF-IDF retrieval works.
- [ ] Sentence-embedding retrieval works when the model is available.
- [ ] Hybrid retrieval works and handles fallback states.
- [ ] Topic clustering works on a suitable corpus.
- [ ] Topic labels can be inspected and edited.
- [ ] Students can ask questions and retrieve relevant source passages.
- [ ] Students can take quizzes.
- [ ] Quiz answers are validated by the server.
- [ ] Quiz attempts are persisted.
- [ ] BKT updates after each valid submitted answer.
- [ ] Mastery history can be inspected.
- [ ] The weakness classifier can be trained when adequate labelled data exists.
- [ ] Insufficient training data is handled honestly.
- [ ] Recommendations are computed from available content and learner information.
- [ ] Cold-start users receive useful content-based recommendations.
- [ ] Source passages are attached to revision suggestions.
- [ ] Progress charts reflect real stored data.
- [ ] Data ownership is enforced.
- [ ] Course and document deletion follow a documented cleanup policy.

## 28.2 Engineering quality

- [ ] The codebase has clear module boundaries.
- [ ] Critical functions have explicit types and docstrings where useful.
- [ ] Database migrations are included.
- [ ] Configuration is environment-based.
- [ ] Secrets are not committed.
- [ ] Errors are handled consistently.
- [ ] Logs do not expose sensitive information.
- [ ] Indices and model artefacts can be rebuilt.
- [ ] The system can be run locally using documented instructions.
- [ ] Docker Compose works in a clean environment.
- [ ] CI is configured.
- [ ] Automated tests cover critical paths.
- [ ] Frontend and backend production builds succeed where applicable.
- [ ] The repository does not contain unnecessary generated files or private data.

## 28.3 Research quality

- [ ] TF-IDF, embeddings, and hybrid retrieval can be compared.
- [ ] Retrieval metrics are computed correctly.
- [ ] Clustering evaluation is implemented.
- [ ] The classifier is compared with a baseline.
- [ ] Data leakage safeguards are implemented.
- [ ] BKT equations are tested.
- [ ] Recommendation scores are explainable.
- [ ] Synthetic results are clearly separated from real-data results.
- [ ] Unavailable or incomplete experiments are documented honestly.

## 28.4 Documentation quality

- [ ] The README contains the complete project overview.
- [ ] The README explains the architecture.
- [ ] The README explains all implemented ML components.
- [ ] The README contains setup and run instructions.
- [ ] The README documents API usage.
- [ ] The README explains model training and evaluation.
- [ ] The README documents testing and security.
- [ ] The README describes limitations and future work.
- [ ] The README contains a repository structure explanation.
- [ ] Technical references are included.
- [ ] All documented commands have been checked where feasible.
- [ ] No unsupported performance claims or fabricated results appear in the documentation.

---

# 29. Required final outputs

At completion, provide the following deliverables.

1. **Complete source code:** Backend, frontend, database migrations, ML modules, evaluation tools, tests, and configuration.
2. **Running application:** A working local development workflow and Docker Compose configuration.
3. **Content engine:** TF-IDF, semantic embeddings, hybrid retrieval, and topic clustering.
4. **Learner engine:** Supervised weakness prediction with baselines, and Bayesian Knowledge Tracing.
5. **Recommendation engine:** Ranked, explainable study recommendations connected to source material.
6. **Functional UI:** Dashboard, document management, topic explorer, search, quizzes, progress, and recommendations.
7. **Demo workflow:** Clearly labelled sample documents, curated quiz data, and a reproducible demo-data script.
8. **Evaluation suite:** Reproducible retrieval, clustering, classifier, and BKT validation scripts.
9. **Automated tests:** Unit, integration, API, ML, and frontend tests.
10. **Engineering infrastructure:** Docker, migrations, environment configuration, logging, health checks, and CI.
11. **Root README:** A detailed portfolio-quality technical presentation of the entire project.
12. **Technical documentation:** Architecture, methodology, evaluation, API, database, security, and development documentation.
13. **Final status report:** A clear breakdown of implemented features, tests actually run, experiments actually completed, known failures, measured results, and remaining work.

If the execution environment supports file creation, terminal commands, and repository editing, use those capabilities to create and validate the actual files rather than merely describing them.

If you cannot execute a step because of an environmental restriction, report the exact limitation and provide the corresponding reproducible command.

---

# 30. Final instructions to the coding agent

Treat this project as something that will be reviewed by a technically strong interviewer.

The reviewer may inspect the source code, ask why each algorithm was chosen, challenge the evaluation methodology, inspect the database design, and attempt to break the application through invalid inputs or cross-user access.

Write the software so that the implementation can withstand that scrutiny.

Do not optimise for the number of files, the number of technologies, or the appearance of sophistication.

Optimise for:

- Correctness.
- Clarity.
- Reproducibility.
- Maintainability.
- Measurable ML behaviour.
- Explainability.
- Security.
- Usability.
- Technical depth.
- Honest documentation.

Do not use hardcoded outputs to imitate ML functionality. Do not fabricate metrics. Do not claim a feature is implemented when it is only represented by a button or placeholder.

Do not silently swallow exceptions. Do not create an enormous monolithic file. Do not leave core methods as `TODO` stubs. Do not build a frontend that relies on hardcoded JSON instead of the actual backend.

Use sensible defaults, add configuration where it materially improves the system, and keep the implementation compatible with a modest local development machine.

**Begin by inspecting the repository and producing a concise implementation plan. Then implement the project in the five phases above, validating each phase before moving forward. Continue until the core application is working, the tests have been run, and the README and technical documentation accurately describe the actual result.**

At the end, provide a concise engineering handoff containing:

- What was built.
- The final repository structure.
- How to run the project from a clean environment.
- How to run the tests.
- How to train or fit each model.
- How to run the evaluation suite.
- Which tests passed and failed.
- Which experiments have actually been completed.
- The measured results, if available.
- Known limitations.
- Remaining tasks, if any.

The objective is a **complete, reproducible, technically defensible, portfolio-ready StudyPal application** that demonstrates genuine full-stack engineering and applied machine learning—not merely a project synopsis converted into code.
