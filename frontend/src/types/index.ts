export type Topic =
  | "travel"
  | "culture"
  | "cost_of_living"
  | "academics"
  | "housing"
  | "jobs"
  | "general";

export type Sentiment = "positive" | "neutral" | "negative";

export type PostStatus = "published" | "flagged" | "removed";

export type VerificationStatus =
  | "PENDING"
  | "verified_pending"
  | "awaiting_domain_review"
  | "VERIFIED"
  | "REJECTED";

export interface University {
  id: string;
  name: string;
  domain: string;
  city: string | null;
  short_name?: string | null;
  state?: string | null;
  type?: string | null;
  website?: string | null;
  verified_student_count?: number;
}

export interface User {
  id: string;
  email: string;
  display_name: string;
  country: string;
  university: string | null;
  program: string | null;
  year_of_study: string | null;
  is_verified: boolean;
  email_confirmed_at?: string | null;
  is_admin?: boolean;
  verification_status: VerificationStatus;
  university_link?: University | null;
  created_at: string;
}

export interface WatchlistMatch {
  name: string;
  university_domain?: string | null;
  role?: string | null;
}

export interface RegisterResponse {
  id: string;
  email: string;
  is_verified: boolean;
  next: string;
  access_token?: string | null;
}

export interface Author {
  id: string;
  display_name: string;
  university: University | null;
}

export interface Post {
  id: string;
  title: string;
  body: string;
  topic: Topic;
  sentiment: Sentiment;
  status: PostStatus;
  score: number;
  upvotes: number;
  downvotes: number;
  comment_count: number;
  author: Author;
  university: University | null;
  created_at: string;
  my_vote: number;
  /** @deprecated use my_vote */
  user_vote?: number | null;
  is_hidden?: boolean;
  hidden_reason?: string | null;
  watchlist_matches?: WatchlistMatch[] | null;
}

export interface Comment {
  id: string;
  body: string;
  post_id: string;
  parent_comment_id: string | null;
  is_deleted: boolean;
  score: number;
  upvotes: number;
  downvotes: number;
  author: Author;
  created_at: string;
  my_vote: number;
  is_hidden?: boolean;
  hidden_reason?: string | null;
  watchlist_matches?: WatchlistMatch[] | null;
}

export interface VoteCounts {
  upvotes: number;
  downvotes: number;
  score: number;
  my_vote: number;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export const TOPIC_LABELS: Record<Topic, string> = {
  travel: "Travel",
  culture: "Culture",
  cost_of_living: "Cost of Living",
  academics: "Academics",
  housing: "Housing",
  jobs: "Jobs",
  general: "General",
};

export const SENTIMENT_LABELS: Record<Sentiment, string> = {
  positive: "Positive",
  neutral: "Neutral",
  negative: "Negative",
};
