/**
 * Centralised API client for the Ink & Quill backend (FastAPI).
 *
 * All requests go to /api/v1/* on the same origin (Next.js proxies in dev,
 * same host in production).  Cookies are always sent so the HttpOnly
 * session cookie is included automatically.
 */

import type {
  BalanceState,
  BillingDashboard,
  InterviewQuestionsPayload,
  InterviewStatusPayload,
  MaintenanceState,
  OwnerFamilySummary,
  ReferralHistoryResponse,
  ReferralRewardsResponse,
  ReferralStats,
  SessionUser,
  UserInsightsPayload,
} from "@/lib/types";

const API_BASE = "/api/v1";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });

  if (!res.ok) {
    let message = `Request failed: ${res.status} ${res.statusText}`;
    try {
      const body = (await res.json()) as { detail?: unknown; message?: string };
      if (typeof body.detail === "string") {
        message = body.detail;
      } else if (Array.isArray(body.detail)) {
        // FastAPI Pydantic validation errors: [{loc, msg, type}, ...]
        message = body.detail
          .map((e: { msg?: string; loc?: string[] }) =>
            e.msg ?? JSON.stringify(e)
          )
          .join("; ");
      } else if (body.message) {
        message = body.message;
      }
    } catch {
      // ignore JSON parse failures
    }
    throw new Error(message);
  }

  // 204 No Content
  if (res.status === 204) return undefined as unknown as T;

  const envelope = (await res.json()) as { data?: T; success?: boolean } | T;
  // Backend wraps most responses in { success, data, ... }
  if (envelope !== null && typeof envelope === "object" && "data" in (envelope as object)) {
    return (envelope as { data: T }).data;
  }
  return envelope as T;
}

/** Returns the raw response JSON without unwrapping the `data` envelope. */
async function apiFetchRaw<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });

  if (!res.ok) {
    let message = `Request failed: ${res.status} ${res.statusText}`;
    try {
      const body = (await res.json()) as { detail?: unknown; message?: string };
      if (typeof body.detail === "string") {
        message = body.detail;
      } else if (Array.isArray(body.detail)) {
        message = body.detail
          .map((e: { msg?: string; loc?: string[] }) =>
            e.msg ?? JSON.stringify(e)
          )
          .join("; ");
      } else if (body.message) {
        message = body.message;
      }
    } catch {
      // ignore JSON parse failures
    }
    throw new Error(message);
  }

  if (res.status === 204) return undefined as unknown as T;
  return res.json() as Promise<T>;
}

async function sameOriginFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    credentials: "include",
    ...init,
  });

  if (!res.ok) {
    let message = `Request failed: ${res.status} ${res.statusText}`;
    try {
      const body = (await res.json()) as { detail?: unknown; message?: string };
      if (typeof body.detail === "string") {
        message = body.detail;
      } else if (Array.isArray(body.detail)) {
        message = body.detail
          .map((e: { msg?: string; loc?: string[] }) =>
            e.msg ?? JSON.stringify(e)
          )
          .join("; ");
      } else if (body.message) {
        message = body.message;
      }
    } catch {
      // ignore JSON parse failures
    }
    throw new Error(message);
  }

  if (res.status === 204) return undefined as unknown as T;

  const envelope = (await res.json()) as { data?: T; success?: boolean } | T;
  if (envelope !== null && typeof envelope === "object" && "data" in (envelope as object)) {
    return (envelope as { data: T }).data;
  }
  return envelope as T;
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export async function fetchSession(): Promise<SessionUser | null> {
  try {
    return await apiFetch<SessionUser>("/users/me");
  } catch {
    return null;
  }
}

export async function loginUser(credentials: { username: string; password: string }): Promise<void> {
  const body = new URLSearchParams();
  body.set("username", credentials.username);
  body.set("password", credentials.password);
  await apiFetch<unknown>("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });
}

export async function logoutUser(): Promise<void> {
  await apiFetch<unknown>("/auth/logout", { method: "POST" });
}

export async function registerUser(payload: {
  username: string;
  email: string;
  password: string;
  display_name?: string;
  terms_accepted?: boolean;
}): Promise<{ data: SessionUser }> {
  return apiFetchRaw<{ data: SessionUser }>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function requestPasswordReset(payload: { email: string }): Promise<{ message: string }> {
  return apiFetchRaw<{ message: string }>("/auth/password-reset/request", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function confirmPasswordReset(payload: {
  token: string;
  new_password: string;
}): Promise<{ message: string }> {
  return apiFetchRaw<{ message: string }>("/auth/password-reset/confirm", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getGoogleSignInUrl(): string {
  return `${API_BASE}/auth/google`;
}

// ---------------------------------------------------------------------------
// Users / Profile
// ---------------------------------------------------------------------------

export async function updateCurrentUserProfile(payload: {
  display_name?: string;
  email?: string;
  username?: string;
}): Promise<SessionUser> {
  return apiFetch<SessionUser>("/users/me", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

// ---------------------------------------------------------------------------
// Balance
// ---------------------------------------------------------------------------

export async function fetchBalance(): Promise<BalanceState> {
  return apiFetch<BalanceState>("/billing/balance");
}

// ---------------------------------------------------------------------------
// Maintenance
// ---------------------------------------------------------------------------

export async function fetchMaintenanceStatus(): Promise<MaintenanceState> {
  return apiFetch<MaintenanceState>("/maintenance/status");
}

// ---------------------------------------------------------------------------
// Billing
// ---------------------------------------------------------------------------

export async function fetchBillingDashboard(): Promise<BillingDashboard> {
  return apiFetch<BillingDashboard>("/billing/dashboard");
}

// ---------------------------------------------------------------------------
// Onboarding / Interview
// ---------------------------------------------------------------------------

export async function fetchInterviewQuestions(interviewId: string): Promise<InterviewQuestionsPayload> {
  return apiFetch<InterviewQuestionsPayload>(`/interview/questions/${interviewId}`);
}

export async function fetchInterviewStatus(interviewId: string): Promise<InterviewStatusPayload> {
  return apiFetch<InterviewStatusPayload>(`/interview/status/${interviewId}`);
}

export async function fetchUserInsights(): Promise<UserInsightsPayload> {
  return apiFetch<UserInsightsPayload>("/interview/user-insights");
}

// ---------------------------------------------------------------------------
// Referrals
// ---------------------------------------------------------------------------

export async function fetchReferralStats(): Promise<ReferralStats> {
  return apiFetch<ReferralStats>("/referrals");
}

export async function fetchReferralHistory(): Promise<ReferralHistoryResponse> {
  return apiFetch<ReferralHistoryResponse>("/referrals/history");
}

export async function fetchReferralRewards(): Promise<ReferralRewardsResponse> {
  return apiFetch<ReferralRewardsResponse>("/referrals/rewards");
}

// ---------------------------------------------------------------------------
// Storytelling — Stories
// ---------------------------------------------------------------------------

export interface StoryEntry {
  id: number;
  title: string;
  short_description?: string | null;
  story_genre?: string | null;
  story_type: string;
  created_at: string;
  updated_at: string;
}

export async function fetchUserStories(): Promise<StoryEntry[]> {
  return apiFetch<StoryEntry[]>("/stories/");
}

export interface StoryDetail extends StoryEntry {
  user_id: number;
  world_id: number;
  ai_summary?: string | null;
  image_url?: string | null;
  image_prompt_definition?: string | null;
  story_tone?: string | null;
  primary_conflict_type?: string | null;
}

export async function fetchStory(storyId: number): Promise<StoryDetail> {
  return apiFetch<StoryDetail>(`/stories/${storyId}`);
}

export interface StoryCreatePayload {
  title: string;
  short_description?: string | null;
  story_genre?: string | null;
  story_tone?: string | null;
  primary_conflict_type?: string | null;
  image_prompt_definition?: string | null;
  world_id?: number | null;
  story_type?: string;
}

export interface StoryCreateResponse {
  data: StoryDetail;
}

export async function createStory(payload: StoryCreatePayload): Promise<StoryDetail> {
  return apiFetch<StoryDetail>("/stories/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export interface StoryUpdatePayload {
  title?: string;
  short_description?: string | null;
  ai_summary?: string | null;
  world_id?: number | null;
  image_prompt_definition?: string | null;
  story_genre?: string | null;
  story_tone?: string | null;
  primary_conflict_type?: string | null;
}

export async function updateStory(storyId: number, payload: StoryUpdatePayload): Promise<StoryDetail> {
  return apiFetch<StoryDetail>(`/stories/${storyId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteStory(storyId: number): Promise<void> {
  return apiFetch<void>(`/stories/${storyId}`, { method: "DELETE" });
}

export interface StoryPublishPayload {
  visibility?: string; // "public" | "private"
  description?: string | null;
}

export interface StoryPublishResult {
  message: string;
  published_url?: string | null;
  filename?: string | null;
  status: string;
}

export async function publishStory(storyId: number, payload: StoryPublishPayload): Promise<StoryPublishResult> {
  return apiFetch<StoryPublishResult>(`/stories/${storyId}/publish`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export interface StoryUpgradePayload {
  world_id?: number | null;
}

export async function upgradeStory(storyId: number, payload: StoryUpgradePayload): Promise<StoryDetail> {
  return apiFetch<StoryDetail>(`/stories/${storyId}/upgrade`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export interface StoryImage {
  id: number;
  url?: string | null;
  prompt?: string | null;
  revised_prompt?: string | null;
  created_at: string;
  is_current: boolean;
}

export async function fetchStoryImages(storyId: number): Promise<StoryImage[]> {
  return apiFetch<StoryImage[]>(`/stories/${storyId}/images`);
}

export async function setCurrentStoryImage(storyId: number, imageId: number): Promise<{ message: string; image_id: number; image_url?: string | null }> {
  return apiFetch<{ message: string; image_id: number; image_url?: string | null }>(`/stories/${storyId}/set-current-image/${imageId}`, {
    method: "POST",
  });
}

// ---------------------------------------------------------------------------
// Storytelling — Acts
// ---------------------------------------------------------------------------

export interface ActEntry {
  id: number;
  title: string;
  description?: string | null;
  act_number: number;
  story_id: number;
  act_summary?: string | null;
  ai_summary?: string | null;
  writer_notes?: string | null;
  image_url?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ActCreatePayload {
  title: string;
  description?: string | null;
  act_number: number;
  act_summary?: string | null;
  writer_notes?: string | null;
  image_prompt_definition?: string | null;
  system_prompt_id?: number | null;
  story_class_id?: number | null;
}

export async function fetchActsForStory(storyId: number): Promise<ActEntry[]> {
  return apiFetch<ActEntry[]>(`/stories/${storyId}/acts/`);
}

export async function createActForStory(storyId: number, payload: ActCreatePayload): Promise<ActEntry> {
  return apiFetch<ActEntry>(`/stories/${storyId}/acts/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateAct(actId: number, payload: Partial<ActCreatePayload>): Promise<ActEntry> {
  return apiFetch<ActEntry>(`/acts/${actId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteAct(actId: number): Promise<void> {
  return apiFetch<void>(`/acts/${actId}`, { method: "DELETE" });
}

// ---------------------------------------------------------------------------
// Storytelling — Scenes
// ---------------------------------------------------------------------------

export interface SceneEntry {
  id: number;
  title: string;
  content?: string | null;
  summary?: string | null;
  ai_summary?: string | null;
  scene_number: number;
  act_id: number;
  image_url?: string | null;
  created_at: string;
  updated_at: string;
}

export interface SceneCreatePayload {
  title: string;
  content?: string | null;
  summary?: string | null;
  scene_number: number;
}

export async function fetchScenesForAct(actId: number): Promise<SceneEntry[]> {
  return apiFetch<SceneEntry[]>(`/acts/${actId}/scenes/`);
}

export async function createSceneForAct(actId: number, payload: SceneCreatePayload): Promise<SceneEntry> {
  return apiFetch<SceneEntry>(`/acts/${actId}/scenes/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateScene(sceneId: number, payload: Partial<SceneCreatePayload>): Promise<SceneEntry> {
  return apiFetch<SceneEntry>(`/scenes/${sceneId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteScene(sceneId: number): Promise<void> {
  return apiFetch<void>(`/scenes/${sceneId}`, { method: "DELETE" });
}

// ---------------------------------------------------------------------------
// Storytelling — Worlds
// ---------------------------------------------------------------------------

export interface WorldEntry {
  id: number;
  name: string;
  short_description?: string | null;
  is_free_chat_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export async function fetchUserWorlds(): Promise<WorldEntry[]> {
  return apiFetch<WorldEntry[]>("/worlds/");
}

// ---------------------------------------------------------------------------
// Publishing — Published Stories
// ---------------------------------------------------------------------------

export interface PublishedStoryEntry {
  id: number;
  story_id: number;
  user_id: number;
  title: string;
  description?: string | null;
  published_url: string;
  filename: string;
  word_count?: number | null;
  is_public: boolean;
  is_featured: boolean;
  view_count: number;
  like_count: number;
  comment_count: number;
  average_rating?: number | null;
  published_at: string;
  updated_at: string;
  publisher_username?: string | null;
  publisher_display_name?: string | null;
  world_name?: string | null;
}

export interface PublishedStoryDetail extends PublishedStoryEntry {
  story_title?: string | null;
  story_short_description?: string | null;
  has_user_rated: boolean;
  user_rating?: number | null;
}

export interface PublishedStoryListResponse {
  stories: PublishedStoryEntry[];
  total: number;
  page: number;
  per_page: number;
}

export async function fetchPublishedStories(params?: {
  search?: string;
  sort_by?: string;
  is_featured?: boolean;
  page?: number;
  per_page?: number;
}): Promise<PublishedStoryListResponse> {
  const query = new URLSearchParams();
  if (params?.search) query.set("search", params.search);
  if (params?.sort_by) query.set("sort_by", params.sort_by);
  if (params?.is_featured !== undefined) query.set("is_featured", String(params.is_featured));
  if (params?.page) query.set("page", String(params.page));
  if (params?.per_page) query.set("per_page", String(params.per_page));
  const qs = query.toString();
  return apiFetch<PublishedStoryListResponse>(`/published-stories/${qs ? `?${qs}` : ""}`);
}

export async function fetchPublishedStory(storyId: number): Promise<PublishedStoryDetail> {
  return apiFetch<PublishedStoryDetail>(`/published-stories/${storyId}`);
}

export interface StoryComment {
  id: number;
  published_story_id: number;
  user_id: number;
  commenter_username?: string | null;
  commenter_display_name?: string | null;
  content: string;
  is_approved: boolean;
  created_at: string;
  updated_at: string;
}

export async function fetchStoryComments(storyId: number): Promise<StoryComment[]> {
  return apiFetch<StoryComment[]>(`/published-stories/${storyId}/comments`);
}

export async function createStoryComment(storyId: number, content: string): Promise<StoryComment> {
  return apiFetch<StoryComment>(`/published-stories/${storyId}/comments`, {
    method: "POST",
    body: JSON.stringify({ published_story_id: storyId, content }),
  });
}

export async function ratePublishedStory(storyId: number, rating: number): Promise<void> {
  await apiFetch<unknown>(`/published-stories/${storyId}/rate`, {
    method: "POST",
    body: JSON.stringify({ published_story_id: storyId, rating }),
  });
}

// ---------------------------------------------------------------------------
// Community — Forum
// ---------------------------------------------------------------------------

export interface ForumCategory {
  id: number;
  name: string;
  description?: string | null;
  slug: string;
  sort_order: number;
  is_active: boolean;
  icon?: string | null;
  thread_count: number;
  created_at: string;
  updated_at: string;
}

export async function fetchForumCategories(): Promise<ForumCategory[]> {
  return sameOriginFetch<ForumCategory[]>("/api/forum/categories/");
}

export interface ForumThreadSummary {
  id: number;
  title: string;
  slug: string;
  status: string;
  category_id: number;
  category_name?: string | null;
  user_id: number;
  username: string;
  world_id?: number | null;
  world_name?: string | null;
  story_id?: number | null;
  story_title?: string | null;
  view_count: number;
  post_count: number;
  last_post_at?: string | null;
  last_post_by_username?: string | null;
  is_pinned: boolean;
  is_locked: boolean;
  created_at: string;
  app_source?: string;
}

export interface ForumPost {
  id: number;
  content: string;
  content_html?: string | null;
  thread_id: number;
  user_id: number;
  username: string;
  user_display_name?: string | null;
  upvote_count: number;
  downvote_count: number;
  score: number;
  user_vote?: "upvote" | "downvote" | null;
  edit_count: number;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface ForumThreadDetail extends ForumThreadSummary {
  updated_at: string;
  posts: ForumPost[];
}

export async function fetchForumThreads(params?: { category_id?: number; app_source?: string }): Promise<ForumThreadSummary[]> {
  const query = new URLSearchParams();
  if (params?.category_id !== undefined) query.set("category_id", String(params.category_id));
  if (params?.app_source) query.set("app_source", params.app_source);
  const qs = query.toString();
  return sameOriginFetch<ForumThreadSummary[]>(`/api/forum/threads/${qs ? `?${qs}` : ""}`);
}

export async function fetchForumThread(threadId: number): Promise<ForumThreadDetail> {
  return sameOriginFetch<ForumThreadDetail>(`/api/forum/threads/${threadId}`);
}

export async function createForumThread(payload: {
  title: string;
  category_id: number;
  initial_post_content: string;
  app_source?: string;
}): Promise<ForumThreadDetail> {
  return sameOriginFetch<ForumThreadDetail>("/api/forum/threads/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function createForumPost(payload: {
  thread_id: number;
  content: string;
}): Promise<ForumPost> {
  return sameOriginFetch<ForumPost>("/api/forum/posts/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function voteForumPost(postId: number, voteType: "upvote" | "downvote"): Promise<{
  post_id: number;
  upvote_count: number;
  downvote_count: number;
  score: number;
  user_vote: string;
}> {
  return sameOriginFetch<{ post_id: number; upvote_count: number; downvote_count: number; score: number; user_vote: string }>(
    `/api/forum/posts/${postId}/vote`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ post_id: postId, vote_type: voteType }),
    }
  );
}

// ---------------------------------------------------------------------------
// Blog Comments
// ---------------------------------------------------------------------------

export interface BlogComment {
  id: number;
  content: string;
  author_id: number;
  post_id: number;
  parent_comment_id?: number | null;
  status: string;
  like_count: number;
  reply_count: number;
  is_author_reply: boolean;
  created_at: string;
  updated_at: string;
  author?: {
    id: number | null;
    username: string;
    display_name: string | null;
    profile_picture_url?: string | null;
  };
  replies?: BlogComment[];
}

export async function fetchBlogComments(postId: number): Promise<BlogComment[]> {
  return sameOriginFetch<BlogComment[]>(`/api/blog/posts/${postId}/comments`);
}

export async function createBlogComment(postId: number, content: string, parentCommentId?: number | null): Promise<BlogComment> {
  return sameOriginFetch<BlogComment>(`/api/blog/posts/${postId}/comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, parent_comment_id: parentCommentId ?? null }),
  });
}

export interface BlogPost {
  id: number;
  title: string;
  slug: string;
  content: string;
  excerpt?: string | null;
  featured_image_url?: string | null;
  status: string;
  author_id: number;
  view_count: number;
  like_count: number;
  comment_count: number;
  published_at?: string | null;
  created_at: string;
  updated_at: string;
}

export async function fetchBlogPosts(params?: { search?: string; category_id?: number; app_source?: string }): Promise<BlogPost[]> {
  const query = new URLSearchParams();
  if (params?.search) query.set("search", params.search);
  if (params?.category_id !== undefined) query.set("category_id", String(params.category_id));
  if (params?.app_source) query.set("app_source", params.app_source);
  const qs = query.toString();
  return sameOriginFetch<BlogPost[]>(`/api/blog/posts${qs ? `?${qs}` : ""}`);
}

export async function fetchBlogPost(slug: string): Promise<BlogPost> {
  return sameOriginFetch<BlogPost>(`/api/blog/posts/${slug}`);
}

export async function fetchBlogSearch(q: string): Promise<BlogPost[]> {
  return sameOriginFetch<BlogPost[]>(`/api/blog/search/?q=${encodeURIComponent(q)}`);
}

// ---------------------------------------------------------------------------
// Care Circle — Providers
// ---------------------------------------------------------------------------

export interface CareCircleProvider {
  providerKey: string;
  label: string;
  category: string;
  icon: string | null;
  enabled: boolean;
  patientVisible: boolean;
  description: string | null;
}

export async function fetchCareCircleProviders(): Promise<CareCircleProvider[]> {
  return apiFetch<CareCircleProvider[]>("/care-circle/providers");
}

// ---------------------------------------------------------------------------
// Care Circle — Family / Patients
// ---------------------------------------------------------------------------

export interface PatientHighlight {
  providerKey: string;
  displayOrder: number;
  kind: string;
  title: string;
  body: string;
  renderedHtml: string | null;
  feedback: "like" | "dislike" | null;
}

export interface CareCirclePatientPreferences {
  recipientName: string | null;
  preferredPronoun: string | null;
  hometown: string | null;
  cityForWeather: string | null;
  eraOfYouth: string | null;
  nationalityOrBackground: string | null;
  mobilityLevel: string | null;
  familyMembers: string[];
  lifeRoles: string[];
  pets: string[];
  hobbies: string[];
  favoriteActivities: string[];
  favoriteSingers: string[];
  favouriteFoods: string[];
  favouriteTvShows: string[];
}

const EMPTY_PREFERENCES: CareCirclePatientPreferences = {
  recipientName: null,
  preferredPronoun: null,
  hometown: null,
  cityForWeather: null,
  eraOfYouth: null,
  nationalityOrBackground: null,
  mobilityLevel: null,
  familyMembers: [],
  lifeRoles: [],
  pets: [],
  hobbies: [],
  favoriteActivities: [],
  favoriteSingers: [],
  favouriteFoods: [],
  favouriteTvShows: [],
};

export { EMPTY_PREFERENCES };

export interface CareCirclePatientRecord {
  id: string;
  familyName: string;
  displayName: string;
  stage: string;
  accessState: string;
  timezone: string;
  preferredLanguage: string;
  country: string;
  postalCode: string | null;
  latitude: number | null;
  longitude: number | null;
  deliveryTime: string | null;
  days: string[];
  authImageKeys: string[];
  joinCode: string;
  email: string | null;
  phoneNumber: string | null;
  preferences: CareCirclePatientPreferences;
  created_at: string;
  highlights?: PatientHighlight[];
}

export interface CareCirclePatientUpdateInput {
  familyName: string;
  joinCode: string;
  displayName: string;
  stage: string;
  accessState: string;
  timezone: string;
  preferredLanguage: string;
  country: string;
  postalCode: string | null;
  deliveryTime: string | null;
  days: string[];
  authImageKeys: string[];
  email: string | null;
  phoneNumber: string | null;
  preferences: CareCirclePatientPreferences;
}

export interface CareCirclePatientCreateInput {
  displayName: string;
  familyName?: string;
  stage?: string;
  accessState?: string;
  timezone?: string;
  preferredLanguage?: string;
  country?: string;
  postalCode?: string | null;
  deliveryTime?: string | null;
  preferences?: string[];
}

export async function createCareCirclePatient(
  payload: CareCirclePatientCreateInput,
): Promise<CareCirclePatientRecord> {
  return apiFetch<CareCirclePatientRecord>("/care-circle/family/patients", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export interface SendNewsletterResult {
  patient_id: number;
  patient_name: string;
  status: string;
  email_sent: boolean;
  sms_sent: boolean;
}

export async function sendPatientNewsletter(patientId: string): Promise<SendNewsletterResult> {
  return apiFetch<SendNewsletterResult>(`/care-circle/family/patients/${patientId}/send-newsletter`, {
    method: "POST",
  });
}

export async function fetchCareCirclePatients(): Promise<CareCirclePatientRecord[]> {
  return apiFetch<CareCirclePatientRecord[]>("/care-circle/family/patients");
}

export interface CareCircleActivityEvent {
  id: string;
  type: string;
  title: string;
  description: string;
  tone: "success" | "info" | "warning" | "error";
  occurred_at: string;
  patient_id: number | null;
  patient_name: string | null;
  provider_key: string | null;
}

export async function fetchCareCircleActivityEvents(): Promise<CareCircleActivityEvent[]> {
  return apiFetch<CareCircleActivityEvent[]>("/care-circle/family/events");
}

export interface CareCircleMediaItem {
  id: string;
  filename: string;
  storage_path: string;
  original_filename: string;
  url: string;
  file_type: string;
  content_type: string;
  file_size: number;
  alt_text?: string | null;
  caption?: string | null;
  uploaded_by?: number | null;
  created_at: string;
  thumbnail_url?: string | null;
  width?: number | null;
  height?: number | null;
  format?: string | null;
  aspect_ratio_urls?: Record<string, string> | null;
}

function encodeStoragePath(storagePath: string): string {
  return storagePath
    .split("/")
    .map((segment) => encodeURIComponent(segment))
    .join("/");
}

export async function fetchCareCircleMediaLibrary(): Promise<CareCircleMediaItem[]> {
  return sameOriginFetch<CareCircleMediaItem[]>("/api/blog/media/list");
}

export async function uploadCareCircleMedia(
  file: File,
  options?: { altText?: string; caption?: string },
): Promise<CareCircleMediaItem> {
  const formData = new FormData();
  formData.append("file", file);
  if (options?.altText) {
    formData.append("alt_text", options.altText);
  }
  if (options?.caption) {
    formData.append("caption", options.caption);
  }

  const data = await sameOriginFetch<{ message: string; media: CareCircleMediaItem }>(
    "/api/blog/media/upload",
    {
      method: "POST",
      body: formData,
    },
  );

  return data.media;
}

export async function deleteCareCircleMedia(storagePath: string): Promise<void> {
  await sameOriginFetch<void>(`/api/blog/media/${encodeStoragePath(storagePath)}`, {
    method: "DELETE",
  });
}

export async function fetchCareCirclePatient(patientId: string): Promise<CareCirclePatientRecord> {
  return apiFetch<CareCirclePatientRecord>(`/care-circle/family/patients/${patientId}`);
}

export async function updateCareCirclePatient(
  patientId: string,
  payload: CareCirclePatientUpdateInput,
): Promise<CareCirclePatientRecord> {
  return apiFetch<CareCirclePatientRecord>(`/care-circle/family/patients/${patientId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteCareCirclePatient(patientId: string | number): Promise<void> {
  return apiFetch<void>(`/care-circle/family/patients/${patientId}`, { method: "DELETE" });
}

export interface RegenerateNewsletterResult {
  job_id: string;
  state: string;
  message: string;
}

export interface RegenerateNewsletterJobStatus {
  job_id: string;
  state: string;
  status_message: string | null;
  result_message: string | null;
  created_at: string;
  updated_at: string;
}

export async function regeneratePatientNewsletter(patientId: string | number): Promise<RegenerateNewsletterResult> {
  return apiFetch(`/care-circle/family/patients/${patientId}/regenerate-newsletter`, { method: "POST" });
}

export async function fetchRegeneratePatientNewsletterStatus(
  patientId: string | number,
  jobId: string,
): Promise<RegenerateNewsletterJobStatus> {
  return apiFetch(`/care-circle/family/patients/${patientId}/regenerate-newsletter/${jobId}`);
}

export interface PatientNewsletterPreview {
  date: string;
  html: string;
  has_content: boolean;
}

export async function fetchPatientNewsletterPreview(
  patientId: string | number,
  forDate?: string,
): Promise<PatientNewsletterPreview> {
  const qs = forDate ? `?for_date=${forDate}` : "";
  return apiFetch<PatientNewsletterPreview>(`/care-circle/family/patients/${patientId}/newsletter-preview${qs}`);
}

// ---------------------------------------------------------------------------
// Care Circle — Patient Provider Configs
// ---------------------------------------------------------------------------

export interface CareCircleProviderConfig {
  provider_key: string;
  is_enabled: boolean;
  display_order: number | null;
  custom_parameters: Record<string, unknown>;
}

export async function fetchCareCirclePatientProviderConfigs(
  patientId: string,
): Promise<CareCircleProviderConfig[]> {
  return apiFetch<CareCircleProviderConfig[]>(
    `/care-circle/family/patients/${patientId}/provider-configs`,
  );
}

export async function updateCareCirclePatientProviderConfig(
  patientId: string,
  providerKey: string,
  payload: { is_enabled: boolean; custom_parameters?: Record<string, unknown> | null; display_order?: number | null },
): Promise<CareCircleProviderConfig> {
  return apiFetch<CareCircleProviderConfig>(
    `/care-circle/family/patients/${patientId}/provider-configs/${providerKey}`,
    { method: "PUT", body: JSON.stringify(payload) },
  );
}

export async function reorderCareCirclePatientProviderConfigs(
  patientId: string,
  ordering: { provider_key: string; display_order: number }[],
): Promise<void> {
  await apiFetch<void>(
    `/care-circle/family/patients/${patientId}/provider-configs/reorder`,
    { method: "POST", body: JSON.stringify({ ordering }) },
  );
}

// ---------------------------------------------------------------------------
// Care Circle — Family membership / join requests
// ---------------------------------------------------------------------------

export interface FamilyJoinRequest {
  id: number;
  user_id: number;
  username: string;
  display_name: string | null;
  email: string | null;
  requested_at: string | null;
}

export interface FamilyMember {
  id: number;
  user_id: number;
  username: string;
  display_name: string | null;
  email: string | null;
  role: string;
  joined_at: string | null;
}

export interface AdminFamily {
  id: number;
  name: string;
  join_code: string;
  is_disabled: boolean;
  owner_username: string | null;
  owner_display_name: string | null;
  member_count: number;
  patient_count: number;
  pending_requests: number;
  created_at: string | null;
}

export async function joinFamily(joinCode: string): Promise<{ status: string; family_name: string }> {
  return apiFetch("/care-circle/family/join", {
    method: "POST",
    body: JSON.stringify({ join_code: joinCode }),
  });
}

export async function fetchOwnerFamilySummary(): Promise<OwnerFamilySummary> {
  return apiFetch<OwnerFamilySummary>("/care-circle/family/owner-summary");
}

export async function sendFamilyInviteEmail(email: string): Promise<{ sent: boolean; email: string; join_code: string }> {
  return apiFetch("/care-circle/family/invite-email", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export async function fetchJoinRequests(): Promise<FamilyJoinRequest[]> {
  return apiFetch<FamilyJoinRequest[]>("/care-circle/family/join-requests");
}

export async function approveJoinRequest(membershipId: number): Promise<void> {
  await apiFetch<void>(`/care-circle/family/join-requests/${membershipId}/approve`, { method: "PUT" });
}

export async function rejectJoinRequest(membershipId: number): Promise<void> {
  await apiFetch<void>(`/care-circle/family/join-requests/${membershipId}/reject`, { method: "PUT" });
}

export async function fetchFamilyMembers(): Promise<FamilyMember[]> {
  return apiFetch<FamilyMember[]>("/care-circle/family/members");
}

export async function removeFamilyMember(membershipId: number): Promise<void> {
  await apiFetch<void>(`/care-circle/family/members/${membershipId}`, { method: "DELETE" });
}

// ---------------------------------------------------------------------------
// Care Circle — Admin family management
// ---------------------------------------------------------------------------

export async function adminFetchFamilies(): Promise<AdminFamily[]> {
  return apiFetch<AdminFamily[]>("/care-circle/admin/families");
}

export async function adminDisableFamily(familyId: number, disabled: boolean): Promise<void> {
  await apiFetch<void>(`/care-circle/admin/families/${familyId}/disable`, {
    method: "PUT",
    body: JSON.stringify({ disabled }),
  });
}

export async function adminDeleteFamily(familyId: number): Promise<void> {
  await apiFetch<void>(`/care-circle/admin/families/${familyId}`, { method: "DELETE" });
}

// ---------------------------------------------------------------------------
// Care Circle — Patient Auth
// ---------------------------------------------------------------------------

export interface CareCircleAuthCatalogItem {
  key: string;
  label: string;
  emoji: string;
  image_url: string | null;
}

export async function fetchCareCirclePatientAuthCatalog(): Promise<CareCircleAuthCatalogItem[]> {
  return apiFetch<CareCircleAuthCatalogItem[]>("/care-circle/patient/auth/catalog");
}

export async function loginCareCirclePatient(
  selectedKeys: string[],
): Promise<CareCirclePatientRecord> {
  return apiFetch<CareCirclePatientRecord>("/care-circle/patient/auth/login", {
    method: "POST",
    body: JSON.stringify({ selected_image_keys: selectedKeys }),
  });
}

export async function fetchCareCirclePatientSession(
  patientId: string,
): Promise<CareCirclePatientRecord> {
  return apiFetch<CareCirclePatientRecord>(`/care-circle/patient/session/${patientId}`);
}

export async function saveCareCirclePatientProviderFeedback(
  patientId: string,
  providerKey: string,
  feedback: "like" | "dislike" | null,
): Promise<{ patient_id: number; provider_key: string; feedback: "like" | "dislike" | null }> {
  return apiFetch<{ patient_id: number; provider_key: string; feedback: "like" | "dislike" | null }>(
    `/care-circle/patient/session/${patientId}/provider-feedback/${providerKey}`,
    {
      method: "PUT",
      body: JSON.stringify({ feedback }),
    },
  );
}

// ---------------------------------------------------------------------------
// Admin
// ---------------------------------------------------------------------------

export interface AdminUser {
  id: number;
  username: string;
  email?: string | null;
  display_name?: string | null;
  is_active: boolean;
  is_admin: boolean;
  created_at?: string | null;
}

export async function fetchAdminUsers(): Promise<AdminUser[]> {
  return apiFetch<AdminUser[]>("/users/?limit=1000");
}

export async function toggleUserActive(userId: number): Promise<AdminUser> {
  return apiFetch<AdminUser>(`/users/${userId}/toggle-active`, { method: "PATCH" });
}

export interface AdminBillingDashboard {
  system_stats: Record<string, unknown>;
  recent_transactions: unknown[];
  user_accounts: unknown[];
}

export async function fetchAdminBillingDashboard(): Promise<AdminBillingDashboard> {
  return apiFetch<AdminBillingDashboard>("/admin/billing/dashboard");
}

export async function adminAdjustCredits(userId: number, amount: number, description: string): Promise<void> {
  await apiFetch<void>("/admin/billing/adjust-credits", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, amount, description }),
  });
}

export interface MaintenanceStatus {
  enabled: boolean;
  message?: string | null;
  estimated_end_time?: string | null;
}

export async function fetchMaintenanceStatusAdmin(): Promise<MaintenanceStatus> {
  return apiFetch<MaintenanceStatus>("/maintenance/status");
}

export async function enableMaintenanceMode(message?: string, durationMinutes = 5): Promise<{ status: string }> {
  const params = new URLSearchParams({ duration_minutes: String(durationMinutes) });
  if (message) params.set("message", message);
  return apiFetch<{ status: string }>(`/maintenance/enable?${params.toString()}`, { method: "POST" });
}

export async function disableMaintenanceMode(): Promise<{ status: string }> {
  return apiFetch<{ status: string }>("/maintenance/disable", { method: "POST" });
}

export interface AdminCTA {
  id: number;
  title: string;
  subtitle?: string | null;
  position: string;
  style: string;
  is_active: boolean;
  sort_order: number;
  primary_button_text?: string | null;
  primary_button_url?: string | null;
  show_for_anonymous: boolean;
  show_for_authenticated: boolean;
}

export async function fetchAdminCTAs(): Promise<AdminCTA[]> {
  return apiFetch<AdminCTA[]>("/admin/cta-content?include_inactive=true");
}

export async function toggleCTAActive(ctaId: number): Promise<{ is_active: boolean; message: string }> {
  return apiFetch<{ is_active: boolean; message: string }>(`/admin/cta-content/${ctaId}/toggle-active`, { method: "POST" });
}

export async function deleteCTA(ctaId: number): Promise<void> {
  await apiFetch<void>(`/admin/cta-content/${ctaId}`, { method: "DELETE" });
}

// ---------------------------------------------------------------------------
// Chatbot
// ---------------------------------------------------------------------------

export interface ChatbotMessage {
  id: number;
  session_id: number;
  role: "user" | "assistant";
  content: string;
  input_tokens?: number | null;
  output_tokens?: number | null;
  cost_usd?: number | null;
  model_name?: string | null;
  created_at: string;
}

export interface ChatbotSession {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ChatbotSessionWithMessages extends ChatbotSession {
  messages: ChatbotMessage[];
}

export interface ChatbotSendResponse {
  user_message: ChatbotMessage;
  ai_message: ChatbotMessage;
  input_tokens?: number | null;
  output_tokens?: number | null;
  cost_usd?: number | null;
  model_name?: string | null;
}

export async function fetchChatbotSessions(): Promise<ChatbotSession[]> {
  return apiFetch<ChatbotSession[]>("/chatbot/sessions");
}

export async function fetchChatbotSession(sessionId: number): Promise<ChatbotSessionWithMessages> {
  return apiFetch<ChatbotSessionWithMessages>(`/chatbot/sessions/${sessionId}`);
}

export async function createChatbotSession(title?: string): Promise<ChatbotSession> {
  return apiFetch<ChatbotSession>("/chatbot/sessions", {
    method: "POST",
    body: JSON.stringify({ title: title ?? "New conversation" }),
  });
}

export async function renameChatbotSession(sessionId: number, title: string): Promise<ChatbotSession> {
  return apiFetch<ChatbotSession>(`/chatbot/sessions/${sessionId}`, {
    method: "PUT",
    body: JSON.stringify({ title }),
  });
}

export async function deleteChatbotSession(sessionId: number): Promise<void> {
  await apiFetch<void>(`/chatbot/sessions/${sessionId}`, { method: "DELETE" });
}

export async function sendChatbotMessage(sessionId: number, message: string): Promise<ChatbotSendResponse> {
  return apiFetch<ChatbotSendResponse>(`/chatbot/sessions/${sessionId}/messages`, {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

// ---------------------------------------------------------------------------
// Prompts
// ---------------------------------------------------------------------------

export interface PromptEntry {
  id: number;
  title: string;
  prompt_content: string;
  reason_to_use?: string | null;
  comment?: string | null;
  is_active: boolean;
  prompt_type: string;
  age_target: string;
  user_id?: number | null;
  created_at: string;
  updated_at: string;
}

export async function fetchMyPrompts(): Promise<PromptEntry[]> {
  return apiFetch<PromptEntry[]>("/prompts/my-prompts");
}

export async function fetchSharedPrompts(): Promise<PromptEntry[]> {
  return apiFetch<PromptEntry[]>("/prompts/shared");
}

export async function createPrompt(payload: {
  title: string;
  prompt_content: string;
  prompt_type: string;
  reason_to_use?: string;
  is_active?: boolean;
}): Promise<PromptEntry> {
  return apiFetch<PromptEntry>("/prompts/", {
    method: "POST",
    body: JSON.stringify({ age_target: "ALL_AGES", is_active: true, ...payload }),
  });
}

export async function deletePrompt(promptId: number): Promise<void> {
  await apiFetch<void>(`/prompts/${promptId}`, { method: "DELETE" });
}

// ---------------------------------------------------------------------------
// LLM Models
// ---------------------------------------------------------------------------

export interface LLMModelEntry {
  id: number;
  display_name: string;
  model_name: string;
  description?: string | null;
  provider: string;
  model_type: string;
  is_active: boolean;
  max_tokens: number;
  temperature: number;
  user_price_input_usd_pm: number;
  user_price_output_usd_pm: number;
}

export interface LLMModelsResponse {
  models: LLMModelEntry[];
  total_count: number;
  active_count: number;
  providers: string[];
}

export async function fetchLLMModels(): Promise<LLMModelsResponse> {
  return apiFetch<LLMModelsResponse>("/llm-models/");
}

// ---------------------------------------------------------------------------
// Blog authoring
// ---------------------------------------------------------------------------

export interface BlogPostDraft extends BlogPost {
  content_html?: string | null;
}

export async function fetchAuthorBlogPosts(userId: number, appSource?: string): Promise<BlogPost[]> {
  const qs = new URLSearchParams();
  qs.set("author_id", String(userId));
  if (appSource) qs.set("app_source", appSource);
  return sameOriginFetch<BlogPost[]>(`/api/blog/posts?${qs.toString()}`);
}

export async function fetchBlogPostById(postId: number): Promise<BlogPost> {
  return sameOriginFetch<BlogPost>(`/api/blog/posts/${postId}`);
}

export async function createBlogPost(payload: {
  title: string;
  content: string;
  excerpt?: string;
  status?: string;
  app_source?: string;
}): Promise<BlogPost> {
  return sameOriginFetch<BlogPost>("/api/blog/posts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function updateBlogPost(
  postId: number,
  payload: { title?: string; content?: string; excerpt?: string; status?: string },
): Promise<BlogPost> {
  return sameOriginFetch<BlogPost>(`/api/blog/posts/${postId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function publishBlogPost(postId: number): Promise<BlogPost> {
  return sameOriginFetch<BlogPost>(`/api/blog/posts/${postId}/publish`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
}

export async function deleteBlogPost(postId: number): Promise<void> {
  await sameOriginFetch<void>(`/api/blog/posts/${postId}`, { method: "DELETE" });
}

// ---------------------------------------------------------------------------
// Care Circle — ISO Codes
// ---------------------------------------------------------------------------

export interface IsoCodeEntry {
  code: string;
  name: string;
}

export interface IsoCodesResponse {
  languages: IsoCodeEntry[];
  countries: IsoCodeEntry[];
}

function normalizeIsoCodeMap(
  input: IsoCodeEntry[] | Record<string, string> | null | undefined,
): IsoCodeEntry[] {
  if (Array.isArray(input)) {
    return input;
  }
  if (!input || typeof input !== "object") {
    return [];
  }
  return Object.entries(input)
    .map(([code, name]) => ({ code, name }))
    .sort((a, b) => a.name.localeCompare(b.name));
}

export async function fetchIsoCodes(): Promise<IsoCodesResponse> {
  const data = await apiFetch<{
    languages?: IsoCodeEntry[] | Record<string, string>;
    countries?: IsoCodeEntry[] | Record<string, string>;
  }>("/care-circle/iso-codes");

  return {
    languages: normalizeIsoCodeMap(data.languages),
    countries: normalizeIsoCodeMap(data.countries),
  };
}
