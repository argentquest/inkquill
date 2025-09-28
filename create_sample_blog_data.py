"""Script to create sample blog data for testing."""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import async_session_local
from app.models.user import User

from app.models.blog_category import BlogCategory
from app.models.blog_tag import BlogTag, blog_post_tags
from app.models.blog_post import BlogPost, BlogPostStatus
from app.core.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_sample_data():
    """Create sample blog data."""
    async with async_session_local() as session:
        try:
            # Check if we already have posts
            existing_posts = await session.execute(
                select(BlogPost).limit(1)
            )
            if existing_posts.scalar_one_or_none():
                logger.info("Sample blog posts already exist!")
                return
            
            # Get or create test users
            logger.info("Getting or creating test users...")
            test_users = []
            for i in range(3):
                username = f"blogger{i+1}"
                result = await session.execute(
                    select(User).where(User.username == username)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    user = User(
                        username=username,
                        email=f"{username}@example.com",
                        display_name=f"Test Blogger {i+1}",
                        hashed_password=get_password_hash("password123"),
                        is_active=True,
                        email_verified=True
                    )
                    session.add(user)
                test_users.append(user)
            
            await session.flush()
            
            # Ensure categories exist
            logger.info("Checking categories...")
            categories_result = await session.execute(
                select(BlogCategory).order_by(BlogCategory.display_order)
            )
            categories = categories_result.scalars().all()
            
            if not categories:
                logger.error("No categories found! Please run seed_blog_categories.py first.")
                return
            
            # Create tags
            logger.info("Creating tags...")
            tag_data = [
                ("fiction", "fiction"),
                ("fantasy", "fantasy"),
                ("sci-fi", "sci-fi"),
                ("writing", "writing"),
                ("creativity", "creativity"),
                ("tips", "tips"),
                ("tutorial", "tutorial"),
                ("beginner", "beginner"),
                ("advanced", "advanced"),
                ("ai-assisted", "ai-assisted")
            ]
            
            tags = []
            for name, slug in tag_data:
                result = await session.execute(
                    select(BlogTag).where(BlogTag.slug == slug)
                )
                tag = result.scalar_one_or_none()
                
                if not tag:
                    tag = BlogTag(name=name, slug=slug)
                    session.add(tag)
                tags.append(tag)
            
            await session.flush()
            
            # Create blog posts
            logger.info("Creating blog posts...")
            sample_posts = [
                {
                    "title": "10 Essential Tips for Writing Compelling Characters",
                    "excerpt": "Creating memorable characters is the cornerstone of great storytelling. Here are 10 tips to help you craft characters that resonate with readers.",
                    "content": """<h2>Introduction</h2>
<p>Great characters are the heart of any compelling story. They drive the plot, engage readers emotionally, and make your narrative memorable long after the final page. But how do you create characters that feel real, complex, and captivating?</p>

<h2>1. Give Your Characters Clear Motivations</h2>
<p>Every character should want something, even if it's just a glass of water. Clear motivations drive your story forward and help readers understand why characters make the choices they do.</p>

<h2>2. Create Flawed Heroes</h2>
<p>Perfect characters are boring. Give your protagonists weaknesses, fears, and mistakes. These flaws make them relatable and create opportunities for growth throughout your story.</p>

<h2>3. Develop Distinct Voices</h2>
<p>Each character should speak and think in a unique way. Consider their background, education, personality, and experiences when crafting their dialogue and internal monologue.</p>

<h2>4. Show, Don't Tell</h2>
<p>Instead of telling readers that a character is brave, show them acting courageously. Actions, choices, and reactions reveal character more effectively than descriptions.</p>

<h2>5. Create Rich Backstories</h2>
<p>While you won't include every detail in your story, knowing your characters' histories helps you write them consistently and authentically.</p>

<h2>6. Give Characters Agency</h2>
<p>Characters should drive the plot through their choices and actions, not simply react to events. Active characters are more engaging than passive ones.</p>

<h2>7. Use Contrast and Conflict</h2>
<p>Place characters in situations that challenge their beliefs and force them to make difficult choices. Internal and external conflicts create compelling drama.</p>

<h2>8. Avoid Stereotypes</h2>
<p>Dig deeper than surface-level character types. Add unexpected traits and nuances that make your characters unique and memorable.</p>

<h2>9. Let Characters Grow</h2>
<p>Character arcs are essential. Your protagonists should change and evolve throughout the story, learning from their experiences and challenges.</p>

<h2>10. Write What You Don't Know</h2>
<p>Research and empathy allow you to write characters different from yourself. Talk to people, read widely, and approach unfamiliar perspectives with respect and curiosity.</p>

<h2>Conclusion</h2>
<p>Creating compelling characters takes practice, observation, and empathy. By following these tips and continuing to hone your craft, you'll develop characters that readers will remember and care about long after they finish your story.</p>""",
                    "category_slug": "character-development",
                    "tags": ["writing", "tips", "tutorial", "beginner"],
                    "featured_image_url": "/static/images/blog/character-tips.jpg"
                },
                {
                    "title": "Building Fantasy Worlds: A Comprehensive Guide",
                    "excerpt": "Learn how to create immersive, believable fantasy worlds that will transport your readers to new realms of imagination.",
                    "content": """<h2>The Art of World Building</h2>
<p>Creating a fantasy world is one of the most rewarding aspects of writing speculative fiction. A well-crafted world can elevate your story from good to unforgettable. This guide will walk you through the essential elements of building a fantasy world that feels real, consistent, and captivating.</p>

<h2>Start with the Big Picture</h2>
<p>Before diving into details, establish the fundamental rules of your world. What makes it different from our reality? Is there magic? Different physics? Unique geography? These core decisions will influence every other aspect of your world.</p>

<h2>Geography and Climate</h2>
<p>Map out your world's physical features. Consider how geography affects culture, trade, and conflict. Mountains create natural borders, rivers enable commerce, and climate shapes everything from architecture to cuisine.</p>

<h2>Magic Systems</h2>
<p>If your world includes magic, establish clear rules and limitations. The best magic systems have costs and consequences. Consider who can use magic, how it works, and what price must be paid for its power.</p>

<h2>Cultures and Societies</h2>
<p>Develop distinct cultures with their own values, traditions, and conflicts. Think about government systems, social hierarchies, religions, and daily life. Rich cultures make your world feel lived-in and authentic.</p>

<h2>History and Mythology</h2>
<p>Create a sense of depth with history. What events shaped your world? What do people believe about their origins? Myths and legends add texture and can provide plot elements for your story.</p>

<h2>Economy and Technology</h2>
<p>Consider how people make a living, what they trade, and what level of technology exists. These practical elements ground your world in reality and create opportunities for conflict and plot development.</p>

<h2>Language and Names</h2>
<p>Develop naming conventions that feel consistent within each culture. You don't need to create full languages, but having linguistic rules helps maintain immersion.</p>

<h2>The Iceberg Principle</h2>
<p>You should know more about your world than you reveal. Like an iceberg, most of your world-building remains beneath the surface, giving your visible world depth and authenticity.</p>

<h2>Conclusion</h2>
<p>World-building is an iterative process. Start with broad strokes and add detail as needed for your story. Remember, the goal isn't to create an encyclopedia but to build a stage where your characters' stories can unfold in a believable, engaging way.</p>""",
                    "category_slug": "world-building",
                    "tags": ["fantasy", "writing", "tutorial", "world-building"],
                    "featured_image_url": "/static/images/blog/fantasy-world.jpg"
                },
                {
                    "title": "How AI is Revolutionizing Creative Writing",
                    "excerpt": "Explore how artificial intelligence tools are changing the landscape of creative writing and storytelling.",
                    "content": """<h2>The New Era of AI-Assisted Writing</h2>
<p>Artificial Intelligence is transforming how we approach creative writing. From generating ideas to polishing prose, AI tools are becoming invaluable companions for writers at all levels. Let's explore how this technology is reshaping the creative process.</p>

<h2>AI as a Creative Partner</h2>
<p>Modern AI doesn't replace human creativity—it enhances it. Writers use AI to brainstorm ideas, overcome writer's block, and explore narrative possibilities they might not have considered. It's like having a tireless collaborator who's always ready to riff on your ideas.</p>

<h2>Overcoming Writer's Block</h2>
<p>One of AI's greatest strengths is helping writers push past creative obstacles. When you're stuck, AI can suggest plot developments, character actions, or even alternative phrasings that spark new directions for your story.</p>

<h2>Research and World-Building</h2>
<p>AI excels at quickly gathering and synthesizing information. Writers can use it to research historical periods, scientific concepts, or cultural details, making their fiction more accurate and immersive.</p>

<h2>Style and Voice Development</h2>
<p>By analyzing text patterns, AI can help writers maintain consistency in tone and style. It can also help experiment with different narrative voices, allowing writers to stretch their creative muscles.</p>

<h2>The Editing Assistant</h2>
<p>AI-powered editing tools go beyond simple grammar checks. They can identify pacing issues, suggest stronger word choices, and help tighten prose while maintaining the author's unique voice.</p>

<h2>Ethical Considerations</h2>
<p>As we embrace AI in creative writing, it's important to consider attribution, originality, and the value of human creativity. The best approach treats AI as a tool that amplifies human imagination rather than replacing it.</p>

<h2>The Future of AI and Writing</h2>
<p>We're only beginning to explore AI's potential in creative writing. As the technology evolves, we can expect more sophisticated tools that better understand narrative structure, emotional resonance, and the subtle art of storytelling.</p>

<h2>Conclusion</h2>
<p>AI is not the future of writing—it's the present. By embracing these tools while maintaining our unique human perspective, we can push the boundaries of storytelling and create works that neither human nor machine could produce alone.</p>""",
                    "category_slug": "ai-writing",
                    "tags": ["ai-assisted", "writing", "creativity", "advanced"],
                    "featured_image_url": "/static/images/blog/ai-writing.jpg"
                },
                {
                    "title": "The Three-Act Structure: A Timeless Framework",
                    "excerpt": "Master the fundamentals of story structure with this deep dive into the three-act format used by storytellers for centuries.",
                    "content": """<h2>Understanding the Three-Act Structure</h2>
<p>The three-act structure is one of the oldest and most reliable frameworks for crafting compelling narratives. From ancient Greek plays to modern blockbusters, this structure provides a solid foundation for storytelling.</p>

<h2>Act One: The Setup (25%)</h2>
<p>The first act introduces your world, characters, and the central conflict. It should:</p>
<ul>
<li>Establish the protagonist's normal life</li>
<li>Introduce the main characters and their relationships</li>
<li>Present the inciting incident that disrupts the status quo</li>
<li>End with a turning point that propels the story into Act Two</li>
</ul>

<h2>Act Two: The Confrontation (50%)</h2>
<p>The longest section of your story, Act Two develops the conflict and challenges your protagonist. Key elements include:</p>
<ul>
<li>Rising action and escalating stakes</li>
<li>Character development through trials and obstacles</li>
<li>The midpoint twist that changes the protagonist's approach</li>
<li>Building toward the crisis that leads to Act Three</li>
</ul>

<h2>Act Three: The Resolution (25%)</h2>
<p>The final act brings everything to a climax and resolution:</p>
<ul>
<li>The climax where the protagonist faces their greatest challenge</li>
<li>The resolution of all major plot threads</li>
<li>Character transformation demonstrated through action</li>
<li>The new normal established after the conflict</li>
</ul>

<h2>Why the Three-Act Structure Works</h2>
<p>This structure mirrors the natural rhythm of human experience: beginning, middle, and end. It provides enough flexibility for creativity while offering a proven framework that satisfies audience expectations.</p>

<h2>Variations and Flexibility</h2>
<p>While the basic structure remains consistent, writers can play with pacing, add subplots, or experiment with non-linear storytelling. The three-act structure is a guide, not a rigid formula.</p>

<h2>Conclusion</h2>
<p>Mastering the three-act structure gives you a powerful tool for crafting satisfying narratives. Whether you follow it closely or use it as a starting point for experimentation, understanding this framework is essential for any storyteller.</p>""",
                    "category_slug": "plot-structure",
                    "tags": ["writing", "storytelling", "tutorial", "beginner"],
                    "featured_image_url": "/static/images/blog/three-acts.jpg"
                },
                {
                    "title": "Creating Believable Dialogue: Tips from the Pros",
                    "excerpt": "Learn how to write dialogue that sounds natural, reveals character, and advances your plot.",
                    "content": """<h2>The Art of Authentic Dialogue</h2>
<p>Great dialogue can make or break a story. It reveals character, advances plot, and creates the illusion of real conversation while being far more purposeful and polished. Here's how to master this essential skill.</p>

<h2>Listen to Real Conversations</h2>
<p>The foundation of good dialogue is observation. Listen to how people actually speak—their rhythms, interruptions, and the way they often talk around subjects rather than addressing them directly.</p>

<h2>Each Character's Unique Voice</h2>
<p>Every character should have a distinct way of speaking. Consider their:</p>
<ul>
<li>Educational background</li>
<li>Regional dialect or accent</li>
<li>Personality traits</li>
<li>Current emotional state</li>
<li>Relationship to the listener</li>
</ul>

<h2>Subtext is Everything</h2>
<p>People rarely say exactly what they mean. Great dialogue operates on multiple levels, with characters pursuing hidden agendas or avoiding difficult truths. The tension between what's said and what's meant creates compelling drama.</p>

<h2>Avoid Information Dumps</h2>
<p>Dialogue should never feel like a vehicle for exposition. If characters are explaining things they both already know for the reader's benefit, find another way to convey that information.</p>

<h2>Read It Aloud</h2>
<p>The best test for dialogue is the ear. Read your conversations aloud to catch awkward phrasing, unnatural rhythms, or places where characters all sound the same.</p>

<h2>Less is More</h2>
<p>Real conversation includes a lot of filler, but fictional dialogue should be lean and purposeful. Every line should either reveal character or advance the plot—ideally both.</p>

<h2>Action Beats and Tags</h2>
<p>Break up dialogue with action beats that show what characters are doing while they speak. This adds visual interest and can reveal emotional subtext through body language.</p>

<h2>Conclusion</h2>
<p>Writing great dialogue is a skill that improves with practice. Pay attention to the conversations around you, read dialogue-heavy authors you admire, and always remember that dialogue in fiction must sound real while being better than real—more focused, more revealing, more impactful.</p>""",
                    "category_slug": "writing-tips",
                    "tags": ["writing", "tips", "tutorial"],
                    "featured_image_url": "/static/images/blog/dialogue-tips.jpg"
                }
            ]
            
            # Create posts with random authors and dates
            for i, post_data in enumerate(sample_posts):
                author = random.choice(test_users)
                
                # Extract tags and category slug
                post_tags = post_data.pop("tags", [])
                category_slug = post_data.pop("category_slug", None)
                
                # Find category
                category = next((c for c in categories if c.slug == category_slug), categories[0])
                
                # Generate slug from title
                slug = post_data["title"].lower().replace(" ", "-").replace(":", "").replace("?", "")
                
                # Create post
                post = BlogPost(
                    **post_data,
                    slug=slug,
                    author_id=author.id,
                    category_id=category.id,
                    status=BlogPostStatus.PUBLISHED,
                    published_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                    view_count=random.randint(100, 5000),
                    like_count=random.randint(10, 500),
                    comment_count=random.randint(0, 50)
                )
                session.add(post)
                await session.flush()
                
                # Add tags to post
                for tag_slug in post_tags:
                    tag = next((t for t in tags if t.slug == tag_slug), None)
                    if tag:
                        stmt = blog_post_tags.insert().values(
                            post_id=post.id,
                            tag_id=tag.id
                        )
                        await session.execute(stmt)
                        tag.usage_count += 1
                
                logger.info(f"Created post: {post.title}")
            
            # Update category post counts
            for category in categories:
                result = await session.execute(
                    select(BlogPost).where(
                        BlogPost.category_id == category.id,
                        BlogPost.status == BlogPostStatus.PUBLISHED
                    )
                )
                posts = result.scalars().all()
                category.post_count = len(posts)
            
            await session.commit()
            logger.info("Sample blog data created successfully!")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating sample data: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(create_sample_data())