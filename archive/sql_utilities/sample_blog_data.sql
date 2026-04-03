-- Sample Blog Data Creation Script
-- Run this to create test blog posts and comments

-- First, check if we have users
DO $$
DECLARE
    user_count INTEGER;
    sample_user_id INTEGER;
    sample_post_id INTEGER;
    comment1_id INTEGER;
BEGIN
    -- Check if users exist
    SELECT COUNT(*) INTO user_count FROM users WHERE is_active = true;
    
    IF user_count = 0 THEN
        RAISE NOTICE 'No active users found. Please create a user first.';
        RETURN;
    END IF;
    
    -- Get first active user
    SELECT id INTO sample_user_id FROM users WHERE is_active = true LIMIT 1;
    RAISE NOTICE 'Using user ID: %', sample_user_id;
    
    -- Create sample blog post if none exist
    INSERT INTO blog_posts (
        title, slug, content, excerpt, author_id, status, published_at, 
        allow_comments, view_count, like_count, comment_count, 
        created_at, updated_at
    ) VALUES (
        'Welcome to Our Blog',
        'welcome-to-our-blog',
        '<h2>Welcome to Our Blog!</h2>
         <p>This is a sample blog post to test the commenting functionality. We''re excited to share our thoughts and hear from you in the comments below.</p>
         <p>Feel free to leave a comment and start a discussion!</p>
         <h3>What You Can Expect</h3>
         <ul>
         <li>Regular updates on exciting topics</li>
         <li>Interactive discussions in the comments</li>
         <li>Community-driven content</li>
         </ul>',
        'Welcome to our blog! This is a sample post to test commenting functionality.',
        sample_user_id,
        'published',
        NOW(),
        true,
        158,
        23,
        4,
        NOW(),
        NOW()
    )
    ON CONFLICT (slug) DO UPDATE SET 
        allow_comments = true,
        updated_at = NOW()
    RETURNING id INTO sample_post_id;
    
    RAISE NOTICE 'Created/Updated blog post ID: %', sample_post_id;
    
    -- If post already existed, get its ID
    IF sample_post_id IS NULL THEN
        SELECT id INTO sample_post_id FROM blog_posts WHERE slug = 'welcome-to-our-blog';
    END IF;
    
    -- Delete existing comments for this post to start fresh
    DELETE FROM blog_comments WHERE post_id = sample_post_id;
    
    -- Create sample comments
    -- Top-level comment 1
    INSERT INTO blog_comments (
        post_id, author_id, content, status, like_count, reply_count, 
        is_author_reply, created_at, updated_at
    ) VALUES (
        sample_post_id, 
        sample_user_id, 
        'Great post! I really enjoyed reading this. The explanation is clear and easy to follow. Looking forward to more content like this!', 
        'approved', 
        5, 
        1, 
        false, 
        NOW() - INTERVAL '2 hours', 
        NOW() - INTERVAL '2 hours'
    ) RETURNING id INTO comment1_id;
    
    -- Reply to comment 1
    INSERT INTO blog_comments (
        post_id, author_id, parent_comment_id, content, status, like_count, 
        reply_count, is_author_reply, created_at, updated_at
    ) VALUES (
        sample_post_id, 
        sample_user_id, 
        comment1_id,
        'Thank you so much for the kind words! We''re thrilled you enjoyed it. Stay tuned for more exciting content!', 
        'approved', 
        2, 
        0, 
        true, 
        NOW() - INTERVAL '1 hour 30 minutes', 
        NOW() - INTERVAL '1 hour 30 minutes'
    );
    
    -- Top-level comment 2
    INSERT INTO blog_comments (
        post_id, author_id, content, status, like_count, reply_count, 
        is_author_reply, created_at, updated_at
    ) VALUES (
        sample_post_id, 
        sample_user_id, 
        'This is exactly what I was looking for! The format is perfect and the content is very helpful. Bookmarking this for future reference.', 
        'approved', 
        3, 
        0, 
        false, 
        NOW() - INTERVAL '1 hour', 
        NOW() - INTERVAL '1 hour'
    );
    
    -- Top-level comment 3
    INSERT INTO blog_comments (
        post_id, author_id, content, status, like_count, reply_count, 
        is_author_reply, created_at, updated_at
    ) VALUES (
        sample_post_id, 
        sample_user_id, 
        'Interesting perspective! I''d love to see more posts on this topic. Maybe you could cover advanced techniques next?', 
        'approved', 
        1, 
        0, 
        false, 
        NOW() - INTERVAL '30 minutes', 
        NOW() - INTERVAL '30 minutes'
    );
    
    -- Update post comment count
    UPDATE blog_posts 
    SET comment_count = 4, updated_at = NOW() 
    WHERE id = sample_post_id;
    
    RAISE NOTICE 'Created 4 sample comments for post ID: %', sample_post_id;
    RAISE NOTICE 'Sample blog data creation completed!';
    RAISE NOTICE 'Visit: /blog/posts/welcome-to-our-blog';
    
END $$;