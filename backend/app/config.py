"""StudyPal application configuration using Pydantic Settings v2."""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application
    APP_NAME: str = "StudyPal"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "studypal_dev_secret_key_super_secure_random_seed_12345!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "sqlite:///./studypal.db"

    # Storage paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "txt"]

    # Ingestion & Chunking
    CHUNK_TARGET_WORDS: int = 200
    CHUNK_MIN_WORDS: int = 30
    CHUNK_MAX_WORDS: int = 400
    CHUNK_OVERLAP_WORDS: int = 30

    # Content Engine & Retrieval
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "cpu"
    MODEL_CACHE_DIR: str = "./models/cache"
    RETRIEVAL_METHOD: str = "hybrid"  # "tfidf", "embedding", "hybrid"
    HYBRID_ALPHA: float = 0.5
    TOP_K_RETRIEVAL: int = 5

    # Topic Discovery (K-Means)
    MIN_CHUNKS_FOR_CLUSTERING: int = 4
    DEFAULT_N_CLUSTERS: int = 3
    CLUSTERING_RANDOM_STATE: int = 42

    # Learner Engine - Bayesian Knowledge Tracing (BKT)
    BKT_P_L0: float = Field(default=0.20, ge=0.0, le=1.0)
    BKT_P_T: float = Field(default=0.15, ge=0.0, le=1.0)
    BKT_P_G: float = Field(default=0.25, ge=0.0, le=1.0)
    BKT_P_S: float = Field(default=0.10, ge=0.0, le=1.0)

    # Learner Engine - Weakness Classifier
    MIN_SAMPLES_FOR_TRAINING: int = 20

    # Recommendation Engine Weights
    REC_WEIGHT_MASTERY: float = 0.5
    REC_WEIGHT_WEAKNESS: float = 0.3
    REC_WEIGHT_RECENCY: float = 0.2

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    def get_upload_path(self) -> Path:
        p = Path(self.UPLOAD_DIR)
        if not p.is_absolute():
            p = self.BASE_DIR / p
        p.mkdir(parents=True, exist_ok=True)
        return p

    def get_model_cache_path(self) -> Path:
        p = Path(self.MODEL_CACHE_DIR)
        if not p.is_absolute():
            p = self.BASE_DIR / p
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
