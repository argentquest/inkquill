-- Add RunPod Flux Dev model configuration
-- Cost: 100000.0 per million output tokens = 1 coin per image (1 token × $100,000/1M = $0.01 = 1 coin)

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
    user_price_output_usd_pm,
    is_public_chat_default
) VALUES (
    'Flux Dev (RunPod)',
    'flux-dev',
    'Black Forest Labs Flux Dev model via RunPod serverless GPUs - Fast, cost-effective image generation with excellent quality.',
    'RUNPOD',
    'GENERATION',
    true,
    1,
    0.0,
    1.0,
    0.0,
    0.0,
    false,
    0.0,
    100000.0,  -- Provider cost per million output tokens
    0.0,
    100000.0,  -- User price: 1 coin per image (1 token × $100,000/1M = $0.01 = 1 coin)
    null
) ON CONFLICT (display_name) DO UPDATE SET
    model_name = EXCLUDED.model_name,
    description = EXCLUDED.description,
    provider = EXCLUDED.provider,
    user_price_output_usd_pm = EXCLUDED.user_price_output_usd_pm,
    is_active = EXCLUDED.is_active;

-- Optionally add Flux Pro model configuration for higher quality
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
    user_price_output_usd_pm,
    is_public_chat_default
) VALUES (
    'Flux Pro (RunPod)',
    'flux-pro',
    'Black Forest Labs Flux Pro model via RunPod serverless GPUs - Highest quality image generation, comparable to DALL-E 3.',
    'RUNPOD',
    'GENERATION',
    false,  -- Start as inactive, can be enabled later
    1,
    0.0,
    1.0,
    0.0,
    0.0,
    false,
    0.0,
    500000.0,  -- Provider cost per million output tokens  
    0.0,
    500000.0,  -- User price: 5 coins per image (1 token × $500,000/1M = $0.05 = 5 coins)
    null
) ON CONFLICT (display_name) DO UPDATE SET
    model_name = EXCLUDED.model_name,
    description = EXCLUDED.description,
    provider = EXCLUDED.provider,
    user_price_output_usd_pm = EXCLUDED.user_price_output_usd_pm,
    is_active = EXCLUDED.is_active;

-- Stable Diffusion XL option for even lower cost
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
    user_price_output_usd_pm,
    is_public_chat_default
) VALUES (
    'Stable Diffusion XL (RunPod)',
    'stable-diffusion-xl',
    'Stability AI Stable Diffusion XL via RunPod serverless GPUs - Ultra low-cost image generation.',
    'RUNPOD',
    'GENERATION',
    false,  -- Start as inactive
    1,
    0.0,
    1.0,
    0.0,
    0.0,
    false,
    0.0,
    50000.0,   -- Provider cost per million output tokens
    0.0,
    50000.0,   -- User price: 0.5 coins per image (1 token × $50,000/1M = $0.005 = 0.5 coins)
    null
) ON CONFLICT (display_name) DO UPDATE SET
    model_name = EXCLUDED.model_name,
    description = EXCLUDED.description,
    provider = EXCLUDED.provider,
    user_price_output_usd_pm = EXCLUDED.user_price_output_usd_pm,
    is_active = EXCLUDED.is_active;