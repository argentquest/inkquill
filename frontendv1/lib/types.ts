// Core platform types shared across the app

// --- Auth / Session ---

export interface SessionUser {
  id: number;
  username: string;
  email: string;
  display_name: string | null;
  is_admin: boolean;
  is_family_owner: boolean;
  is_active: boolean;
  profile_picture_url: string | null;
}

export type SessionStatus = "loading" | "authenticated" | "anonymous" | "error";

export interface SessionState {
  status: SessionStatus;
  user: SessionUser | null;
  error: string | null;
}

// --- Balance ---

export interface BalanceState {
  balance: number;
  currency: string;
  error?: string;
}

// --- Maintenance ---

export interface MaintenanceState {
  enabled: boolean;
  message: string | null;
  updated_at?: string | null;
  end_time?: string | null;
}

// --- Toast ---

export type ToastTone = "success" | "error" | "warning" | "info";

export interface ToastMessage {
  id: string;
  title: string;
  tone: ToastTone;
  detail?: string;
}

// --- Platform / App routing ---

export type PlatformSurfaceId =
  | "storytelling"
  | "care-circle-family"
  | "care-circle-patient"
  | "chatbot"
  | "legacy-app"
  | "public";

export type OwnerScope = "none" | "user" | "family" | "patient";

export interface AppMembership {
  surface_id: PlatformSurfaceId;
  granted: boolean;
  reason: string | null;
}

export interface PlatformCurrentContext {
  surface_id: PlatformSurfaceId;
  app_id: string | null;
  requires_auth: boolean;
  owner_scope: OwnerScope;
  title: string;
  description: string;
  memberships: AppMembership[];
}

// --- Billing ---

export interface BillingAccount {
  currency: string;
  current_balance: number;
  total_spent: number;
  total_credits_added: number;
}

export interface BillingTransaction {
  id: number;
  transaction_type: string;
  amount: number;
  balance_after: number;
  description: string | null;
  created_at: string;
}

export interface CreditPackage {
  id: number;
  name: string;
  description: string | null;
  credit_amount: number;
  price_usd: number;
  bonus_percentage: number;
  is_active: boolean;
  display_order: number;
}

export interface BillingDashboard {
  account: BillingAccount;
  recent_transactions: BillingTransaction[];
  available_packages: CreditPackage[];
}

// --- Onboarding / Interview ---

export interface InterviewQuestion {
  id: number;
  order: number;
  question: string;
  subtitle: string | null;
  question_type: string;
  options: string[] | null;
}

export interface InterviewQuestionsPayload {
  interview_id: string;
  interview_title: string;
  interview_description: string;
  questions: InterviewQuestion[];
}

export interface InterviewStatusPayload {
  completed: boolean;
  completed_at: string | null;
}

export interface UserInsightsPayload {
  has_completed_onboarding: boolean;
  insights: Record<string, unknown> | null;
}

// --- Referrals ---

export interface ReferralStats {
  total_referrals: number;
  converted_referrals: number;
  conversion_rate: number;
  total_coins_earned: number;
  referral_code: string | null;
  referral_url: string | null;
}

export interface ReferralEntry {
  id: number;
  source_platform: string | null;
  source_content_type: string | null;
  is_converted: boolean;
  created_at: string;
  completed_at: string | null;
}

export interface ReferralHistoryResponse {
  referrals: ReferralEntry[];
  total: number;
}

export interface ReferralRewardEntry {
  id: number;
  reward_type: string;
  coin_amount: number;
  awarded_at: string;
  description: string | null;
}

export interface ReferralRewardsResponse {
  rewards: ReferralRewardEntry[];
  total_earned: number;
}

// --- Care Circle family ownership ---

export interface OwnerFamilySummary {
  id: number;
  name: string;
  join_code: string;
  active_member_count: number;
  pending_request_count: number;
}
