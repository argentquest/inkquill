import { Page } from "@playwright/test";

type SessionMode = "anonymous" | "authenticated" | "session-error";
type BalanceMode = "ok" | "error";
type MaintenanceMode = "off" | "on";
type FormMode = "ok" | "error";
type DataMode = "ok" | "error";

interface MockOptions {
  session?: SessionMode;
  balance?: BalanceMode;
  maintenance?: MaintenanceMode;
  login?: FormMode;
  register?: FormMode;
  forgotPassword?: FormMode;
  resetPassword?: FormMode;
  billingDashboard?: DataMode;
  referrals?: DataMode;
  onboarding?: DataMode;
}

const authenticatedUser = {
  id: 7,
  username: "storymaker",
  email: "storymaker@example.com",
  display_name: "Story Maker",
  is_admin: true,
  is_active: true
};

const careCirclePatients = [
  {
    id: "1",
    displayName: "Rose Ellis",
    familyName: "Story Maker household",
    joinCode: "STM111",
    stage: "moderate",
    accessState: "active",
    timezone: "America/Chicago",
    deliveryTime: "08:30",
    days: ["Mon", "Wed", "Fri", "Sun"],
    familyMembers: ["Nina", "Paul", "Maggie"],
    preferences: ["1950s music", "family photos", "tea and biscuits", "gardening"],
    authImageKeys: ["sun", "dog", "house"],
    highlights: [
      {
        title: "Family hello",
        body: "Nina says the daffodils are opening and she saved the first photo for you.",
        kind: "family",
        providerKey: "family_greeting",
        displayOrder: 1
      },
      {
        title: "Memory lane",
        body: "Today’s memory card revisits spring walks and favorite songs from the 1950s.",
        kind: "memory",
        providerKey: "nostalgia",
        displayOrder: 2
      }
    ]
  },
  {
    id: "2",
    displayName: "Arthur Bloom",
    familyName: "Story Maker household",
    joinCode: "STM111",
    stage: "mild",
    accessState: "inactive",
    timezone: "America/New_York",
    deliveryTime: "09:15",
    days: ["Tue", "Thu", "Sat"],
    familyMembers: ["Janet", "Chris"],
    preferences: ["local history", "jazz", "crosswords"],
    authImageKeys: ["tree", "car", "star"],
    highlights: [
      {
        title: "Daily note",
        body: "Chris left a short update about yesterday’s walk by the river.",
        kind: "family",
        providerKey: "family_greeting",
        displayOrder: 1
      }
    ]
  }
];

const patientAuthCatalog = [
  { key: "sun", label: "Sun", emoji: "☀️" },
  { key: "dog", label: "Dog", emoji: "🐶" },
  { key: "flower", label: "Flower", emoji: "🌷" },
  { key: "cake", label: "Cake", emoji: "🎂" },
  { key: "bird", label: "Bird", emoji: "🐦" },
  { key: "car", label: "Car", emoji: "🚗" },
  { key: "tree", label: "Tree", emoji: "🌳" },
  { key: "house", label: "House", emoji: "🏡" },
  { key: "moon", label: "Moon", emoji: "🌙" },
  { key: "star", label: "Star", emoji: "⭐" },
  { key: "boat", label: "Boat", emoji: "⛵" },
  { key: "hat", label: "Hat", emoji: "🎩" }
];

const careCircleProviders = [
  {
    providerKey: "weather",
    label: "Weather",
    icon: "⛅",
    category: "orientation",
    enabled: true,
    displayOrder: 1,
    patientVisible: true,
    familyVisible: true
  },
  {
    providerKey: "joke",
    label: "Daily Joy",
    icon: "😄",
    category: "wellbeing",
    enabled: true,
    displayOrder: 2,
    patientVisible: true,
    familyVisible: true
  }
];

const patientProviderConfigs: Record<string, Array<{
  id: number;
  patient_id: number;
  provider_key: string;
  is_enabled: boolean;
  custom_parameters: Record<string, unknown>;
}>> = {
  "1": [
    {
      id: 1,
      patient_id: 1,
      provider_key: "weather",
      is_enabled: true,
      custom_parameters: {}
    },
    {
      id: 2,
      patient_id: 1,
      provider_key: "joke",
      is_enabled: false,
      custom_parameters: {}
    }
  ],
  "2": []
};

function json(body: unknown, status = 200) {
  return {
    status,
    contentType: "application/json",
    body: JSON.stringify(body)
  };
}

export async function mockAppApis(page: Page, options: MockOptions = {}) {
  let session = options.session ?? "anonymous";
  const balance = options.balance ?? "ok";
  const maintenance = options.maintenance ?? "off";
  const login = options.login ?? "ok";
  const register = options.register ?? "ok";
  const forgotPassword = options.forgotPassword ?? "ok";
  const resetPassword = options.resetPassword ?? "ok";
  const billingDashboard = options.billingDashboard ?? "ok";
  const referrals = options.referrals ?? "ok";
  const onboarding = options.onboarding ?? "ok";
  const currentUser = { ...authenticatedUser };

  await page.route("**/api/v1/**", async (route) => {
    const url = route.request().url();
    const method = route.request().method();

    if (url.endsWith("/users/me")) {
      if (method === "PUT") {
        const body = route.request().postDataJSON() as Partial<typeof authenticatedUser>;
        currentUser.username = body.username ?? currentUser.username;
        currentUser.email = body.email ?? currentUser.email;
        currentUser.display_name = body.display_name ?? currentUser.display_name;
        await route.fulfill(json({ success: true, data: currentUser }));
        return;
      }

      if (session === "authenticated") {
        await route.fulfill(json({ success: true, data: currentUser }));
        return;
      }

      if (session === "session-error") {
        await route.fulfill(json({ success: false, error: { message: "Session failed" } }, 500));
        return;
      }

      await route.fulfill(json({ success: false, error: { message: "Unauthorized" } }, 401));
      return;
    }

    if (url.endsWith("/care-circle/family/patients")) {
      await route.fulfill(json({ success: true, data: careCirclePatients }));
      return;
    }

    if (url.endsWith("/care-circle/providers")) {
      await route.fulfill(json({ success: true, data: careCircleProviders }));
      return;
    }

    if (/\/care-circle\/family\/patients\/\d+\/provider-configs$/.test(url)) {
      const patientId = url.split("/").slice(-2)[0];
      await route.fulfill(json({ success: true, data: patientProviderConfigs[patientId] ?? [] }));
      return;
    }

    if (/\/care-circle\/family\/patients\/\d+$/.test(url)) {
      const patientId = url.split("/").pop();
      const patient = careCirclePatients.find((entry) => entry.id === patientId);
      if (!patient) {
        await route.fulfill(json({ detail: "Patient not found" }, 404));
        return;
      }
      await route.fulfill(json({ success: true, data: patient }));
      return;
    }

    if (/\/care-circle\/family\/patients\/\d+\/provider-configs\/[^/]+$/.test(url) && method === "PUT") {
      const parts = url.split("/");
      const providerKey = parts.at(-1) ?? "";
      const patientId = parts.at(-3) ?? "";
      const body = route.request().postDataJSON() as { is_enabled?: boolean; custom_parameters?: Record<string, unknown> };
      const patientConfigList = patientProviderConfigs[patientId] ?? [];
      let existing = patientConfigList.find((entry) => entry.provider_key === providerKey);

      if (!existing) {
        existing = {
          id: patientConfigList.length + 1,
          patient_id: Number(patientId),
          provider_key: providerKey,
          is_enabled: body.is_enabled ?? true,
          custom_parameters: body.custom_parameters ?? {}
        };
        patientConfigList.push(existing);
        patientProviderConfigs[patientId] = patientConfigList;
      } else {
        existing.is_enabled = body.is_enabled ?? existing.is_enabled;
        existing.custom_parameters = body.custom_parameters ?? existing.custom_parameters;
      }

      await route.fulfill(json({ success: true, data: existing }));
      return;
    }

    if (url.endsWith("/care-circle/patient/auth/catalog")) {
      await route.fulfill(json({ success: true, data: patientAuthCatalog }));
      return;
    }

    if (url.endsWith("/care-circle/patient/auth/login")) {
      const body = route.request().postDataJSON() as { selected_image_keys?: string[] };
      const selection = [...new Set(body.selected_image_keys ?? [])].sort();
      const roseSelection = ["dog", "house", "sun"];
      if (selection.length === roseSelection.length && selection.every((value, index) => value === roseSelection[index])) {
        await route.fulfill(json({ success: true, data: careCirclePatients[0] }));
        return;
      }

      await route.fulfill(
        json(
          {
            success: false,
            errors: [{ code: "INVALID_PATIENT_AUTH", message: "Those pictures did not match an active patient profile." }]
          },
          200
        )
      );
      return;
    }

    if (/\/care-circle\/patient\/session\/\d+$/.test(url)) {
      const patientId = url.split("/").pop();
      const patient = careCirclePatients.find((entry) => entry.id === patientId && entry.accessState !== "archived");
      if (!patient) {
        await route.fulfill(json({ detail: "Patient session not found" }, 404));
        return;
      }
      await route.fulfill(json({ success: true, data: patient }));
      return;
    }

    if (url.endsWith("/billing/balance")) {
      if (balance === "error") {
        await route.fulfill(json({ success: false, error: { message: "Balance failed" } }, 500));
        return;
      }

      await route.fulfill(
        json({
          success: true,
          data: {
            balance: 25.75,
            currency: "Coins",
            error: null
          }
        })
      );
      return;
    }

    if (url.endsWith("/maintenance") || url.endsWith("/maintenance/status")) {
      if (maintenance === "on") {
        await route.fulfill(json({ success: true, data: { enabled: true, message: "Scheduled maintenance", updated_at: "2026-01-10T00:00:00Z", end_time: "2026-01-10T01:00:00Z" } }));
        return;
      }

      await route.fulfill(json({ success: true, data: { enabled: false, message: null, updated_at: null, end_time: null } }));
      return;
    }

    if (url.endsWith("/auth/login") && method === "POST") {
      if (login === "error") {
        await route.fulfill(json({ detail: "Invalid username or password" }, 401));
        return;
      }

      session = "authenticated";
      await route.fulfill(json({ message: "Logged in" }));
      return;
    }

    if (url.endsWith("/auth/register") && method === "POST") {
      if (register === "error") {
        await route.fulfill(json({ detail: "Registration failed" }, 400));
        return;
      }

      session = "authenticated";
      await route.fulfill(json({ success: true, data: currentUser }));
      return;
    }

    if (url.endsWith("/auth/password-reset/request") && method === "POST") {
      if (forgotPassword === "error") {
        await route.fulfill(json({ detail: "Reset request failed" }, 400));
        return;
      }

      await route.fulfill(json({ message: "Password reset email sent" }));
      return;
    }

    if (url.endsWith("/auth/password-reset/confirm") && method === "POST") {
      if (resetPassword === "error") {
        await route.fulfill(json({ detail: "Reset confirmation failed" }, 400));
        return;
      }

      await route.fulfill(json({ message: "Password reset successful" }));
      return;
    }

    if (url.endsWith("/auth/logout") && method === "POST") {
      session = "anonymous";
      await route.fulfill(json({ success: true, data: { message: "Logout successful" } }));
      return;
    }

    if (url.endsWith("/billing/dashboard")) {
      if (billingDashboard === "error") {
        await route.fulfill(json({ success: false, error: { message: "Billing dashboard failed" } }, 500));
        return;
      }

      await route.fulfill(
        json({
          success: true,
          data: {
            account: {
              current_balance: 120,
              total_spent: 45,
              total_credits_added: 165,
              currency: "USD"
            },
            recent_transactions: [
              { id: "txn_1", transaction_type: "credit_top_up", amount: 25, balance_after: 120, description: "Credit top-up" }
            ],
            available_packages: [
              { id: "pkg_1", name: "Starter", credit_amount: 100, price_usd: 25, bonus_percentage: 10 }
            ],
            balance: {
              credits: 120,
              subscription_tier: "Pro",
              renewal_date: "2026-01-15"
            },
            payment_methods: [
              { id: "pm_1", brand: "visa", last4: "4242", is_default: true }
            ],
            invoices: [
              { id: "inv_1", total: 25, status: "paid", issued_at: "2026-01-01" }
            ]
          }
        })
      );
      return;
    }

    if (url.endsWith("/referrals/stats")) {
      if (referrals === "error") {
        await route.fulfill(json({ success: false, error: { message: "Referral stats failed" } }, 500));
        return;
      }

      await route.fulfill(
        json({
          success: true,
          data: {
            referral_code: "STORY123",
            total_referrals: 4,
            converted_referrals: 2,
            conversion_rate: 50,
            total_coins_earned: 40
          }
        })
      );
      return;
    }

    if (url.endsWith("/referrals/history")) {
      await route.fulfill(
        json({
          success: true,
          data: {
            referrals: [
              {
                id: 1,
                source_platform: "email",
                source_content_type: "workspace",
                is_converted: true,
                created_at: "2026-01-01T00:00:00Z"
              }
            ]
          }
        })
      );
      return;
    }

    if (url.endsWith("/referrals/rewards")) {
      await route.fulfill(
        json({
          success: true,
          data: {
            rewards: [
              { id: 1, reward_type: "conversion_bonus", coin_amount: 20, awarded_at: "2026-01-02T00:00:00Z" }
            ]
          }
        })
      );
      return;
    }

    if (url.includes("/interview/questions/")) {
      if (onboarding === "error") {
        await route.fulfill(json({ success: false, error: { message: "Questions failed" } }, 500));
        return;
      }

      await route.fulfill(
        json({
          success: true,
          data: {
            interview_id: "new_user_onboarding",
            interview_title: "Welcome! Let's get to know you better",
            interview_description: "A short shared interview helps the platform tailor your writing workspace before you start drafting.",
            questions: [
              { id: "q1", order: 1, question: "What brings you here?", subtitle: "Tell us the main thing you want to create." },
              { id: "q2", order: 2, question: "What do you want to build?", subtitle: "Choose the flow that fits your first project." }
            ]
          }
        })
      );
      return;
    }

    if (url.includes("/interview/status/")) {
      await route.fulfill(
        json({
          success: true,
          data: {
            interview_id: "new_user_onboarding",
            status: "pending",
            completed: false,
            progress: 0
          }
        })
      );
      return;
    }

    if (url.endsWith("/interview/user-insights")) {
      await route.fulfill(
        json({
          success: true,
          data: {
            has_completed_onboarding: false,
            insights: []
          }
        })
      );
      return;
    }

    await route.fallback();
  });
}
