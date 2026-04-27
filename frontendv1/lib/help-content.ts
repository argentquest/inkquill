import { PageHelpContent } from "@/components/ui/help-modal";

/**
 * Help content for the Login page
 */
export const loginHelp: PageHelpContent = {
  title: "Sign In Help",
  description: "Learn how to access your account securely.",
  sections: [
    {
      title: "Authentication",
      items: [
        {
          title: "Username or Email",
          content: "Enter the username or email address associated with your account. This is the credentials you used during registration or the username assigned to you."
        },
        {
          title: "Password",
          content: "Your password must be at least 8 characters long. Passwords are case-sensitive, so ensure you use the correct capitalization."
        },
        {
          title: "Forgot Password",
          content: "If you've forgotten your password, click the 'Forgot your password?' link to initiate the password reset process. You'll receive an email with instructions."
        },
        {
          title: "Google Sign-In",
          content: "If your account was created using Google, you can sign in quickly using the Google Sign-In button without needing to remember your password."
        }
      ]
    },
    {
      title: "Troubleshooting",
      items: [
        {
          title: "Login Issues",
          content: "If you're having trouble signing in, ensure your account has been verified via email. Check your spam folder if you haven't received the verification email."
        },
        {
          title: "Account Locked",
          content: "After multiple failed login attempts, your account may be temporarily locked. Wait 15 minutes and try again, or use the password reset option."
        }
      ]
    },
    {
      title: "Need Help?",
      items: [
        {
          title: "Contact Support",
          content: "If you continue to experience issues, contact our support team for assistance. We're here to help you regain access to your account."
        }
      ]
    }
  ]
};

/**
 * Help content for the Register page
 */
export const registerHelp: PageHelpContent = {
  title: "Create Account Help",
  description: "Learn how to create your new account.",
  sections: [
    {
      title: "Account Information",
      items: [
        {
          title: "Username",
          content: "Choose a unique username that will identify you on the platform. Usernames must be at least 3 characters and can contain letters, numbers, and underscores."
        },
        {
          title: "Email Address",
          content: "Enter a valid email address. This will be used for account verification, password resets, and important notifications about your account."
        },
        {
          title: "Display Name",
          content: "This is the name other users will see. It can be your real name or a pseudonym. This field is optional and can be changed later in your account settings."
        },
        {
          title: "Password",
          content: "Create a strong password with at least 8 characters. For security, use a mix of uppercase and lowercase letters, numbers, and special characters."
        }
      ]
    },
    {
      title: "Terms of Service",
      items: [
        {
          title: "Accepting Terms",
          content: "You must accept the Terms of Service to create an account. Please read them carefully before proceeding. They outline your rights and responsibilities as a user."
        }
      ]
    },
    {
      title: "After Registration",
      items: [
        {
          title: "Email Verification",
          content: "After registering, you'll receive an email to verify your address. Click the link in the email to activate your account fully."
        },
        {
          title: "Getting Started",
          content: "Once registered, you'll be guided through an onboarding process to set up your workspace and preferences."
        }
      ]
    }
  ]
};

/**
 * Help content for the Forgot Password page
 */
export const forgotPasswordHelp: PageHelpContent = {
  title: "Password Reset Help",
  description: "Learn how to reset your forgotten password.",
  sections: [
    {
      title: "Reset Process",
      items: [
        {
          title: "Enter Your Email",
          content: "Enter the email address associated with your account. We'll send you instructions to reset your password."
        },
        {
          title: "Check Your Email",
          content: "After submitting, check your inbox for an email with the subject line about password reset. Click the link in the email to proceed."
        },
        {
          title: "Create New Password",
          content: "Choose a new password that's different from your previous one. Remember to use a strong password with at least 8 characters."
        }
      ]
    },
    {
      title: "Troubleshooting",
      items: [
        {
          title: "Email Not Received",
          content: "If you don't see the email, check your spam or junk folder. Also, ensure you're using the email address associated with your account."
        },
        {
          title: "Expired Link",
          content: "Password reset links expire after 24 hours. If yours has expired, you can request a new one from the forgot password page."
        }
      ]
    }
  ]
};

/**
 * Help content for the Care Circle Family dashboard
 */
export const careCircleFamilyHelp: PageHelpContent = {
  title: "Care Circle Family Dashboard",
  description: "Manage your family's care circle and track daily highlights for your loved ones.",
  sections: [
    {
      title: "Dashboard Overview",
      items: [
        {
          title: "Family Overview",
          content: "The dashboard provides an overview of all friends and family members in your care circle, showing their daily activity status and recent highlights."
        },
        {
          title: "Navigation",
          content: "Use the sidebar to navigate between different sections: Patients, Providers, Events, Media, and Settings. Each section manages a different aspect of your care circle."
        }
      ]
    },
    {
      title: "Friend Profiles",
      items: [
        {
          title: "Adding Friends",
          content: "Navigate to the Patients section to add new friends to your care circle. You'll need their basic information and consent to create their profile."
        },
        {
          title: "Daily Highlights",
          content: "Each friend receives personalized daily highlights generated from news, memories, and activities. These are designed to spark conversation and provide cognitive stimulation."
        }
      ]
    },
    {
      title: "Content Providers",
      items: [
        {
          title: "Managing Providers",
          content: "Content providers generate the daily highlights for your friends. You can enable, disable, or configure providers based on your friends' interests and needs."
        },
        {
          title: "Newsletter Generation",
          content: "Weekly newsletters are automatically generated with the week's highlights. You can customize the template and timing in the Template Studio."
        }
      ]
    }
  ]
};

/**
 * Help content for the Care Circle Family Patients page
 */
export const careCirclePatientsHelp: PageHelpContent = {
  title: "Friend Profiles Help",
  description: "Manage individual profiles for friends and family members in your care circle.",
  sections: [
    {
      title: "Friend Profiles",
      items: [
        {
          title: "What is a Friend Profile?",
          content: "A friend profile contains all the information needed to personalize daily highlights for someone in your care. This includes their name, interests, care preferences, and access settings."
        },
        {
          title: "Creating a Profile",
          content: "Click 'Add Friend' to create a new profile. Fill in their basic information, set their interests and preferences, and configure how they'll access their daily highlights."
        },
        {
          title: "Profile Information",
          content: "Each profile includes: name, photo (optional), interests and hobbies, cognitive support needs, daily schedule preferences, and caregiver contact information."
        }
      ]
    },
    {
      title: "Access Management",
      items: [
        {
          title: "Patient Login",
          content: "Friends can access their daily highlights through a simple login page. You can set up a memorable username and password for them, or generate a magic link for easy access."
        },
        {
          title: "Session Controls",
          content: "Control session length, feature availability, and content filters to ensure a safe and appropriate experience for your friend."
        }
      ]
    },
    {
      title: "Privacy & Consent",
      items: [
        {
          title: "Data Privacy",
          content: "All friend data is stored securely and used only to generate personalized content. We never share personal information with third parties without explicit consent."
        },
        {
          title: "Obtaining Consent",
          content: "Before creating a profile, ensure you have appropriate consent from the friend or their legal guardian. Document this consent in the profile settings."
        }
      ]
    }
  ]
};

/**
 * Help content for the Care Circle Family Providers page
 */
export const careCircleProvidersHelp: PageHelpContent = {
  title: "Content Providers Help",
  description: "Configure and manage the content providers that generate daily highlights.",
  sections: [
    {
      title: "About Providers",
      items: [
        {
          title: "What are Providers?",
          content: "Content providers fetch and process information from various sources to create personalized daily highlights. Each provider specializes in different content types."
        },
        {
          title: "Available Providers",
          content: "Providers include: News (local and general news), Weather (local forecasts), Memories (photo-based reminiscence), Calendar Events (upcoming dates), and Trivia (cognitive exercises)."
        }
      ]
    },
    {
      title: "Provider Configuration",
      items: [
        {
          title: "Enabling/Disabling",
          content: "Toggle providers on or off based on what content you want your friends to receive. Disabled providers won't contribute to daily highlights."
        },
        {
          title: "Provider Categories",
          content: "Providers are organized by category: News, Memory, Lifestyle, and Entertainment. Each category serves different aspects of the daily highlight experience."
        },
        {
          title: "Quality Settings",
          content: "Adjust the quality and relevance settings for each provider to control how much and what type of content is included in the daily highlights."
        }
      ]
    },
    {
      title: "Troubleshooting",
      items: [
        {
          title: "Provider Errors",
          content: "If a provider shows an error status, it may be temporarily unavailable. The system will automatically retry and resume when the service recovers."
        },
        {
          title: "Content Quality",
          content: "If content seems irrelevant or inappropriate, check the provider's configuration settings and adjust the content filters."
        }
      ]
    }
  ]
};

/**
 * Help content for the Care Circle Patient home page
 */
export const careCirclePatientHomeHelp: PageHelpContent = {
  title: "Daily Highlights Help",
  description: "Your daily highlights are ready to help you stay connected and engaged.",
  sections: [
    {
      title: "What You'll See",
      items: [
        {
          title: "Daily Highlights",
          content: "Your family has prepared personalized content for you each day, including news, memories, weather, and activities designed to spark joy and conversation."
        },
        {
          title: "Navigation",
          content: "Browse through your highlights by swiping or clicking through the cards. Each card represents a different piece of content prepared for you."
        }
      ]
    },
    {
      title: "Content Types",
      items: [
        {
          title: "News & Updates",
          content: "Stay informed with news stories and updates relevant to your interests and local community."
        },
        {
          title: "Memory Lane",
          content: "Reminisce with photos and stories from the past. These memories are shared by your family and are designed to spark happy recollections."
        },
        {
          title: "Weather & Events",
          content: "Know what the weather is like and see upcoming events or dates that might be important."
        }
      ]
    },
    {
      title: "Getting Help",
      items: [
        {
          title: "Switching Accounts",
          content: "If you need to access a different patient's highlights, use the 'Switch patient' button to choose a different profile."
        },
        {
          title: "Technical Issues",
          content: "If you experience any technical difficulties, please contact your family caregiver for assistance."
        }
      ]
    }
  ]
};

/**
 * Help content for the Care Circle Patient login page
 */
export const careCirclePatientLoginHelp: PageHelpContent = {
  title: "Patient Login Help",
  description: "Sign in to access your personalized daily highlights.",
  sections: [
    {
      title: "Signing In",
      items: [
        {
          title: "Easy Login",
          content: "Your family has set up a simple way for you to sign in. You can use your username and password, or your family can provide a direct link for one-click access."
        },
        {
          title: "Remember Me",
          content: "Check the 'Remember me' option if you want to stay signed in on this device. This makes it easier to access your highlights daily."
        }
      ]
    },
    {
      title: "Need Assistance",
      items: [
        {
          title: "Forgot Credentials",
          content: "If you've forgotten your login information, ask your family caregiver. They can reset your password or provide a new login link."
        },
        {
          title: "Contact Family",
          content: "If you're having trouble accessing the system, please contact your family member who set up your account. They can help you get signed in."
        }
      ]
    }
  ]
};

/**
 * Help content for the Storytelling dashboard
 */
export const storytellingHelp: PageHelpContent = {
  title: "Storytelling Help",
  description: "Create and manage your creative stories and worlds.",
  sections: [
    {
      title: "Getting Started",
      items: [
        {
          title: "What is Storytelling?",
          content: "The Storytelling app helps you create, organize, and develop your creative writing projects. You can create stories, build fictional worlds, develop characters, and more."
        },
        {
          title: "Starting a Story",
          content: "Use the chatbot to brainstorm ideas, create outlines, or get writing prompts. The chatbot can help you develop your narrative and overcome writer's block."
        }
      ]
    },
    {
      title: "Writing Tools",
      items: [
        {
          title: "World Building",
          content: "Create rich fictional worlds with locations, lore, and history. Organize your world-building elements to maintain consistency across your stories."
        },
        {
          title: "Character Development",
          content: "Build detailed character profiles including backgrounds, motivations, relationships, and character arcs. Well-developed characters make stories come alive."
        },
        {
          title: "Story Organization",
          content: "Keep your stories organized with categories, tags, and series. This makes it easy to find and manage your writing projects."
        }
      ]
    },
    {
      title: "AI Assistance",
      items: [
        {
          title: "Chatbot Help",
          content: "The AI chatbot can help you brainstorm ideas, develop plots, create dialogue, and improve your writing. Access it anytime from the chatbot button."
        },
        {
          title: "Writing Prompts",
          content: "Need inspiration? The chatbot can generate creative writing prompts tailored to your interests and current project."
        }
      ]
    }
  ]
};

/**
 * Help content for the Account page
 */
export const accountHelp: PageHelpContent = {
  title: "Account Settings Help",
  description: "Manage your account information and preferences.",
  sections: [
    {
      title: "Profile Information",
      items: [
        {
          title: "Username",
          content: "Your username is your unique identifier on the platform. It cannot be changed once set, so choose carefully during registration."
        },
        {
          title: "Display Name",
          content: "This is the name others see when interacting with you. You can update this at any time from your account settings."
        },
        {
          title: "Email Address",
          content: "Your email is used for notifications, password resets, and account verification. Keep it up to date to receive important messages."
        }
      ]
    },
    {
      title: "Security",
      items: [
        {
          title: "Password",
          content: "Update your password regularly for security. Use a strong password with at least 8 characters, mixing letters, numbers, and symbols."
        },
        {
          title: "Two-Factor Authentication",
          content: "Enable two-factor authentication for an extra layer of security. This requires a code from your phone when signing in from new devices."
        }
      ]
    },
    {
      title: "Account Management",
      items: [
        {
          title: "Editing Profile",
          content: "Click 'Edit Profile' to update your personal information. Some changes may require re-verification."
        },
        {
          title: "Account Deletion",
          content: "To delete your account, contact support. Note that this action is permanent and cannot be undone."
        }
      ]
    }
  ]
};

/**
 * Help content for the Billing page
 */
export const billingHelp: PageHelpContent = {
  title: "Billing Help",
  description: "Manage your subscription, payments, and billing information.",
  sections: [
    {
      title: "Subscription",
      items: [
        {
          title: "Current Plan",
          content: "View your current subscription plan and its features. Plans include different levels of access to platform features and usage limits."
        },
        {
          title: "Plan Changes",
          content: "You can upgrade, downgrade, or cancel your subscription at any time. Changes take effect at the start of your next billing cycle."
        },
        {
          title: "Billing Cycle",
          content: "Your subscription renews on the same day each month. You'll receive a reminder email before any charges are processed."
        }
      ]
    },
    {
      title: "Payments",
      items: [
        {
          title: "Payment Methods",
          content: "Add and manage payment methods from your billing settings. We accept major credit cards and PayPal."
        },
        {
          title: "Payment History",
          content: "View all past payments and download invoices for your records. Each invoice includes a detailed breakdown of charges."
        },
        {
          title: "Failed Payments",
          content: "If a payment fails, we'll notify you and retry automatically. Update your payment method promptly to avoid service interruption."
        }
      ]
    },
    {
      title: "Refunds",
      items: [
        {
          title: "Refund Policy",
          content: "We offer refunds within 30 days of payment for annual plans and within 7 days for monthly plans, subject to our refund policy terms."
        },
        {
          title: "Requesting a Refund",
          content: "To request a refund, contact our support team with your reason for the request. We'll process eligible requests within 5-7 business days."
        }
      ]
    }
  ]
};

/**
 * Help content for the Onboarding page
 */
export const onboardingHelp: PageHelpContent = {
  title: "Getting Started Help",
  description: "Complete your account setup and learn how to use the platform.",
  sections: [
    {
      title: "Setup Steps",
      items: [
        {
          title: "Complete Your Profile",
          content: "Fill in your profile information including your display name and preferences. A complete profile helps personalize your experience."
        },
        {
          title: "Explore Features",
          content: "Take a tour of the main features available to you. Each section has helpful tooltips and guides to get you started."
        },
        {
          title: "Set Preferences",
          content: "Configure your notification preferences, theme settings, and other personalization options to suit your workflow."
        }
      ]
    },
    {
      title: "Tips & Tricks",
      items: [
        {
          title: "Keyboard Shortcuts",
          content: "Learn keyboard shortcuts to navigate faster. Press '?' anywhere in the app to see available shortcuts."
        },
        {
          title: "Notifications",
          content: "Configure which notifications you want to receive. You can choose to receive updates via email, in-app, or both."
        },
        {
          title: "Getting Help",
          content: "Use the help button on any page for contextual assistance. You can also access the help center from the main menu."
        }
      ]
    }
  ]
};

/**
 * Help content for the Referrals page
 */
export const referralsHelp: PageHelpContent = {
  title: "Referrals Help",
  description: "Share the platform with friends and earn rewards.",
  sections: [
    {
      title: "How Referrals Work",
      items: [
        {
          title: "Your Referral Link",
          content: "Share your unique referral link with friends. When they sign up using your link, they're linked to your account."
        },
        {
          title: "Referral Tracking",
          content: "Track the status of your referrals from your dashboard. See who's signed up, verified their email, and become active users."
        }
      ]
    },
    {
      title: "Rewards",
      items: [
        {
          title: "Earning Rewards",
          content: "Earn rewards when your referrals complete their registration and verify their email. Some rewards may require referrals to be active subscribers."
        },
        {
          title: "Reward Types",
          content: "Rewards may include platform credits, extended trial periods, or premium features. Check your current offer for specific details."
        },
        {
          title: "Reward Redemption",
          content: "View your accumulated rewards in the referrals dashboard. Rewards are automatically applied to your account or can be manually redeemed."
        }
      ]
    },
    {
      title: "Best Practices",
      items: [
        {
          title: "Effective Sharing",
          content: "Share your referral link authentically with friends who might benefit from the platform. Personal recommendations work best."
        },
        {
          title: "Terms Apply",
          content: "Referral rewards are subject to terms and conditions. Only legitimate referrals count toward rewards. See the full referral policy for details."
        }
      ]
    }
  ]
};

/**
 * Help content for the Admin page
 */
export const adminHelp: PageHelpContent = {
  title: "Admin Dashboard Help",
  description: "Manage platform settings, users, and system configuration.",
  sections: [
    {
      title: "Admin Features",
      items: [
        {
          title: "User Management",
          content: "View and manage user accounts, including verifying accounts, resetting passwords, and adjusting permissions."
        },
        {
          title: "System Configuration",
          content: "Configure platform-wide settings including feature flags, rate limits, and system maintenance schedules."
        },
        {
          title: "Content Moderation",
          content: "Review and moderate user-generated content to ensure it meets community guidelines and platform standards."
        }
      ]
    },
    {
      title: "Scheduler & Tasks",
      items: [
        {
          title: "Background Jobs",
          content: "Monitor and manage background tasks including newsletter generation, email delivery, and data processing jobs."
        },
        {
          title: "Provider Templates",
          content: "Manage the templates used by content providers to generate daily highlights for care circle members."
        }
      ]
    },
    {
      title: "Security",
      items: [
        {
          title: "Access Control",
          content: "Admin access is role-based. Ensure you only grant necessary permissions to admin users."
        },
        {
          title: "Audit Logs",
          content: "Review audit logs for administrative actions. All significant changes are logged with timestamps and user information."
        }
      ]
    }
  ]
};

/**
 * Help content for the Public page
 */
export const publicPageHelp: PageHelpContent = {
  title: "Public Page Help",
  description: "Learn about publicly accessible features and content.",
  sections: [
    {
      title: "Public Content",
      items: [
        {
          title: "What is Public?",
          content: "Public pages contain information and content that is accessible to everyone, even without an account. This includes the home page, about page, and shared content."
        },
        {
          title: "Shared Stories",
          content: "Authors can choose to publish stories publicly. These stories are visible to everyone and showcase the creative work on our platform."
        }
      ]
    },
    {
      title: "Creating an Account",
      items: [
        {
          title: "Sign Up",
          content: "To create and publish your own content, register for a free account. Registration is quick and gives you access to all platform features."
        },
        {
          title: "Benefits of Signing Up",
          content: "Registered users can create stories, participate in forums, access AI writing tools, and connect with other creators."
        }
      ]
    }
  ]
};

/**
 * Help content for the Chatbot page
 */
export const chatbotHelp: PageHelpContent = {
  title: "AI Chatbot Help",
  description: "Your AI writing assistant for creative projects and brainstorming.",
  sections: [
    {
      title: "Getting Started",
      items: [
        {
          title: "What is the Chatbot?",
          content: "The AI chatbot is your creative writing assistant. It can help you brainstorm ideas, develop characters, plot stories, improve your writing, and overcome writer's block."
        },
        {
          title: "Starting a Conversation",
          content: "Simply type your question or request in the chat input. Be specific about what you need help with for the best results."
        }
      ]
    },
    {
      title: "Writing Assistance",
      items: [
        {
          title: "Brainstorming",
          content: "Need ideas? Ask the chatbot to suggest plot points, character traits, setting details, or story themes. It can generate multiple options for you to choose from."
        },
        {
          title: "Character Development",
          content: "The chatbot can help you create detailed character profiles, backstories, motivations, and character arcs. Describe your basic idea and let it help you expand."
        },
        {
          title: "Writing and Editing",
          content: "Share your writing with the chatbot and ask for feedback. It can suggest improvements, point out inconsistencies, and help you refine your prose."
        }
      ]
    },
    {
      title: "Tips for Best Results",
      items: [
        {
          title: "Be Specific",
          content: "The more details you provide, the better the chatbot can help. Include your story's genre, tone, and any specific constraints you have in mind."
        },
        {
          title: "Iterate and Refine",
          content: "Don't hesitate to ask follow-up questions or request revisions. Building on initial ideas through conversation often leads to better results."
        },
        {
          title: "Privacy",
          content: "Your conversations are private and secure. We never share your writing or conversation content with third parties."
        }
      ]
    }
  ]
};

// Export all help content as a map for easy lookup
export const helpContentMap: Record<string, PageHelpContent> = {
  "auth/login": loginHelp,
  "auth/register": registerHelp,
  "auth/forgot-password": forgotPasswordHelp,
  "care-circle-family": careCircleFamilyHelp,
  "care-circle-family/account": accountHelp,
  "care-circle-family/account/edit": accountHelp,
  "care-circle-family/admin": adminHelp,
  "care-circle-family/admin/families": adminHelp,
  "care-circle-family/admin/scheduler": adminHelp,
  "care-circle-family/admin/template-studio": adminHelp,
  "care-circle-family/billing": billingHelp,
  "care-circle-family/events": careCircleFamilyHelp,
  "care-circle-family/media": careCircleFamilyHelp,
  "care-circle-family/members": careCircleFamilyHelp,
  "care-circle-family/patients": careCirclePatientsHelp,
  "care-circle-family/patients/new": careCirclePatientsHelp,
  "care-circle-family/providers": careCircleProvidersHelp,
  "care-circle-family/referrals": referralsHelp,
  "care-circle-patient": careCirclePatientLoginHelp,
  "care-circle-patient/home": careCirclePatientHomeHelp,
  "care-circle-patient/login": careCirclePatientLoginHelp,
  "storytelling/account": accountHelp,
  "storytelling/account/edit": accountHelp,
  "storytelling/billing": billingHelp,
  "storytelling/onboarding": onboardingHelp,
  "storytelling/referrals": referralsHelp,
  "storytelling": storytellingHelp,
  "chatbot": chatbotHelp,
  "account": accountHelp,
  "billing": billingHelp,
  "onboarding": onboardingHelp,
  "referrals": referralsHelp,
  "admin": adminHelp,
  "public": publicPageHelp
};

function createFallbackHelpContent(pathname: string): PageHelpContent {
  const normalized = pathname === "/" ? "home" : pathname.replace(/^\/+|\/+$/g, "");
  const segments = normalized.split("/").filter(Boolean);
  const pageName = segments
    .map((segment) => {
      if (/^\[.+\]$/.test(segment) || /^\d+$/.test(segment)) {
        return "detail";
      }

      return segment
        .replace(/[-_]/g, " ")
        .replace(/\b\w/g, (character) => character.toUpperCase());
    })
    .join(" / ");

  return {
    title: `${pageName} Help`,
    description: "This page includes contextual guidance, tooltips on controls, and direct actions that match the current workflow.",
    sections: [
      {
        title: "Using this page",
        items: [
          {
            title: "Controls and actions",
            content: "Hover or focus buttons, inputs, selectors, and text areas to see quick guidance about what each control does before you interact with it."
          },
          {
            title: "Saving and navigation",
            content: "Use the primary action to commit changes and secondary actions to cancel, go back, or open related workflow areas without losing context."
          }
        ]
      },
      {
        title: "Need more context?",
        items: [
          {
            title: "Route-specific guidance",
            content: "This help panel is generated for the current route so every page always has a guidance entry point, even while deeper documentation is still being refined."
          }
        ]
      }
    ]
  };
}

export function resolveHelpContent(pathname: string): PageHelpContent {
  const normalizedPath = pathname.replace(/^\/+|\/+$/g, "");

  if (!normalizedPath) {
    return publicPageHelp;
  }

  if (helpContentMap[normalizedPath]) {
    return helpContentMap[normalizedPath];
  }

  if (/^care-circle-family\/patients\/[^/]+$/.test(normalizedPath)) {
    return careCirclePatientsHelp;
  }

  if (/^care-circle-family\/providers\/[^/]+$/.test(normalizedPath)) {
    return careCircleProvidersHelp;
  }

  if (/^auth\/password-reset\/confirm/.test(normalizedPath)) {
    return forgotPasswordHelp;
  }

  return createFallbackHelpContent(pathname);
}
