-- SQL insert statement for Venice: Uncensored model
-- Provider: OPENROUTER (OpenRouter.ai)
-- Model: cognitivecomputations/dolphin-mistral-24b-venice-edition:free
-- Free model with 32,768 context window

INSERT INTO ai_model_configurations (
    display_name,
    model_name,
    description,
    provider,
    model_type,
    is_active,
    max_tokens,
    temperature,
    top_p,
    presence_penalty,
    frequency_penalty,
    is_json_mode,
    provider_cost_input_usd_pm,
    provider_cost_output_usd_pm,
    user_price_input_usd_pm,
    user_price_output_usd_pm
) VALUES (
    'Venice: Uncensored (Free)',
    'cognitivecomputations/dolphin-mistral-24b-venice-edition:free',
    'Venice: Uncensored - Cognitive Computations Dolphin Mistral 24B Venice Edition. Free uncensored model with 32,768 context window. Available via OpenRouter.',
    'OPENROUTER',
    'GENERATION',
    true,
    4000,      -- Max tokens for generation
    0.7,       -- Temperature
    1.0,       -- Top-p
    0.0,       -- Presence penalty
    0.0,       -- Frequency penalty
    false,     -- JSON mode
    0.0,       -- Provider cost input (free)
    0.0,       -- Provider cost output (free)
    0.0,       -- User price input (free)
    0.0        -- User price output (free)
);