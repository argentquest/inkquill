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

  await page.route("http://127.0.0.1:8000/api/v1/**", async (route) => {
    const url = route.request().url();
    const method = route.request().method();

    if (url.endsWith("/users/me")) {
      if (method === "PUT") {
        const body = route.request().postDataJSON() as Partial<typeof authenticatedUser>;
        currentUser.username = body.username ?? currentUser.username;
        currentUser.email = body.email ?? currentUser.email;
        currentUser.display_name = body.display_name ?? currentUser.display_name;
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ success: true, data: currentUser })
        });
        return;
      }

      if (session === "authenticated") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ success: true, data: currentUser })
        });
        return;
      }

      if (session === "session-error") {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({ success: false, error: { message: "Session failed" } })
        });
        return;
      }

      await route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({ success: false, error: { message: "Unauthorized" } })
      });
      return;
    }

    if (url.endsWith("/billing/balance")) {
      if (balance === "error") {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({ success: false, error: { message: "Balance failed" } })
        });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true, data: { balance: 25.75, currency: "Coins" } })
      });
      return;
    }

    if (url.endsWith("/maintenance/status")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            enabled: maintenance === "on",
            message: maintenance === "on" ? "Planned maintenance window" : null,
            end_time: maintenance === "on" ? "2026-04-01T23:30:00Z" : null
          }
        })
      });
      return;
    }

    if (url.endsWith("/billing/dashboard")) {
      if (billingDashboard === "error") {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({ success: false, error: { message: "Billing dashboard failed" } })
        });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            account: {
              id: 3,
              user_id: 7,
              current_balance: "2555.0000",
              total_spent: "125.0000",
              total_credits_added: "2680.0000",
              currency: "Coins",
              created_at: "2026-04-01T00:00:00Z",
              updated_at: "2026-04-01T00:00:00Z"
            },
            recent_transactions: [
              {
                id: 10,
                user_account_id: 3,
                transaction_type: "CREDIT_ADD",
                amount: "550.0000",
                balance_after: "2550.0000",
                description: "Package purchase",
                created_at: "2026-04-01T00:00:00Z"
              }
            ],
            available_packages: [
              {
                id: 4,
                name: "Starter Pack",
                description: "Base credits for new workspaces",
                credit_amount: "500.0000",
                price_usd: "4.99",
                bonus_percentage: "10.00",
                display_order: 1,
                is_active: true
              }
            ]
          }
        })
      });
      return;
    }

    if (url.endsWith("/referrals/stats")) {
      if (referrals === "error") {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({ success: false, error: { message: "Referral stats failed" } })
        });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            total_referrals: 5,
            converted_referrals: 2,
            conversion_rate: 40,
            total_coins_earned: 15,
            today: { visits: 1 },
            platform_breakdown: { direct: 3, x: 2 },
            limits: { daily: 10 },
            reward_amounts: { signup: 5 }
          }
        })
      });
      return;
    }

    if (url.endsWith("/referrals/history")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            referrals: [
              {
                id: 9,
                referred_user_id: 11,
                is_anonymous: false,
                source_platform: "direct",
                source_content_type: "world",
                is_converted: true,
                converted_at: "2026-04-01T00:00:00Z",
                has_created_story: true,
                has_published_story: false,
                created_at: "2026-04-01T00:00:00Z"
              }
            ],
            total: 1,
            limit: 100,
            offset: 0
          }
        })
      });
      return;
    }

    if (url.endsWith("/referrals/rewards")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            rewards: [
              {
                id: 2,
                referral_id: 9,
                reward_type: "signup",
                coin_amount: 5,
                awarded_at: "2026-04-01T00:00:00Z"
              }
            ],
            total: 1,
            limit: 100,
            offset: 0
          }
        })
      });
      return;
    }

    if (url.endsWith("/interview/questions/new_user_onboarding")) {
      if (onboarding === "error") {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({ success: false, error: { message: "Questions failed" } })
        });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            interview_id: "new_user_onboarding",
            interview_title: "Welcome! Let's get to know you better",
            interview_description: "This quick interview helps us personalize your writing experience",
            show_progress: true,
            questions: [
              { id: "writing_experience", order: 1, question: "What best describes your writing background?", subtitle: "Check all that apply" },
              { id: "genre_preferences", order: 2, question: "Select all the genres that appeal to you", subtitle: "Check all that apply" },
              { id: "help_needed", order: 3, question: "What would help you most right now?" }
            ]
          }
        })
      });
      return;
    }

    if (url.endsWith("/interview/status/new_user_onboarding")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            completed: false,
            interview_id: "new_user_onboarding"
          }
        })
      });
      return;
    }

    if (url.endsWith("/interview/user-insights")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            has_completed_onboarding: false,
            insights: null
          }
        })
      });
      return;
    }

    if (url.endsWith("/auth/login")) {
      if (login === "error") {
        await route.fulfill({
          status: 401,
          contentType: "application/json",
          body: JSON.stringify({ detail: "Incorrect username or password" })
        });
        return;
      }

      session = "authenticated";
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ message: "Login successful. Token set in cookie." })
      });
      return;
    }

    if (url.endsWith("/auth/register")) {
      if (register === "error") {
        await route.fulfill({
          status: 400,
          contentType: "application/json",
          body: JSON.stringify({ detail: "Username already registered." })
        });
        return;
      }

      session = "authenticated";
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({ success: true, data: authenticatedUser })
      });
      return;
    }

    if (url.endsWith("/auth/logout")) {
      session = "anonymous";
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true, data: { message: "Logout successful" } })
      });
      return;
    }

    if (url.endsWith("/auth/password-reset/request")) {
      if (forgotPassword === "error") {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({ detail: "Email service unavailable" })
        });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ message: "If an account with this email exists, a password reset link has been sent." })
      });
      return;
    }

    if (url.endsWith("/auth/password-reset/confirm")) {
      if (resetPassword === "error") {
        await route.fulfill({
          status: 400,
          contentType: "application/json",
          body: JSON.stringify({ detail: "Invalid or expired reset token" })
        });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ message: "Password has been successfully reset. You can now log in with your new password." })
      });
      return;
    }

    await route.fallback();
  });
}
