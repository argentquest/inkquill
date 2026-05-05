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
  blogPosts?: "default" | "empty";
  authorBlogPosts?: "default" | "empty";
}

const authenticatedUser = {
  id: 7,
  username: "storymaker",
  email: "storymaker@example.com",
  display_name: "Story Maker",
  is_admin: true,
  is_family_owner: true,
  is_active: true
};

const careCirclePatients: any[] = [
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
    authImageKeys: ["sun", "dog", "house"],
    email: null,
    phoneNumber: null,
    created_at: "2026-01-15T10:00:00Z",
    newsletters_sent: 12,
    preferences: {
      recipientName: null, preferredPronoun: "she/her",
      hometown: "Springfield", cityForWeather: "Chicago",
      eraOfYouth: "1950s", nationalityOrBackground: null, mobilityLevel: null,
      familyMembers: ["Nina", "Paul", "Maggie"], lifeRoles: ["mother", "teacher"],
      pets: [], hobbies: ["gardening"], favoriteActivities: [],
      favoriteSingers: [], favouriteFoods: ["tea and biscuits"], favouriteTvShows: [],
    },
    highlights: [
      {
        title: "Family hello",
        body: "Nina says the daffodils are opening and she saved the first photo for you.",
        kind: "family",
        providerKey: "family_greeting",
        displayOrder: 1,
        feedback: null
      },
      {
        title: "Memory lane",
        body: "Today’s memory card revisits spring walks and favorite songs from the 1950s.",
        kind: "memory",
        providerKey: "nostalgia",
        displayOrder: 2,
        feedback: null
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
    authImageKeys: ["tree", "car", "star"],
    email: null,
    phoneNumber: null,
    created_at: "2026-02-01T09:00:00Z",
    newsletters_sent: 5,
    preferences: {
      recipientName: null, preferredPronoun: "he/him",
      hometown: null, cityForWeather: "New York",
      eraOfYouth: "1940s", nationalityOrBackground: null, mobilityLevel: null,
      familyMembers: ["Janet", "Chris"], lifeRoles: [],
      pets: [], hobbies: ["crosswords"], favoriteActivities: [],
      favoriteSingers: [], favouriteFoods: [], favouriteTvShows: [],
    },
    highlights: [
      {
        title: "Daily note",
        body: "Chris left a short update about yesterday’s walk by the river.",
        kind: "family",
        providerKey: "family_greeting",
        displayOrder: 1,
        feedback: null
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

const careCircleActivityEvents = [
  {
    id: "session-output-1",
    type: "provider_output_created",
    title: "Daily content generated",
    description: "Family Greeting generated content for Rose Ellis.",
    tone: "success",
    occurred_at: "2026-04-27T16:30:00Z",
    patient_id: 1,
    patient_name: "Rose Ellis",
    provider_key: "family_greeting"
  },
  {
    id: "provider-run-2",
    type: "provider_run_failed",
    title: "Provider fallback used",
    description: "Weather could not finish for Arthur Bloom.",
    tone: "warning",
    occurred_at: "2026-04-27T15:00:00Z",
    patient_id: 2,
    patient_name: "Arthur Bloom",
    provider_key: "weather"
  }
];

const careCircleMediaSeed = [
  {
    id: "media-1",
    filename: "7_rose-porch.jpg",
    storage_path: "7_rose-porch.jpg",
    original_filename: "rose-porch.jpg",
    url: "/mock-media/rose-porch.jpg",
    thumbnail_url: "/mock-media/rose-porch-thumb.jpg",
    file_type: "image",
    content_type: "image/jpeg",
    file_size: 248000,
    alt_text: "Rose on the front porch",
    caption: "Spring porch visit",
    uploaded_by: 7,
    created_at: "2026-04-27T17:15:00Z",
    width: 1600,
    height: 1200,
    format: "JPEG",
    aspect_ratio_urls: {
      "16x9": "/mock-media/rose-porch-16x9.jpg",
      "5x4": "/mock-media/rose-porch-5x4.jpg",
      "1x1": "/mock-media/rose-porch-1x1.jpg"
    }
  }
];

const userStoriesSeed = [
  {
    id: 1,
    title: "The Silver Compass",
    short_description: "An explorer discovers a map that leads to an ancient realm hidden inside a storm.",
    story_genre: "Fantasy Adventure",
    story_type: "advanced",
    created_at: "2026-04-20T10:00:00Z",
    updated_at: "2026-04-25T14:30:00Z",
  },
  {
    id: 2,
    title: "Ember Coast",
    short_description: "A fishing village learns it sits atop a sleeping volcano with a memory.",
    story_genre: "Literary Fiction",
    story_type: "advanced",
    created_at: "2026-04-22T08:00:00Z",
    updated_at: "2026-04-26T09:45:00Z",
  },
];

const userWorldsSeed = [
  {
    id: 1,
    name: "Aethoria",
    short_description: "A realm of floating islands and ancient sky bridges connecting lost civilisations.",
    is_free_chat_enabled: false,
    created_at: "2026-04-18T09:00:00Z",
    updated_at: "2026-04-24T11:00:00Z",
  },
];

const publishedStoriesSeed = [
  {
    id: 101,
    story_id: 1,
    user_id: 7,
    title: "The Silver Compass — Published",
    description: "An explorer discovers a map that leads to an ancient realm.",
    published_url: "/published/the-silver-compass",
    filename: "the-silver-compass.html",
    word_count: 12400,
    is_public: true,
    is_featured: true,
    view_count: 342,
    like_count: 28,
    comment_count: 5,
    average_rating: 4.2,
    published_at: "2026-04-20T10:00:00Z",
    updated_at: "2026-04-25T14:30:00Z",
    publisher_username: "storymaker",
    publisher_display_name: "Story Maker",
    world_name: "Aethoria",
    story_title: "The Silver Compass",
    story_short_description: "An explorer discovers a map.",
    has_user_rated: false,
    user_rating: null,
  },
];

type PublishedStoryCommentSeed = {
  id: number;
  published_story_id: number;
  user_id: number;
  commenter_username: string | null;
  commenter_display_name: string | null;
  content: string;
  is_approved: boolean;
  created_at: string;
  updated_at: string;
};

const publishedStoryCommentsSeed: Record<number, PublishedStoryCommentSeed[]> = {
  101: [
    {
      id: 1,
      published_story_id: 101,
      user_id: 11,
      commenter_username: "readerone",
      commenter_display_name: "Reader One",
      content: "The opening image really pulled me into the world.",
      is_approved: true,
      created_at: "2026-04-22T14:00:00Z",
      updated_at: "2026-04-22T14:00:00Z"
    }
  ]
};

// ---------------------------------------------------------------------------
// Sprint 11 seed data — Chatbot
// ---------------------------------------------------------------------------

const chatbotSessionsSeed: Array<{
  id: number; user_id: number; title: string; created_at: string; updated_at: string;
}> = [
  { id: 10, user_id: 7, title: "Story scene discussion", created_at: "2026-04-25T10:00:00Z", updated_at: "2026-04-25T10:05:00Z" },
  { id: 11, user_id: 7, title: "Care update draft", created_at: "2026-04-26T08:00:00Z", updated_at: "2026-04-26T08:10:00Z" },
];

const chatbotSessionWithMessages = {
  ...chatbotSessionsSeed[0],
  messages: [
    {
      id: 101,
      session_id: 10,
      role: "user",
      content: "Can you help me outline a scene?",
      input_tokens: null,
      output_tokens: null,
      cost_usd: null,
      model_name: null,
      created_at: "2026-04-25T10:01:00Z",
    },
    {
      id: 102,
      session_id: 10,
      role: "assistant",
      content: "Of course! Start with the setting, introduce the conflict, then end on an unresolved tension.",
      input_tokens: 45,
      output_tokens: 32,
      cost_usd: 0.0003,
      model_name: "gpt-4o",
      created_at: "2026-04-25T10:01:05Z",
    },
  ],
};

// ---------------------------------------------------------------------------
// Sprint 10 seed data
// ---------------------------------------------------------------------------

const promptsSeed = [
  {
    id: 1,
    title: "Fantasy world opener",
    prompt_content: "Write an opening paragraph that establishes an ancient fantasy world with a sense of deep history.",
    reason_to_use: "Use this at the start of a new fantasy story to set the tone.",
    comment: null,
    is_active: true,
    prompt_type: "STORY",
    age_target: "ALL_AGES",
    user_id: 7,
    created_at: "2026-03-01T00:00:00Z",
    updated_at: "2026-03-01T00:00:00Z",
  },
  {
    id: 2,
    title: "Character backstory hook",
    prompt_content: "In one paragraph, reveal a key moment from this character's past that shaped who they are today.",
    reason_to_use: "Use when introducing a new major character.",
    comment: null,
    is_active: true,
    prompt_type: "CHARACTER",
    age_target: "ALL_AGES",
    user_id: 7,
    created_at: "2026-03-05T00:00:00Z",
    updated_at: "2026-03-05T00:00:00Z",
  },
];

const llmModelsSeed = {
  models: [
    {
      id: 1,
      display_name: "GPT-4o",
      model_name: "gpt-4o",
      description: "OpenAI's flagship multimodal model.",
      provider: "openai",
      model_type: "chat",
      is_active: true,
      max_tokens: 4096,
      temperature: 0.7,
      user_price_input_usd_pm: 0.005,
      user_price_output_usd_pm: 0.015,
    },
    {
      id: 2,
      display_name: "Claude 3 Haiku",
      model_name: "claude-haiku-4-5-20251001",
      description: "Fast and efficient Anthropic model.",
      provider: "anthropic",
      model_type: "chat",
      is_active: true,
      max_tokens: 2048,
      temperature: 0.7,
      user_price_input_usd_pm: 0.00025,
      user_price_output_usd_pm: 0.00125,
    },
  ],
  total_count: 2,
  active_count: 2,
  providers: ["openai", "anthropic"],
};

const authorBlogPostsSeed = [
  {
    id: 201,
    title: "My First Blog Post",
    slug: "my-first-blog-post",
    content: "This is the content of my first blog post.",
    excerpt: "An introductory post.",
    featured_image_url: null,
    status: "draft",
    author_id: 7,
    view_count: 0,
    like_count: 0,
    comment_count: 0,
    published_at: null,
    created_at: "2026-04-01T00:00:00Z",
    updated_at: "2026-04-01T00:00:00Z",
  },
  {
    id: 202,
    title: "Writing Tips for Fantasy",
    slug: "writing-tips-fantasy",
    content: "Here are my top five writing tips for fantasy authors.",
    excerpt: "Five tips for fantasy writing.",
    featured_image_url: null,
    status: "published",
    author_id: 7,
    view_count: 42,
    like_count: 5,
    comment_count: 2,
    published_at: "2026-04-10T00:00:00Z",
    created_at: "2026-04-08T00:00:00Z",
    updated_at: "2026-04-10T00:00:00Z",
  },
];

// ---------------------------------------------------------------------------
// Sprint 12 seed data — Admin
// ---------------------------------------------------------------------------

const adminUsersSeed = [
  { id: 7, username: "storymaker", email: "storymaker@example.com", display_name: "Story Maker", is_active: true, is_admin: true, created_at: "2026-01-01T00:00:00Z" },
  { id: 8, username: "alice", email: "alice@example.com", display_name: "Alice Winters", is_active: true, is_admin: false, created_at: "2026-02-01T00:00:00Z" },
  { id: 9, username: "bobwriter", email: "bob@example.com", display_name: null, is_active: false, is_admin: false, created_at: "2026-03-01T00:00:00Z" },
];

const adminBillingDashboardSeed = {
  system_stats: {
    total_users: 42,
    total_coins_issued: 18500,
    total_coins_spent: 7300,
    active_accounts: 38,
  },
  recent_transactions: [
    { id: 1, user_id: 8, description: "Story generation", amount: -50, created_at: "2026-04-28T10:00:00Z" },
    { id: 2, user_id: 7, description: "Monthly top-up", amount: 500, created_at: "2026-04-27T08:00:00Z" },
  ],
  user_accounts: [],
};

const adminCTASeed = [
  { id: 1, title: "Join the Community", subtitle: "Connect with other writers.", position: "home_hero", style: "gradient", is_active: true, sort_order: 0, primary_button_text: "Sign up free", primary_button_url: "/register", show_for_anonymous: true, show_for_authenticated: false },
  { id: 2, title: "Upgrade Your Plan", subtitle: "Get more coins every month.", position: "sidebar", style: "minimal", is_active: false, sort_order: 1, primary_button_text: "View plans", primary_button_url: "/billing", show_for_anonymous: false, show_for_authenticated: true },
];

const maintenanceStatusOffSeed = { enabled: false, message: null, estimated_end_time: null };
const maintenanceStatusOnSeed = { enabled: true, message: "Scheduled maintenance — back in 5 minutes.", estimated_end_time: null };

const forumCategoriesSeed = [
  {
    id: 1,
    name: "World Building",
    description: "Discuss settings, maps, and fictional worlds.",
    slug: "world-building",
    sort_order: 1,
    is_active: true,
    icon: "🌍",
    thread_count: 12,
    app_source: "storytelling",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-04-01T00:00:00Z",
  },
  {
    id: 2,
    name: "Story Craft",
    description: "Plot, character, dialogue, and narrative structure.",
    slug: "story-craft",
    sort_order: 2,
    is_active: true,
    icon: "✍️",
    thread_count: 8,
    app_source: "storytelling",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-04-01T00:00:00Z",
  },
  {
    id: 3,
    name: "Story Feedback & Critique",
    description: "Share works-in-progress and get reader feedback.",
    slug: "story-feedback-critique",
    sort_order: 3,
    is_active: true,
    icon: "💬",
    thread_count: 5,
    app_source: "storytelling",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-04-01T00:00:00Z",
  },
  {
    id: 4,
    name: "Character Workshop",
    description: "Character development, backstories, and motivation deep-dives.",
    slug: "character-workshop",
    sort_order: 4,
    is_active: true,
    icon: "🎭",
    thread_count: 4,
    app_source: "storytelling",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-04-01T00:00:00Z",
  },
  {
    id: 5,
    name: "Writing Craft & Tips",
    description: "General writing advice, prompts, and technique discussions.",
    slug: "writing-craft-tips",
    sort_order: 5,
    is_active: true,
    icon: "📝",
    thread_count: 6,
    app_source: "storytelling",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-04-01T00:00:00Z",
  },
  {
    id: 6,
    name: "AI Collaboration",
    description: "Strategies for working with AI tools, prompt tips, and generation techniques.",
    slug: "ai-collaboration",
    sort_order: 6,
    is_active: true,
    icon: "🤖",
    thread_count: 3,
    app_source: "storytelling",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-04-01T00:00:00Z",
  },
  {
    id: 7,
    name: "Care Tips & Resources",
    description: "Caregiving advice, medical info, daily routines, and best practices.",
    slug: "care-tips-resources",
    sort_order: 1,
    is_active: true,
    icon: "🩺",
    thread_count: 2,
    app_source: "care-circle",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-04-01T00:00:00Z",
  },
  {
    id: 8,
    name: "Family Coordination",
    description: "Planning, schedules, events, and logistics for the care circle.",
    slug: "family-coordination",
    sort_order: 2,
    is_active: true,
    icon: "📅",
    thread_count: 1,
    app_source: "care-circle",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-04-01T00:00:00Z",
  },
  {
    id: 9,
    name: "Memory Lane",
    description: "Sharing memories, photos, and stories about friends and loved ones.",
    slug: "memory-lane",
    sort_order: 3,
    is_active: true,
    icon: "📸",
    thread_count: 1,
    app_source: "care-circle",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-04-01T00:00:00Z",
  },
  {
    id: 10,
    name: "Wellness & Activities",
    description: "Ideas for outings, activities, and keeping friends engaged.",
    slug: "wellness-activities",
    sort_order: 4,
    is_active: true,
    icon: "🌿",
    thread_count: 1,
    app_source: "care-circle",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-04-01T00:00:00Z",
  },
  {
    id: 11,
    name: "Getting Help",
    description: "Questions about using the Circle Friends app and troubleshooting.",
    slug: "getting-help",
    sort_order: 5,
    is_active: true,
    icon: "❓",
    thread_count: 0,
    app_source: "care-circle",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-04-01T00:00:00Z",
  },
];

const forumThreadsSeed = [
  {
    id: 1,
    title: "How do you structure a magic system?",
    slug: "how-do-you-structure-a-magic-system",
    status: "open",
    category_id: 1,
    category_name: "World Building",
    user_id: 7,
    username: "storymaker",
    world_id: null,
    world_name: null,
    story_id: null,
    story_title: null,
    view_count: 120,
    post_count: 7,
    last_post_at: "2026-04-26T09:00:00Z",
    last_post_by_username: "storymaker",
    is_pinned: false,
    is_locked: false,
    created_at: "2026-04-20T08:00:00Z",
    updated_at: "2026-04-26T09:00:00Z",
    app_source: "storytelling",
    posts: [
      {
        id: 1,
        content: "I always start with the limitations before the powers.",
        content_html: "<p>I always start with the limitations before the powers.</p>",
        thread_id: 1,
        user_id: 7,
        username: "storymaker",
        user_display_name: "Story Maker",
        upvote_count: 15,
        downvote_count: 1,
        score: 14,
        edit_count: 0,
        is_deleted: false,
        created_at: "2026-04-20T08:00:00Z",
        updated_at: "2026-04-20T08:00:00Z",
      },
    ],
  },
  {
    id: 2,
    title: "Best routines for morning care?",
    slug: "best-routines-for-morning-care",
    status: "open",
    category_id: 3,
    category_name: "Care Tips & Resources",
    user_id: 7,
    username: "storymaker",
    world_id: null,
    world_name: null,
    story_id: null,
    story_title: null,
    view_count: 45,
    post_count: 3,
    last_post_at: "2026-04-25T10:00:00Z",
    last_post_by_username: "storymaker",
    is_pinned: false,
    is_locked: false,
    created_at: "2026-04-22T08:00:00Z",
    updated_at: "2026-04-25T10:00:00Z",
    app_source: "care-circle",
    posts: [],
  },
  {
    id: 3,
    title: "Favorite AI prompts for character voice?",
    slug: "favorite-ai-prompts-for-character-voice",
    status: "open",
    category_id: 6,
    category_name: "AI Collaboration",
    user_id: 7,
    username: "storymaker",
    world_id: null,
    world_name: null,
    story_id: null,
    story_title: null,
    view_count: 88,
    post_count: 4,
    last_post_at: "2026-04-28T11:00:00Z",
    last_post_by_username: "storymaker",
    is_pinned: false,
    is_locked: false,
    created_at: "2026-04-25T08:00:00Z",
    updated_at: "2026-04-28T11:00:00Z",
    app_source: "storytelling",
    posts: [],
  },
  {
    id: 4,
    title: "Plot twist techniques that actually work",
    slug: "plot-twist-techniques-that-actually-work",
    status: "open",
    category_id: 5,
    category_name: "Writing Craft & Tips",
    user_id: 7,
    username: "storymaker",
    world_id: null,
    world_name: null,
    story_id: null,
    story_title: null,
    view_count: 210,
    post_count: 12,
    last_post_at: "2026-04-29T14:00:00Z",
    last_post_by_username: "storymaker",
    is_pinned: false,
    is_locked: false,
    created_at: "2026-04-18T08:00:00Z",
    updated_at: "2026-04-29T14:00:00Z",
    app_source: "storytelling",
    posts: [],
  },
  {
    id: 5,
    title: "Creating believable political systems",
    slug: "creating-believable-political-systems",
    status: "open",
    category_id: 1,
    category_name: "World Building",
    user_id: 7,
    username: "storymaker",
    world_id: null,
    world_name: null,
    story_id: null,
    story_title: null,
    view_count: 156,
    post_count: 8,
    last_post_at: "2026-04-30T09:00:00Z",
    last_post_by_username: "storymaker",
    is_pinned: false,
    is_locked: false,
    created_at: "2026-04-23T08:00:00Z",
    updated_at: "2026-04-30T09:00:00Z",
    app_source: "storytelling",
    posts: [],
  },
  {
    id: 6,
    title: "Photo sharing tips for Memory Lane?",
    slug: "photo-sharing-tips-for-memory-lane",
    status: "open",
    category_id: 9,
    category_name: "Memory Lane",
    user_id: 7,
    username: "storymaker",
    world_id: null,
    world_name: null,
    story_id: null,
    story_title: null,
    view_count: 34,
    post_count: 2,
    last_post_at: "2026-04-27T10:00:00Z",
    last_post_by_username: "storymaker",
    is_pinned: false,
    is_locked: false,
    created_at: "2026-04-24T08:00:00Z",
    updated_at: "2026-04-27T10:00:00Z",
    app_source: "care-circle",
    posts: [],
  },
  {
    id: 7,
    title: "Character arcs vs flat characters",
    slug: "character-arcs-vs-flat-characters",
    status: "open",
    category_id: 4,
    category_name: "Character Workshop",
    user_id: 7,
    username: "storymaker",
    world_id: null,
    world_name: null,
    story_id: null,
    story_title: null,
    view_count: 172,
    post_count: 9,
    last_post_at: "2026-05-01T10:00:00Z",
    last_post_by_username: "storymaker",
    is_pinned: false,
    is_locked: false,
    created_at: "2026-04-26T08:00:00Z",
    updated_at: "2026-05-01T10:00:00Z",
    app_source: "storytelling",
    posts: [],
  },
];

const blogPostsSeed = [
  {
    id: 1,
    title: "Introducing World Builder 2.0",
    slug: "introducing-world-builder-2",
    content: "<p>We've rebuilt the world builder from the ground up.</p>",
    excerpt: "A major update to how you create and manage fictional worlds.",
    featured_image_url: null,
    status: "published",
    author_id: 7,
    view_count: 890,
    like_count: 42,
    comment_count: 11,
    published_at: "2026-04-15T12:00:00Z",
    created_at: "2026-04-15T10:00:00Z",
    updated_at: "2026-04-15T12:00:00Z",
    app_source: "storytelling",
  },
  {
    id: 2,
    title: "Welcome to Care Circle",
    slug: "welcome-to-care-circle",
    content: "<p>Getting started with your family care circle.</p>",
    excerpt: "Tips for setting up your first care circle.",
    featured_image_url: null,
    status: "published",
    author_id: 7,
    view_count: 120,
    like_count: 8,
    comment_count: 2,
    published_at: "2026-04-20T10:00:00Z",
    created_at: "2026-04-20T10:00:00Z",
    updated_at: "2026-04-20T10:00:00Z",
    app_source: "care-circle",
  },
  {
    id: 3,
    title: "AI Prompting for Dialogue",
    slug: "ai-prompting-for-dialogue",
    content: "<p>Tips for generating natural dialogue with AI.</p>",
    excerpt: "How to craft prompts that yield realistic character conversations.",
    featured_image_url: null,
    status: "published",
    author_id: 7,
    view_count: 340,
    like_count: 18,
    comment_count: 4,
    published_at: "2026-04-22T10:00:00Z",
    created_at: "2026-04-22T08:00:00Z",
    updated_at: "2026-04-22T10:00:00Z",
    app_source: "storytelling",
  },
  {
    id: 4,
    title: "Using Memory Lane with Photos",
    slug: "using-memory-lane-with-photos",
    content: "<p>How to share photos in Memory Lane.</p>",
    excerpt: "A guide to uploading and organizing family photos.",
    featured_image_url: null,
    status: "published",
    author_id: 7,
    view_count: 85,
    like_count: 5,
    comment_count: 1,
    published_at: "2026-04-24T10:00:00Z",
    created_at: "2026-04-24T08:00:00Z",
    updated_at: "2026-04-24T10:00:00Z",
    app_source: "care-circle",
  },
  {
    id: 5,
    title: "Building Fantasy Economies",
    slug: "building-fantasy-economies",
    content: "<p>Trade, currency, and resource systems in world building.</p>",
    excerpt: "Designing believable economic systems for your fantasy world.",
    featured_image_url: null,
    status: "published",
    author_id: 7,
    view_count: 520,
    like_count: 31,
    comment_count: 7,
    published_at: "2026-04-25T10:00:00Z",
    created_at: "2026-04-25T08:00:00Z",
    updated_at: "2026-04-25T10:00:00Z",
    app_source: "storytelling",
  },
  {
    id: 6,
    title: "Care Circle Scheduling Tips",
    slug: "care-circle-scheduling-tips",
    content: "<p>How to set up daily schedules for your circle.</p>",
    excerpt: "Best practices for scheduling care visits and activities.",
    featured_image_url: null,
    status: "published",
    author_id: 7,
    view_count: 200,
    like_count: 12,
    comment_count: 3,
    published_at: "2026-04-26T10:00:00Z",
    created_at: "2026-04-26T08:00:00Z",
    updated_at: "2026-04-26T10:00:00Z",
    app_source: "care-circle",
  },
  {
    id: 7,
    title: "Character Voice Worksheets",
    slug: "character-voice-worksheets",
    content: "<p>Downloadable worksheets for developing character voice.</p>",
    excerpt: "Free worksheets to help define how your characters speak.",
    featured_image_url: null,
    status: "published",
    author_id: 7,
    view_count: 410,
    like_count: 24,
    comment_count: 5,
    published_at: "2026-04-27T10:00:00Z",
    created_at: "2026-04-27T08:00:00Z",
    updated_at: "2026-04-27T10:00:00Z",
    app_source: "storytelling",
  },
  {
    id: 8,
    title: "Writing Rituals That Stick",
    slug: "writing-rituals-that-stick",
    content: "<p>Building a consistent writing practice.</p>",
    excerpt: "How to create writing habits that last.",
    featured_image_url: null,
    status: "published",
    author_id: 7,
    view_count: 670,
    like_count: 45,
    comment_count: 9,
    published_at: "2026-04-28T10:00:00Z",
    created_at: "2026-04-28T08:00:00Z",
    updated_at: "2026-04-28T10:00:00Z",
    app_source: "storytelling",
  },
];

const adminFamiliesSeed = [
  {
    id: 11,
    name: "Story Maker household",
    join_code: "STM111",
    is_disabled: false,
    owner_username: "storymaker",
    owner_display_name: "Story Maker",
    member_count: 3,
    patient_count: 2,
    pending_requests: 1,
    created_at: "2026-04-24T18:00:00Z"
  },
  {
    id: 12,
    name: "Arthur's Circle",
    join_code: "ART222",
    is_disabled: true,
    owner_username: "arthur_admin",
    owner_display_name: "Arthur Admin",
    member_count: 2,
    patient_count: 1,
    pending_requests: 0,
    created_at: "2026-04-23T18:00:00Z"
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

const schedulerHealth = {
  status: "healthy",
  scheduler_running: true,
  registered_tasks: 7,
  scheduled_jobs: 7
};

const schedulerStatus = {
  tasks: [
    {
      key: "care_circle.precache_providers",
      name: "Provider Output Pre-cache",
      cron: "0 2 * * *",
      next_run: "2026-04-25T02:00:00Z",
      is_running: true
    },
    {
      key: "care_circle.daily_session",
      name: "Daily Session Pre-generation",
      cron: "0 6 * * *",
      next_run: "2026-04-25T06:00:00Z",
      is_running: true
    },
    {
      key: "care_circle.daily_newsletter",
      name: "Daily Care Circle Newsletter",
      cron: "0 8 * * *",
      next_run: "2026-04-25T08:00:00Z",
      is_running: true
    }
  ]
};

const schedulerJobs = {
  jobs: [
    {
      id: "care_circle.precache_providers",
      name: "Provider Output Pre-cache",
      next_run: "2026-04-25T02:00:00Z",
      trigger: "cron[hour='2', minute='0']"
    },
    {
      id: "care_circle.daily_session",
      name: "Daily Session Pre-generation",
      next_run: "2026-04-25T06:00:00Z",
      trigger: "cron[hour='6', minute='0']"
    }
  ]
};

const templateInventory = {
  providers: [
    { name: "weather", label: "Weather", icon: "⛅", order: 1, enabled: true },
    { name: "joke", label: "Daily Joy", icon: "😄", order: 2, enabled: true },
  ],
  themes: ["classic"],
};

const templateDocument = {
  providerKey: "weather",
  label: "Weather",
  theme: "classic",
  templateHtml: "<div>Weather template</div>",
  providerThemeCss: "body { color: blue; }",
  sharedThemeCss: "body { background: white; }",
  availableThemes: ["classic"],
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
  let adminFamilies = adminFamiliesSeed.map((family) => ({ ...family }));
  let careCircleMedia = careCircleMediaSeed.map((item) => ({ ...item, aspect_ratio_urls: { ...(item.aspect_ratio_urls ?? {}) } }));
  let publishedStories: any[] = publishedStoriesSeed.map((story) => ({ ...story }));
  let publishedStoryComments = Object.fromEntries(
    Object.entries(publishedStoryCommentsSeed).map(([storyId, comments]) => [
      Number(storyId),
      comments.map((comment) => ({ ...comment })),
    ])
  ) as Record<number, PublishedStoryCommentSeed[]>;

  let mutableForumThreads: any[] = forumThreadsSeed.map((t) => ({
    ...t,
    posts: t.posts.map((p) => ({ ...p })),
  }));
  let mutableBlogPosts: any[] = blogPostsSeed.map((p) => ({ ...p }));
  let mutableAuthorBlogPosts: any[] = authorBlogPostsSeed.map((p) => ({ ...p }));

  let mutableChatbotSession = {
    ...chatbotSessionWithMessages,
    messages: chatbotSessionWithMessages.messages.map((m: any) => ({ ...m })),
  };
  let mutableChatbotSessions: any[] = chatbotSessionsSeed.map((s) => ({ ...s }));
  const mutableChatbotMessages: Record<number, any[]> = {};

  await page.route("**/api/admin/scheduler/**", async (route) => {
    const url = route.request().url();
    const method = route.request().method();

    if (url.endsWith("/health")) {
      await route.fulfill(json(schedulerHealth));
      return;
    }

    if (url.endsWith("/status")) {
      await route.fulfill(json(schedulerStatus));
      return;
    }

    if (url.endsWith("/jobs") && method === "GET") {
      await route.fulfill(json(schedulerJobs));
      return;
    }

    if (/\/api\/admin\/scheduler\/jobs\/.+\/(run|pause|resume|reschedule)$/.test(url) && method === "POST") {
      const segments = new URL(url).pathname.split("/");
      const action = segments.at(-1) ?? "run";
      const taskKey = segments.at(-2) ?? "unknown";
      await route.fulfill(
        json({
          success: true,
          message: `Task ${taskKey} ${action} completed`,
          task_key: taskKey
        })
      );
      return;
    }

    await route.fallback();
  });

  await page.route("**/api/admin/care-circle/templates**", async (route) => {
    const url = route.request().url();
    const method = route.request().method();

    if (url.endsWith("/api/admin/care-circle/templates") && method === "GET") {
      await route.fulfill(json(templateInventory));
      return;
    }

    const docMatch = url.match(/\/api\/admin\/care-circle\/templates\/([^?]+)/);
    if (docMatch && method === "GET") {
      await route.fulfill(json(templateDocument));
      return;
    }

    if (docMatch && method === "PUT") {
      await route.fulfill(json({ message: "Template saved." }));
      return;
    }

    await route.fallback();
  });

  await page.route("**/api/forum/**", async (route) => {
    const url = route.request().url();
    const method = route.request().method();

    if (url.includes("/api/forum/categories") && method === "GET") {
      const searchParams = new URL(url).searchParams;
      const appSource = searchParams.get("app_source");
      const filtered = appSource
        ? forumCategoriesSeed.filter((c) => c.app_source === appSource)
        : forumCategoriesSeed;
      await route.fulfill(json({ success: true, data: filtered }));
      return;
    }

    const threadDetailMatch = url.match(/\/api\/forum\/threads\/(\d+)$/);
    if (threadDetailMatch && method === "GET") {
      const threadId = Number(threadDetailMatch[1]);
      const thread = mutableForumThreads.find((t) => t.id === threadId);
      if (!thread) {
        await route.fulfill(json({ detail: "Thread not found" }, 404));
        return;
      }
      await route.fulfill(json({ success: true, data: thread }));
      return;
    }

    if (url.includes("/api/forum/threads") && method === "POST") {
      const body = JSON.parse(route.request().postData() ?? "{}") as {
        title?: string;
        category_id?: number;
        initial_post_content?: string;
        app_source?: string;
      };
      const appSource = body.app_source ?? "storytelling";
      const category = forumCategoriesSeed.find((c) => c.id === body.category_id);
      const now = new Date().toISOString();
      const newThread = {
        id: 99,
        title: body.title ?? "New thread",
        slug: "new-thread",
        status: "open",
        category_id: body.category_id ?? 1,
        category_name: category?.name ?? "General",
        user_id: 7,
        username: "storymaker",
        world_id: null,
        world_name: null,
        story_id: null,
        story_title: null,
        view_count: 0,
        post_count: 1,
        last_post_at: now,
        last_post_by_username: "storymaker",
        is_pinned: false,
        is_locked: false,
        created_at: now,
        updated_at: now,
        app_source: appSource,
        posts: [
          {
            id: 999,
            content: body.initial_post_content ?? "",
            content_html: null,
            thread_id: 99,
            user_id: 7,
            username: "storymaker",
            user_display_name: "Story Maker",
            upvote_count: 0,
            downvote_count: 0,
            score: 0,
            edit_count: 0,
            is_deleted: false,
            created_at: now,
            updated_at: now,
          },
        ],
      };
      mutableForumThreads.push(newThread);
      await route.fulfill(json({ success: true, data: newThread }, 201));
      return;
    }

    if (url.includes("/api/forum/threads") && method === "GET") {
      const searchParams = new URL(url).searchParams;
      const appSource = searchParams.get("app_source");
      const filtered = appSource
        ? mutableForumThreads.filter((t) => t.app_source === appSource)
        : mutableForumThreads;
      await route.fulfill(json({ success: true, data: filtered }));
      return;
    }

    if (url.includes("/api/forum/posts") && method === "POST") {
      const body = JSON.parse(route.request().postData() ?? "{}") as {
        thread_id?: number;
        content?: string;
      };
      const newPost = {
        id: 888,
        content: body.content ?? "",
        content_html: null,
        thread_id: body.thread_id ?? 1,
        user_id: 1,
        username: "testuser",
        user_display_name: "Test User",
        upvote_count: 0,
        downvote_count: 0,
        score: 0,
        edit_count: 0,
        is_deleted: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      await route.fulfill(json({ success: true, data: newPost }, 201));
      return;
    }

    await route.fallback();
  });

  await page.route("**/api/blog/search/**", async (route) => {
    const url = route.request().url();
    const searchParams = new URL(url).searchParams;
    const q = searchParams.get("q") ?? "";
    const results = blogPostsSeed.filter(
      (p) => p.title.toLowerCase().includes(q.toLowerCase()) || (p.excerpt ?? "").toLowerCase().includes(q.toLowerCase())
    );
    await route.fulfill(json({ success: true, data: results }));
  });

  await page.route("**/api/blog/posts/**", async (route) => {
    const url = route.request().url();
    const method = route.request().method();

    const pathMatch = url.match(/\/api\/blog\/posts\/([^?]+)$/);
    if (pathMatch && method === "GET") {
      const slug = pathMatch[1];
      const post = blogPostsSeed.find((p) => p.slug === slug);
      if (!post) {
        await route.fulfill(json({ detail: "Blog post not found" }, 404));
        return;
      }
      await route.fulfill(json({ success: true, data: post }));
      return;
    }

    await route.fallback();
  });

  await page.route("**/api/blog/media/**", async (route) => {
    const url = route.request().url();
    const method = route.request().method();

    if (url.endsWith("/api/blog/media/list") && method === "GET") {
      await route.fulfill(json({ success: true, data: careCircleMedia }));
      return;
    }

    if (url.endsWith("/api/blog/media/upload") && method === "POST") {
      const uploaded = {
        id: `media-${careCircleMedia.length + 1}`,
        filename: `7_upload-${careCircleMedia.length + 1}.jpg`,
        storage_path: `7_upload-${careCircleMedia.length + 1}.jpg`,
        original_filename: `upload-${careCircleMedia.length + 1}.jpg`,
        url: `/mock-media/upload-${careCircleMedia.length + 1}.jpg`,
        thumbnail_url: `/mock-media/upload-${careCircleMedia.length + 1}-thumb.jpg`,
        file_type: "image",
        content_type: "image/jpeg",
        file_size: 128000,
        alt_text: "",
        caption: "",
        uploaded_by: 7,
        created_at: "2026-04-28T18:00:00Z",
        width: 1080,
        height: 1080,
        format: "JPEG",
        aspect_ratio_urls: {
          "16x9": `/mock-media/upload-${careCircleMedia.length + 1}-16x9.jpg`,
          "5x4": `/mock-media/upload-${careCircleMedia.length + 1}-5x4.jpg`,
          "1x1": `/mock-media/upload-${careCircleMedia.length + 1}-1x1.jpg`
        }
      };
      careCircleMedia = [uploaded, ...careCircleMedia];
      await route.fulfill(json({ success: true, data: { message: "File uploaded successfully", media: uploaded } }));
      return;
    }

    if (url.includes("/api/blog/media/") && method === "DELETE") {
      const storagePath = decodeURIComponent(url.split("/api/blog/media/")[1] ?? "");
      careCircleMedia = careCircleMedia.filter((item) => item.storage_path !== storagePath);
      await route.fulfill({ status: 204, body: "" });
      return;
    }

    await route.fallback();
  });

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

    if (url.endsWith("/stories/") && method === "GET") {
      await route.fulfill(json({ success: true, data: userStoriesSeed }));
      return;
    }

    const publishedStoryDetailMatch = url.match(/\/published-stories\/(\d+)(?:\/comments|\/rate)?$/);
    if (publishedStoryDetailMatch) {
      const storyId = Number(publishedStoryDetailMatch[1]);
      const story = publishedStories.find((s) => s.id === storyId);

      if (url.endsWith("/comments") && method === "GET") {
        await route.fulfill(json({ success: true, data: publishedStoryComments[storyId] ?? [] }));
        return;
      }

      if (url.endsWith("/comments") && method === "POST") {
        const body = route.request().postDataJSON() as { content?: string };
        const nextComment = {
          id: (publishedStoryComments[storyId]?.length ?? 0) + 1,
          published_story_id: storyId,
          user_id: currentUser.id,
          commenter_username: currentUser.username,
          commenter_display_name: currentUser.display_name,
          content: body.content ?? "",
          is_approved: true,
          created_at: "2026-04-28T19:30:00Z",
          updated_at: "2026-04-28T19:30:00Z"
        };
        publishedStoryComments[storyId] = [...(publishedStoryComments[storyId] ?? []), nextComment];
        publishedStories = publishedStories.map((entry) =>
          entry.id === storyId
            ? {
                ...entry,
                comment_count: (publishedStoryComments[storyId] ?? []).length
              }
            : entry
        );
        await route.fulfill(json({ success: true, data: nextComment }));
        return;
      }

      if (url.endsWith("/rate") && method === "POST") {
        const body = route.request().postDataJSON() as { rating?: number };
        if (!story) {
          await route.fulfill(json({ detail: "Published story not found" }, 404));
          return;
        }
        publishedStories = publishedStories.map((entry) =>
          entry.id === storyId
            ? {
                ...entry,
                has_user_rated: true,
                user_rating: body.rating ?? entry.user_rating,
                average_rating: body.rating ?? entry.average_rating
              }
            : entry
        );
        await route.fulfill(json({ success: true, data: { rating: body.rating ?? null } }));
        return;
      }

      if (method === "GET") {
        const refreshedStory = publishedStories.find((s) => s.id === storyId);
        if (!refreshedStory) {
          await route.fulfill(json({ detail: "Published story not found" }, 404));
          return;
        }
        await route.fulfill(json({ success: true, data: refreshedStory }));
        return;
      }

      if (!story) {
        await route.fulfill(json({ detail: "Published story not found" }, 404));
        return;
      }
    }

    if (url.includes("/published-stories/") && method === "GET") {
      const searchParams = new URL(url).searchParams;
      const page = Number(searchParams.get("page") ?? "1");
      const perPage = Number(searchParams.get("per_page") ?? "20");
      await route.fulfill(json({
        success: true,
        data: { stories: publishedStories, total: publishedStories.length, page, per_page: perPage }
      }));
      return;
    }

    if (url.endsWith("/worlds/") && method === "GET") {
      await route.fulfill(json({ success: true, data: userWorldsSeed }));
      return;
    }

    const worldDetailMatch = url.match(/\/worlds\/(\d+)$/);
    if (worldDetailMatch && method === "GET") {
      const worldId = Number(worldDetailMatch[1]);
      const world = userWorldsSeed.find((w) => w.id === worldId);
      if (!world) {
        await route.fulfill(json({ detail: "World not found" }, 404));
        return;
      }
      await route.fulfill(json({ success: true, data: { ...world, user_id: 7, description: world.short_description } }));
      return;
    }

    if (url.endsWith("/care-circle/family/patients")) {
      await route.fulfill(json({ success: true, data: careCirclePatients }));
      return;
    }

    if (url.endsWith("/care-circle/family/events")) {
      await route.fulfill(json({ success: true, data: careCircleActivityEvents }));
      return;
    }

    if (url.endsWith("/care-circle/family/owner-summary")) {
      await route.fulfill(
        json({
          success: true,
          data: {
            id: 11,
            name: "Story Maker household",
            join_code: "STM111",
            active_member_count: 3,
            pending_request_count: 1
          }
        })
      );
      return;
    }

    if (url.endsWith("/care-circle/admin/families") && method === "GET") {
      await route.fulfill(json({ success: true, data: adminFamilies }));
      return;
    }

    if (/\/care-circle\/admin\/families\/\d+\/disable$/.test(url) && method === "PUT") {
      const familyId = Number(url.split("/").slice(-2)[0]);
      const body = route.request().postDataJSON() as { disabled?: boolean };
      adminFamilies = adminFamilies.map((family) =>
        family.id === familyId ? { ...family, is_disabled: Boolean(body.disabled) } : family
      );
      const family = adminFamilies.find((entry) => entry.id === familyId);
      await route.fulfill(json({ success: true, data: { id: familyId, is_disabled: family?.is_disabled ?? false } }));
      return;
    }

    if (/\/care-circle\/admin\/families\/\d+$/.test(url) && method === "DELETE") {
      const familyId = Number(url.split("/").pop());
      adminFamilies = adminFamilies.filter((family) => family.id !== familyId);
      await route.fulfill(json({ success: true, data: { message: "Family deleted" } }));
      return;
    }

    if (url.endsWith("/care-circle/family/invite-email") && method === "POST") {
      const body = route.request().postDataJSON() as { email?: string };
      await route.fulfill(
        json({
          success: true,
          data: {
            sent: true,
            email: body.email ?? "family.member@example.com",
            join_code: "STM111"
          }
        }, 201)
      );
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
            detail: "Those pictures did not match an active patient profile."
          },
          401
        )
      );
      return;
    }

    if (/\/care-circle\/patient\/session\/\d+\/provider-feedback\/[^/]+$/.test(url) && method === "PUT") {
      const parts = url.split("/");
      const providerKey = parts.at(-1) ?? "";
      const patientId = parts.at(-3) ?? "";
      const body = route.request().postDataJSON() as { feedback?: "like" | "dislike" | null };
      const patient = careCirclePatients.find((entry: any) => entry.id === patientId && entry.accessState !== "archived");
      const highlight = patient?.highlights?.find((entry: any) => entry.providerKey === providerKey);

      if (!patient || !highlight) {
        await route.fulfill(json({ detail: "Patient session not found" }, 404));
        return;
      }

      highlight.feedback = body.feedback ?? null;
      await route.fulfill(
        json({
          success: true,
          data: {
            patient_id: Number(patientId),
            provider_key: providerKey,
            feedback: highlight.feedback
          }
        })
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

    if (url.match(/\/api\/v1\/billing\/dashboard$/)) {
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

    if (url.endsWith("/referrals")) {
      if (referrals === "error") {
        await route.fulfill(json({ success: false, error: { message: "Referral stats failed" } }, 500));
        return;
      }

      await route.fulfill(
        json({
          success: true,
          data: {
            referral_code: "STORY123",
            referral_url: "https://inkandquill.example/join?ref=STORY123",
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

    // Sprint 11 — Chatbot sessions
    const chatSessionDetailMatch = url.match(/\/chatbot\/sessions\/(\d+)$/);
    const chatMessageMatch = url.match(/\/chatbot\/sessions\/(\d+)\/messages/);

    if (url.includes("/chatbot/sessions") && method === "GET" && !chatSessionDetailMatch) {
      await route.fulfill(json({ success: true, data: mutableChatbotSessions }));
      return;
    }

    if (chatSessionDetailMatch && method === "GET") {
      const id = Number(chatSessionDetailMatch[1]);
      if (id === mutableChatbotSession.id) {
        await route.fulfill(json({ success: true, data: mutableChatbotSession }));
      } else {
        const session = mutableChatbotSessions.find((s) => s.id === id);
        if (session) {
          await route.fulfill(json({ success: true, data: { ...session, messages: mutableChatbotMessages[id] ?? [] } }));
        } else {
          await route.fulfill(json({ detail: "Session not found" }, 404));
        }
      }
      return;
    }

    if (url.includes("/chatbot/sessions") && method === "POST" && !chatMessageMatch) {
      const body = JSON.parse(route.request().postData() ?? "{}") as { title?: string };
      const created = { id: 99, user_id: 7, title: body.title ?? "New conversation", created_at: new Date().toISOString(), updated_at: new Date().toISOString() };
      mutableChatbotSessions.push(created);
      await route.fulfill(json({ success: true, data: created }, 201));
      return;
    }

    if (chatMessageMatch && method === "POST") {
      const sessionId = Number(chatMessageMatch[1]);
      const body = JSON.parse(route.request().postData() ?? "{}") as { message?: string };
      const userMsg = { id: 800, session_id: sessionId, role: "user", content: body.message ?? "", input_tokens: null, output_tokens: null, cost_usd: null, model_name: null, created_at: new Date().toISOString() };
      const aiMsg = { id: 801, session_id: sessionId, role: "assistant", content: "Understood. Here is a helpful response.", input_tokens: 50, output_tokens: 30, cost_usd: 0.0004, model_name: "gpt-4o", created_at: new Date().toISOString() };
      if (sessionId === mutableChatbotSession.id) {
        mutableChatbotSession.messages.push(userMsg, aiMsg);
      } else {
        mutableChatbotMessages[sessionId] = [...(mutableChatbotMessages[sessionId] ?? []), userMsg, aiMsg];
      }
      await new Promise((r) => setTimeout(r, 400));
      await route.fulfill(json({ success: true, data: { user_message: userMsg, ai_message: aiMsg, input_tokens: 50, output_tokens: 30, cost_usd: 0.0004, model_name: "gpt-4o" } }));
      return;
    }

    if (chatSessionDetailMatch && method === "DELETE") {
      const id = Number(chatSessionDetailMatch[1]);
      mutableChatbotSessions = mutableChatbotSessions.filter((s) => s.id !== id);
      if (id === mutableChatbotSession.id) {
        mutableChatbotSession.messages = [];
      }
      delete mutableChatbotMessages[id];
      await route.fulfill({ status: 204 });
      return;
    }

    if (chatSessionDetailMatch && method === "PUT") {
      const body = JSON.parse(route.request().postData() ?? "{}") as { title?: string };
      const id = Number(chatSessionDetailMatch[1]);
      const idx = mutableChatbotSessions.findIndex((x) => x.id === id);
      if (idx !== -1) {
        mutableChatbotSessions[idx] = { ...mutableChatbotSessions[idx], title: body.title ?? mutableChatbotSessions[idx].title };
      }
      const s = mutableChatbotSessions.find((x) => x.id === id) ?? mutableChatbotSessions[0];
      await route.fulfill(json({ success: true, data: s }));
      return;
    }

    // Sprint 10 — Prompts
    if (url.includes("/prompts/my-prompts") && method === "GET") {
      await route.fulfill(json({ success: true, data: promptsSeed }));
      return;
    }

    if (url.includes("/prompts/shared") && method === "GET") {
      await route.fulfill(json({ success: true, data: [] }));
      return;
    }

    if (url.includes("/prompts/") && method === "POST") {
      const body = JSON.parse(route.request().postData() ?? "{}") as { title?: string; prompt_content?: string; prompt_type?: string };
      const newPrompt = {
        ...promptsSeed[0],
        id: 99,
        title: body.title ?? "New prompt",
        prompt_content: body.prompt_content ?? "",
        prompt_type: body.prompt_type ?? "GENERAL",
      };
      await route.fulfill(json({ success: true, data: newPrompt }, 201));
      return;
    }

    if (url.match(/\/prompts\/\d+/) && method === "DELETE") {
      await route.fulfill({ status: 204 });
      return;
    }

    // Sprint 10 — LLM models
    if (url.includes("/llm-models/") && method === "GET") {
      await route.fulfill(json({ success: true, data: llmModelsSeed }));
      return;
    }

    // Sprint 12 — Admin users
    if (url.includes("/users/") && url.includes("toggle-active") && method === "PATCH") {
      const idMatch = url.match(/\/users\/(\d+)\/toggle-active/);
      const userId = idMatch ? Number(idMatch[1]) : 0;
      const user = adminUsersSeed.find((u) => u.id === userId) ?? adminUsersSeed[1];
      await route.fulfill(json({ success: true, data: { ...user, is_active: !user.is_active } }));
      return;
    }

    if (url.includes("/users/") && method === "GET" && !url.includes("/users/me")) {
      await route.fulfill(json({ success: true, data: adminUsersSeed }));
      return;
    }

    // Sprint 12 — Admin billing
    if (url.includes("/admin/billing/dashboard") && method === "GET") {
      await route.fulfill(json({ success: true, data: adminBillingDashboardSeed }));
      return;
    }

    if (url.includes("/admin/billing/adjust-credits") && method === "POST") {
      await route.fulfill(json({ success: true, data: { success: true, message: "Credits adjusted successfully", transaction_id: 999 } }));
      return;
    }

    // Sprint 12 — Maintenance enable/disable
    if (url.includes("/maintenance/enable") && method === "POST") {
      await route.fulfill(json({ success: true, data: { status: "Maintenance mode enabled", message: "Scheduled maintenance" } }));
      return;
    }

    if (url.includes("/maintenance/disable") && method === "POST") {
      await route.fulfill(json({ success: true, data: { status: "Maintenance mode disabled" } }));
      return;
    }

    // Sprint 12 — Admin CTA
    if (url.includes("/admin/cta-content") && url.includes("toggle-active") && method === "POST") {
      const idMatch = url.match(/\/admin\/cta-content\/(\d+)\/toggle-active/);
      const ctaId = idMatch ? Number(idMatch[1]) : 0;
      const cta = adminCTASeed.find((c) => c.id === ctaId) ?? adminCTASeed[0];
      await route.fulfill(json({ success: true, data: { is_active: !cta.is_active, message: "CTA toggled" } }));
      return;
    }

    if (url.match(/\/admin\/cta-content\/\d+/) && method === "DELETE") {
      await route.fulfill(json({ success: true, data: { message: "CTA deleted successfully" } }));
      return;
    }

    if (url.includes("/admin/cta-content") && method === "GET") {
      await route.fulfill(json({ success: true, data: adminCTASeed }));
      return;
    }

    await route.fallback();
  });

  // Sprint 10 — Blog authoring routes (same-origin /api/blog/posts with author_id filter)
  // Also handles public blog listings (app_source filter).
  await page.route("**/api/blog/posts**", async (route) => {
    const url = route.request().url();
    const method = route.request().method();

    const postIdMatch = url.match(/\/api\/blog\/posts\/(\d+)/);
    const slugMatch = url.match(/\/api\/blog\/posts\/([^/?]+)/);
    const urlObj = new URL(url);
    const hasAuthorId = urlObj.searchParams.has("author_id");

    if (method === "GET" && !postIdMatch && !slugMatch) {
      if (hasAuthorId) {
        const authorPosts =
          options.authorBlogPosts === "empty" ? [] : mutableAuthorBlogPosts;
        await route.fulfill(json({ success: true, data: authorPosts }));
        return;
      }
      const search = urlObj.searchParams.get("search");
      const appSource = urlObj.searchParams.get("app_source");
      let posts = options.blogPosts === "empty" ? [] : mutableBlogPosts;
      if (appSource) {
        posts = posts.filter((p) => p.app_source === appSource);
      }
      if (search) {
        posts = posts.filter((p) => p.title.toLowerCase().includes(search.toLowerCase()));
      }
      await route.fulfill(json({ success: true, data: posts }));
      return;
    }

    if (method === "GET" && postIdMatch) {
      const id = Number(postIdMatch[1]);
      const found = mutableAuthorBlogPosts.find((p) => p.id === id);
      if (found) {
        await route.fulfill(json({ success: true, data: found }));
      } else {
        await route.fulfill(json({ detail: "Not found" }, 404));
      }
      return;
    }

    if (method === "POST" && !postIdMatch) {
      const body = JSON.parse(route.request().postData() ?? "{}") as { title?: string; content?: string; status?: string; app_source?: string };
      const created = { ...authorBlogPostsSeed[0], id: 299, title: body.title ?? "New post", status: body.status ?? "draft", app_source: body.app_source ?? "storytelling" };
      mutableBlogPosts.unshift(created);
      mutableAuthorBlogPosts.unshift(created);
      await route.fulfill(json({ success: true, data: created }, 201));
      return;
    }

    if (method === "PUT" && postIdMatch) {
      const id = Number(postIdMatch[1]);
      const base = mutableAuthorBlogPosts.find((p) => p.id === id) ?? authorBlogPostsSeed[0];
      const body = JSON.parse(route.request().postData() ?? "{}") as Partial<typeof base>;
      await route.fulfill(json({ success: true, data: { ...base, ...body } }));
      return;
    }

    if (method === "DELETE" && postIdMatch) {
      await route.fulfill({ status: 204 });
      return;
    }

    await route.fallback();
  });

  await page.route("**/api/blog/posts/*/publish", async (route) => {
    if (route.request().method() !== "POST") { await route.fallback(); return; }
    const url = route.request().url();
    const match = url.match(/\/api\/blog\/posts\/(\d+)\/publish/);
    const id = match ? Number(match[1]) : 0;
    const base = mutableAuthorBlogPosts.find((p) => p.id === id) ?? authorBlogPostsSeed[0];
    await route.fulfill(json({ success: true, data: { ...base, status: "published" } }));
  });
}
