-- SQL insert statements for new AI models available in Azure AI Foundry
-- Compatible with RAG system (generation models, not embedding models)
-- Provider: AZURE (Azure AI Foundry)

-- 1. DeepSeek-V3-0324
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
    'DeepSeek V3',
    'DeepSeek-V3-0324',
    'DeepSeek V3 - 671B parameter MoE model with 37B activated parameters. Advanced reasoning and coding capabilities with 128K context. Available via Azure AI Foundry.',
    'AZURE',
    'GENERATION',
    true,
    4000,
    0.7,
    1.0,
    0.0,
    0.0,
    false,
    0.14,  -- Azure AI Foundry pricing for input tokens
    0.28,  -- Azure AI Foundry pricing for output tokens
    0.16,  -- User price with markup
    0.32   -- User price with markup
);

-- 2. Llama-4-Scout-17B-16E-Instruct
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
    'Llama 4 Scout 17B',
    'Llama-4-Scout-17B-16E-Instruct',
    'Llama 4 Scout - 17B activated parameters (109B total) with multimodal capabilities. Vision and text generation with 128K context. Available via Azure AI Foundry.',
    'AZURE',
    'GENERATION',
    true,
    4000,
    0.7,
    1.0,
    0.0,
    0.0,
    false,
    0.18,  -- Azure AI Foundry pricing for input tokens
    0.36,  -- Azure AI Foundry pricing for output tokens
    0.20,  -- User price with markup
    0.40   -- User price with markup
);

-- 3. Mistral Medium 2505 (Mistral Medium 3)
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
    'Mistral Medium 3',
    'mistral-medium-2505',
    'Mistral Medium 3 - Advanced multimodal model with reasoning, coding, and vision capabilities. Cost-efficient with high performance. Available via Azure AI Foundry.',
    'AZURE',
    'GENERATION',
    true,
    4000,
    0.7,
    1.0,
    0.0,
    0.0,
    false,
    0.265, -- Azure AI Foundry pricing for input tokens
    1.065, -- Azure AI Foundry pricing for output tokens
    0.30,  -- User price with markup
    1.20   -- User price with markup
);