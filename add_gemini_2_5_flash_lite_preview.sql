-- SQL insert statement for Google Gemini 2.5 Flash Lite Preview model
-- Provider: OPENROUTER
-- Model: google/gemini-2.5-flash-lite-preview-06-17
-- 
-- Pricing Note: Based on OpenRouter's Gemini 2.5 Flash Preview pricing ($0.15/$0.60 per million tokens)
-- and the fact that "lite" versions are typically 30-50% cheaper, estimated pricing below.
-- Verify current pricing at: https://openrouter.ai/google/gemini-2.5-flash-lite-preview-06-17

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
    'Gemini 2.5 Flash Lite Preview',
    'google/gemini-2.5-flash-lite-preview-06-17',
    'Google Gemini 2.5 Flash Lite Preview - Cost-optimized version of Gemini 2.5 with the lowest latency and cost in the 2.5 family. Designed for high throughput tasks like classification and summarization. Optional reasoning/thinking capability via API parameter. Available via OpenRouter.',
    'OPENROUTER',
    'GENERATION',
    true,
    8000,      -- High token limit for lite model
    0.8,       -- Good balance for creative tasks
    1.0,
    0.0,
    0.0,
    false,     -- JSON mode capability (verify with OpenRouter docs)
    0.10,      -- Estimated ~33% cheaper than regular Flash Preview ($0.15)
    0.40,      -- Estimated ~33% cheaper than regular Flash Preview ($0.60)
    0.12,      -- User price with 20% markup
    0.48       -- User price with 20% markup
);

-- Verification queries to check the insertion
-- Run these after the INSERT to verify:

-- Check if the model was added successfully
/*
SELECT 
    id,
    display_name,
    model_name,
    provider,
    is_active,
    provider_cost_input_usd_pm,
    provider_cost_output_usd_pm
FROM ai_model_configurations 
WHERE model_name = 'google/gemini-2.5-flash-lite-preview-06-17';
*/

-- Check all OpenRouter models
/*
SELECT 
    display_name,
    model_name,
    provider_cost_input_usd_pm,
    provider_cost_output_usd_pm,
    is_active
FROM ai_model_configurations 
WHERE provider = 'OPENROUTER'
ORDER BY display_name;
*/

-- IMPORTANT NOTES:
-- 1. Pricing is estimated based on regular Gemini 2.5 Flash Preview pricing
--    Verify current OpenRouter pricing before production use
-- 2. JSON mode capability should be verified in OpenRouter documentation
-- 3. Max tokens set to 8000 - adjust based on actual model limits
-- 4. Temperature optimized for creative tasks - already configured in temperature_optimizer.py