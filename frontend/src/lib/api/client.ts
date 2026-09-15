import type {
  ApiErrorPayload,
  ApiRequestOptions,
  CategoryRead,
  CommentCreate,
  CommentRead,
  CommentStatus,
  MediaUploadResponse,
  PostCreate,
  PostList,
  PostRead,
  PostUpdate,
  PostStatus,
  Role,
  TagRead,
  TokenResponse,
  UserRead,
} from "./types";

const publicApiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const serverApiUrl = process.env.INTERNAL_API_URL ?? publicApiUrl;

function getApiUrl() {
  if (typeof window !== "undefined") return "/api/v1";
  const origin = typeof window === "undefined" ? serverApiUrl : publicApiUrl;
  return origin.replace(/\/$/, "").endsWith("/api/v1")
    ? origin.replace(/\/$/, "")
    : `${origin.replace(/\/$/, "")}/api/v1`;
}

function errorMessage(payload: ApiErrorPayload) {
  if (typeof payload.detail === "string") return payload.detail;
  if (Array.isArray(payload.detail)) return payload.detail.map((item) => item.msg).filter(Boolean).join(", ");
  return "The request could not be completed.";
}

async function request<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { accessToken, headers, ...init } = options;
  const response = await fetch(`${getApiUrl()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...headers,
    },
    credentials: "include",
    cache: init.cache ?? "no-store",
  });

  if (!response.ok) {
    let payload: ApiErrorPayload = {};
    try {
      payload = await response.json();
    } catch {
      // Keep the status-based message when the backend sends an empty response.
    }
    throw new Error(errorMessage(payload));
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

function query(params: Record<string, string | number | undefined>) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") search.set(key, String(value));
  }
  const value = search.toString();
  return value ? `?${value}` : "";
}

export const api = {
  login(email: string, password: string) {
    return request<TokenResponse>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
  },
  refresh() {
    return request<TokenResponse>("/auth/refresh", { method: "POST" });
  },
  logout() {
    return request<void>("/auth/logout", { method: "POST" });
  },
  getPosts(params: { cursor?: string; limit?: number; category?: string; tag?: string } = {}) {
    return request<PostList>(`/posts${query(params)}`, { next: { revalidate: 30 } });
  },
  getBreakingPosts() {
    return request<PostRead[]>("/posts/breaking", { next: { revalidate: 15 } });
  },
  getPost(slug: string) {
    return request<PostRead>(`/posts/${encodeURIComponent(slug)}`, { next: { revalidate: 60 } });
  },
  getManagePosts(params: { status?: PostStatus; cursor?: string; limit?: number }, accessToken: string) {
    return request<PostList>(`/posts/manage${query(params)}`, { accessToken });
  },
  getManagePost(postId: number, accessToken: string) {
    return request<PostRead>(`/posts/manage/${postId}`, { accessToken });
  },
  getCategories() {
    return request<CategoryRead[]>("/categories", { next: { revalidate: 300 } });
  },
  getCategoryPosts(slug: string, limit = 20) {
    return request<PostList>(`/categories/${encodeURIComponent(slug)}/posts${query({ limit })}`, { next: { revalidate: 30 } });
  },
  getTags() {
    return request<TagRead[]>("/tags", { next: { revalidate: 300 } });
  },
  searchPosts(term: string) {
    return request<PostRead[]>(`/search${query({ q: term })}`, { next: { revalidate: 15 } });
  },
  createComment(postId: number, payload: CommentCreate) {
    return request<CommentRead>(`/posts/${postId}/comments`, { method: "POST", body: JSON.stringify(payload) });
  },
  createPost(payload: PostCreate, accessToken: string) {
    return request<PostRead>("/posts", { method: "POST", body: JSON.stringify(payload), accessToken });
  },
  updatePost(postId: number, payload: PostUpdate, accessToken: string) {
    return request<PostRead>(`/posts/${postId}`, { method: "PATCH", body: JSON.stringify(payload), accessToken });
  },
  publishPost(postId: number, accessToken: string) {
    return request<PostRead>(`/posts/${postId}/publish`, { method: "POST", accessToken });
  },
  schedulePost(postId: number, publishedAt: string, accessToken: string) {
    return request<PostRead>(`/posts/${postId}/schedule${query({ published_at: publishedAt })}`, { method: "POST", accessToken });
  },
  unpublishPost(postId: number, accessToken: string) {
    return request<PostRead>(`/posts/${postId}/unpublish`, { method: "POST", accessToken });
  },
  flagBreaking(postId: number, accessToken: string) {
    return request<PostRead>(`/posts/${postId}/flag-breaking`, { method: "POST", accessToken });
  },
  getPendingComments(accessToken: string) {
    return request<CommentRead[]>("/admin/comments/pending", { accessToken });
  },
  moderateComment(commentId: number, status: CommentStatus, accessToken: string) {
    return request<CommentRead>(`/admin/comments/${commentId}/moderate`, { method: "PATCH", body: JSON.stringify({ status }), accessToken });
  },
  createUser(payload: { email: string; password: string; name: string; role: Role }, accessToken: string) {
    return request<UserRead>("/users", { method: "POST", body: JSON.stringify(payload), accessToken });
  },
  updateUserRole(userId: number, role: Role, accessToken: string) {
    return request<UserRead>(`/users/${userId}/role`, { method: "PATCH", body: JSON.stringify({ role }), accessToken });
  },
  requestUpload(payload: { filename: string; content_type: string; alt_text: string; post_id?: number }, accessToken: string) {
    return request<MediaUploadResponse>("/media/upload-url", { method: "POST", body: JSON.stringify(payload), accessToken });
  },
};
