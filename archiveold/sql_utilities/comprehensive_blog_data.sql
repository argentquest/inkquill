-- Comprehensive Blog Data Creation Script
-- Creates sample data covering all enum values

-- First, check the actual enum values in the database
DO $$
DECLARE
    user_count INTEGER;
    sample_user_id INTEGER;
    draft_post_id INTEGER;
    published_post_id INTEGER;
    archived_post_id INTEGER;
    comment_id INTEGER;
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
    
    -- Show current enum values
    RAISE NOTICE 'BlogPostStatus enum values: DRAFT, PUBLISHED, ARCHIVED';
    RAISE NOTICE 'CommentStatus enum values: PENDING, APPROVED, REJECTED, DELETED';
    
    -- Clean up existing test data
    DELETE FROM blog_comments WHERE post_id IN (
        SELECT id FROM blog_posts WHERE slug LIKE 'test-%'
    );
    DELETE FROM blog_posts WHERE slug LIKE 'test-%';
    
    -- Create DRAFT post
    INSERT INTO blog_posts (
        title, slug, content, excerpt, author_id, status, 
        allow_comments, view_count, like_count, comment_count, 
        created_at, updated_at
    ) VALUES (
        'Test Draft Post',
        'test-draft-post',
        '<h2>Draft Post</h2><p>This is a draft post for testing.</p>',
        'A draft post for testing purposes.',
        sample_user_id,
        'DRAFT',
        true,
        5,
        1,
        0,
        NOW() - INTERVAL '3 days',
        NOW() - INTERVAL '3 days'
    ) RETURNING id INTO draft_post_id;
    
    RAISE NOTICE 'Created DRAFT post ID: %', draft_post_id;
    
    -- Create PUBLISHED post with comments
    INSERT INTO blog_posts (
        title, slug, content, excerpt, author_id, status, published_at,
        allow_comments, view_count, like_count, comment_count, 
        created_at, updated_at
    ) VALUES (
        'Test Published Post - Welcome to Our Blog',
        'test-published-post',
        '<h2>Welcome to Our Blog!</h2>
         <p>This is a published blog post to test the commenting functionality. We''re excited to share our thoughts and hear from you in the comments below.</p>
         <p>Feel free to leave a comment and start a discussion!</p>
         <h3>What You Can Expect</h3>
         <ul>
         <li>Regular updates on exciting topics</li>
         <li>Interactive discussions in the comments</li>
         <li>Community-driven content</li>
         </ul>',
        'Welcome to our blog! This published post tests all comment functionality.',
        sample_user_id,
        'PUBLISHED',
        NOW() - INTERVAL '1 day',
        true,
        158,
        23,
        0, -- Will update after creating comments
        NOW() - INTERVAL '1 day',
        NOW() - INTERVAL '1 day'
    ) RETURNING id INTO published_post_id;
    
    RAISE NOTICE 'Created PUBLISHED post ID: %', published_post_id;
    
    -- Create ARCHIVED post
    INSERT INTO blog_posts (
        title, slug, content, excerpt, author_id, status, published_at,
        allow_comments, view_count, like_count, comment_count, 
        created_at, updated_at
    ) VALUES (
        'Test Archived Post',
        'test-archived-post',
        '<h2>Archived Post</h2><p>This post has been archived for testing.</p>',
        'An archived post for testing purposes.',
        sample_user_id,
        'ARCHIVED',
        NOW() - INTERVAL '30 days',
        false, -- Usually archived posts don't allow comments
        200,
        15,
        3,
        NOW() - INTERVAL '30 days',
        NOW() - INTERVAL '7 days'
    ) RETURNING id INTO archived_post_id;
    
    RAISE NOTICE 'Created ARCHIVED post ID: %', archived_post_id;
    
    -- Now create comments with all statuses for the PUBLISHED post
    
    -- APPROVED comment (top-level)
    INSERT INTO blog_comments (
        post_id, author_id, content, status, like_count, reply_count, 
        is_author_reply, created_at, updated_at
    ) VALUES (
        published_post_id, 
        sample_user_id, 
        'This is an APPROVED comment. Great post! Really enjoyed reading this content.', 
        'APPROVED', 
        5, 
        0, 
        false, 
        NOW() - INTERVAL '12 hours', 
        NOW() - INTERVAL '12 hours'
    ) RETURNING id INTO comment_id;
    
    -- APPROVED reply to above comment
    INSERT INTO blog_comments (
        post_id, author_id, parent_comment_id, content, status, like_count, 
        reply_count, is_author_reply, created_at, updated_at
    ) VALUES (
        published_post_id, 
        sample_user_id, 
        comment_id,
        'Thank you! This is an APPROVED reply from the author.', 
        'APPROVED', 
        2, 
        0, 
        true, 
        NOW() - INTERVAL '10 hours', 
        NOW() - INTERVAL '10 hours'
    );
    
    -- Update reply count
    UPDATE blog_comments SET reply_count = 1 WHERE id = comment_id;
    
    -- PENDING comment
    INSERT INTO blog_comments (
        post_id, author_id, content, status, like_count, reply_count, 
        is_author_reply, created_at, updated_at
    ) VALUES (
        published_post_id, 
        sample_user_id, 
        'This is a PENDING comment waiting for moderation.', 
        'PENDING', 
        0, 
        0, 
        false, 
        NOW() - INTERVAL '2 hours', 
        NOW() - INTERVAL '2 hours'
    );
    
    -- REJECTED comment
    INSERT INTO blog_comments (
        post_id, author_id, content, status, like_count, reply_count, 
        is_author_reply, created_at, updated_at
    ) VALUES (
        published_post_id, 
        sample_user_id, 
        'This is a REJECTED comment that was disapproved.', 
        'REJECTED', 
        0, 
        0, 
        false, 
        NOW() - INTERVAL '6 hours', 
        NOW() - INTERVAL '5 hours'
    );
    
    -- DELETED comment
    INSERT INTO blog_comments (
        post_id, author_id, content, status, like_count, reply_count, 
        is_author_reply, deleted_at, created_at, updated_at
    ) VALUES (
        published_post_id, 
        sample_user_id, 
        'This is a DELETED comment that was removed.', 
        'DELETED', 
        0, 
        0, 
        false, 
        NOW() - INTERVAL '1 hour',
        NOW() - INTERVAL '8 hours', 
        NOW() - INTERVAL '1 hour'
    );
    
    -- Additional APPROVED comments for the published post
    INSERT INTO blog_comments (
        post_id, author_id, content, status, like_count, reply_count, 
        is_author_reply, created_at, updated_at
    ) VALUES (
        published_post_id, 
        sample_user_id, 
        'Another APPROVED comment. The content format is perfect and very helpful!', 
        'APPROVED', 
        3, 
        0, 
        false, 
        NOW() - INTERVAL '4 hours', 
        NOW() - INTERVAL '4 hours'
    ),
    (
        published_post_id, 
        sample_user_id, 
        'One more APPROVED comment. Looking forward to more posts like this!', 
        'APPROVED', 
        1, 
        0, 
        false, 
        NOW() - INTERVAL '1 hour', 
        NOW() - INTERVAL '1 hour'
    );
    
    -- Update post comment count (only count APPROVED comments)
    UPDATE blog_posts 
    SET comment_count = (
        SELECT COUNT(*) 
        FROM blog_comments 
        WHERE post_id = published_post_id 
        AND status = 'APPROVED'
        AND deleted_at IS NULL
    ),
    updated_at = NOW() 
    WHERE id = published_post_id;
    
    -- Summary
    RAISE NOTICE '=== SUMMARY ===';
    RAISE NOTICE 'Created 3 blog posts covering all statuses:';
    RAISE NOTICE '- DRAFT post: /blog/posts/test-draft-post';
    RAISE NOTICE '- PUBLISHED post: /blog/posts/test-published-post (with comments)';
    RAISE NOTICE '- ARCHIVED post: /blog/posts/test-archived-post';
    RAISE NOTICE '';
    RAISE NOTICE 'Created comments with all statuses:';
    RAISE NOTICE '- APPROVED: 4 comments (visible on frontend)';
    RAISE NOTICE '- PENDING: 1 comment (awaiting moderation)';
    RAISE NOTICE '- REJECTED: 1 comment (disapproved)';
    RAISE NOTICE '- DELETED: 1 comment (soft deleted)';
    RAISE NOTICE '';
    RAISE NOTICE 'Visit the published post to test comments: /blog/posts/test-published-post';
    
END $$;

-- Verification queries
SELECT 'Blog Posts by Status' as info;
SELECT bp.status, COUNT(*) as count 
FROM blog_posts bp
WHERE bp.slug LIKE 'test-%' 
GROUP BY bp.status;

SELECT 'Comments by Status' as info;
SELECT bc.status, COUNT(*) as count 
FROM blog_comments bc
JOIN blog_posts bp ON bc.post_id = bp.id
WHERE bp.slug LIKE 'test-%'
GROUP BY bc.status;