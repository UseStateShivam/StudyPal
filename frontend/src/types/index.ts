export interface User {
  id: string;
  email: string;
  display_name: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Course {
  id: string;
  owner_id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  document_count: number;
  topic_count: number;
}

export interface DocumentItem {
  id: string;
  course_id: string;
  original_filename: string;
  file_type: string;
  file_size_bytes: number;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string;
  total_pages?: number;
  chunk_count: number;
  uploaded_at: string;
  completed_at?: string;
}

export interface TopicItem {
  id: string;
  course_id: string;
  cluster_index: number;
  label: string;
  is_custom_label: boolean;
  keywords?: string;
  summary?: string;
  chunk_count: number;
  created_at: string;
}

export interface SearchResultItem {
  chunk_id: string;
  document_id: string;
  document_title: string;
  passage: string;
  page_number?: number;
  similarity_score: number;
  retrieval_method: string;
  topic_label?: string;
}

export interface SearchResponse {
  query: string;
  retrieval_method_used: string;
  total_results: number;
  results: SearchResultItem[];
}

export interface QuizQuestion {
  id: string;
  topic_id: string;
  question_text: string;
  options: string[];
  difficulty: string;
  provenance: string;
}

export interface QuizSession {
  session_id: string;
  course_id: string;
  topic_id?: string;
  total_questions: number;
  questions: QuizQuestion[];
}

export interface QuizAnswerResult {
  question_id: string;
  selected_option_index: number;
  correct_option_index: number;
  is_correct: boolean;
  explanation?: string;
  updated_mastery_probability: number;
  feedback: string;
}

export interface LearnerTopicState {
  topic_id: string;
  topic_label: string;
  mastery_probability: number;
  total_attempts: number;
  correct_attempts: number;
  last_practiced_at?: string;
}

export interface CourseProgressOverview {
  course_id: string;
  overall_mastery: number;
  total_quizzes_taken: number;
  total_questions_answered: number;
  overall_accuracy: number;
  topics_state: LearnerTopicState[];
  mastery_timeline: Array<{
    timestamp: string;
    topic_label: string;
    mastery: number;
    is_correct: boolean;
  }>;
}

export interface RecommendationItem {
  topic_id: string;
  topic_label: string;
  priority_rank: number;
  revision_score: number;
  mastery_probability: number;
  weakness_probability?: number;
  has_attempted_quizzes: boolean;
  primary_reason: string;
  recommended_action: string;
  suggested_passages: SearchResultItem[];
  contributing_scores: {
    mastery_weight_contrib: number;
    weakness_weight_contrib: number;
    recency_weight_contrib: number;
  };
}

export interface RecommendationResponse {
  course_id: string;
  is_cold_start: boolean;
  recommendation_mode: 'content-based' | 'personalised-learner';
  recommendations: RecommendationItem[];
}
