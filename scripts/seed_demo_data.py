"""Demo Data Seeder: Creates sample student account, realistic course notes, and curated quiz questions."""

import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, Base, engine
from app.db.models import User, Course, Document, DocumentChunk, Topic, QuizQuestion, LearnerTopicState
from app.core.security import get_password_hash
from app.ml.ingestion.chunker import chunk_document
from app.ml.content.retrieval import retrieval_engine
from app.ml.content.clustering import topic_clusterer
from app.logging_config import setup_logging, logger

setup_logging()


SAMPLE_NOTES = {
    "supervised_learning.txt": """Supervised Learning and Classification Fundamentals

Supervised machine learning algorithms build a mathematical model of a set of data that contains both the inputs and the desired outputs. The data is known as training data and consists of a set of training examples. Each training example has one or more inputs and a desired output, also known as a supervisory signal or label.

In classification tasks, the computer program is asked to specify which of k categories some input belongs to. To solve this task, the learning algorithm is usually asked to produce a function mapping an input vector to a category. Examples of classification include object recognition, speech recognition, and medical diagnosis.

Logistic Regression is a foundational linear model for binary classification. It models the probability that an observation belongs to a particular class using the sigmoid activation function. The model optimizes parameters by minimizing the cross-entropy loss function using gradient descent. Regularization techniques such as L1 Lasso and L2 Ridge are applied to mitigate overfitting on high-dimensional feature spaces.

Evaluation metrics for supervised classification include Accuracy, Precision, Recall, and the F1-score. Precision measures the fraction of relevant instances among the retrieved instances, while Recall measures the fraction of relevant instances that were retrieved. When classes are heavily imbalanced, relying solely on accuracy produces misleading assessments, making Precision-Recall curves and F1-score essential diagnostic tools.
""",
    "unsupervised_clustering.txt": """Unsupervised Learning and Concept Clustering

Unsupervised learning is a type of machine learning that looks for previously undetected patterns in a dataset with no pre-existing labels and with a minimum of human supervision. In contrast to supervised learning that usually makes use of human-labelled data, unsupervised learning allows for the modeling of probability densities over inputs.

Cluster analysis or clustering is the task of grouping a set of objects in such a way that objects in the same group, called a cluster, are more similar to each other than to those in other groups. It is a main task of exploratory data analysis and a common technique for statistical data analysis used in machine learning, pattern recognition, and information retrieval.

K-Means clustering is one of the most widely used unsupervised partitioning algorithms. Given a set of observations, k-means clustering aims to partition the n observations into k sets so as to minimize the within-cluster sum of squares or variance. The algorithm begins by selecting k initial cluster centroids, frequently employing the K-Means++ initialization heuristic to spread initial seeds and avoid poor local optima.

The Silhouette Coefficient is an evaluation metric used to calculate the goodness of a clustering technique. Its value ranges from -1 to 1, where a high value indicates that the object is well matched to its own cluster and poorly matched to neighboring clusters. If many points have a low or negative value, the clustering configuration may have too many or too few clusters.
""",
    "knowledge_tracing.txt": """Bayesian Knowledge Tracing and Adaptive Student Modeling

Bayesian Knowledge Tracing, or BKT, is an algorithm used in intelligent tutoring systems to model each learner's mastery of the knowledge components being taught. BKT assumes that a student's knowledge state is binary: a skill is either learned or not learned.

The standard BKT formulation utilizes four key probability parameters:
1. P(L0): The initial probability that the student already knows the skill before any practice opportunities.
2. P(T): The probability that the student transitions from the unlearned state to the learned state following an opportunity.
3. P(G): The probability of a Guess, meaning the student answers correctly despite not knowing the skill.
4. P(S): The probability of a Slip, meaning the student answers incorrectly despite genuinely possessing knowledge of the skill.

At each practice event, BKT observes student correctness and applies Bayes rule to compute the posterior probability that the student knew the skill prior to the attempt. Then, it incorporates the learning transition parameter P(T) to project the updated mastery probability into the future. Intelligent tutoring systems use this updated mastery to identify student misconceptions, schedule spaced practice, and generate personalized revision recommendations.
"""
}

SAMPLE_QUESTIONS = [
    {
        "topic_keyword": "supervised",
        "question": "What is the primary difference between classification and regression in supervised learning?",
        "options": [
            "Classification predicts discrete class labels while regression predicts continuous numerical values.",
            "Classification uses unlabelled data while regression requires labels.",
            "Regression uses neural networks while classification only uses linear formulas.",
            "Classification cannot be evaluated with accuracy metrics."
        ],
        "correct_index": 0,
        "explanation": "Classification models output categorical labels, whereas regression models estimate continuous numeric values.",
        "difficulty": "easy"
    },
    {
        "topic_keyword": "supervised",
        "question": "Why is accuracy often an insufficient metric for evaluating classifiers on imbalanced datasets?",
        "options": [
            "Accuracy requires GPU acceleration to compute.",
            "A naive model predicting only the majority class can yield high accuracy while failing to detect the minority class.",
            "Accuracy cannot be calculated on binary targets.",
            "Precision and Recall are always equal to accuracy."
        ],
        "correct_index": 1,
        "explanation": "On imbalanced data, predicting only the dominant class achieves high accuracy despite failing to identify minority instances.",
        "difficulty": "medium"
    },
    {
        "topic_keyword": "clustering",
        "question": "What is the key advantage of K-Means++ initialization over uniform random seed initialization?",
        "options": [
            "It automatically determines the true number of clusters k.",
            "It guarantees that the clustering will execute in zero iterations.",
            "It spreads initial centroids apart based on squared distances, reducing the risk of converging to poor local minima.",
            "It transforms the algorithm into a supervised classifier."
        ],
        "correct_index": 2,
        "explanation": "K-Means++ samples initial seeds with probability proportional to squared distance from the nearest existing centroid, leading to provably better clusterings.",
        "difficulty": "medium"
    },
    {
        "topic_keyword": "clustering",
        "question": "What does a negative Silhouette score typically indicate about an observation's cluster assignment?",
        "options": [
            "The point is positioned closer to neighboring clusters than to its assigned cluster centroid.",
            "The clustering achieved optimal global convergence.",
            "The dataset has zero variance.",
            "K-Means was executed with an infinite number of clusters."
        ],
        "correct_index": 0,
        "explanation": "Negative silhouette values mean that the average dissimilarity to members of the same cluster is greater than the dissimilarity to the nearest neighboring cluster.",
        "difficulty": "hard"
    },
    {
        "topic_keyword": "tracing",
        "question": "In Bayesian Knowledge Tracing (BKT), what does the parameter P(S) represent?",
        "options": [
            "Probability that a student guesses the answer correctly without understanding.",
            "Probability that a student slips and answers incorrectly despite knowing the skill.",
            "Probability of initial mastery prior to observing any practice attempts.",
            "Probability that a student learns the concept during an attempt."
        ],
        "correct_index": 1,
        "explanation": "P(S), or the Slip probability, accounts for careless errors where a knowledgeable student responds incorrectly.",
        "difficulty": "easy"
    },
    {
        "topic_keyword": "tracing",
        "question": "In BKT, how does an incorrect response affect the posterior mastery probability before the learning transition is applied?",
        "options": [
            "The posterior mastery probability strictly decreases relative to prior mastery.",
            "The posterior mastery probability immediately resets to 1.0.",
            "An incorrect response has no mathematical impact on posterior mastery.",
            "Mastery probability is multiplied by the guess parameter P(G)."
        ],
        "correct_index": 0,
        "explanation": "Under standard BKT conditions where (1 - P(G)) > P(S), observing an incorrect response lowers the posterior belief that the skill was mastered.",
        "difficulty": "medium"
    }
]


def seed_demo_data():
    db: Session = SessionLocal()
    try:
        # Create or retrieve demo student
        demo_email = "demo@studypal.edu"
        user = db.query(User).filter(User.email == demo_email).first()
        if not user:
            user = User(
                email=demo_email,
                hashed_password=get_password_hash("StudyPalDemo2026!"),
                display_name="Alex Rivera (Demo Student)",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created demo student account: {demo_email} / StudyPalDemo2026!")

        # Create or retrieve demo course
        course = db.query(Course).filter(Course.owner_id == user.id, Course.name == "Machine Learning & Cognitive Systems").first()
        if not course:
            course = Course(
                owner_id=user.id,
                name="Machine Learning & Cognitive Systems",
                description="Comprehensive course covering supervised classification, unsupervised clustering, and intelligent student modeling.",
            )
            db.add(course)
            db.commit()
            db.refresh(course)
            print(f"Created demo course: '{course.name}'")

        # Ingest sample documents and chunks
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        for filename, text_content in SAMPLE_NOTES.items():
            file_path = upload_dir / filename
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text_content)

            existing_doc = db.query(Document).filter(Document.course_id == course.id, Document.original_filename == filename).first()
            if not existing_doc:
                doc = Document(
                    course_id=course.id,
                    original_filename=filename,
                    storage_identifier=str(file_path),
                    file_type="txt",
                    file_size_bytes=len(text_content.encode("utf-8")),
                    content_checksum=f"demo_checksum_{filename}",
                    processing_status="completed",
                    total_pages=1,
                    chunk_count=0,
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)

                # Chunk and embed
                pages = [{"page_number": 1, "text": text_content}]
                raw_chunks = chunk_document(pages, target_words=120, min_words=20, max_words=200)
                embeddings = retrieval_engine.encode_embeddings([c["text_content"] for c in raw_chunks])

                for idx, c in enumerate(raw_chunks):
                    chunk_obj = DocumentChunk(
                        document_id=doc.id,
                        course_id=course.id,
                        chunk_index=c["chunk_index"],
                        text_content=c["text_content"],
                        word_count=c["word_count"],
                        page_number=1,
                        embedding_vector=json.dumps(embeddings[idx]),
                    )
                    db.add(chunk_obj)

                doc.chunk_count = len(raw_chunks)
                db.commit()
                print(f"Ingested note '{filename}' with {len(raw_chunks)} chunks.")

        # Fit TF-IDF & Discover Topics
        all_chunks = db.query(DocumentChunk).filter(DocumentChunk.course_id == course.id).all()
        retrieval_engine.fit_tfidf(course.id, [c.text_content for c in all_chunks])

        chunk_payload = [{"id": c.id, "text_content": c.text_content, "embedding_vector": c.embedding_vector} for c in all_chunks]
        clust_res = topic_clusterer.discover_topics(chunk_payload, n_clusters=3)

        created_topics = []
        for top_item in clust_res.get("topics", []):
            existing_t = db.query(Topic).filter(Topic.course_id == course.id, Topic.cluster_index == top_item["cluster_index"]).first()
            if not existing_t:
                new_t = Topic(
                    course_id=course.id,
                    cluster_index=top_item["cluster_index"],
                    label=top_item["label"],
                    keywords=top_item["keywords"],
                    chunk_count=len(top_item["chunk_indices"]),
                )
                db.add(new_t)
                db.commit()
                db.refresh(new_t)
                created_topics.append(new_t)
                for c_idx in top_item["chunk_indices"]:
                    all_chunks[c_idx].topic_id = new_t.id
            else:
                created_topics.append(existing_t)
        db.commit()
        print(f"Discovered and assigned {len(created_topics)} topics.")

        # Seed Curated Quiz Questions
        for q_data in SAMPLE_QUESTIONS:
            # Map to nearest topic
            matched_topic = created_topics[0]
            for t in created_topics:
                if q_data["topic_keyword"] in t.label.lower() or q_data["topic_keyword"] in (t.keywords or "").lower():
                    matched_topic = t
                    break

            existing_q = db.query(QuizQuestion).filter(
                QuizQuestion.course_id == course.id,
                QuizQuestion.question_text == q_data["question"]
            ).first()
            if not existing_q:
                q_obj = QuizQuestion(
                    course_id=course.id,
                    topic_id=matched_topic.id,
                    question_text=q_data["question"],
                    options_json=json.dumps(q_data["options"]),
                    correct_option_index=q_data["correct_index"],
                    explanation=q_data["explanation"],
                    difficulty=q_data["difficulty"],
                    provenance="curated",
                    is_active=True,
                )
                db.add(q_obj)
        db.commit()
        print(f"Seeded {len(SAMPLE_QUESTIONS)} curated quiz questions.")

        print("\nDemo data seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_demo_data()
