// Shared types for the Reddit Worry Finder application

export interface SearchQuery {
  original_text: string;
  normalized_text: string;
  keyphrases: string[];
  search_terms: string[];
  expanded_terms: Record<string, string[]>;
}

export interface Subreddit {
  name: string;
  title: string;
  relevance_score: number;
  quality_score: number;
}

export interface Post {
  id: string;
  title: string;
  selftext?: string;
  author: string;
  score: number;
  num_comments: number;
  url: string;
  permalink: string;
  created_utc: string;
  subreddit: string;
  ranking_scores?: {
    composite: number;
    semantic_similarity: number;
    recency_score: number;
    subreddit_quality: number;
    score_normalized: number;
    comments_normalized: number;
  };
}

export interface SearchResults {
  query: SearchQuery;
  subreddits: Subreddit[];
  posts: Post[];
  metadata: {
    total_posts_found: number;
    subreddits_searched: number;
    processing_time_seconds: number;
    search_terms_used: number;
  };
}

export interface Draft {
  title: string;
  body: string;
  generated_by: "llm" | "template";
  reddit_submit_url?: string;
}

export interface Alert {
  id: string;
  query_text: string;
  positive_filters?: string[];
  negative_filters?: string[];
  subreddits?: string[];
  frequency_minutes: number;
  is_active: boolean;
  created_at: string;
}

// API Request/Response types
export interface SearchRequest {
  text: string;
  max_results?: number;
  max_subreddits?: number;
}

export interface DraftRequest {
  text: string;
  region?: string;
}

export interface AlertCreateRequest {
  query_text: string;
  positive_filters?: string[];
  negative_filters?: string[];
  subreddits?: string[];
  frequency_minutes?: number;
}

// Error types
export interface APIError {
  detail: string;
  status_code: number;
}

// Health check response
export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}
