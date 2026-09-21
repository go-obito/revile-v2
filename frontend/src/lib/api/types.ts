export type Role = "admin" | "editor" | "author" | "reader";
export type PostStatus = "draft" | "scheduled" | "published" | "archived";
export type CommentStatus = "pending" | "flagged" | "approved" | "spam" | "rejected";

export interface UserRead {
  id: number;
  email: string;
  name: string;
  role: Role;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserRead;
}

export interface CategoryRead {
  id: number;
  name: string;
  slug: string;
}

export type TagRead = CategoryRead;

export interface PostRead {
  id: number;
  title: string;
  slug: string;
  dek: string | null;
  body: string;
  featured_image_url: string | null;
  featured_image_alt: string;
  status: PostStatus;
  is_breaking: boolean;
  author_id: number;
  author_name?: string | null;
  editor_id: number | null;
  published_at: string | null;
  updated_at: string;
  created_at: string;
  categories: CategoryRead[];
  tags: TagRead[];
}

export interface PostList {
  items: PostRead[];
  next_cursor: string | null;
}

export interface CommentRead {
  id: number;
  post_id: number;
  parent_id: number | null;
  author_name: string;
  body: string;
  status: CommentStatus;
  created_at: string;
}

export interface ImageKitAuthResponse {
  token: string;
  expire: number;
  signature: string;
}

export interface ModerationCommentRead extends CommentRead {
  spam_score: number | null;
  spam_reason: string | null;
}

export interface CommentReportRead {
  id: number;
  comment_id: number;
  reason: string;
  reported_at: string;
}

export interface ReportedCommentRead extends ModerationCommentRead {
  reports: CommentReportRead[];
}

export interface CommentAuditRead {
  id: number;
  comment_id: number;
  actor_id: number;
  action: string;
  created_at: string;
}

export interface MediaRead {
  id: number;
  file_url: string;
  imagekit_file_id: string;
  alt_text: string;
  post_id: number | null;
}

export interface PostCreate {
  title: string;
  slug: string;
  dek?: string | null;
  body: string;
  category_ids?: number[];
  tag_ids?: number[];
  is_breaking?: boolean;
}

export interface PostUpdate {
  title?: string;
  slug?: string;
  dek?: string | null;
  body?: string;
  category_ids?: number[];
  tag_ids?: number[];
  is_breaking?: boolean;
}

export interface CommentCreate {
  author_name: string;
  author_email: string;
  body: string;
  parent_id?: number | null;
  idempotency_key: string;
}

export interface NewsletterSubscriptionResponse {
  message: string;
}

export interface ApiErrorPayload {
  detail?: string | { msg?: string }[];
}

export interface ApiRequestOptions extends RequestInit {
  accessToken?: string;
}
