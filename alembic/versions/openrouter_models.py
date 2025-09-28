"""add openrouter models

Revision ID: openrouter_models
Revises: d4573230eacc
Create Date: 2025-06-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'openrouter_models'
down_revision = 'd4573230eacc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use direct SQL INSERT statements with proper enum casting
    op.execute("""
        INSERT INTO ai_model_configurations (
            display_name, model_name, description, provider, model_type, 
            is_active, is_public_chat_default, max_tokens, temperature, top_p,
            presence_penalty, frequency_penalty, is_json_mode,
            provider_cost_input_usd_pm, provider_cost_output_usd_pm,
            user_price_input_usd_pm, user_price_output_usd_pm
        ) VALUES 
        (
            'Claude 3.5 Sonnet (OpenRouter)',
            'anthropic/claude-3.5-sonnet',
            'Anthropic Claude 3.5 Sonnet via OpenRouter - Excellent for creative writing and complex reasoning',
            'OPENROUTER'::ai_provider_enum,
            'GENERATION'::ai_model_type_enum,
            true, false, 4000, 0.7, 1.0, 0.0, 0.0, true,
            3.00, 15.00, 3.00, 15.00
        ),
        (
            'DeepSeek R1 (OpenRouter)',
            'deepseek/deepseek-r1',
            'DeepSeek R1 via OpenRouter - Advanced reasoning model, cost-effective',
            'OPENROUTER'::ai_provider_enum,
            'GENERATION'::ai_model_type_enum,
            true, false, 8000, 0.7, 1.0, 0.0, 0.0, true,
            0.55, 2.19, 0.55, 2.19
        ),
        (
            'GPT-4o (OpenRouter)',
            'openai/gpt-4o',
            'OpenAI GPT-4o via OpenRouter - Latest GPT-4 model with improved capabilities',
            'OPENROUTER'::ai_provider_enum,
            'GENERATION'::ai_model_type_enum,
            true, false, 4000, 0.7, 1.0, 0.0, 0.0, true,
            2.50, 10.00, 2.50, 10.00
        ),
        (
            'Llama 3.1 405B (OpenRouter)',
            'meta-llama/llama-3.1-405b-instruct',
            'Meta Llama 3.1 405B via OpenRouter - Powerful open-source model',
            'OPENROUTER'::ai_provider_enum,
            'GENERATION'::ai_model_type_enum,
            true, false, 4000, 0.7, 1.0, 0.0, 0.0, true,
            2.70, 2.70, 2.70, 2.70
        ),
        (
            'Qwen 2.5 Coder 32B (OpenRouter)',
            'qwen/qwen-2.5-coder-32b-instruct',
            'Qwen 2.5 Coder 32B via OpenRouter - Specialized for code generation and technical tasks',
            'OPENROUTER'::ai_provider_enum,
            'GENERATION'::ai_model_type_enum,
            true, false, 4000, 0.7, 1.0, 0.0, 0.0, true,
            0.90, 0.90, 0.90, 0.90
        ),
        (
            'Mixtral 8x7B (OpenRouter)',
            'mistralai/mixtral-8x7b-instruct',
            'Mistral Mixtral 8x7B via OpenRouter - Efficient mixture of experts model',
            'OPENROUTER'::ai_provider_enum,
            'GENERATION'::ai_model_type_enum,
            true, false, 4000, 0.7, 1.0, 0.0, 0.0, true,
            0.24, 0.24, 0.24, 0.24
        );
    """)


def downgrade() -> None:
    # Remove OpenRouter model configurations
    op.execute(
        "DELETE FROM ai_model_configurations WHERE provider = 'OPENROUTER'::ai_provider_enum"
    )