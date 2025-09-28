"""Blog AI service for AI-assisted blog writing using existing Quill approach."""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai_client_factory import AIClientFactory
from app.services.cost_tracker_service import CostTrackerService
from app.services.billing_service import billing_service
from app.models.ai_model_config import AIModelConfiguration
from app.models.blog_post import BlogPost
from app.services.blog_prompt_service import BlogPromptService

logger = logging.getLogger(__name__)


class BlogAIService:
    """AI integration service for blog content using existing AI infrastructure."""
    
    def __init__(self):
        self.cost_tracker = CostTrackerService()
    
    async def enhance_content(
        self,
        db: AsyncSession,
        user_id: int,
        content: str,
        enhancement_type: str,
        model_config_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Enhance blog content using AI (improve, expand, rewrite, continue)."""
        try:
            # Get AI model configuration
            if model_config_id:
                model_config = await self._get_model_config(db, model_config_id)
            else:
                model_config = await self._get_default_model_config(db)
            
            if not model_config:
                raise ValueError("No AI model configuration available")
            
            # Check user balance
            if not await billing_service.check_sufficient_balance(db, user_id, 100):  # Minimum 100 coins
                raise ValueError("Insufficient balance for AI operation")
            
            # Create AI client
            client = AIClientFactory.create_client(model_config.provider)
            
            # Get prompt from prompt service
            system_prompt = BlogPromptService.get_enhancement_prompt(enhancement_type)
            if not system_prompt:
                raise ValueError(f"No prompt available for enhancement type: {enhancement_type}")
            
            user_prompt = f"Content to enhance:\n\n{content}"
            
            # Make AI request
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await client.chat.completions.create(
                model=model_config.model_name,
                messages=messages,
                max_tokens=model_config.max_tokens or 1000,
                temperature=model_config.temperature or 0.7
            )
            
            enhanced_content = response.choices[0].message.content
            
            # Track cost
            cost_log_id = await self.cost_tracker.log_ai_call(
                db=db,
                user_id=user_id,
                model_name=model_config.model_name,
                provider=model_config.provider.value,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                estimated_cost_usd=self._calculate_cost(response.usage, model_config)
            )
            
            # Deduct cost from user balance
            await billing_service.deduct_ai_cost(db, user_id, model_config.model_name, cost_log_id)
            
            return {
                "enhanced_content": enhanced_content,
                "original_content": content,
                "enhancement_type": enhancement_type,
                "tokens_used": response.usage.total_tokens,
                "cost_log_id": cost_log_id
            }
            
        except Exception as e:
            logger.error(f"Error enhancing blog content: {e}")
            raise
    
    async def generate_title_suggestions(
        self,
        db: AsyncSession,
        user_id: int,
        content: str,
        count: int = 5
    ) -> List[str]:
        """Generate title suggestions based on blog content."""
        try:
            model_config = await self._get_default_model_config(db)
            if not model_config:
                raise ValueError("No AI model configuration available")
            
            # Check user balance
            if not await billing_service.check_sufficient_balance(db, user_id, 50):
                raise ValueError("Insufficient balance for AI operation")
            
            client = AIClientFactory.create_client(model_config.provider)
            
            system_prompt = BlogPromptService.format_title_suggestions_prompt(content, count)
            if not system_prompt:
                raise ValueError("No prompt available for title generation")
            
            user_prompt = f"Blog content:\n\n{content[:1000]}..."  # Limit content length
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await client.chat.completions.create(
                model=model_config.model_name,
                messages=messages,
                max_tokens=200,
                temperature=0.8
            )
            
            # Parse titles from response
            titles = [title.strip() for title in response.choices[0].message.content.split('\n') if title.strip()]
            
            # Track cost
            cost_log_id = await self.cost_tracker.log_ai_call(
                db=db,
                user_id=user_id,
                model_name=model_config.model_name,
                provider=model_config.provider.value,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                estimated_cost_usd=self._calculate_cost(response.usage, model_config)
            )
            
            await billing_service.deduct_ai_cost(db, user_id, model_config.model_name, cost_log_id)
            
            return titles[:count]
            
        except Exception as e:
            logger.error(f"Error generating title suggestions: {e}")
            raise
    
    async def generate_tags(
        self,
        db: AsyncSession,
        user_id: int,
        title: str,
        content: str
    ) -> List[str]:
        """Generate relevant tags for blog post."""
        try:
            model_config = await self._get_default_model_config(db)
            if not model_config:
                raise ValueError("No AI model configuration available")
            
            # Check user balance
            if not await billing_service.check_sufficient_balance(db, user_id, 30):
                raise ValueError("Insufficient balance for AI operation")
            
            client = AIClientFactory.create_client(model_config.provider)
            
            system_prompt = BlogPromptService.format_tags_generation_prompt()
            if not system_prompt:
                raise ValueError("No prompt available for tag generation")
            
            user_prompt = f"Title: {title}\n\nContent: {content[:800]}..."
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await client.chat.completions.create(
                model=model_config.model_name,
                messages=messages,
                max_tokens=100,
                temperature=0.6
            )
            
            # Parse tags from response
            tags_text = response.choices[0].message.content
            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
            
            # Track cost
            cost_log_id = await self.cost_tracker.log_ai_call(
                db=db,
                user_id=user_id,
                model_name=model_config.model_name,
                provider=model_config.provider.value,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                estimated_cost_usd=self._calculate_cost(response.usage, model_config)
            )
            
            await billing_service.deduct_ai_cost(db, user_id, model_config.model_name, cost_log_id)
            
            return tags
            
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            raise
    
    async def generate_excerpt(
        self,
        db: AsyncSession,
        user_id: int,
        content: str,
        max_length: int = 200
    ) -> str:
        """Generate blog post excerpt."""
        try:
            model_config = await self._get_default_model_config(db)
            if not model_config:
                raise ValueError("No AI model configuration available")
            
            # Check user balance
            if not await billing_service.check_sufficient_balance(db, user_id, 25):
                raise ValueError("Insufficient balance for AI operation")
            
            client = AIClientFactory.create_client(model_config.provider)
            
            system_prompt = BlogPromptService.format_excerpt_generation_prompt(max_length)
            if not system_prompt:
                raise ValueError("No prompt available for excerpt generation")
            
            user_prompt = f"Blog content:\n\n{content[:1500]}..."
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await client.chat.completions.create(
                model=model_config.model_name,
                messages=messages,
                max_tokens=100,
                temperature=0.7
            )
            
            excerpt = response.choices[0].message.content.strip()
            
            # Ensure excerpt doesn't exceed max length
            if len(excerpt) > max_length:
                excerpt = excerpt[:max_length-3] + "..."
            
            # Track cost
            cost_log_id = await self.cost_tracker.log_ai_call(
                db=db,
                user_id=user_id,
                model_name=model_config.model_name,
                provider=model_config.provider.value,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                estimated_cost_usd=self._calculate_cost(response.usage, model_config)
            )
            
            await billing_service.deduct_ai_cost(db, user_id, model_config.model_name, cost_log_id)
            
            return excerpt
            
        except Exception as e:
            logger.error(f"Error generating excerpt: {e}")
            raise
    
    # Removed _get_enhancement_prompt method - now using BlogPromptService
    
    async def _get_model_config(self, db: AsyncSession, config_id: int) -> Optional[AIModelConfiguration]:
        """Get AI model configuration by ID."""
        from sqlalchemy import select
        result = await db.execute(
            select(AIModelConfiguration).where(AIModelConfiguration.id == config_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_default_model_config(self, db: AsyncSession) -> Optional[AIModelConfiguration]:
        """Get default AI model configuration."""
        from sqlalchemy import select
        result = await db.execute(
            select(AIModelConfiguration)
            .where(AIModelConfiguration.is_active == True)
            .order_by(AIModelConfiguration.id)
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    def _calculate_cost(self, usage, model_config: AIModelConfiguration) -> float:
        """Calculate cost based on token usage and model pricing."""
        # This would use the actual pricing from the model config
        # For now, use a simple calculation
        prompt_cost = (usage.prompt_tokens / 1000) * 0.001  # $0.001 per 1K tokens
        completion_cost = (usage.completion_tokens / 1000) * 0.002  # $0.002 per 1K tokens
        return prompt_cost + completion_cost


# Create service instance
blog_ai_service = BlogAIService()