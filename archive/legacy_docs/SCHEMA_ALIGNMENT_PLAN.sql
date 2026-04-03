-- Schema alignment plan generated from SQLAlchemy metadata vs live PostgreSQL schema
-- Source of truth: code models
BEGIN;

-- Missing table: ai_model_configurations

CREATE TABLE ai_model_configurations (
	id SERIAL NOT NULL, 
	display_name VARCHAR(100) NOT NULL, 
	model_name VARCHAR(255) NOT NULL, 
	description TEXT, 
	provider ai_provider_enum NOT NULL, 
	model_type ai_model_type_enum NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	is_public_chat_default BOOLEAN, 
	max_tokens INTEGER NOT NULL, 
	temperature FLOAT NOT NULL, 
	top_p FLOAT NOT NULL, 
	presence_penalty FLOAT NOT NULL, 
	frequency_penalty FLOAT NOT NULL, 
	is_json_mode BOOLEAN NOT NULL, 
	provider_cost_input_usd_pm FLOAT NOT NULL, 
	provider_cost_output_usd_pm FLOAT NOT NULL, 
	user_price_input_usd_pm FLOAT NOT NULL, 
	user_price_output_usd_pm FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (display_name)
);

-- Missing table: blog_categories

CREATE TABLE blog_categories (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	slug VARCHAR(100) NOT NULL, 
	description TEXT, 
	color VARCHAR(7), 
	icon VARCHAR(50), 
	post_count INTEGER NOT NULL, 
	display_order INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

-- Missing table: blog_tags

CREATE TABLE blog_tags (
	id SERIAL NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	slug VARCHAR(50) NOT NULL, 
	description TEXT, 
	usage_count INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

-- Missing table: chat_samples

CREATE TABLE chat_samples (
	id SERIAL NOT NULL, 
	title VARCHAR(100) NOT NULL, 
	prompt_text TEXT NOT NULL, 
	category VARCHAR(50), 
	is_active BOOLEAN NOT NULL, 
	sort_order INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

-- Missing table: credit_packages

CREATE TABLE credit_packages (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	credit_amount DECIMAL(10, 4) NOT NULL, 
	price_usd DECIMAL(10, 2) NOT NULL, 
	bonus_percentage DECIMAL(5, 2) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	display_order INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

-- Missing table: cta_contents

CREATE TABLE cta_contents (
	id SERIAL NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	subtitle VARCHAR(500), 
	content TEXT, 
	position ctaposition NOT NULL, 
	sort_order INTEGER, 
	style ctastyle, 
	background_color VARCHAR(200), 
	text_color VARCHAR(50), 
	icon_class VARCHAR(100), 
	features TEXT, 
	primary_button_text VARCHAR(100), 
	primary_button_url VARCHAR(500), 
	primary_button_icon VARCHAR(50), 
	secondary_button_text VARCHAR(100), 
	secondary_button_url VARCHAR(500), 
	secondary_button_icon VARCHAR(50), 
	show_for_anonymous BOOLEAN, 
	show_for_authenticated BOOLEAN, 
	show_for_admin BOOLEAN, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITH TIME ZONE, 
	campaign_name VARCHAR(100), 
	utm_source VARCHAR(100), 
	utm_medium VARCHAR(100), 
	utm_campaign VARCHAR(100), 
	PRIMARY KEY (id)
);

-- Missing table: forum_categories

CREATE TABLE forum_categories (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	slug VARCHAR(100) NOT NULL, 
	sort_order INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	icon VARCHAR(50), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

-- Missing table: anonymous_user_sessions

CREATE TABLE anonymous_user_sessions (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	session_token VARCHAR(64) NOT NULL, 
	ip_address VARCHAR(45), 
	browser_fingerprint VARCHAR(32), 
	user_agent TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Missing table: blog_author_profiles

CREATE TABLE blog_author_profiles (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	bio TEXT, 
	profile_image_url VARCHAR(500), 
	website_url VARCHAR(255), 
	twitter_handle VARCHAR(50), 
	instagram_handle VARCHAR(50), 
	linkedin_url VARCHAR(255), 
	allow_comments_default BOOLEAN NOT NULL, 
	auto_publish BOOLEAN NOT NULL, 
	email_notifications BOOLEAN NOT NULL, 
	total_posts INTEGER NOT NULL, 
	total_views INTEGER NOT NULL, 
	total_likes INTEGER NOT NULL, 
	follower_count INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT unique_user_profile UNIQUE (user_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Missing table: blog_follows

CREATE TABLE blog_follows (
	id SERIAL NOT NULL, 
	author_id INTEGER NOT NULL, 
	follower_id INTEGER NOT NULL, 
	notification_enabled BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT unique_author_follower UNIQUE (author_id, follower_id), 
	FOREIGN KEY(author_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(follower_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Missing table: blog_posts

CREATE TABLE blog_posts (
	id SERIAL NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	slug VARCHAR(255) NOT NULL, 
	content TEXT NOT NULL, 
	excerpt TEXT, 
	featured_image_url VARCHAR(500), 
	status blogpoststatus NOT NULL, 
	author_id INTEGER NOT NULL, 
	category_id INTEGER, 
	view_count INTEGER NOT NULL, 
	like_count INTEGER NOT NULL, 
	comment_count INTEGER NOT NULL, 
	meta_title VARCHAR(255), 
	meta_description TEXT, 
	meta_keywords TEXT, 
	og_title VARCHAR(255), 
	og_description TEXT, 
	og_image_url VARCHAR(500), 
	is_featured BOOLEAN NOT NULL, 
	allow_comments BOOLEAN NOT NULL, 
	is_ai_generated BOOLEAN NOT NULL, 
	published_at TIMESTAMP WITH TIME ZONE, 
	last_viewed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	deleted_at TIMESTAMP WITH TIME ZONE, 
	search_vector TSVECTOR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(author_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(category_id) REFERENCES blog_categories (id) ON DELETE SET NULL
);

-- Missing table: blog_subscriptions

CREATE TABLE blog_subscriptions (
	id SERIAL NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	user_id INTEGER, 
	status subscriptionstatus NOT NULL, 
	frequency subscriptionfrequency NOT NULL, 
	include_categories TEXT, 
	include_tags TEXT, 
	confirmation_token VARCHAR(255), 
	unsubscribe_token VARCHAR(255) NOT NULL, 
	last_sent_at TIMESTAMP WITH TIME ZONE, 
	total_emails_sent INTEGER NOT NULL, 
	last_opened_at TIMESTAMP WITH TIME ZONE, 
	open_count INTEGER NOT NULL, 
	click_count INTEGER NOT NULL, 
	bounce_count INTEGER NOT NULL, 
	complaint_count INTEGER NOT NULL, 
	last_bounce_at TIMESTAMP WITH TIME ZONE, 
	last_complaint_at TIMESTAMP WITH TIME ZONE, 
	source VARCHAR(100), 
	ip_address VARCHAR(45), 
	user_agent TEXT, 
	confirmed_at TIMESTAMP WITH TIME ZONE, 
	unsubscribed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Missing table: refresh_tokens

CREATE TABLE refresh_tokens (
	id SERIAL NOT NULL, 
	token VARCHAR(255) NOT NULL, 
	user_id INTEGER NOT NULL, 
	issued_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	revoked_at TIMESTAMP WITH TIME ZONE, 
	ip_address VARCHAR(45), 
	user_agent VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Missing table: social_share_daily_summaries

CREATE TABLE social_share_daily_summaries (
	id UUID NOT NULL, 
	user_id INTEGER NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	total_shares INTEGER NOT NULL, 
	coins_earned INTEGER NOT NULL, 
	max_coins_reached BOOLEAN NOT NULL, 
	facebook_shares INTEGER NOT NULL, 
	twitter_shares INTEGER NOT NULL, 
	linkedin_shares INTEGER NOT NULL, 
	reddit_shares INTEGER NOT NULL, 
	whatsapp_shares INTEGER NOT NULL, 
	email_shares INTEGER NOT NULL, 
	copy_link_shares INTEGER NOT NULL, 
	pinterest_shares INTEGER NOT NULL, 
	telegram_shares INTEGER NOT NULL, 
	image_preview_shares INTEGER NOT NULL, 
	published_story_shares INTEGER NOT NULL, 
	ai_public_chat_shares INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Missing table: social_shares

CREATE TABLE social_shares (
	id UUID NOT NULL, 
	user_id INTEGER, 
	content_type VARCHAR(50) NOT NULL, 
	content_id VARCHAR(255) NOT NULL, 
	content_title VARCHAR(500), 
	content_url TEXT NOT NULL, 
	platform VARCHAR(50) NOT NULL, 
	shared_text TEXT, 
	shared_hashtags VARCHAR(500), 
	ip_address VARCHAR(45), 
	user_agent TEXT, 
	referrer TEXT, 
	coin_awarded BOOLEAN NOT NULL, 
	coin_amount INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Missing table: user_accounts

CREATE TABLE user_accounts (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	current_balance DECIMAL(10, 4) NOT NULL, 
	total_spent DECIMAL(10, 4) NOT NULL, 
	total_credits_added DECIMAL(10, 4) NOT NULL, 
	currency VARCHAR(3) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_positive_balance CHECK (current_balance >= 0), 
	UNIQUE (user_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Missing table: user_activities

CREATE TABLE user_activities (
	id UUID NOT NULL, 
	user_id INTEGER, 
	action_type VARCHAR(100) NOT NULL, 
	action_category VARCHAR(50), 
	action_details TEXT, 
	endpoint VARCHAR(255), 
	method VARCHAR(10), 
	status_code INTEGER, 
	duration_ms FLOAT, 
	ip_address VARCHAR(45), 
	user_agent VARCHAR(500), 
	request_id VARCHAR(36), 
	request_data JSON, 
	response_data JSON, 
	extra_data JSON, 
	error_message TEXT, 
	error_type VARCHAR(100), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Missing table: user_interview_responses

CREATE TABLE user_interview_responses (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	interview_id VARCHAR(100) NOT NULL, 
	json_response TEXT NOT NULL, 
	completed_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

-- Missing table: blog_analytics_summary

CREATE TABLE blog_analytics_summary (
	id SERIAL NOT NULL, 
	post_id INTEGER NOT NULL, 
	date DATE NOT NULL, 
	unique_views INTEGER NOT NULL, 
	total_views INTEGER NOT NULL, 
	new_likes INTEGER NOT NULL, 
	new_comments INTEGER NOT NULL, 
	avg_read_time INTEGER NOT NULL, 
	bounce_rate DECIMAL(5, 2) NOT NULL, 
	social_shares INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT unique_post_date UNIQUE (post_id, date), 
	FOREIGN KEY(post_id) REFERENCES blog_posts (id) ON DELETE CASCADE
);

-- Missing table: blog_comments

CREATE TABLE blog_comments (
	id SERIAL NOT NULL, 
	post_id INTEGER NOT NULL, 
	author_id INTEGER NOT NULL, 
	parent_comment_id INTEGER, 
	content TEXT NOT NULL, 
	status commentstatus NOT NULL, 
	like_count INTEGER NOT NULL, 
	reply_count INTEGER NOT NULL, 
	is_author_reply BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	deleted_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(post_id) REFERENCES blog_posts (id) ON DELETE CASCADE, 
	FOREIGN KEY(author_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(parent_comment_id) REFERENCES blog_comments (id) ON DELETE CASCADE
);

-- Missing table: blog_content_links

CREATE TABLE blog_content_links (
	id SERIAL NOT NULL, 
	post_id INTEGER NOT NULL, 
	link_type linktype NOT NULL, 
	link_id INTEGER NOT NULL, 
	link_text VARCHAR(255), 
	link_context TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(post_id) REFERENCES blog_posts (id) ON DELETE CASCADE
);

-- Missing table: blog_likes

CREATE TABLE blog_likes (
	id SERIAL NOT NULL, 
	post_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT unique_post_like UNIQUE (post_id, user_id), 
	FOREIGN KEY(post_id) REFERENCES blog_posts (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Missing table: blog_post_associations

CREATE TABLE blog_post_associations (
	id SERIAL NOT NULL, 
	post_id INTEGER NOT NULL, 
	association_type associationtype NOT NULL, 
	association_id INTEGER NOT NULL, 
	association_title VARCHAR(255), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(post_id) REFERENCES blog_posts (id) ON DELETE CASCADE
);

-- Missing table: blog_post_tags

CREATE TABLE blog_post_tags (
	id SERIAL NOT NULL, 
	post_id INTEGER NOT NULL, 
	tag_id INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	FOREIGN KEY(post_id) REFERENCES blog_posts (id) ON DELETE CASCADE, 
	FOREIGN KEY(tag_id) REFERENCES blog_tags (id) ON DELETE CASCADE
);

-- Missing table: blog_views

CREATE TABLE blog_views (
	id SERIAL NOT NULL, 
	post_id INTEGER NOT NULL, 
	user_id INTEGER, 
	ip_address INET, 
	user_agent TEXT, 
	referrer_url VARCHAR(500), 
	session_id VARCHAR(100), 
	view_duration INTEGER, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(post_id) REFERENCES blog_posts (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
);

-- Missing table: brainstorm_sessions

CREATE TABLE brainstorm_sessions (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	interview_response_id INTEGER NOT NULL, 
	session_name VARCHAR(200), 
	generated_concepts TEXT NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(interview_response_id) REFERENCES user_interview_responses (id)
);

-- Missing table: brainstorm_favorites

CREATE TABLE brainstorm_favorites (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	session_id INTEGER NOT NULL, 
	concept_id VARCHAR(50) NOT NULL, 
	concept_data TEXT NOT NULL, 
	is_selected BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(session_id) REFERENCES brainstorm_sessions (id)
);

-- Missing table: chat_sessions

CREATE TABLE chat_sessions (
	id SERIAL NOT NULL, 
	world_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(world_id) REFERENCES worlds (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Missing table: world_collaborators

CREATE TABLE world_collaborators (
	id SERIAL NOT NULL, 
	world_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	role VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	invited_by_user_id INTEGER, 
	invited_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	joined_at TIMESTAMP WITH TIME ZONE, 
	permissions JSON, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_world_collaborator UNIQUE (world_id, user_id), 
	FOREIGN KEY(world_id) REFERENCES worlds (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(invited_by_user_id) REFERENCES users (id) ON DELETE SET NULL
);

-- Missing table: world_roles

CREATE TABLE world_roles (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description VARCHAR(500), 
	world_id INTEGER, 
	created_by_user_id INTEGER, 
	is_predefined BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(world_id) REFERENCES worlds (id) ON DELETE CASCADE, 
	FOREIGN KEY(created_by_user_id) REFERENCES users (id) ON DELETE SET NULL
);

-- Missing table: brainstorm_stories

CREATE TABLE brainstorm_stories (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	favorite_id INTEGER NOT NULL, 
	story_id INTEGER, 
	title VARCHAR(200) NOT NULL, 
	three_act_structure TEXT NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(favorite_id) REFERENCES brainstorm_favorites (id), 
	FOREIGN KEY(story_id) REFERENCES stories (id)
);

-- Missing table: forum_threads

CREATE TABLE forum_threads (
	id SERIAL NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	slug VARCHAR(255) NOT NULL, 
	status thread_status_enum NOT NULL, 
	category_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	world_id INTEGER, 
	story_id INTEGER, 
	view_count INTEGER NOT NULL, 
	post_count INTEGER NOT NULL, 
	last_post_at TIMESTAMP WITH TIME ZONE, 
	last_post_by_id INTEGER, 
	is_pinned BOOLEAN NOT NULL, 
	is_locked BOOLEAN NOT NULL, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at TIMESTAMP WITH TIME ZONE, 
	deleted_by_id INTEGER, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_thread_category_slug UNIQUE (category_id, slug), 
	FOREIGN KEY(category_id) REFERENCES forum_categories (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(world_id) REFERENCES worlds (id) ON DELETE SET NULL, 
	FOREIGN KEY(story_id) REFERENCES stories (id) ON DELETE SET NULL, 
	FOREIGN KEY(last_post_by_id) REFERENCES users (id) ON DELETE SET NULL, 
	FOREIGN KEY(deleted_by_id) REFERENCES users (id) ON DELETE SET NULL
);

-- Missing table: published_stories

CREATE TABLE published_stories (
	id SERIAL NOT NULL, 
	story_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	published_url VARCHAR(1024) NOT NULL, 
	filename VARCHAR(255) NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	description TEXT, 
	word_count INTEGER, 
	is_public BOOLEAN NOT NULL, 
	is_featured BOOLEAN NOT NULL, 
	view_count INTEGER NOT NULL, 
	like_count INTEGER NOT NULL, 
	comment_count INTEGER NOT NULL, 
	average_rating FLOAT, 
	published_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	search_vector TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(story_id) REFERENCES stories (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Missing table: story_location_associations

CREATE TABLE story_location_associations (
	id SERIAL NOT NULL, 
	story_id INTEGER NOT NULL, 
	location_id INTEGER NOT NULL, 
	roles JSON NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(story_id) REFERENCES stories (id) ON DELETE CASCADE, 
	FOREIGN KEY(location_id) REFERENCES locations (id) ON DELETE CASCADE
);

-- Missing table: act_character_associations

CREATE TABLE act_character_associations (
	id SERIAL NOT NULL, 
	act_id INTEGER NOT NULL, 
	character_id INTEGER NOT NULL, 
	roles JSON NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(act_id) REFERENCES acts (id) ON DELETE CASCADE, 
	FOREIGN KEY(character_id) REFERENCES characters (id) ON DELETE CASCADE
);

-- Missing table: act_location_associations

CREATE TABLE act_location_associations (
	id SERIAL NOT NULL, 
	act_id INTEGER NOT NULL, 
	location_id INTEGER NOT NULL, 
	roles JSON NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(act_id) REFERENCES acts (id) ON DELETE CASCADE, 
	FOREIGN KEY(location_id) REFERENCES locations (id) ON DELETE CASCADE
);

-- Missing table: act_lore_item_associations

CREATE TABLE act_lore_item_associations (
	id SERIAL NOT NULL, 
	act_id INTEGER NOT NULL, 
	lore_item_id INTEGER NOT NULL, 
	roles JSON NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(act_id) REFERENCES acts (id) ON DELETE CASCADE, 
	FOREIGN KEY(lore_item_id) REFERENCES lore_items (id) ON DELETE CASCADE
);

-- Missing table: chat_messages

CREATE TABLE chat_messages (
	id SERIAL NOT NULL, 
	session_id INTEGER NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	content TEXT NOT NULL, 
	full_context JSON, 
	element_type VARCHAR(50), 
	element_id INTEGER, 
	cost_log_id INTEGER, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE, 
	FOREIGN KEY(cost_log_id) REFERENCES ai_call_logs (id) ON DELETE SET NULL
);

-- Missing table: forum_posts

CREATE TABLE forum_posts (
	id SERIAL NOT NULL, 
	content TEXT NOT NULL, 
	content_html TEXT, 
	thread_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	parent_post_id INTEGER, 
	character_id INTEGER, 
	location_id INTEGER, 
	upvote_count INTEGER NOT NULL, 
	downvote_count INTEGER NOT NULL, 
	score INTEGER NOT NULL, 
	edit_count INTEGER NOT NULL, 
	edited_at TIMESTAMP WITH TIME ZONE, 
	edited_by_id INTEGER, 
	is_deleted BOOLEAN NOT NULL, 
	deleted_at TIMESTAMP WITH TIME ZONE, 
	deleted_by_id INTEGER, 
	deletion_reason VARCHAR(255), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(thread_id) REFERENCES forum_threads (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(parent_post_id) REFERENCES forum_posts (id) ON DELETE CASCADE, 
	FOREIGN KEY(character_id) REFERENCES characters (id) ON DELETE SET NULL, 
	FOREIGN KEY(location_id) REFERENCES locations (id) ON DELETE SET NULL, 
	FOREIGN KEY(edited_by_id) REFERENCES users (id) ON DELETE SET NULL, 
	FOREIGN KEY(deleted_by_id) REFERENCES users (id) ON DELETE SET NULL
);

-- Missing table: forum_subscriptions

CREATE TABLE forum_subscriptions (
	id SERIAL NOT NULL, 
	thread_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	notify_email BOOLEAN NOT NULL, 
	notify_in_app BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_subscription_thread_user UNIQUE (thread_id, user_id), 
	FOREIGN KEY(thread_id) REFERENCES forum_threads (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Missing table: story_character_associations

CREATE TABLE story_character_associations (
	id SERIAL NOT NULL, 
	story_id INTEGER NOT NULL, 
	character_id INTEGER NOT NULL, 
	roles JSON NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(story_id) REFERENCES stories (id) ON DELETE CASCADE, 
	FOREIGN KEY(character_id) REFERENCES characters (id) ON DELETE CASCADE
);

-- Missing table: story_comments

CREATE TABLE story_comments (
	id SERIAL NOT NULL, 
	published_story_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	parent_comment_id INTEGER, 
	content TEXT NOT NULL, 
	is_approved BOOLEAN NOT NULL, 
	is_deleted BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(published_story_id) REFERENCES published_stories (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(parent_comment_id) REFERENCES story_comments (id) ON DELETE CASCADE
);

-- Missing table: story_lore_item_associations

CREATE TABLE story_lore_item_associations (
	id SERIAL NOT NULL, 
	story_id INTEGER NOT NULL, 
	lore_item_id INTEGER NOT NULL, 
	roles JSON NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(story_id) REFERENCES stories (id) ON DELETE CASCADE, 
	FOREIGN KEY(lore_item_id) REFERENCES lore_items (id) ON DELETE CASCADE
);

-- Missing table: story_ratings

CREATE TABLE story_ratings (
	id SERIAL NOT NULL, 
	published_story_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	rating INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT unique_user_story_rating UNIQUE (published_story_id, user_id), 
	CONSTRAINT valid_rating_range CHECK (rating >= 1 AND rating <= 5), 
	FOREIGN KEY(published_story_id) REFERENCES published_stories (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Missing table: user_transactions

CREATE TABLE user_transactions (
	id SERIAL NOT NULL, 
	user_account_id INTEGER NOT NULL, 
	transaction_type VARCHAR(20) NOT NULL, 
	amount DECIMAL(10, 4) NOT NULL, 
	balance_after DECIMAL(10, 4) NOT NULL, 
	description TEXT, 
	ai_cost_log_id INTEGER, 
	credit_package_id INTEGER, 
	payment_reference VARCHAR(255), 
	transaction_metadata JSONB, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_non_zero_amount CHECK (amount != 0), 
	FOREIGN KEY(user_account_id) REFERENCES user_accounts (id) ON DELETE CASCADE, 
	FOREIGN KEY(ai_cost_log_id) REFERENCES ai_call_logs (id) ON DELETE SET NULL, 
	FOREIGN KEY(credit_package_id) REFERENCES credit_packages (id) ON DELETE SET NULL
);

-- Missing table: forum_votes

CREATE TABLE forum_votes (
	id SERIAL NOT NULL, 
	post_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	vote_type vote_type_enum NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_vote_post_user UNIQUE (post_id, user_id), 
	FOREIGN KEY(post_id) REFERENCES forum_posts (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Missing table: scene_character_associations

CREATE TABLE scene_character_associations (
	id SERIAL NOT NULL, 
	scene_id INTEGER NOT NULL, 
	character_id INTEGER NOT NULL, 
	roles JSON NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(scene_id) REFERENCES scenes (id) ON DELETE CASCADE, 
	FOREIGN KEY(character_id) REFERENCES characters (id) ON DELETE CASCADE
);

-- Missing table: scene_location_associations

CREATE TABLE scene_location_associations (
	id SERIAL NOT NULL, 
	scene_id INTEGER NOT NULL, 
	location_id INTEGER NOT NULL, 
	roles JSON NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(scene_id) REFERENCES scenes (id) ON DELETE CASCADE, 
	FOREIGN KEY(location_id) REFERENCES locations (id) ON DELETE CASCADE
);

-- Missing table: scene_lore_item_associations

CREATE TABLE scene_lore_item_associations (
	id SERIAL NOT NULL, 
	scene_id INTEGER NOT NULL, 
	lore_item_id INTEGER NOT NULL, 
	roles JSON NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(scene_id) REFERENCES scenes (id) ON DELETE CASCADE, 
	FOREIGN KEY(lore_item_id) REFERENCES lore_items (id) ON DELETE CASCADE
);

-- Missing column: acts.ai_summary
ALTER TABLE public.acts ADD COLUMN ai_summary TEXT;

-- Missing column: acts.current_image_id
ALTER TABLE public.acts ADD COLUMN current_image_id INTEGER;

-- Missing column: acts.image_prompt_definition
ALTER TABLE public.acts ADD COLUMN image_prompt_definition TEXT;

-- REVIEW TYPE: acts.created_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: acts.updated_at code=DATETIME db=TIMESTAMP
-- Missing column: ai_call_logs.input_prompt
ALTER TABLE public.ai_call_logs ADD COLUMN input_prompt TEXT;

-- Missing column: ai_call_logs.model_config_id
ALTER TABLE public.ai_call_logs ADD COLUMN model_config_id INTEGER;

-- REVIEW TYPE: ai_call_logs.created_at code=DATETIME db=TIMESTAMP
-- Missing column: characters.age_category
ALTER TABLE public.characters ADD COLUMN age_category VARCHAR(50);

-- Missing column: characters.core_motivation
ALTER TABLE public.characters ADD COLUMN core_motivation VARCHAR(255);

-- Missing column: characters.core_motivations
ALTER TABLE public.characters ADD COLUMN core_motivations JSON;

-- Missing column: characters.first_meeting_message
ALTER TABLE public.characters ADD COLUMN first_meeting_message TEXT;

-- Missing column: characters.gender
ALTER TABLE public.characters ADD COLUMN gender VARCHAR(50);

-- Missing column: characters.generated_narrative
ALTER TABLE public.characters ADD COLUMN generated_narrative TEXT;

-- Missing column: characters.genre
ALTER TABLE public.characters ADD COLUMN genre VARCHAR(100);

-- Missing column: characters.genre_specific_answers
ALTER TABLE public.characters ADD COLUMN genre_specific_answers JSON;

-- Missing column: characters.importance_rating
ALTER TABLE public.characters ADD COLUMN importance_rating INTEGER;

-- Missing column: characters.is_ai_generated
ALTER TABLE public.characters ADD COLUMN is_ai_generated BOOLEAN;

-- Missing column: characters.key_relationships
ALTER TABLE public.characters ADD COLUMN key_relationships JSON;

-- Missing column: characters.narrative_filter_results
ALTER TABLE public.characters ADD COLUMN narrative_filter_results JSON;

-- Missing column: characters.next_quest_scenario
ALTER TABLE public.characters ADD COLUMN next_quest_scenario TEXT;

-- Missing column: characters.physical_attributes
ALTER TABLE public.characters ADD COLUMN physical_attributes JSON;

-- Missing column: characters.profession
ALTER TABLE public.characters ADD COLUMN profession VARCHAR(100);

-- Missing column: characters.relationships
ALTER TABLE public.characters ADD COLUMN relationships TEXT;

-- Missing column: characters.short_backstory
ALTER TABLE public.characters ADD COLUMN short_backstory TEXT;

-- Missing column: characters.species
ALTER TABLE public.characters ADD COLUMN species VARCHAR(100);

-- Missing column: characters.visual_prompt
ALTER TABLE public.characters ADD COLUMN visual_prompt TEXT;

-- REVIEW TYPE: characters.created_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: characters.updated_at code=DATETIME db=TIMESTAMP
-- Missing column: generated_images.aspect_ratio
ALTER TABLE public.generated_images ADD COLUMN aspect_ratio VARCHAR(10);

-- REVIEW TYPE: generated_images.created_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: generated_images.image_uuid code=CHAR(32) db=UUID
-- REVIEW TYPE: job_statuses.created_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: job_statuses.updated_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: location_connections.created_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: location_connections.updated_at code=DATETIME db=TIMESTAMP
-- Missing column: locations.connected_elements
ALTER TABLE public.locations ADD COLUMN connected_elements TEXT;

-- Missing column: locations.cultural_context
ALTER TABLE public.locations ADD COLUMN cultural_context TEXT;

-- Missing column: locations.geography
ALTER TABLE public.locations ADD COLUMN geography TEXT;

-- Missing column: locations.importance_rating
ALTER TABLE public.locations ADD COLUMN importance_rating INTEGER;

-- REVIEW TYPE: locations.created_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: locations.dimension_x code=FLOAT db=DOUBLE PRECISION
-- REVIEW TYPE: locations.dimension_y code=FLOAT db=DOUBLE PRECISION
-- REVIEW TYPE: locations.dimension_z code=FLOAT db=DOUBLE PRECISION
-- REVIEW TYPE: locations.map_x code=FLOAT db=DOUBLE PRECISION
-- REVIEW TYPE: locations.map_y code=FLOAT db=DOUBLE PRECISION
-- REVIEW TYPE: locations.map_z code=FLOAT db=DOUBLE PRECISION
-- REVIEW TYPE: locations.updated_at code=DATETIME db=TIMESTAMP
-- Missing column: lore_items.importance_rating
ALTER TABLE public.lore_items ADD COLUMN importance_rating INTEGER;

-- Missing column: lore_items.related_elements
ALTER TABLE public.lore_items ADD COLUMN related_elements TEXT;

-- REVIEW TYPE: lore_items.created_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: lore_items.updated_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: prompts.created_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: prompts.updated_at code=DATETIME db=TIMESTAMP
-- Missing column: scenes.ai_summary
ALTER TABLE public.scenes ADD COLUMN ai_summary TEXT;

-- Missing column: scenes.image_prompt_definition
ALTER TABLE public.scenes ADD COLUMN image_prompt_definition TEXT;

-- REVIEW TYPE: scenes.created_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: scenes.updated_at code=DATETIME db=TIMESTAMP
-- Missing column: stories.ai_summary
ALTER TABLE public.stories ADD COLUMN ai_summary TEXT;

-- Missing column: stories.current_image_id
ALTER TABLE public.stories ADD COLUMN current_image_id INTEGER;

-- Missing column: stories.image_blob_path
ALTER TABLE public.stories ADD COLUMN image_blob_path VARCHAR(1024);

-- Missing column: stories.image_prompt_definition
ALTER TABLE public.stories ADD COLUMN image_prompt_definition TEXT;

-- Missing column: stories.primary_conflict_type
ALTER TABLE public.stories ADD COLUMN primary_conflict_type VARCHAR(100);

-- Missing column: stories.story_genre
ALTER TABLE public.stories ADD COLUMN story_genre VARCHAR(100);

-- Missing column: stories.story_tone
ALTER TABLE public.stories ADD COLUMN story_tone VARCHAR(100);

-- Missing column: stories.story_type
ALTER TABLE public.stories ADD COLUMN story_type VARCHAR(20) DEFAULT 'advanced' NOT NULL;

-- REVIEW TYPE: stories.created_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: stories.updated_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: story_classes.created_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: story_classes.updated_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: uploaded_documents.processed_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: uploaded_documents.updated_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: uploaded_documents.uploaded_at code=DATETIME db=TIMESTAMP
-- Missing column: users.auth_provider
ALTER TABLE public.users ADD COLUMN auth_provider VARCHAR(50) DEFAULT 'local' NOT NULL;

-- Missing column: users.bonus1
ALTER TABLE public.users ADD COLUMN bonus1 BOOLEAN DEFAULT FALSE NOT NULL;

-- Missing column: users.bonus10
ALTER TABLE public.users ADD COLUMN bonus10 BOOLEAN DEFAULT FALSE NOT NULL;

-- Missing column: users.bonus2
ALTER TABLE public.users ADD COLUMN bonus2 BOOLEAN DEFAULT FALSE NOT NULL;

-- Missing column: users.bonus3
ALTER TABLE public.users ADD COLUMN bonus3 BOOLEAN DEFAULT FALSE NOT NULL;

-- Missing column: users.bonus4
ALTER TABLE public.users ADD COLUMN bonus4 BOOLEAN DEFAULT FALSE NOT NULL;

-- Missing column: users.bonus5
ALTER TABLE public.users ADD COLUMN bonus5 BOOLEAN DEFAULT FALSE NOT NULL;

-- Missing column: users.bonus6
ALTER TABLE public.users ADD COLUMN bonus6 BOOLEAN DEFAULT FALSE NOT NULL;

-- Missing column: users.bonus7
ALTER TABLE public.users ADD COLUMN bonus7 BOOLEAN DEFAULT FALSE NOT NULL;

-- Missing column: users.bonus8
ALTER TABLE public.users ADD COLUMN bonus8 BOOLEAN DEFAULT FALSE NOT NULL;

-- Missing column: users.bonus9
ALTER TABLE public.users ADD COLUMN bonus9 BOOLEAN DEFAULT FALSE NOT NULL;

-- Missing column: users.interview_data
ALTER TABLE public.users ADD COLUMN interview_data JSON;

-- Missing column: users.is_admin
ALTER TABLE public.users ADD COLUMN is_admin BOOLEAN;

-- Missing column: users.profile_picture_url
ALTER TABLE public.users ADD COLUMN profile_picture_url VARCHAR(500);

-- Missing column: users.provider_data
ALTER TABLE public.users ADD COLUMN provider_data JSON;

-- Missing column: users.provider_id
ALTER TABLE public.users ADD COLUMN provider_id VARCHAR(255);

-- Missing column: users.referral_count
ALTER TABLE public.users ADD COLUMN referral_count INTEGER DEFAULT 0 NOT NULL;

-- Missing column: users.referred_by_user_id
ALTER TABLE public.users ADD COLUMN referred_by_user_id INTEGER;

-- Missing column: users.reset_token
ALTER TABLE public.users ADD COLUMN reset_token VARCHAR(255);

-- Missing column: users.reset_token_expires
ALTER TABLE public.users ADD COLUMN reset_token_expires TIMESTAMP WITH TIME ZONE;

-- REVIEW TYPE: users.created_at code=DATETIME db=TIMESTAMP
ALTER TABLE public.users ALTER COLUMN hashed_password DROP NOT NULL;
-- REVIEW TYPE: users.updated_at code=DATETIME db=TIMESTAMP
-- Missing column: worlds.current_image_id
ALTER TABLE public.worlds ADD COLUMN current_image_id INTEGER;

-- Missing column: worlds.image_blob_path
ALTER TABLE public.worlds ADD COLUMN image_blob_path VARCHAR(1024);

-- Missing column: worlds.image_prompt_definition
ALTER TABLE public.worlds ADD COLUMN image_prompt_definition TEXT;

-- Missing column: worlds.is_free_chat_enabled
ALTER TABLE public.worlds ADD COLUMN is_free_chat_enabled BOOLEAN DEFAULT FALSE NOT NULL;

-- Missing column: worlds.is_shadow
ALTER TABLE public.worlds ADD COLUMN is_shadow BOOLEAN DEFAULT 'false' NOT NULL;

-- Missing column: worlds.short_description
ALTER TABLE public.worlds ADD COLUMN short_description TEXT;

-- Missing column: worlds.world_builder_data
ALTER TABLE public.worlds ADD COLUMN world_builder_data JSON;

-- REVIEW TYPE: worlds.created_at code=DATETIME db=TIMESTAMP
-- REVIEW TYPE: worlds.updated_at code=DATETIME db=TIMESTAMP

COMMIT;
