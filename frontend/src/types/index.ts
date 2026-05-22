export type Topic =
  | "travel"
  | "culture"
  | "cost_of_living"
  | "academics"
  | "housing"
  | "jobs"
  | "general";

export type PostStatus = "published" | "flagged" | "removed";

export type VerificationStatus = "pending" | "verified" | "rejected";

export interface University {
  id: string;
  name: string;
  domain: string;
  country: string;
  city: string | null;
}

export interface User {
  id: string;
  email: string;
  display_name: string;
  country: string | null;
  verification_status: VerificationStatus;
  university: University | null;
  created_at: string;
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
  status: PostStatus;
  score: number;
  comment_count: number;
  author: Author;
  university: University | null;
  created_at: string;
  user_vote: number | null;
}

export interface Comment {
  id: string;
  body: string;
  status: PostStatus;
  author: Author;
  created_at: string;
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
