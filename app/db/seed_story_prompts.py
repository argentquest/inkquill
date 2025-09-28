#!/usr/bin/env python3
"""
Seed data script for character roles and story generation prompts.
Run this after applying migrations to populate the prompts table.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import async_session_maker
from app.models.prompt import Prompt, PromptTypeEnum, AgeTargetEnum
from app.crud.prompt import crud_prompt

async def seed_character_roles(db: AsyncSession):
    """Seed character role prompts."""
    print("Seeding character roles...")
    
    character_roles = [
        # Primary Roles
        {
            "title": "Protagonist",
            "prompt_content": "Protagonist",
            "reason_to_use": "The main character driving the story forward, facing challenges and growing through the narrative",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Antagonist",
            "prompt_content": "Antagonist",
            "reason_to_use": "The primary opposing force creating conflict for the protagonist, not necessarily evil but with opposing goals",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Deuteragonist",
            "prompt_content": "Deuteragonist",
            "reason_to_use": "The second most important character, often a close ally, rival, or complementary force to the protagonist",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        
        # Supporting Roles
        {
            "title": "Mentor",
            "prompt_content": "Mentor",
            "reason_to_use": "Wise guide who provides advice, training, or magical gifts to help the protagonist on their journey",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Sidekick",
            "prompt_content": "Sidekick",
            "reason_to_use": "Loyal companion providing support, comic relief, or assistance to the main character",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Love Interest",
            "prompt_content": "Love Interest",
            "reason_to_use": "Romantic partner or potential partner creating emotional stakes and personal growth opportunities",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Comic Relief",
            "prompt_content": "Comic Relief",
            "reason_to_use": "Character providing humor and levity to balance serious or tense moments in the story",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        
        # Archetypal Roles
        {
            "title": "Herald",
            "prompt_content": "Herald",
            "reason_to_use": "Brings the call to adventure or important news that sets the protagonist's journey in motion",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Threshold Guardian",
            "prompt_content": "Threshold Guardian",
            "reason_to_use": "Tests the hero's resolve and worthiness before allowing progress to the next stage of the journey",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Shapeshifter",
            "prompt_content": "Shapeshifter",
            "reason_to_use": "Character whose loyalty, nature, or allegiance is uncertain, creating doubt and tension",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Shadow",
            "prompt_content": "Shadow",
            "reason_to_use": "Represents the dark side, repressed aspects, or negative potential of the protagonist",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Trickster",
            "prompt_content": "Trickster",
            "reason_to_use": "Catalyst for change through mischief, rule-breaking, and questioning the status quo",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        
        # Supporting Cast
        {
            "title": "Ally",
            "prompt_content": "Ally",
            "reason_to_use": "Supporting character who helps the protagonist achieve their goals",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Rival",
            "prompt_content": "Rival",
            "reason_to_use": "Competitive character who challenges the protagonist, not necessarily evil but pursuing similar goals",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Minion",
            "prompt_content": "Minion",
            "reason_to_use": "Subordinate of the antagonist who carries out orders and creates obstacles",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Victim",
            "prompt_content": "Victim",
            "reason_to_use": "Character in need of rescue or protection, raising the stakes and urgency",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Witness",
            "prompt_content": "Witness",
            "reason_to_use": "Observer who provides crucial information, testimony, or perspective on events",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Background Character",
            "prompt_content": "Background Character",
            "reason_to_use": "Populates the world to make it feel lived-in without significant story impact",
            "prompt_type": PromptTypeEnum.CHARACTER_ROLE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        }
    ]
    
    for role_data in character_roles:
        # Check if already exists
        existing = await db.execute(
            db.query(Prompt).filter(
                Prompt.title == role_data["title"],
                Prompt.prompt_type == role_data["prompt_type"]
            )
        )
        if not existing.scalar_one_or_none():
            prompt = Prompt(**role_data)
            db.add(prompt)
    
    await db.commit()
    print(f"Seeded {len(character_roles)} character roles")


async def seed_story_genres(db: AsyncSession):
    """Seed story genre prompts."""
    print("Seeding story genres...")
    
    story_genres = [
        {
            "title": "Fantasy Adventure",
            "prompt_content": "Fantasy Adventure",
            "reason_to_use": "Epic quests with magic, mythical creatures, and heroic journeys in imaginary worlds",
            "prompt_type": PromptTypeEnum.STORY_GENRE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Sci-Fi Thriller",
            "prompt_content": "Sci-Fi Thriller",
            "reason_to_use": "Suspenseful stories featuring advanced technology, space exploration, or dystopian futures",
            "prompt_type": PromptTypeEnum.STORY_GENRE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Mystery Drama",
            "prompt_content": "Mystery Drama",
            "reason_to_use": "Character-driven narratives centered around solving puzzles, crimes, or uncovering secrets",
            "prompt_type": PromptTypeEnum.STORY_GENRE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Romance Comedy",
            "prompt_content": "Romance Comedy",
            "reason_to_use": "Light-hearted love stories with humor, misunderstandings, and happy endings",
            "prompt_type": PromptTypeEnum.STORY_GENRE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Horror Suspense",
            "prompt_content": "Horror Suspense",
            "reason_to_use": "Frightening tales that build tension, fear, and dread through atmosphere and threats",
            "prompt_type": PromptTypeEnum.STORY_GENRE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Historical Fiction",
            "prompt_content": "Historical Fiction",
            "reason_to_use": "Stories set in authentic historical periods with period-accurate details and real events",
            "prompt_type": PromptTypeEnum.STORY_GENRE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Urban Fantasy",
            "prompt_content": "Urban Fantasy",
            "reason_to_use": "Magic and supernatural elements hidden within modern city settings",
            "prompt_type": PromptTypeEnum.STORY_GENRE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Space Opera",
            "prompt_content": "Space Opera",
            "reason_to_use": "Grand-scale adventures across galaxies with alien civilizations and cosmic conflicts",
            "prompt_type": PromptTypeEnum.STORY_GENRE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Cyberpunk",
            "prompt_content": "Cyberpunk",
            "reason_to_use": "High-tech, low-life stories exploring the intersection of humanity and technology",
            "prompt_type": PromptTypeEnum.STORY_GENRE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Epic Fantasy",
            "prompt_content": "Epic Fantasy",
            "reason_to_use": "World-spanning adventures with complex magic systems, politics, and mythology",
            "prompt_type": PromptTypeEnum.STORY_GENRE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Psychological Thriller",
            "prompt_content": "Psychological Thriller",
            "reason_to_use": "Mind-bending stories that explore perception, memory, and the human psyche",
            "prompt_type": PromptTypeEnum.STORY_GENRE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Coming of Age",
            "prompt_content": "Coming of Age",
            "reason_to_use": "Personal growth stories focusing on the transition from youth to adulthood",
            "prompt_type": PromptTypeEnum.STORY_GENRE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        }
    ]
    
    for genre_data in story_genres:
        existing = await db.execute(
            db.query(Prompt).filter(
                Prompt.title == genre_data["title"],
                Prompt.prompt_type == genre_data["prompt_type"]
            )
        )
        if not existing.scalar_one_or_none():
            prompt = Prompt(**genre_data)
            db.add(prompt)
    
    await db.commit()
    print(f"Seeded {len(story_genres)} story genres")


async def seed_story_tones(db: AsyncSession):
    """Seed story tone prompts."""
    print("Seeding story tones...")
    
    story_tones = [
        {
            "title": "Hopeful",
            "prompt_content": "Hopeful",
            "reason_to_use": "Creates an optimistic atmosphere where characters overcome challenges with positive outcomes",
            "prompt_type": PromptTypeEnum.STORY_TONE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Dark",
            "prompt_content": "Dark",
            "reason_to_use": "Establishes a serious, grim mood exploring difficult themes and moral ambiguity",
            "prompt_type": PromptTypeEnum.STORY_TONE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Whimsical",
            "prompt_content": "Whimsical",
            "reason_to_use": "Brings playful, imaginative elements with unexpected twists and magical realism",
            "prompt_type": PromptTypeEnum.STORY_TONE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Gritty",
            "prompt_content": "Gritty",
            "reason_to_use": "Raw, realistic portrayal of harsh realities and tough character choices",
            "prompt_type": PromptTypeEnum.STORY_TONE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Humorous",
            "prompt_content": "Humorous",
            "reason_to_use": "Light-hearted approach using comedy to entertain and provide relief",
            "prompt_type": PromptTypeEnum.STORY_TONE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Melancholic",
            "prompt_content": "Melancholic",
            "reason_to_use": "Thoughtful, wistful atmosphere exploring loss, nostalgia, and bittersweet emotions",
            "prompt_type": PromptTypeEnum.STORY_TONE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Adventurous",
            "prompt_content": "Adventurous",
            "reason_to_use": "Exciting, fast-paced tone emphasizing action, exploration, and discovery",
            "prompt_type": PromptTypeEnum.STORY_TONE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Mysterious",
            "prompt_content": "Mysterious",
            "reason_to_use": "Enigmatic atmosphere with secrets to uncover and questions to answer",
            "prompt_type": PromptTypeEnum.STORY_TONE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Romantic",
            "prompt_content": "Romantic",
            "reason_to_use": "Emphasizes emotional connections, passion, and matters of the heart",
            "prompt_type": PromptTypeEnum.STORY_TONE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Epic",
            "prompt_content": "Epic",
            "reason_to_use": "Grand, sweeping tone with high stakes and legendary scope",
            "prompt_type": PromptTypeEnum.STORY_TONE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Intimate",
            "prompt_content": "Intimate",
            "reason_to_use": "Personal, character-focused tone with deep emotional exploration",
            "prompt_type": PromptTypeEnum.STORY_TONE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Satirical",
            "prompt_content": "Satirical",
            "reason_to_use": "Uses irony and humor to critique society, politics, or human nature",
            "prompt_type": PromptTypeEnum.STORY_TONE,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        }
    ]
    
    for tone_data in story_tones:
        existing = await db.execute(
            db.query(Prompt).filter(
                Prompt.title == tone_data["title"],
                Prompt.prompt_type == tone_data["prompt_type"]
            )
        )
        if not existing.scalar_one_or_none():
            prompt = Prompt(**tone_data)
            db.add(prompt)
    
    await db.commit()
    print(f"Seeded {len(story_tones)} story tones")


async def seed_story_conflicts(db: AsyncSession):
    """Seed story conflict type prompts."""
    print("Seeding story conflict types...")
    
    story_conflicts = [
        {
            "title": "Character vs. Self",
            "prompt_content": "Character vs. Self",
            "reason_to_use": "Internal struggles with personal demons, difficult decisions, or identity crises",
            "prompt_type": PromptTypeEnum.STORY_CONFLICT,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Character vs. Character",
            "prompt_content": "Character vs. Character",
            "reason_to_use": "Direct opposition between individuals with conflicting goals, beliefs, or desires",
            "prompt_type": PromptTypeEnum.STORY_CONFLICT,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Character vs. Society",
            "prompt_content": "Character vs. Society",
            "reason_to_use": "Protagonist challenges social norms, unjust systems, or cultural expectations",
            "prompt_type": PromptTypeEnum.STORY_CONFLICT,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Character vs. Nature",
            "prompt_content": "Character vs. Nature",
            "reason_to_use": "Survival against natural disasters, wilderness, or environmental forces",
            "prompt_type": PromptTypeEnum.STORY_CONFLICT,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Character vs. Technology",
            "prompt_content": "Character vs. Technology",
            "reason_to_use": "Struggle against artificial intelligence, machines, or technological systems",
            "prompt_type": PromptTypeEnum.STORY_CONFLICT,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Character vs. Supernatural",
            "prompt_content": "Character vs. Supernatural",
            "reason_to_use": "Confrontation with ghosts, demons, magic, or otherworldly forces",
            "prompt_type": PromptTypeEnum.STORY_CONFLICT,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Character vs. Fate",
            "prompt_content": "Character vs. Fate",
            "reason_to_use": "Struggle against destiny, prophecy, or seemingly inevitable outcomes",
            "prompt_type": PromptTypeEnum.STORY_CONFLICT,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Character vs. Time",
            "prompt_content": "Character vs. Time",
            "reason_to_use": "Racing against deadlines, aging, or temporal paradoxes",
            "prompt_type": PromptTypeEnum.STORY_CONFLICT,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        },
        {
            "title": "Character vs. Unknown",
            "prompt_content": "Character vs. Unknown",
            "reason_to_use": "Facing mysterious forces, unexplained phenomena, or the fear of the unfamiliar",
            "prompt_type": PromptTypeEnum.STORY_CONFLICT,
            "age_target": AgeTargetEnum.ALL_AGES,
            "is_active": True
        }
    ]
    
    for conflict_data in story_conflicts:
        existing = await db.execute(
            db.query(Prompt).filter(
                Prompt.title == conflict_data["title"],
                Prompt.prompt_type == conflict_data["prompt_type"]
            )
        )
        if not existing.scalar_one_or_none():
            prompt = Prompt(**conflict_data)
            db.add(prompt)
    
    await db.commit()
    print(f"Seeded {len(story_conflicts)} story conflict types")


async def main():
    """Run all seed functions."""
    async with async_session_maker() as db:
        try:
            await seed_character_roles(db)
            await seed_story_genres(db)
            await seed_story_tones(db)
            await seed_story_conflicts(db)
            print("\nAll story prompts seeded successfully!")
        except Exception as e:
            print(f"Error seeding data: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())