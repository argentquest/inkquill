/* SVG icons for every Care Circle provider_key.
   Each icon uses the same inline-SVG pattern as care-circle-feature-icons.tsx:
   explicit hex colours, 56×56 viewBox, fill washes + stroked geometry. */

function ComicIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="6" width="44" height="32" rx="6" fill="#6366f1" opacity="0.12" stroke="#6366f1" strokeWidth="2.5" />
      <line x1="6" y1="22" x2="50" y2="22" stroke="#6366f1" strokeWidth="1.5" opacity="0.35" />
      <line x1="28" y1="6" x2="28" y2="38" stroke="#6366f1" strokeWidth="1.5" opacity="0.35" />
      <path d="M14 44l6-6h10" stroke="#8b5cf6" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="16" cy="16" r="3" fill="#8b5cf6" opacity="0.5" />
      <circle cx="38" cy="28" r="4" fill="#6366f1" opacity="0.4" />
    </svg>
  );
}

function AnimalIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="28" cy="30" r="14" fill="#0d9488" opacity="0.12" stroke="#0d9488" strokeWidth="2.5" />
      <circle cx="20" cy="18" r="5" fill="#0d9488" opacity="0.25" stroke="#0d9488" strokeWidth="2" />
      <circle cx="36" cy="18" r="5" fill="#0d9488" opacity="0.25" stroke="#0d9488" strokeWidth="2" />
      <path d="M21 30c0-3.9 3.1-7 7-7s7 3.1 7 7" fill="#f97316" opacity="0.2" />
      <circle cx="22" cy="32" r="3" fill="#0d9488" />
      <circle cx="34" cy="32" r="3" fill="#0d9488" />
      <circle cx="28" cy="36" r="2.5" fill="#f97316" />
    </svg>
  );
}

function NatureIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="28" cy="24" r="16" fill="#059669" opacity="0.12" stroke="#059669" strokeWidth="2.5" />
      <path d="M28 44V28" stroke="#059669" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M28 34c-6 0-10-4-10-10 6 0 10 4 10 10z" fill="#10b981" opacity="0.3" stroke="#059669" strokeWidth="2" strokeLinejoin="round" />
      <path d="M28 30c6 0 10-4 10-10-6 0-10 4-10 10z" fill="#10b981" opacity="0.3" stroke="#059669" strokeWidth="2" strokeLinejoin="round" />
      <circle cx="28" cy="18" r="5" fill="#f59e0b" opacity="0.5" />
    </svg>
  );
}

function WeatherIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="24" cy="22" r="10" fill="#f59e0b" opacity="0.18" stroke="#f59e0b" strokeWidth="2.5" />
      <path d="M24 10v-4M24 38v-4M10 24H6M42 24h-4M14.1 13.1l-2.8-2.8M36.7 35.7l-2.8-2.8M14.1 34.9l-2.8 2.8M36.7 12.3l-2.8 2.8" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round" />
      <circle cx="34" cy="34" r="10" fill="#60a5fa" opacity="0.2" stroke="#3b82f6" strokeWidth="2.5" />
      <path d="M26 40c0-4.4 3.6-8 8-8s8 3.6 8 8" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function PuzzleIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="8" y="8" width="16" height="16" rx="3" fill="#f59e0b" opacity="0.2" stroke="#f59e0b" strokeWidth="2.5" />
      <rect x="32" y="8" width="16" height="16" rx="3" fill="#d86c3d" opacity="0.18" stroke="#d86c3d" strokeWidth="2.5" />
      <rect x="8" y="32" width="16" height="16" rx="3" fill="#d86c3d" opacity="0.18" stroke="#d86c3d" strokeWidth="2.5" />
      <rect x="32" y="32" width="16" height="16" rx="3" fill="#f59e0b" opacity="0.2" stroke="#f59e0b" strokeWidth="2.5" />
      <circle cx="28" cy="28" r="4" fill="#1f3b36" opacity="0.25" />
    </svg>
  );
}

function WordIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="12" width="44" height="32" rx="6" fill="#0891b2" opacity="0.1" stroke="#0891b2" strokeWidth="2.5" />
      <text x="12" y="32" fontFamily="Georgia, serif" fontSize="14" fontWeight="700" fill="#0891b2" opacity="0.8">A</text>
      <text x="24" y="32" fontFamily="Georgia, serif" fontSize="14" fontWeight="700" fill="#0891b2" opacity="0.55">B</text>
      <text x="36" y="32" fontFamily="Georgia, serif" fontSize="14" fontWeight="700" fill="#0891b2" opacity="0.35">C</text>
      <line x1="12" y1="38" x2="44" y2="38" stroke="#0891b2" strokeWidth="1.5" opacity="0.3" strokeLinecap="round" />
    </svg>
  );
}

function BrainIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M28 8c-8.8 0-16 7.2-16 16 0 5.5 2.8 10.4 7 13.3V44h18v-6.7c4.2-2.9 7-7.8 7-13.3 0-8.8-7.2-16-16-16z" fill="#7c3aed" opacity="0.1" stroke="#7c3aed" strokeWidth="2.5" strokeLinejoin="round" />
      <path d="M22 24c0-3.3 2.7-6 6-6" stroke="#7c3aed" strokeWidth="2" strokeLinecap="round" opacity="0.6" />
      <circle cx="28" cy="22" r="2.5" fill="#f59e0b" />
      <path d="M20 44h16" stroke="#7c3aed" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}

function WellnessIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="28" cy="28" r="20" fill="#f43f5e" opacity="0.08" stroke="#f43f5e" strokeWidth="2.5" />
      <path d="M28 38s-12-7-12-16a8 8 0 0 1 12-6.9A8 8 0 0 1 40 22c0 9-12 16-12 16z" fill="#f43f5e" opacity="0.2" stroke="#f43f5e" strokeWidth="2.5" strokeLinejoin="round" />
      <circle cx="28" cy="22" r="3" fill="#f59e0b" />
    </svg>
  );
}

function QuoteIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="10" width="44" height="36" rx="6" fill="#1f3b36" opacity="0.08" stroke="#1f3b36" strokeWidth="2.5" />
      <path d="M16 28c0-4 2.5-7 6-8v4c-1.5 0.5-2.5 2-2.5 4v4H16v-4z" fill="#1f3b36" opacity="0.4" />
      <path d="M28 28c0-4 2.5-7 6-8v4c-1.5 0.5-2.5 2-2.5 4v4H28v-4z" fill="#1f3b36" opacity="0.4" />
      <line x1="16" y1="38" x2="40" y2="38" stroke="#d86c3d" strokeWidth="2" strokeLinecap="round" opacity="0.5" />
    </svg>
  );
}

function MusicIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="10" width="44" height="36" rx="6" fill="#7c3aed" opacity="0.1" stroke="#7c3aed" strokeWidth="2.5" />
      <path d="M22 38V20l20-4v18" stroke="#7c3aed" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="18" cy="38" r="4" fill="#7c3aed" opacity="0.4" stroke="#7c3aed" strokeWidth="2" />
      <circle cx="38" cy="34" r="4" fill="#7c3aed" opacity="0.4" stroke="#7c3aed" strokeWidth="2" />
    </svg>
  );
}

function ArtIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="8" y="8" width="40" height="34" rx="5" fill="#d97706" opacity="0.1" stroke="#d97706" strokeWidth="2.5" />
      <rect x="14" y="14" width="28" height="22" rx="3" fill="#d97706" opacity="0.1" />
      <path d="M14 30l10-10 8 8 6-6 8 8" stroke="#d86c3d" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="20" cy="20" r="3" fill="#f59e0b" />
      <line x1="14" y1="46" x2="42" y2="46" stroke="#d97706" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}

function FamilyLetterIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="14" width="44" height="32" rx="5" fill="#d86c3d" opacity="0.12" stroke="#d86c3d" strokeWidth="2.5" />
      <path d="M6 19l22 14 22-14" stroke="#d86c3d" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="28" cy="10" r="5" fill="#1f3b36" opacity="0.2" stroke="#1f3b36" strokeWidth="2" />
    </svg>
  );
}

function ActivityIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="28" cy="14" r="6" fill="#0891b2" opacity="0.25" stroke="#0891b2" strokeWidth="2.5" />
      <path d="M28 20v16" stroke="#0891b2" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M16 28h24" stroke="#0891b2" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M20 36l8 10 8-10" stroke="#0891b2" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="42" cy="28" r="4" fill="#f59e0b" opacity="0.5" />
    </svg>
  );
}

function RecipeIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 22c0-8.8 7.2-16 18-16s18 7.2 18 16H10z" fill="#059669" opacity="0.15" stroke="#059669" strokeWidth="2.5" strokeLinejoin="round" />
      <rect x="10" y="22" width="36" height="22" rx="4" fill="#059669" opacity="0.1" stroke="#059669" strokeWidth="2.5" />
      <line x1="28" y1="22" x2="28" y2="44" stroke="#059669" strokeWidth="2" opacity="0.4" />
      <path d="M18 32h8M30 32h8" stroke="#f59e0b" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}

function HistoryIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="28" cy="28" r="20" fill="#92400e" opacity="0.08" stroke="#92400e" strokeWidth="2.5" />
      <circle cx="28" cy="28" r="14" fill="#92400e" opacity="0.06" stroke="#d97706" strokeWidth="2" />
      <path d="M28 16v12l8 4" stroke="#d97706" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="28" cy="28" r="2" fill="#d97706" />
    </svg>
  );
}

function NewsIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 8h28l8 8v32a4 4 0 0 1-4 4H10a4 4 0 0 1-4-4V12a4 4 0 0 1 4-4z" fill="#2563eb" opacity="0.1" stroke="#2563eb" strokeWidth="2.5" />
      <path d="M38 8v8h8" stroke="#2563eb" strokeWidth="2.5" strokeLinejoin="round" />
      <line x1="16" y1="26" x2="40" y2="26" stroke="#2563eb" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="16" y1="34" x2="32" y2="34" stroke="#2563eb" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="16" y1="42" x2="28" y2="42" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function NewsletterLayoutIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="6" width="44" height="44" rx="6" fill="#231913" opacity="0.06" stroke="#231913" strokeWidth="2.5" opacity="0.2" />
      <rect x="12" y="12" width="32" height="8" rx="2" fill="#d86c3d" opacity="0.3" stroke="#d86c3d" strokeWidth="2" />
      <line x1="12" y1="26" x2="44" y2="26" stroke="#635048" strokeWidth="2" strokeLinecap="round" opacity="0.4" />
      <line x1="12" y1="32" x2="38" y2="32" stroke="#635048" strokeWidth="2" strokeLinecap="round" opacity="0.3" />
      <line x1="12" y1="38" x2="30" y2="38" stroke="#635048" strokeWidth="2" strokeLinecap="round" opacity="0.25" />
      <rect x="12" y="42" width="32" height="6" rx="2" fill="#d86c3d" opacity="0.2" stroke="#d86c3d" strokeWidth="1.5" />
    </svg>
  );
}

function JokeIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="28" cy="28" r="20" fill="#f59e0b" opacity="0.12" stroke="#f59e0b" strokeWidth="2.5" />
      <circle cx="22" cy="24" r="3" fill="#f59e0b" />
      <circle cx="34" cy="24" r="3" fill="#f59e0b" />
      <path d="M18 34c2 4 6 6 10 6s8-2 10-6" stroke="#f59e0b" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}

function BingoIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="8" y="8" width="40" height="40" rx="5" fill="#e11d48" opacity="0.08" stroke="#e11d48" strokeWidth="2.5" />
      <line x1="8" y1="21" x2="48" y2="21" stroke="#e11d48" strokeWidth="1.5" opacity="0.35" />
      <line x1="8" y1="34" x2="48" y2="34" stroke="#e11d48" strokeWidth="1.5" opacity="0.35" />
      <line x1="21" y1="8" x2="21" y2="48" stroke="#e11d48" strokeWidth="1.5" opacity="0.35" />
      <line x1="34" y1="8" x2="34" y2="48" stroke="#e11d48" strokeWidth="1.5" opacity="0.35" />
      <circle cx="14" cy="14" r="3.5" fill="#e11d48" opacity="0.5" />
      <circle cx="28" cy="28" r="4.5" fill="#e11d48" />
      <circle cx="42" cy="14" r="3.5" fill="#e11d48" opacity="0.5" />
      <circle cx="42" cy="42" r="3.5" fill="#e11d48" opacity="0.5" />
      <circle cx="14" cy="42" r="3.5" fill="#e11d48" opacity="0.5" />
    </svg>
  );
}

function ColorMatchIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="20" cy="22" r="12" fill="#f43f5e" opacity="0.25" />
      <circle cx="36" cy="22" r="12" fill="#2563eb" opacity="0.25" />
      <circle cx="28" cy="36" r="12" fill="#f59e0b" opacity="0.25" />
      <path d="M24 22c1.2-2 3.6-3.3 6-2.8 2.4.5 4.2 2.5 4.5 5-1.2 2-3.6 3.3-6 2.8-2.4-.5-4.2-2.5-4.5-5z" fill="#9333ea" opacity="0.5" />
    </svg>
  );
}

function MemoryPhotoIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="12" width="44" height="34" rx="5" fill="#92400e" opacity="0.1" stroke="#92400e" strokeWidth="2.5" />
      <circle cx="28" cy="28" r="9" fill="#92400e" opacity="0.15" stroke="#d97706" strokeWidth="2.5" />
      <circle cx="28" cy="28" r="4" fill="#d97706" />
      <circle cx="18" cy="18" r="2.5" fill="#f59e0b" opacity="0.6" />
      <path d="M6 38l12-12 8 8 6-6 14 16" stroke="#d97706" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" opacity="0.4" />
    </svg>
  );
}

function GratitudeIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M28 46s-18-10-18-24a10 10 0 0 1 18-6 10 10 0 0 1 18 6c0 14-18 24-18 24z" fill="#10b981" opacity="0.15" stroke="#10b981" strokeWidth="2.5" strokeLinejoin="round" />
      <path d="M20 26l4 4 8-8" stroke="#10b981" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function SpotDifferenceIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="4" y="12" width="22" height="32" rx="4" fill="#6366f1" opacity="0.1" stroke="#6366f1" strokeWidth="2.5" />
      <rect x="30" y="12" width="22" height="32" rx="4" fill="#6366f1" opacity="0.1" stroke="#6366f1" strokeWidth="2.5" />
      <circle cx="15" cy="28" r="5" fill="#6366f1" opacity="0.3" stroke="#6366f1" strokeWidth="2" />
      <circle cx="41" cy="28" r="5" fill="#f43f5e" opacity="0.45" stroke="#f43f5e" strokeWidth="2.5" />
      <path d="M26 28h4" stroke="#6366f1" strokeWidth="2" strokeLinecap="round" strokeDasharray="2 2" />
    </svg>
  );
}

function DefaultProviderIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="10" y="6" width="36" height="44" rx="5" fill="#a87a42" opacity="0.1" stroke="#a87a42" strokeWidth="2.5" />
      <line x1="18" y1="20" x2="38" y2="20" stroke="#a87a42" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="18" y1="28" x2="38" y2="28" stroke="#a87a42" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="18" y1="36" x2="30" y2="36" stroke="#a87a42" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}

// ── Lookup map ────────────────────────────────────────────────────────────────

const ICON_MAP: Record<string, (props: { className?: string }) => React.ReactElement> = {
  // Comics
  comic_abe_martin:          ComicIcon,
  comic_ascii:               ComicIcon,
  comic_brownies:            ComicIcon,
  comic_buster_brown:        ComicIcon,
  comic_dino_cartoons:       ComicIcon,
  comic_dream_rarebit_fiend: ComicIcon,
  comic_gasoline_alley:      ComicIcon,
  comic_happy_hooligan:      ComicIcon,
  comic_little_nemo:         ComicIcon,
  comic_moose_lake:          ComicIcon,
  comic_mr_skygack:          ComicIcon,
  comic_pepper_carrot:       ComicIcon,
  comic_polly_and_her_pals:  ComicIcon,
  comic_wuffle:              ComicIcon,

  // Animals
  animal_friend: AnimalIcon,
  cat_fact:      AnimalIcon,
  dog_photo:     AnimalIcon,

  // Nature / outdoor
  nature_park:  NatureIcon,
  nature_scene: NatureIcon,
  weather:      WeatherIcon,
  seasonal_poem: NatureIcon,

  // Puzzles / grids
  bingo:           BingoIcon,
  color_match:     ColorMatchIcon,
  gridless_crossword: PuzzleIcon,
  number_sequence:   PuzzleIcon,
  odd_one_out:       PuzzleIcon,
  puzzle:            PuzzleIcon,
  simple_math:       BrainIcon,
  spot_the_difference: SpotDifferenceIcon,

  // Word games
  complete_the_duo:  WordIcon,
  finish_phrase:     WordIcon,
  missing_vowels:    WordIcon,
  old_saying_match:  WordIcon,
  word_connect:      WordIcon,
  word_of_the_day:   WordIcon,
  word_scramble:     WordIcon,

  // Brain / trivia
  ai_trivia:     BrainIcon,
  brain_booster: BrainIcon,
  riddle:        BrainIcon,

  // Wellness / mindfulness
  daily_affirmation:   WellnessIcon,
  daily_blessing:      WellnessIcon,
  gentle_exercise:     ActivityIcon,
  mindful_moment:      WellnessIcon,
  morning_stretch:     ActivityIcon,
  personal_affirmation: WellnessIcon,
  sensory:             WellnessIcon,

  // Quotes & reflection
  daily_quote: QuoteIcon,
  gratitude:   GratitudeIcon,

  // Music / arts
  classic_art:      ArtIcon,
  famous_face:      ArtIcon,
  hymn_of_the_day:  MusicIcon,
  song_of_the_day:  MusicIcon,
  wikimedia_gallery: ArtIcon,

  // Family / letters
  family_greeting: FamilyLetterIcon,
  letter_to_family: FamilyLetterIcon,
  pen_pal_letter:   FamilyLetterIcon,

  // Activities
  activity_suggestion: ActivityIcon,
  hobby_spotlight:     ActivityIcon,

  // Food
  simple_recipe: RecipeIcon,

  // History / learning
  country_spotlight: HistoryIcon,
  local_history:     HistoryIcon,
  memory_lane_photo: MemoryPhotoIcon,
  nostalgia:         HistoryIcon,
  this_day_history:  HistoryIcon,

  // News
  gnews:      NewsIcon,
  world_news: NewsIcon,

  // Newsletter structure
  newsletter_footer: NewsletterLayoutIcon,
  newsletter_header: NewsletterLayoutIcon,

  // Humour
  joke: JokeIcon,
};

// ── Public component ──────────────────────────────────────────────────────────

export function ProviderIcon({
  providerKey,
  className,
}: {
  providerKey: string;
  className?: string;
}) {
  const Icon = ICON_MAP[providerKey] ?? DefaultProviderIcon;
  return <Icon className={className} />;
}
