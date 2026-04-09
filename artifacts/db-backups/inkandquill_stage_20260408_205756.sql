--
-- PostgreSQL database dump
--

\restrict SYs6sxL4ETBEpbv3rASBNeVYwgI311hvODct4p2E5UJVHXaw0IKwXeSSYHLS6jI

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: age_target_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.age_target_enum AS ENUM (
    'AGES_2_5',
    'AGES_6_8',
    'AGES_9_12',
    'AGES_13_15',
    'AGES_16_18',
    'ALL_AGES'
);


--
-- Name: ai_model_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.ai_model_type_enum AS ENUM (
    'GENERATION',
    'EMBEDDING'
);


--
-- Name: ai_provider_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.ai_provider_enum AS ENUM (
    'OPENROUTER',
    'OPENAI',
    'RUNPOD'
);


--
-- Name: associationtype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.associationtype AS ENUM (
    'STORY',
    'WORLD',
    'CHARACTER',
    'LOCATION',
    'LORE_ITEM'
);


--
-- Name: blogpoststatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.blogpoststatus AS ENUM (
    'DRAFT',
    'PUBLISHED',
    'ARCHIVED'
);


--
-- Name: commentstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.commentstatus AS ENUM (
    'PENDING',
    'APPROVED',
    'REJECTED',
    'DELETED'
);


--
-- Name: ctaposition; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.ctaposition AS ENUM (
    'HOME_MAIN_TOP',
    'HOME_WELCOME_TOP',
    'HOME_WELCOME_BOTTOM',
    'HOME_QUICK_ACTIONS_TOP',
    'HOME_QUICK_ACTIONS_BOTTOM',
    'HOME_LOGIN_REGISTER_TOP',
    'HOME_LOGIN_REGISTER_BOTTOM',
    'HOME_BLOG_SECTION_TOP',
    'HOME_BLOG_SECTION_BOTTOM',
    'HOME_MAIN_BOTTOM',
    'HOME_SIDEBAR_TOP',
    'HOME_SIDEBAR_BOTTOM',
    'HOME_AI_CHAT_WORLDS_TOP',
    'HOME_AI_CHAT_WORLDS_BOTTOM',
    'HOME_PUBLISHED_STORIES_TOP',
    'HOME_PUBLISHED_STORIES_BOTTOM',
    'HOME_GENERATED_IMAGES_TOP',
    'HOME_GENERATED_IMAGES_BOTTOM',
    'STORY_LIST_TOP',
    'WORLD_LIST_TOP',
    'BLOG_SIDEBAR'
);


--
-- Name: ctastyle; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.ctastyle AS ENUM (
    'GRADIENT',
    'SOLID',
    'BORDERED',
    'MINIMAL',
    'HERO'
);


--
-- Name: document_status_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.document_status_enum AS ENUM (
    'UPLOADED',
    'PENDING',
    'PROCESSING_TEXT',
    'CHUNKING',
    'PREPARING_CONTEXT',
    'STORING_CONTEXT',
    'COMPLETED',
    'ERROR'
);


--
-- Name: job_state_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.job_state_enum AS ENUM (
    'PENDING',
    'RUNNING',
    'COMPLETED',
    'FAILED'
);


--
-- Name: job_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.job_type_enum AS ENUM (
    'WORLD_EXTRACTION_FROM_DOC',
    'DOCUMENT_CONTEXT_PROCESSING',
    'WORLD_IMPORT_FROM_TITLE',
    'IMAGE_GENERATION'
);


--
-- Name: linktype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.linktype AS ENUM (
    'CHARACTER',
    'LOCATION',
    'LORE_ITEM'
);


--
-- Name: location_scale_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.location_scale_enum AS ENUM (
    'REGION',
    'CITY',
    'BUILDING',
    'ROOM',
    'AREA',
    'OBJECT',
    'POINT',
    'OTHER'
);


--
-- Name: lore_item_category_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.lore_item_category_enum AS ENUM (
    'MAGIC_SYSTEM',
    'HISTORICAL_EVENT',
    'ARTIFACT',
    'DEITY',
    'CREATURE',
    'FACTION_ORGANIZATION',
    'CULTURE_CUSTOM',
    'TECHNOLOGY',
    'PHILOSOPHY_BELIEF',
    'OTHER_LORE'
);


--
-- Name: prompt_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.prompt_type_enum AS ENUM (
    'GENERAL',
    'CHARACTER_DEVELOPMENT',
    'PLOT_POINT',
    'WORLD_BUILDING',
    'DIALOGUE',
    'SCENE_GENERATION',
    'SYSTEM',
    'ACT',
    'STORY',
    'IMAGE_STYLE',
    'CHARACTER_ROLE',
    'STORY_GENRE',
    'STORY_TONE',
    'STORY_CONFLICT',
    'QUICK_AI',
    'OTHER'
);


--
-- Name: source_element_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.source_element_type_enum AS ENUM (
    'USER_UPLOADED',
    'CHARACTER_LORE',
    'LOCATION_LORE',
    'LORE_ITEM_LORE'
);


--
-- Name: subscriptionfrequency; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.subscriptionfrequency AS ENUM (
    'IMMEDIATE',
    'DAILY',
    'WEEKLY',
    'MONTHLY'
);


--
-- Name: subscriptionstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.subscriptionstatus AS ENUM (
    'ACTIVE',
    'PENDING',
    'UNSUBSCRIBED',
    'BOUNCED',
    'COMPLAINED'
);


--
-- Name: thread_status_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.thread_status_enum AS ENUM (
    'OPEN',
    'CLOSED',
    'LOCKED',
    'PINNED'
);


--
-- Name: vote_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.vote_type_enum AS ENUM (
    'UPVOTE',
    'DOWNVOTE'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: act_character_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.act_character_associations (
    id integer NOT NULL,
    act_id integer NOT NULL,
    character_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: act_character_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.act_character_associations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: act_character_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.act_character_associations_id_seq OWNED BY public.act_character_associations.id;


--
-- Name: act_location_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.act_location_associations (
    id integer NOT NULL,
    act_id integer NOT NULL,
    location_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: act_location_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.act_location_associations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: act_location_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.act_location_associations_id_seq OWNED BY public.act_location_associations.id;


--
-- Name: act_lore_item_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.act_lore_item_associations (
    id integer NOT NULL,
    act_id integer NOT NULL,
    lore_item_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: act_lore_item_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.act_lore_item_associations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: act_lore_item_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.act_lore_item_associations_id_seq OWNED BY public.act_lore_item_associations.id;


--
-- Name: acts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.acts (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    act_number integer NOT NULL,
    act_summary text,
    ai_summary text,
    writer_notes text,
    image_prompt_definition text,
    system_prompt_id integer,
    story_class_id integer,
    story_id integer NOT NULL,
    current_image_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: acts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.acts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: acts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.acts_id_seq OWNED BY public.acts.id;


--
-- Name: ai_call_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ai_call_logs (
    id integer NOT NULL,
    job_id character varying(255),
    user_id integer NOT NULL,
    model_config_id integer,
    input_prompt text,
    call_type character varying(50) NOT NULL,
    model_name character varying(255) NOT NULL,
    object_id integer,
    prompt_tokens integer NOT NULL,
    completion_tokens integer NOT NULL,
    total_tokens integer NOT NULL,
    calculated_cost_usd numeric(10,8) NOT NULL,
    duration_ms integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: ai_call_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ai_call_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ai_call_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ai_call_logs_id_seq OWNED BY public.ai_call_logs.id;


--
-- Name: ai_model_configurations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ai_model_configurations (
    id integer NOT NULL,
    display_name character varying(100) NOT NULL,
    model_name character varying(255) NOT NULL,
    description text,
    provider public.ai_provider_enum NOT NULL,
    model_type public.ai_model_type_enum NOT NULL,
    is_active boolean NOT NULL,
    is_public_chat_default boolean,
    max_tokens integer NOT NULL,
    temperature double precision NOT NULL,
    top_p double precision NOT NULL,
    presence_penalty double precision NOT NULL,
    frequency_penalty double precision NOT NULL,
    is_json_mode boolean NOT NULL,
    provider_cost_input_usd_pm double precision NOT NULL,
    provider_cost_output_usd_pm double precision NOT NULL,
    user_price_input_usd_pm double precision NOT NULL,
    user_price_output_usd_pm double precision NOT NULL
);


--
-- Name: ai_model_configurations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ai_model_configurations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ai_model_configurations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ai_model_configurations_id_seq OWNED BY public.ai_model_configurations.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: anonymous_user_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.anonymous_user_sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    session_token character varying(64) NOT NULL,
    ip_address character varying(45),
    browser_fingerprint character varying(32),
    user_agent text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    last_seen_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean NOT NULL
);


--
-- Name: anonymous_user_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.anonymous_user_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: anonymous_user_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.anonymous_user_sessions_id_seq OWNED BY public.anonymous_user_sessions.id;


--
-- Name: blog_analytics_summary; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blog_analytics_summary (
    id integer NOT NULL,
    post_id integer NOT NULL,
    date date NOT NULL,
    unique_views integer NOT NULL,
    total_views integer NOT NULL,
    new_likes integer NOT NULL,
    new_comments integer NOT NULL,
    avg_read_time integer NOT NULL,
    bounce_rate numeric(5,2) NOT NULL,
    social_shares integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: blog_analytics_summary_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blog_analytics_summary_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blog_analytics_summary_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blog_analytics_summary_id_seq OWNED BY public.blog_analytics_summary.id;


--
-- Name: blog_author_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blog_author_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    bio text,
    profile_image_url character varying(500),
    website_url character varying(255),
    twitter_handle character varying(50),
    instagram_handle character varying(50),
    linkedin_url character varying(255),
    allow_comments_default boolean NOT NULL,
    auto_publish boolean NOT NULL,
    email_notifications boolean NOT NULL,
    total_posts integer NOT NULL,
    total_views integer NOT NULL,
    total_likes integer NOT NULL,
    follower_count integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: blog_author_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blog_author_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blog_author_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blog_author_profiles_id_seq OWNED BY public.blog_author_profiles.id;


--
-- Name: blog_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blog_categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    slug character varying(100) NOT NULL,
    description text,
    color character varying(7),
    icon character varying(50),
    post_count integer NOT NULL,
    display_order integer NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: blog_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blog_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blog_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blog_categories_id_seq OWNED BY public.blog_categories.id;


--
-- Name: blog_comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blog_comments (
    id integer NOT NULL,
    post_id integer NOT NULL,
    author_id integer NOT NULL,
    parent_comment_id integer,
    content text NOT NULL,
    status public.commentstatus NOT NULL,
    like_count integer NOT NULL,
    reply_count integer NOT NULL,
    is_author_reply boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


--
-- Name: blog_comments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blog_comments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blog_comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blog_comments_id_seq OWNED BY public.blog_comments.id;


--
-- Name: blog_content_links; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blog_content_links (
    id integer NOT NULL,
    post_id integer NOT NULL,
    link_type public.linktype NOT NULL,
    link_id integer NOT NULL,
    link_text character varying(255),
    link_context text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: blog_content_links_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blog_content_links_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blog_content_links_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blog_content_links_id_seq OWNED BY public.blog_content_links.id;


--
-- Name: blog_follows; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blog_follows (
    id integer NOT NULL,
    author_id integer NOT NULL,
    follower_id integer NOT NULL,
    notification_enabled boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: blog_follows_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blog_follows_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blog_follows_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blog_follows_id_seq OWNED BY public.blog_follows.id;


--
-- Name: blog_likes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blog_likes (
    id integer NOT NULL,
    post_id integer NOT NULL,
    user_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: blog_likes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blog_likes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blog_likes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blog_likes_id_seq OWNED BY public.blog_likes.id;


--
-- Name: blog_post_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blog_post_associations (
    id integer NOT NULL,
    post_id integer NOT NULL,
    association_type public.associationtype NOT NULL,
    association_id integer NOT NULL,
    association_title character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: blog_post_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blog_post_associations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blog_post_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blog_post_associations_id_seq OWNED BY public.blog_post_associations.id;


--
-- Name: blog_post_tags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blog_post_tags (
    id integer NOT NULL,
    post_id integer NOT NULL,
    tag_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: blog_post_tags_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blog_post_tags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blog_post_tags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blog_post_tags_id_seq OWNED BY public.blog_post_tags.id;


--
-- Name: blog_posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blog_posts (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    slug character varying(255) NOT NULL,
    content text NOT NULL,
    excerpt text,
    featured_image_url character varying(500),
    status public.blogpoststatus NOT NULL,
    author_id integer NOT NULL,
    category_id integer,
    view_count integer NOT NULL,
    like_count integer NOT NULL,
    comment_count integer NOT NULL,
    meta_title character varying(255),
    meta_description text,
    meta_keywords text,
    og_title character varying(255),
    og_description text,
    og_image_url character varying(500),
    is_featured boolean NOT NULL,
    allow_comments boolean NOT NULL,
    is_ai_generated boolean NOT NULL,
    published_at timestamp with time zone,
    last_viewed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    search_vector tsvector
);


--
-- Name: blog_posts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blog_posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blog_posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blog_posts_id_seq OWNED BY public.blog_posts.id;


--
-- Name: blog_subscriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blog_subscriptions (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    user_id integer,
    status public.subscriptionstatus NOT NULL,
    frequency public.subscriptionfrequency NOT NULL,
    include_categories text,
    include_tags text,
    confirmation_token character varying(255),
    unsubscribe_token character varying(255) NOT NULL,
    last_sent_at timestamp with time zone,
    total_emails_sent integer NOT NULL,
    last_opened_at timestamp with time zone,
    open_count integer NOT NULL,
    click_count integer NOT NULL,
    bounce_count integer NOT NULL,
    complaint_count integer NOT NULL,
    last_bounce_at timestamp with time zone,
    last_complaint_at timestamp with time zone,
    source character varying(100),
    ip_address character varying(45),
    user_agent text,
    confirmed_at timestamp with time zone,
    unsubscribed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: blog_subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blog_subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blog_subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blog_subscriptions_id_seq OWNED BY public.blog_subscriptions.id;


--
-- Name: blog_tags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blog_tags (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL,
    description text,
    usage_count integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: blog_tags_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blog_tags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blog_tags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blog_tags_id_seq OWNED BY public.blog_tags.id;


--
-- Name: blog_views; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blog_views (
    id integer NOT NULL,
    post_id integer NOT NULL,
    user_id integer,
    ip_address inet,
    user_agent text,
    referrer_url character varying(500),
    session_id character varying(100),
    view_duration integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: blog_views_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blog_views_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blog_views_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blog_views_id_seq OWNED BY public.blog_views.id;


--
-- Name: brainstorm_favorites; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.brainstorm_favorites (
    id integer NOT NULL,
    user_id integer NOT NULL,
    session_id integer NOT NULL,
    concept_id character varying(50) NOT NULL,
    concept_data text NOT NULL,
    is_selected boolean,
    created_at timestamp without time zone
);


--
-- Name: brainstorm_favorites_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.brainstorm_favorites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: brainstorm_favorites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.brainstorm_favorites_id_seq OWNED BY public.brainstorm_favorites.id;


--
-- Name: brainstorm_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.brainstorm_sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    interview_response_id integer NOT NULL,
    session_name character varying(200),
    generated_concepts text NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: brainstorm_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.brainstorm_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: brainstorm_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.brainstorm_sessions_id_seq OWNED BY public.brainstorm_sessions.id;


--
-- Name: brainstorm_stories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.brainstorm_stories (
    id integer NOT NULL,
    user_id integer NOT NULL,
    favorite_id integer NOT NULL,
    story_id integer,
    title character varying(200) NOT NULL,
    three_act_structure text NOT NULL,
    created_at timestamp without time zone
);


--
-- Name: brainstorm_stories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.brainstorm_stories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: brainstorm_stories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.brainstorm_stories_id_seq OWNED BY public.brainstorm_stories.id;


--
-- Name: care_circle_families; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.care_circle_families (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    created_by_user_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    join_code character varying(20) NOT NULL
);


--
-- Name: care_circle_families_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.care_circle_families_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: care_circle_families_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.care_circle_families_id_seq OWNED BY public.care_circle_families.id;


--
-- Name: care_circle_family_memberships; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.care_circle_family_memberships (
    id integer NOT NULL,
    family_id integer NOT NULL,
    user_id integer NOT NULL,
    role character varying(50) NOT NULL,
    is_primary boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: care_circle_family_memberships_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.care_circle_family_memberships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: care_circle_family_memberships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.care_circle_family_memberships_id_seq OWNED BY public.care_circle_family_memberships.id;


--
-- Name: care_circle_patient_content_cards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.care_circle_patient_content_cards (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    provider_key character varying(120) NOT NULL,
    title character varying(255) NOT NULL,
    body text NOT NULL,
    card_kind character varying(50) NOT NULL,
    display_order integer NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    rendered_html text
);


--
-- Name: care_circle_patient_content_cards_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.care_circle_patient_content_cards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: care_circle_patient_content_cards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.care_circle_patient_content_cards_id_seq OWNED BY public.care_circle_patient_content_cards.id;


--
-- Name: care_circle_patient_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.care_circle_patient_profiles (
    id integer NOT NULL,
    family_id integer NOT NULL,
    created_by_user_id integer,
    display_name character varying(255) NOT NULL,
    stage character varying(50) NOT NULL,
    access_state character varying(50) NOT NULL,
    timezone character varying(100) NOT NULL,
    delivery_time character varying(20),
    delivery_days json NOT NULL,
    auth_image_keys json NOT NULL,
    preferences json NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: care_circle_patient_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.care_circle_patient_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: care_circle_patient_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.care_circle_patient_profiles_id_seq OWNED BY public.care_circle_patient_profiles.id;


--
-- Name: care_circle_provider_catalog; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.care_circle_provider_catalog (
    id integer NOT NULL,
    provider_key character varying(120) NOT NULL,
    label character varying(255) NOT NULL,
    icon character varying(20),
    category character varying(100) NOT NULL,
    enabled boolean DEFAULT true NOT NULL,
    display_order integer NOT NULL,
    patient_visible boolean DEFAULT true NOT NULL,
    family_visible boolean DEFAULT true NOT NULL,
    source_app character varying(100) DEFAULT 'daily_newsletter'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: care_circle_provider_catalog_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.care_circle_provider_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: care_circle_provider_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.care_circle_provider_catalog_id_seq OWNED BY public.care_circle_provider_catalog.id;


--
-- Name: care_circle_provider_patient_configs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.care_circle_provider_patient_configs (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    provider_key character varying(120) NOT NULL,
    is_enabled boolean NOT NULL,
    schedule_expression character varying(100),
    custom_parameters json NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: care_circle_provider_patient_configs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.care_circle_provider_patient_configs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: care_circle_provider_patient_configs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.care_circle_provider_patient_configs_id_seq OWNED BY public.care_circle_provider_patient_configs.id;


--
-- Name: care_circle_provider_run_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.care_circle_provider_run_logs (
    id integer NOT NULL,
    provider_key character varying(120) NOT NULL,
    patient_id integer,
    family_id integer,
    status character varying(50) NOT NULL,
    error_message text,
    execution_time_ms integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: care_circle_provider_run_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.care_circle_provider_run_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: care_circle_provider_run_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.care_circle_provider_run_logs_id_seq OWNED BY public.care_circle_provider_run_logs.id;


--
-- Name: care_circle_provider_session_outputs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.care_circle_provider_session_outputs (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    provider_key character varying(120) NOT NULL,
    run_log_id integer,
    output_json json NOT NULL,
    session_date timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: care_circle_provider_session_outputs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.care_circle_provider_session_outputs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: care_circle_provider_session_outputs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.care_circle_provider_session_outputs_id_seq OWNED BY public.care_circle_provider_session_outputs.id;


--
-- Name: characters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.characters (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    gender character varying(50),
    species character varying(100),
    description text,
    personality_traits text,
    backstory text,
    image_prompt_definition text,
    image_blob_path character varying(1024),
    world_id integer NOT NULL,
    current_location_id integer,
    placement_note text,
    current_image_id integer,
    importance_rating integer,
    relationships text,
    core_motivation character varying(255),
    core_motivations json,
    physical_attributes json,
    key_relationships json,
    genre character varying(100),
    genre_specific_answers json,
    generated_narrative text,
    is_ai_generated boolean,
    next_quest_scenario text,
    first_meeting_message text,
    age_category character varying(50),
    profession character varying(100),
    short_backstory text,
    visual_prompt text,
    narrative_filter_results json,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: characters_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.characters_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: characters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.characters_id_seq OWNED BY public.characters.id;


--
-- Name: chat_messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_messages (
    id integer NOT NULL,
    session_id integer NOT NULL,
    role character varying(20) NOT NULL,
    content text NOT NULL,
    full_context json,
    element_type character varying(50),
    element_id integer,
    cost_log_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: chat_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chat_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chat_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chat_messages_id_seq OWNED BY public.chat_messages.id;


--
-- Name: chat_samples; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_samples (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    prompt_text text NOT NULL,
    category character varying(50),
    is_active boolean NOT NULL,
    sort_order integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: chat_samples_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chat_samples_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chat_samples_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chat_samples_id_seq OWNED BY public.chat_samples.id;


--
-- Name: chat_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_sessions (
    id integer NOT NULL,
    world_id integer NOT NULL,
    user_id integer NOT NULL,
    title character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: chat_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chat_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chat_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chat_sessions_id_seq OWNED BY public.chat_sessions.id;


--
-- Name: credit_packages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.credit_packages (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    credit_amount numeric(10,4) NOT NULL,
    price_usd numeric(10,2) NOT NULL,
    bonus_percentage numeric(5,2) NOT NULL,
    is_active boolean NOT NULL,
    display_order integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: credit_packages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.credit_packages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: credit_packages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.credit_packages_id_seq OWNED BY public.credit_packages.id;


--
-- Name: cta_contents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cta_contents (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    subtitle character varying(500),
    content text,
    "position" public.ctaposition NOT NULL,
    sort_order integer,
    style public.ctastyle,
    background_color character varying(200),
    text_color character varying(50),
    icon_class character varying(100),
    features text,
    primary_button_text character varying(100),
    primary_button_url character varying(500),
    primary_button_icon character varying(50),
    secondary_button_text character varying(100),
    secondary_button_url character varying(500),
    secondary_button_icon character varying(50),
    show_for_anonymous boolean,
    show_for_authenticated boolean,
    show_for_admin boolean,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    campaign_name character varying(100),
    utm_source character varying(100),
    utm_medium character varying(100),
    utm_campaign character varying(100)
);


--
-- Name: cta_contents_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cta_contents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cta_contents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cta_contents_id_seq OWNED BY public.cta_contents.id;


--
-- Name: forum_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.forum_categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    slug character varying(100) NOT NULL,
    sort_order integer NOT NULL,
    is_active boolean NOT NULL,
    icon character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: forum_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.forum_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: forum_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.forum_categories_id_seq OWNED BY public.forum_categories.id;


--
-- Name: forum_posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.forum_posts (
    id integer NOT NULL,
    content text NOT NULL,
    content_html text,
    thread_id integer NOT NULL,
    user_id integer NOT NULL,
    parent_post_id integer,
    character_id integer,
    location_id integer,
    upvote_count integer NOT NULL,
    downvote_count integer NOT NULL,
    score integer NOT NULL,
    edit_count integer NOT NULL,
    edited_at timestamp with time zone,
    edited_by_id integer,
    is_deleted boolean NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by_id integer,
    deletion_reason character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: forum_posts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.forum_posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: forum_posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.forum_posts_id_seq OWNED BY public.forum_posts.id;


--
-- Name: forum_subscriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.forum_subscriptions (
    id integer NOT NULL,
    thread_id integer NOT NULL,
    user_id integer NOT NULL,
    notify_email boolean NOT NULL,
    notify_in_app boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: forum_subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.forum_subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: forum_subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.forum_subscriptions_id_seq OWNED BY public.forum_subscriptions.id;


--
-- Name: forum_threads; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.forum_threads (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    slug character varying(255) NOT NULL,
    status public.thread_status_enum NOT NULL,
    category_id integer NOT NULL,
    user_id integer NOT NULL,
    world_id integer,
    story_id integer,
    view_count integer NOT NULL,
    post_count integer NOT NULL,
    last_post_at timestamp with time zone,
    last_post_by_id integer,
    is_pinned boolean NOT NULL,
    is_locked boolean NOT NULL,
    is_deleted boolean NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: forum_threads_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.forum_threads_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: forum_threads_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.forum_threads_id_seq OWNED BY public.forum_threads.id;


--
-- Name: forum_votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.forum_votes (
    id integer NOT NULL,
    post_id integer NOT NULL,
    user_id integer NOT NULL,
    vote_type public.vote_type_enum NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: forum_votes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.forum_votes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: forum_votes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.forum_votes_id_seq OWNED BY public.forum_votes.id;


--
-- Name: generated_images; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.generated_images (
    id integer NOT NULL,
    image_uuid uuid NOT NULL,
    blob_path character varying(1024) NOT NULL,
    prompt text NOT NULL,
    revised_prompt text,
    element_type character varying(50) NOT NULL,
    associated_element_id integer NOT NULL,
    aspect_ratio character varying(10),
    user_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: generated_images_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.generated_images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: generated_images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.generated_images_id_seq OWNED BY public.generated_images.id;


--
-- Name: job_statuses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.job_statuses (
    id integer NOT NULL,
    job_id character varying(255) NOT NULL,
    job_type public.job_type_enum NOT NULL,
    state public.job_state_enum NOT NULL,
    status_message character varying(512),
    result_message text,
    user_id integer NOT NULL,
    world_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: job_statuses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.job_statuses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: job_statuses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.job_statuses_id_seq OWNED BY public.job_statuses.id;


--
-- Name: location_connections; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.location_connections (
    from_location_id integer NOT NULL,
    to_location_id integer NOT NULL,
    path_description text,
    reverse_path_description text,
    is_bidirectional boolean NOT NULL,
    dm_notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: locations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.locations (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    atmosphere character varying(255),
    significance text,
    image_prompt_definition text,
    image_blob_path character varying(1024),
    scale public.location_scale_enum,
    parent_location_id integer,
    map_x double precision,
    map_y double precision,
    map_z double precision,
    dimension_x double precision,
    dimension_y double precision,
    dimension_z double precision,
    dimension_unit character varying(50),
    current_image_id integer,
    geography text,
    cultural_context text,
    importance_rating integer,
    connected_elements text,
    world_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: locations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: locations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.locations_id_seq OWNED BY public.locations.id;


--
-- Name: lore_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.lore_items (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    category public.lore_item_category_enum NOT NULL,
    image_prompt_definition text,
    image_blob_path character varying(1024),
    world_id integer NOT NULL,
    current_location_id integer,
    placement_note text,
    current_image_id integer,
    importance_rating integer,
    related_elements text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: lore_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.lore_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: lore_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.lore_items_id_seq OWNED BY public.lore_items.id;


--
-- Name: prompts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.prompts (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    prompt_content text NOT NULL,
    reason_to_use text,
    comment text,
    is_active boolean NOT NULL,
    prompt_type public.prompt_type_enum NOT NULL,
    age_target public.age_target_enum NOT NULL,
    user_id integer,
    last_updated_by_user_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: prompts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.prompts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: prompts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.prompts_id_seq OWNED BY public.prompts.id;


--
-- Name: published_stories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.published_stories (
    id integer NOT NULL,
    story_id integer NOT NULL,
    user_id integer NOT NULL,
    published_url character varying(1024) NOT NULL,
    filename character varying(255) NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    word_count integer,
    is_public boolean NOT NULL,
    is_featured boolean NOT NULL,
    view_count integer NOT NULL,
    like_count integer NOT NULL,
    comment_count integer NOT NULL,
    average_rating double precision,
    published_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    search_vector text
);


--
-- Name: published_stories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.published_stories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: published_stories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.published_stories_id_seq OWNED BY public.published_stories.id;


--
-- Name: refresh_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.refresh_tokens (
    id integer NOT NULL,
    token character varying(255) NOT NULL,
    user_id integer NOT NULL,
    issued_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    revoked_at timestamp with time zone,
    ip_address character varying(45),
    user_agent character varying(255)
);


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.refresh_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.refresh_tokens_id_seq OWNED BY public.refresh_tokens.id;


--
-- Name: scene_character_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scene_character_associations (
    id integer NOT NULL,
    scene_id integer NOT NULL,
    character_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: scene_character_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.scene_character_associations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: scene_character_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.scene_character_associations_id_seq OWNED BY public.scene_character_associations.id;


--
-- Name: scene_location_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scene_location_associations (
    id integer NOT NULL,
    scene_id integer NOT NULL,
    location_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: scene_location_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.scene_location_associations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: scene_location_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.scene_location_associations_id_seq OWNED BY public.scene_location_associations.id;


--
-- Name: scene_lore_item_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scene_lore_item_associations (
    id integer NOT NULL,
    scene_id integer NOT NULL,
    lore_item_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: scene_lore_item_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.scene_lore_item_associations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: scene_lore_item_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.scene_lore_item_associations_id_seq OWNED BY public.scene_lore_item_associations.id;


--
-- Name: scenes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scenes (
    id integer NOT NULL,
    scene_number integer NOT NULL,
    title character varying(255),
    summary text,
    ai_summary text,
    content text,
    characters_present text,
    plot_points text,
    mood character varying(100),
    image_prompt_definition text,
    act_id integer NOT NULL,
    story_class_id integer,
    current_image_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: scenes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.scenes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: scenes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.scenes_id_seq OWNED BY public.scenes.id;


--
-- Name: social_share_daily_summaries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.social_share_daily_summaries (
    id uuid NOT NULL,
    user_id integer NOT NULL,
    date timestamp without time zone NOT NULL,
    total_shares integer NOT NULL,
    coins_earned integer NOT NULL,
    max_coins_reached boolean NOT NULL,
    facebook_shares integer NOT NULL,
    twitter_shares integer NOT NULL,
    linkedin_shares integer NOT NULL,
    reddit_shares integer NOT NULL,
    whatsapp_shares integer NOT NULL,
    email_shares integer NOT NULL,
    copy_link_shares integer NOT NULL,
    pinterest_shares integer NOT NULL,
    telegram_shares integer NOT NULL,
    image_preview_shares integer NOT NULL,
    published_story_shares integer NOT NULL,
    ai_public_chat_shares integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: social_shares; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.social_shares (
    id uuid NOT NULL,
    user_id integer,
    content_type character varying(50) NOT NULL,
    content_id character varying(255) NOT NULL,
    content_title character varying(500),
    content_url text NOT NULL,
    platform character varying(50) NOT NULL,
    shared_text text,
    shared_hashtags character varying(500),
    ip_address character varying(45),
    user_agent text,
    referrer text,
    coin_awarded boolean NOT NULL,
    coin_amount integer NOT NULL,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: stories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stories (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    short_description text,
    ai_summary text,
    user_id integer NOT NULL,
    world_id integer NOT NULL,
    story_type character varying(20) DEFAULT 'advanced'::character varying NOT NULL,
    image_prompt_definition text,
    image_blob_path character varying(1024),
    current_image_id integer,
    story_genre character varying(100),
    story_tone character varying(100),
    primary_conflict_type character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: stories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.stories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: stories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.stories_id_seq OWNED BY public.stories.id;


--
-- Name: story_character_association; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.story_character_association (
    story_id integer NOT NULL,
    character_id integer NOT NULL,
    role_in_story character varying(255)
);


--
-- Name: story_character_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.story_character_associations (
    id integer NOT NULL,
    story_id integer NOT NULL,
    character_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: story_character_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.story_character_associations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: story_character_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.story_character_associations_id_seq OWNED BY public.story_character_associations.id;


--
-- Name: story_chat_messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.story_chat_messages (
    id integer NOT NULL,
    session_id integer NOT NULL,
    role character varying(20) NOT NULL,
    content text NOT NULL,
    full_context json,
    story_context json,
    target_element character varying(50),
    target_element_id integer,
    cost_log_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: story_chat_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.story_chat_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: story_chat_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.story_chat_messages_id_seq OWNED BY public.story_chat_messages.id;


--
-- Name: story_chat_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.story_chat_sessions (
    id integer NOT NULL,
    story_id integer NOT NULL,
    user_id integer NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    focus_area character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: story_chat_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.story_chat_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: story_chat_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.story_chat_sessions_id_seq OWNED BY public.story_chat_sessions.id;


--
-- Name: story_classes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.story_classes (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(500),
    color character varying(7) NOT NULL,
    world_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: story_classes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.story_classes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: story_classes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.story_classes_id_seq OWNED BY public.story_classes.id;


--
-- Name: story_comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.story_comments (
    id integer NOT NULL,
    published_story_id integer NOT NULL,
    user_id integer NOT NULL,
    parent_comment_id integer,
    content text NOT NULL,
    is_approved boolean NOT NULL,
    is_deleted boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: story_comments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.story_comments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: story_comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.story_comments_id_seq OWNED BY public.story_comments.id;


--
-- Name: story_location_association; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.story_location_association (
    story_id integer NOT NULL,
    location_id integer NOT NULL,
    significance_to_story text
);


--
-- Name: story_location_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.story_location_associations (
    id integer NOT NULL,
    story_id integer NOT NULL,
    location_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: story_location_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.story_location_associations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: story_location_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.story_location_associations_id_seq OWNED BY public.story_location_associations.id;


--
-- Name: story_lore_item_association; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.story_lore_item_association (
    story_id integer NOT NULL,
    lore_item_id integer NOT NULL,
    relevance_to_story text
);


--
-- Name: story_lore_item_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.story_lore_item_associations (
    id integer NOT NULL,
    story_id integer NOT NULL,
    lore_item_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: story_lore_item_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.story_lore_item_associations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: story_lore_item_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.story_lore_item_associations_id_seq OWNED BY public.story_lore_item_associations.id;


--
-- Name: story_ratings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.story_ratings (
    id integer NOT NULL,
    published_story_id integer NOT NULL,
    user_id integer NOT NULL,
    rating integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT valid_rating_range CHECK (((rating >= 1) AND (rating <= 5)))
);


--
-- Name: story_ratings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.story_ratings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: story_ratings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.story_ratings_id_seq OWNED BY public.story_ratings.id;


--
-- Name: storytelling_act_character_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_act_character_associations (
    id integer NOT NULL,
    act_id integer NOT NULL,
    character_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_act_character_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_act_character_associations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_act_character_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_act_character_associations_id_seq OWNED BY public.storytelling_act_character_associations.id;


--
-- Name: storytelling_act_location_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_act_location_associations (
    id integer NOT NULL,
    act_id integer NOT NULL,
    location_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_act_location_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_act_location_associations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_act_location_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_act_location_associations_id_seq OWNED BY public.storytelling_act_location_associations.id;


--
-- Name: storytelling_act_lore_item_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_act_lore_item_associations (
    id integer NOT NULL,
    act_id integer NOT NULL,
    lore_item_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_act_lore_item_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_act_lore_item_associations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_act_lore_item_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_act_lore_item_associations_id_seq OWNED BY public.storytelling_act_lore_item_associations.id;


--
-- Name: storytelling_acts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_acts (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    act_number integer NOT NULL,
    act_summary text,
    ai_summary text,
    writer_notes text,
    image_prompt_definition text,
    system_prompt_id integer,
    story_class_id integer,
    story_id integer NOT NULL,
    current_image_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_acts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_acts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_acts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_acts_id_seq OWNED BY public.storytelling_acts.id;


--
-- Name: storytelling_brainstorm_favorites; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_brainstorm_favorites (
    id integer NOT NULL,
    user_id integer NOT NULL,
    session_id integer NOT NULL,
    concept_id character varying(50) NOT NULL,
    concept_data text NOT NULL,
    is_selected boolean,
    created_at timestamp without time zone
);


--
-- Name: storytelling_brainstorm_favorites_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_brainstorm_favorites_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_brainstorm_favorites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_brainstorm_favorites_id_seq OWNED BY public.storytelling_brainstorm_favorites.id;


--
-- Name: storytelling_brainstorm_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_brainstorm_sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    interview_response_id integer NOT NULL,
    session_name character varying(200),
    generated_concepts text NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: storytelling_brainstorm_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_brainstorm_sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_brainstorm_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_brainstorm_sessions_id_seq OWNED BY public.storytelling_brainstorm_sessions.id;


--
-- Name: storytelling_brainstorm_stories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_brainstorm_stories (
    id integer NOT NULL,
    user_id integer NOT NULL,
    favorite_id integer NOT NULL,
    story_id integer,
    title character varying(200) NOT NULL,
    three_act_structure text NOT NULL,
    created_at timestamp without time zone
);


--
-- Name: storytelling_brainstorm_stories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_brainstorm_stories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_brainstorm_stories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_brainstorm_stories_id_seq OWNED BY public.storytelling_brainstorm_stories.id;


--
-- Name: storytelling_characters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_characters (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    gender character varying(50),
    species character varying(100),
    description text,
    personality_traits text,
    backstory text,
    image_prompt_definition text,
    image_blob_path character varying(1024),
    world_id integer NOT NULL,
    current_location_id integer,
    placement_note text,
    current_image_id integer,
    importance_rating integer,
    relationships text,
    core_motivation character varying(255),
    core_motivations json,
    physical_attributes json,
    key_relationships json,
    genre character varying(100),
    genre_specific_answers json,
    generated_narrative text,
    is_ai_generated boolean,
    next_quest_scenario text,
    first_meeting_message text,
    age_category character varying(50),
    profession character varying(100),
    short_backstory text,
    visual_prompt text,
    narrative_filter_results json,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_characters_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_characters_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_characters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_characters_id_seq OWNED BY public.storytelling_characters.id;


--
-- Name: storytelling_location_connections; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_location_connections (
    from_location_id integer NOT NULL,
    to_location_id integer NOT NULL,
    path_description text,
    reverse_path_description text,
    is_bidirectional boolean NOT NULL,
    dm_notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_locations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_locations (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    atmosphere character varying(255),
    significance text,
    image_prompt_definition text,
    image_blob_path character varying(1024),
    scale public.location_scale_enum,
    parent_location_id integer,
    map_x double precision,
    map_y double precision,
    map_z double precision,
    dimension_x double precision,
    dimension_y double precision,
    dimension_z double precision,
    dimension_unit character varying(50),
    current_image_id integer,
    geography text,
    cultural_context text,
    importance_rating integer,
    connected_elements text,
    world_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_locations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_locations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_locations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_locations_id_seq OWNED BY public.storytelling_locations.id;


--
-- Name: storytelling_lore_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_lore_items (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    category public.lore_item_category_enum NOT NULL,
    image_prompt_definition text,
    image_blob_path character varying(1024),
    world_id integer NOT NULL,
    current_location_id integer,
    placement_note text,
    current_image_id integer,
    importance_rating integer,
    related_elements text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_lore_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_lore_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_lore_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_lore_items_id_seq OWNED BY public.storytelling_lore_items.id;


--
-- Name: storytelling_published_stories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_published_stories (
    id integer NOT NULL,
    story_id integer NOT NULL,
    user_id integer NOT NULL,
    published_url character varying(1024) NOT NULL,
    filename character varying(255) NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    word_count integer,
    is_public boolean NOT NULL,
    is_featured boolean NOT NULL,
    view_count integer NOT NULL,
    like_count integer NOT NULL,
    comment_count integer NOT NULL,
    average_rating double precision,
    published_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    search_vector text
);


--
-- Name: storytelling_published_stories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_published_stories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_published_stories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_published_stories_id_seq OWNED BY public.storytelling_published_stories.id;


--
-- Name: storytelling_scene_character_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_scene_character_associations (
    id integer NOT NULL,
    scene_id integer NOT NULL,
    character_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_scene_character_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_scene_character_associations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_scene_character_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_scene_character_associations_id_seq OWNED BY public.storytelling_scene_character_associations.id;


--
-- Name: storytelling_scene_location_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_scene_location_associations (
    id integer NOT NULL,
    scene_id integer NOT NULL,
    location_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_scene_location_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_scene_location_associations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_scene_location_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_scene_location_associations_id_seq OWNED BY public.storytelling_scene_location_associations.id;


--
-- Name: storytelling_scene_lore_item_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_scene_lore_item_associations (
    id integer NOT NULL,
    scene_id integer NOT NULL,
    lore_item_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_scene_lore_item_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_scene_lore_item_associations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_scene_lore_item_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_scene_lore_item_associations_id_seq OWNED BY public.storytelling_scene_lore_item_associations.id;


--
-- Name: storytelling_scenes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_scenes (
    id integer NOT NULL,
    scene_number integer NOT NULL,
    title character varying(255),
    summary text,
    ai_summary text,
    content text,
    characters_present text,
    plot_points text,
    mood character varying(100),
    image_prompt_definition text,
    act_id integer NOT NULL,
    story_class_id integer,
    current_image_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_scenes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_scenes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_scenes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_scenes_id_seq OWNED BY public.storytelling_scenes.id;


--
-- Name: storytelling_stories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_stories (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    short_description text,
    ai_summary text,
    user_id integer NOT NULL,
    world_id integer NOT NULL,
    story_type character varying(20) DEFAULT 'advanced'::character varying NOT NULL,
    image_prompt_definition text,
    image_blob_path character varying(1024),
    current_image_id integer,
    story_genre character varying(100),
    story_tone character varying(100),
    primary_conflict_type character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_stories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_stories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_stories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_stories_id_seq OWNED BY public.storytelling_stories.id;


--
-- Name: storytelling_story_character_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_story_character_associations (
    id integer NOT NULL,
    story_id integer NOT NULL,
    character_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_story_character_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_story_character_associations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_story_character_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_story_character_associations_id_seq OWNED BY public.storytelling_story_character_associations.id;


--
-- Name: storytelling_story_chat_messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_story_chat_messages (
    id integer NOT NULL,
    session_id integer NOT NULL,
    role character varying(20) NOT NULL,
    content text NOT NULL,
    full_context json,
    story_context json,
    target_element character varying(50),
    target_element_id integer,
    cost_log_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_story_chat_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_story_chat_messages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_story_chat_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_story_chat_messages_id_seq OWNED BY public.storytelling_story_chat_messages.id;


--
-- Name: storytelling_story_chat_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_story_chat_sessions (
    id integer NOT NULL,
    story_id integer NOT NULL,
    user_id integer NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    focus_area character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_story_chat_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_story_chat_sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_story_chat_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_story_chat_sessions_id_seq OWNED BY public.storytelling_story_chat_sessions.id;


--
-- Name: storytelling_story_classes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_story_classes (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(500),
    color character varying(7) NOT NULL,
    world_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: storytelling_story_classes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_story_classes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_story_classes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_story_classes_id_seq OWNED BY public.storytelling_story_classes.id;


--
-- Name: storytelling_story_comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_story_comments (
    id integer NOT NULL,
    published_story_id integer NOT NULL,
    user_id integer NOT NULL,
    parent_comment_id integer,
    content text NOT NULL,
    is_approved boolean NOT NULL,
    is_deleted boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_story_comments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_story_comments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_story_comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_story_comments_id_seq OWNED BY public.storytelling_story_comments.id;


--
-- Name: storytelling_story_location_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_story_location_associations (
    id integer NOT NULL,
    story_id integer NOT NULL,
    location_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_story_location_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_story_location_associations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_story_location_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_story_location_associations_id_seq OWNED BY public.storytelling_story_location_associations.id;


--
-- Name: storytelling_story_lore_item_associations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_story_lore_item_associations (
    id integer NOT NULL,
    story_id integer NOT NULL,
    lore_item_id integer NOT NULL,
    roles json NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_story_lore_item_associations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_story_lore_item_associations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_story_lore_item_associations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_story_lore_item_associations_id_seq OWNED BY public.storytelling_story_lore_item_associations.id;


--
-- Name: storytelling_story_ratings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_story_ratings (
    id integer NOT NULL,
    published_story_id integer NOT NULL,
    user_id integer NOT NULL,
    rating integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT valid_rating_range CHECK (((rating >= 1) AND (rating <= 5)))
);


--
-- Name: storytelling_story_ratings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_story_ratings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_story_ratings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_story_ratings_id_seq OWNED BY public.storytelling_story_ratings.id;


--
-- Name: storytelling_user_interview_responses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_user_interview_responses (
    id integer NOT NULL,
    user_id integer NOT NULL,
    interview_id character varying(100) NOT NULL,
    json_response text NOT NULL,
    completed_at timestamp without time zone NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: storytelling_user_interview_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_user_interview_responses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_user_interview_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_user_interview_responses_id_seq OWNED BY public.storytelling_user_interview_responses.id;


--
-- Name: storytelling_world_collaborators; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_world_collaborators (
    id integer NOT NULL,
    world_id integer NOT NULL,
    user_id integer NOT NULL,
    role character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    invited_by_user_id integer,
    invited_at timestamp with time zone DEFAULT now() NOT NULL,
    joined_at timestamp with time zone,
    permissions json,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_world_collaborators_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_world_collaborators_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_world_collaborators_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_world_collaborators_id_seq OWNED BY public.storytelling_world_collaborators.id;


--
-- Name: storytelling_world_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_world_roles (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(500),
    world_id integer,
    created_by_user_id integer,
    is_predefined boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_world_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_world_roles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_world_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_world_roles_id_seq OWNED BY public.storytelling_world_roles.id;


--
-- Name: storytelling_worlds; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storytelling_worlds (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    short_description text,
    world_builder_data json,
    user_id integer NOT NULL,
    image_prompt_definition text,
    image_blob_path character varying(1024),
    current_image_id integer,
    is_free_chat_enabled boolean NOT NULL,
    is_shadow boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storytelling_worlds_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.storytelling_worlds_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: storytelling_worlds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.storytelling_worlds_id_seq OWNED BY public.storytelling_worlds.id;


--
-- Name: uploaded_documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.uploaded_documents (
    id integer NOT NULL,
    filename character varying(255) NOT NULL,
    content_type character varying(100),
    blob_storage_path character varying NOT NULL,
    status public.document_status_enum NOT NULL,
    error_message text,
    uploaded_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    processed_at timestamp with time zone,
    user_id integer NOT NULL,
    world_id integer,
    source_element_type public.source_element_type_enum,
    source_character_id integer,
    source_location_id integer,
    source_lore_item_id integer
);


--
-- Name: uploaded_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.uploaded_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: uploaded_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.uploaded_documents_id_seq OWNED BY public.uploaded_documents.id;


--
-- Name: user_accounts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_accounts (
    id integer NOT NULL,
    user_id integer NOT NULL,
    current_balance numeric(10,4) NOT NULL,
    total_spent numeric(10,4) NOT NULL,
    total_credits_added numeric(10,4) NOT NULL,
    currency character varying(3) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT check_positive_balance CHECK ((current_balance >= (0)::numeric))
);


--
-- Name: user_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_accounts_id_seq OWNED BY public.user_accounts.id;


--
-- Name: user_activities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_activities (
    id uuid NOT NULL,
    user_id integer,
    action_type character varying(100) NOT NULL,
    action_category character varying(50),
    action_details text,
    endpoint character varying(255),
    method character varying(10),
    status_code integer,
    duration_ms double precision,
    ip_address character varying(45),
    user_agent character varying(500),
    request_id character varying(36),
    request_data json,
    response_data json,
    extra_data json,
    error_message text,
    error_type character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: user_interview_responses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_interview_responses (
    id integer NOT NULL,
    user_id integer NOT NULL,
    interview_id character varying(100) NOT NULL,
    json_response text NOT NULL,
    completed_at timestamp without time zone NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: user_interview_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_interview_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_interview_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_interview_responses_id_seq OWNED BY public.user_interview_responses.id;


--
-- Name: user_transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_transactions (
    id integer NOT NULL,
    user_account_id integer NOT NULL,
    transaction_type character varying(20) NOT NULL,
    amount numeric(10,4) NOT NULL,
    balance_after numeric(10,4) NOT NULL,
    description text,
    ai_cost_log_id integer,
    credit_package_id integer,
    payment_reference character varying(255),
    transaction_metadata jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT check_non_zero_amount CHECK ((amount <> (0)::numeric))
);


--
-- Name: user_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_transactions_id_seq OWNED BY public.user_transactions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(100) NOT NULL,
    email character varying(255),
    hashed_password character varying,
    display_name character varying(100),
    auth_provider character varying(50) NOT NULL,
    provider_id character varying(255),
    provider_data json,
    profile_picture_url character varying(500),
    is_active boolean NOT NULL,
    is_admin boolean,
    interview_data json,
    bonus1 boolean NOT NULL,
    bonus2 boolean NOT NULL,
    bonus3 boolean NOT NULL,
    bonus4 boolean NOT NULL,
    bonus5 boolean NOT NULL,
    bonus6 boolean NOT NULL,
    bonus7 boolean NOT NULL,
    bonus8 boolean NOT NULL,
    bonus9 boolean NOT NULL,
    bonus10 boolean NOT NULL,
    referred_by_user_id integer,
    referral_count integer NOT NULL,
    reset_token character varying(255),
    reset_token_expires timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: world_collaborators; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.world_collaborators (
    id integer NOT NULL,
    world_id integer NOT NULL,
    user_id integer NOT NULL,
    role character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    invited_by_user_id integer,
    invited_at timestamp with time zone DEFAULT now() NOT NULL,
    joined_at timestamp with time zone,
    permissions json,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: world_collaborators_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.world_collaborators_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: world_collaborators_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.world_collaborators_id_seq OWNED BY public.world_collaborators.id;


--
-- Name: world_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.world_roles (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(500),
    world_id integer,
    created_by_user_id integer,
    is_predefined boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: world_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.world_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: world_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.world_roles_id_seq OWNED BY public.world_roles.id;


--
-- Name: worlds; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.worlds (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    short_description text,
    world_builder_data json,
    user_id integer NOT NULL,
    image_prompt_definition text,
    image_blob_path character varying(1024),
    current_image_id integer,
    is_free_chat_enabled boolean NOT NULL,
    is_shadow boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: worlds_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.worlds_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: worlds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.worlds_id_seq OWNED BY public.worlds.id;


--
-- Name: act_character_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.act_character_associations ALTER COLUMN id SET DEFAULT nextval('public.act_character_associations_id_seq'::regclass);


--
-- Name: act_location_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.act_location_associations ALTER COLUMN id SET DEFAULT nextval('public.act_location_associations_id_seq'::regclass);


--
-- Name: act_lore_item_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.act_lore_item_associations ALTER COLUMN id SET DEFAULT nextval('public.act_lore_item_associations_id_seq'::regclass);


--
-- Name: acts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.acts ALTER COLUMN id SET DEFAULT nextval('public.acts_id_seq'::regclass);


--
-- Name: ai_call_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_call_logs ALTER COLUMN id SET DEFAULT nextval('public.ai_call_logs_id_seq'::regclass);


--
-- Name: ai_model_configurations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_model_configurations ALTER COLUMN id SET DEFAULT nextval('public.ai_model_configurations_id_seq'::regclass);


--
-- Name: anonymous_user_sessions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anonymous_user_sessions ALTER COLUMN id SET DEFAULT nextval('public.anonymous_user_sessions_id_seq'::regclass);


--
-- Name: blog_analytics_summary id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_analytics_summary ALTER COLUMN id SET DEFAULT nextval('public.blog_analytics_summary_id_seq'::regclass);


--
-- Name: blog_author_profiles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_author_profiles ALTER COLUMN id SET DEFAULT nextval('public.blog_author_profiles_id_seq'::regclass);


--
-- Name: blog_categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_categories ALTER COLUMN id SET DEFAULT nextval('public.blog_categories_id_seq'::regclass);


--
-- Name: blog_comments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_comments ALTER COLUMN id SET DEFAULT nextval('public.blog_comments_id_seq'::regclass);


--
-- Name: blog_content_links id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_content_links ALTER COLUMN id SET DEFAULT nextval('public.blog_content_links_id_seq'::regclass);


--
-- Name: blog_follows id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_follows ALTER COLUMN id SET DEFAULT nextval('public.blog_follows_id_seq'::regclass);


--
-- Name: blog_likes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_likes ALTER COLUMN id SET DEFAULT nextval('public.blog_likes_id_seq'::regclass);


--
-- Name: blog_post_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_post_associations ALTER COLUMN id SET DEFAULT nextval('public.blog_post_associations_id_seq'::regclass);


--
-- Name: blog_post_tags id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_post_tags ALTER COLUMN id SET DEFAULT nextval('public.blog_post_tags_id_seq'::regclass);


--
-- Name: blog_posts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_posts ALTER COLUMN id SET DEFAULT nextval('public.blog_posts_id_seq'::regclass);


--
-- Name: blog_subscriptions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_subscriptions ALTER COLUMN id SET DEFAULT nextval('public.blog_subscriptions_id_seq'::regclass);


--
-- Name: blog_tags id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_tags ALTER COLUMN id SET DEFAULT nextval('public.blog_tags_id_seq'::regclass);


--
-- Name: blog_views id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_views ALTER COLUMN id SET DEFAULT nextval('public.blog_views_id_seq'::regclass);


--
-- Name: brainstorm_favorites id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.brainstorm_favorites ALTER COLUMN id SET DEFAULT nextval('public.brainstorm_favorites_id_seq'::regclass);


--
-- Name: brainstorm_sessions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.brainstorm_sessions ALTER COLUMN id SET DEFAULT nextval('public.brainstorm_sessions_id_seq'::regclass);


--
-- Name: brainstorm_stories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.brainstorm_stories ALTER COLUMN id SET DEFAULT nextval('public.brainstorm_stories_id_seq'::regclass);


--
-- Name: care_circle_families id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_families ALTER COLUMN id SET DEFAULT nextval('public.care_circle_families_id_seq'::regclass);


--
-- Name: care_circle_family_memberships id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_family_memberships ALTER COLUMN id SET DEFAULT nextval('public.care_circle_family_memberships_id_seq'::regclass);


--
-- Name: care_circle_patient_content_cards id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_patient_content_cards ALTER COLUMN id SET DEFAULT nextval('public.care_circle_patient_content_cards_id_seq'::regclass);


--
-- Name: care_circle_patient_profiles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_patient_profiles ALTER COLUMN id SET DEFAULT nextval('public.care_circle_patient_profiles_id_seq'::regclass);


--
-- Name: care_circle_provider_catalog id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_provider_catalog ALTER COLUMN id SET DEFAULT nextval('public.care_circle_provider_catalog_id_seq'::regclass);


--
-- Name: care_circle_provider_patient_configs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_provider_patient_configs ALTER COLUMN id SET DEFAULT nextval('public.care_circle_provider_patient_configs_id_seq'::regclass);


--
-- Name: care_circle_provider_run_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_provider_run_logs ALTER COLUMN id SET DEFAULT nextval('public.care_circle_provider_run_logs_id_seq'::regclass);


--
-- Name: care_circle_provider_session_outputs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_provider_session_outputs ALTER COLUMN id SET DEFAULT nextval('public.care_circle_provider_session_outputs_id_seq'::regclass);


--
-- Name: characters id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.characters ALTER COLUMN id SET DEFAULT nextval('public.characters_id_seq'::regclass);


--
-- Name: chat_messages id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages ALTER COLUMN id SET DEFAULT nextval('public.chat_messages_id_seq'::regclass);


--
-- Name: chat_samples id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_samples ALTER COLUMN id SET DEFAULT nextval('public.chat_samples_id_seq'::regclass);


--
-- Name: chat_sessions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_sessions ALTER COLUMN id SET DEFAULT nextval('public.chat_sessions_id_seq'::regclass);


--
-- Name: credit_packages id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.credit_packages ALTER COLUMN id SET DEFAULT nextval('public.credit_packages_id_seq'::regclass);


--
-- Name: cta_contents id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cta_contents ALTER COLUMN id SET DEFAULT nextval('public.cta_contents_id_seq'::regclass);


--
-- Name: forum_categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_categories ALTER COLUMN id SET DEFAULT nextval('public.forum_categories_id_seq'::regclass);


--
-- Name: forum_posts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_posts ALTER COLUMN id SET DEFAULT nextval('public.forum_posts_id_seq'::regclass);


--
-- Name: forum_subscriptions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_subscriptions ALTER COLUMN id SET DEFAULT nextval('public.forum_subscriptions_id_seq'::regclass);


--
-- Name: forum_threads id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_threads ALTER COLUMN id SET DEFAULT nextval('public.forum_threads_id_seq'::regclass);


--
-- Name: forum_votes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_votes ALTER COLUMN id SET DEFAULT nextval('public.forum_votes_id_seq'::regclass);


--
-- Name: generated_images id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.generated_images ALTER COLUMN id SET DEFAULT nextval('public.generated_images_id_seq'::regclass);


--
-- Name: job_statuses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_statuses ALTER COLUMN id SET DEFAULT nextval('public.job_statuses_id_seq'::regclass);


--
-- Name: locations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations ALTER COLUMN id SET DEFAULT nextval('public.locations_id_seq'::regclass);


--
-- Name: lore_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lore_items ALTER COLUMN id SET DEFAULT nextval('public.lore_items_id_seq'::regclass);


--
-- Name: prompts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prompts ALTER COLUMN id SET DEFAULT nextval('public.prompts_id_seq'::regclass);


--
-- Name: published_stories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.published_stories ALTER COLUMN id SET DEFAULT nextval('public.published_stories_id_seq'::regclass);


--
-- Name: refresh_tokens id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_tokens ALTER COLUMN id SET DEFAULT nextval('public.refresh_tokens_id_seq'::regclass);


--
-- Name: scene_character_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scene_character_associations ALTER COLUMN id SET DEFAULT nextval('public.scene_character_associations_id_seq'::regclass);


--
-- Name: scene_location_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scene_location_associations ALTER COLUMN id SET DEFAULT nextval('public.scene_location_associations_id_seq'::regclass);


--
-- Name: scene_lore_item_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scene_lore_item_associations ALTER COLUMN id SET DEFAULT nextval('public.scene_lore_item_associations_id_seq'::regclass);


--
-- Name: scenes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scenes ALTER COLUMN id SET DEFAULT nextval('public.scenes_id_seq'::regclass);


--
-- Name: stories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stories ALTER COLUMN id SET DEFAULT nextval('public.stories_id_seq'::regclass);


--
-- Name: story_character_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_character_associations ALTER COLUMN id SET DEFAULT nextval('public.story_character_associations_id_seq'::regclass);


--
-- Name: story_chat_messages id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_chat_messages ALTER COLUMN id SET DEFAULT nextval('public.story_chat_messages_id_seq'::regclass);


--
-- Name: story_chat_sessions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_chat_sessions ALTER COLUMN id SET DEFAULT nextval('public.story_chat_sessions_id_seq'::regclass);


--
-- Name: story_classes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_classes ALTER COLUMN id SET DEFAULT nextval('public.story_classes_id_seq'::regclass);


--
-- Name: story_comments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_comments ALTER COLUMN id SET DEFAULT nextval('public.story_comments_id_seq'::regclass);


--
-- Name: story_location_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_location_associations ALTER COLUMN id SET DEFAULT nextval('public.story_location_associations_id_seq'::regclass);


--
-- Name: story_lore_item_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_lore_item_associations ALTER COLUMN id SET DEFAULT nextval('public.story_lore_item_associations_id_seq'::regclass);


--
-- Name: story_ratings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_ratings ALTER COLUMN id SET DEFAULT nextval('public.story_ratings_id_seq'::regclass);


--
-- Name: storytelling_act_character_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_act_character_associations ALTER COLUMN id SET DEFAULT nextval('public.storytelling_act_character_associations_id_seq'::regclass);


--
-- Name: storytelling_act_location_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_act_location_associations ALTER COLUMN id SET DEFAULT nextval('public.storytelling_act_location_associations_id_seq'::regclass);


--
-- Name: storytelling_act_lore_item_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_act_lore_item_associations ALTER COLUMN id SET DEFAULT nextval('public.storytelling_act_lore_item_associations_id_seq'::regclass);


--
-- Name: storytelling_acts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_acts ALTER COLUMN id SET DEFAULT nextval('public.storytelling_acts_id_seq'::regclass);


--
-- Name: storytelling_brainstorm_favorites id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_brainstorm_favorites ALTER COLUMN id SET DEFAULT nextval('public.storytelling_brainstorm_favorites_id_seq'::regclass);


--
-- Name: storytelling_brainstorm_sessions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_brainstorm_sessions ALTER COLUMN id SET DEFAULT nextval('public.storytelling_brainstorm_sessions_id_seq'::regclass);


--
-- Name: storytelling_brainstorm_stories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_brainstorm_stories ALTER COLUMN id SET DEFAULT nextval('public.storytelling_brainstorm_stories_id_seq'::regclass);


--
-- Name: storytelling_characters id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_characters ALTER COLUMN id SET DEFAULT nextval('public.storytelling_characters_id_seq'::regclass);


--
-- Name: storytelling_locations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_locations ALTER COLUMN id SET DEFAULT nextval('public.storytelling_locations_id_seq'::regclass);


--
-- Name: storytelling_lore_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_lore_items ALTER COLUMN id SET DEFAULT nextval('public.storytelling_lore_items_id_seq'::regclass);


--
-- Name: storytelling_published_stories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_published_stories ALTER COLUMN id SET DEFAULT nextval('public.storytelling_published_stories_id_seq'::regclass);


--
-- Name: storytelling_scene_character_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scene_character_associations ALTER COLUMN id SET DEFAULT nextval('public.storytelling_scene_character_associations_id_seq'::regclass);


--
-- Name: storytelling_scene_location_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scene_location_associations ALTER COLUMN id SET DEFAULT nextval('public.storytelling_scene_location_associations_id_seq'::regclass);


--
-- Name: storytelling_scene_lore_item_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scene_lore_item_associations ALTER COLUMN id SET DEFAULT nextval('public.storytelling_scene_lore_item_associations_id_seq'::regclass);


--
-- Name: storytelling_scenes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scenes ALTER COLUMN id SET DEFAULT nextval('public.storytelling_scenes_id_seq'::regclass);


--
-- Name: storytelling_stories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_stories ALTER COLUMN id SET DEFAULT nextval('public.storytelling_stories_id_seq'::regclass);


--
-- Name: storytelling_story_character_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_character_associations ALTER COLUMN id SET DEFAULT nextval('public.storytelling_story_character_associations_id_seq'::regclass);


--
-- Name: storytelling_story_chat_messages id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_chat_messages ALTER COLUMN id SET DEFAULT nextval('public.storytelling_story_chat_messages_id_seq'::regclass);


--
-- Name: storytelling_story_chat_sessions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_chat_sessions ALTER COLUMN id SET DEFAULT nextval('public.storytelling_story_chat_sessions_id_seq'::regclass);


--
-- Name: storytelling_story_classes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_classes ALTER COLUMN id SET DEFAULT nextval('public.storytelling_story_classes_id_seq'::regclass);


--
-- Name: storytelling_story_comments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_comments ALTER COLUMN id SET DEFAULT nextval('public.storytelling_story_comments_id_seq'::regclass);


--
-- Name: storytelling_story_location_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_location_associations ALTER COLUMN id SET DEFAULT nextval('public.storytelling_story_location_associations_id_seq'::regclass);


--
-- Name: storytelling_story_lore_item_associations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_lore_item_associations ALTER COLUMN id SET DEFAULT nextval('public.storytelling_story_lore_item_associations_id_seq'::regclass);


--
-- Name: storytelling_story_ratings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_ratings ALTER COLUMN id SET DEFAULT nextval('public.storytelling_story_ratings_id_seq'::regclass);


--
-- Name: storytelling_user_interview_responses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_user_interview_responses ALTER COLUMN id SET DEFAULT nextval('public.storytelling_user_interview_responses_id_seq'::regclass);


--
-- Name: storytelling_world_collaborators id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_world_collaborators ALTER COLUMN id SET DEFAULT nextval('public.storytelling_world_collaborators_id_seq'::regclass);


--
-- Name: storytelling_world_roles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_world_roles ALTER COLUMN id SET DEFAULT nextval('public.storytelling_world_roles_id_seq'::regclass);


--
-- Name: storytelling_worlds id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_worlds ALTER COLUMN id SET DEFAULT nextval('public.storytelling_worlds_id_seq'::regclass);


--
-- Name: uploaded_documents id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uploaded_documents ALTER COLUMN id SET DEFAULT nextval('public.uploaded_documents_id_seq'::regclass);


--
-- Name: user_accounts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_accounts ALTER COLUMN id SET DEFAULT nextval('public.user_accounts_id_seq'::regclass);


--
-- Name: user_interview_responses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_interview_responses ALTER COLUMN id SET DEFAULT nextval('public.user_interview_responses_id_seq'::regclass);


--
-- Name: user_transactions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_transactions ALTER COLUMN id SET DEFAULT nextval('public.user_transactions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: world_collaborators id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.world_collaborators ALTER COLUMN id SET DEFAULT nextval('public.world_collaborators_id_seq'::regclass);


--
-- Name: world_roles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.world_roles ALTER COLUMN id SET DEFAULT nextval('public.world_roles_id_seq'::regclass);


--
-- Name: worlds id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.worlds ALTER COLUMN id SET DEFAULT nextval('public.worlds_id_seq'::regclass);


--
-- Data for Name: act_character_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.act_character_associations (id, act_id, character_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: act_location_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.act_location_associations (id, act_id, location_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: act_lore_item_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.act_lore_item_associations (id, act_id, lore_item_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: acts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.acts (id, title, description, act_number, act_summary, ai_summary, writer_notes, image_prompt_definition, system_prompt_id, story_class_id, story_id, current_image_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: ai_call_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ai_call_logs (id, job_id, user_id, model_config_id, input_prompt, call_type, model_name, object_id, prompt_tokens, completion_tokens, total_tokens, calculated_cost_usd, duration_ms, created_at) FROM stdin;
\.


--
-- Data for Name: ai_model_configurations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ai_model_configurations (id, display_name, model_name, description, provider, model_type, is_active, is_public_chat_default, max_tokens, temperature, top_p, presence_penalty, frequency_penalty, is_json_mode, provider_cost_input_usd_pm, provider_cost_output_usd_pm, user_price_input_usd_pm, user_price_output_usd_pm) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
d4e5f6a7b8c9
\.


--
-- Data for Name: anonymous_user_sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.anonymous_user_sessions (id, user_id, session_token, ip_address, browser_fingerprint, user_agent, created_at, last_seen_at, is_active) FROM stdin;
\.


--
-- Data for Name: blog_analytics_summary; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.blog_analytics_summary (id, post_id, date, unique_views, total_views, new_likes, new_comments, avg_read_time, bounce_rate, social_shares, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: blog_author_profiles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.blog_author_profiles (id, user_id, bio, profile_image_url, website_url, twitter_handle, instagram_handle, linkedin_url, allow_comments_default, auto_publish, email_notifications, total_posts, total_views, total_likes, follower_count, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: blog_categories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.blog_categories (id, name, slug, description, color, icon, post_count, display_order, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: blog_comments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.blog_comments (id, post_id, author_id, parent_comment_id, content, status, like_count, reply_count, is_author_reply, created_at, updated_at, deleted_at) FROM stdin;
\.


--
-- Data for Name: blog_content_links; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.blog_content_links (id, post_id, link_type, link_id, link_text, link_context, created_at) FROM stdin;
\.


--
-- Data for Name: blog_follows; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.blog_follows (id, author_id, follower_id, notification_enabled, created_at) FROM stdin;
\.


--
-- Data for Name: blog_likes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.blog_likes (id, post_id, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: blog_post_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.blog_post_associations (id, post_id, association_type, association_id, association_title, created_at) FROM stdin;
\.


--
-- Data for Name: blog_post_tags; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.blog_post_tags (id, post_id, tag_id, created_at) FROM stdin;
\.


--
-- Data for Name: blog_posts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.blog_posts (id, title, slug, content, excerpt, featured_image_url, status, author_id, category_id, view_count, like_count, comment_count, meta_title, meta_description, meta_keywords, og_title, og_description, og_image_url, is_featured, allow_comments, is_ai_generated, published_at, last_viewed_at, created_at, updated_at, deleted_at, search_vector) FROM stdin;
\.


--
-- Data for Name: blog_subscriptions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.blog_subscriptions (id, email, user_id, status, frequency, include_categories, include_tags, confirmation_token, unsubscribe_token, last_sent_at, total_emails_sent, last_opened_at, open_count, click_count, bounce_count, complaint_count, last_bounce_at, last_complaint_at, source, ip_address, user_agent, confirmed_at, unsubscribed_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: blog_tags; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.blog_tags (id, name, slug, description, usage_count, created_at) FROM stdin;
\.


--
-- Data for Name: blog_views; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.blog_views (id, post_id, user_id, ip_address, user_agent, referrer_url, session_id, view_duration, created_at) FROM stdin;
\.


--
-- Data for Name: brainstorm_favorites; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.brainstorm_favorites (id, user_id, session_id, concept_id, concept_data, is_selected, created_at) FROM stdin;
\.


--
-- Data for Name: brainstorm_sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.brainstorm_sessions (id, user_id, interview_response_id, session_name, generated_concepts, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: brainstorm_stories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.brainstorm_stories (id, user_id, favorite_id, story_id, title, three_act_structure, created_at) FROM stdin;
\.


--
-- Data for Name: care_circle_families; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.care_circle_families (id, name, created_by_user_id, created_at, updated_at, join_code) FROM stdin;
\.


--
-- Data for Name: care_circle_family_memberships; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.care_circle_family_memberships (id, family_id, user_id, role, is_primary, created_at) FROM stdin;
\.


--
-- Data for Name: care_circle_patient_content_cards; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.care_circle_patient_content_cards (id, patient_id, provider_key, title, body, card_kind, display_order, is_active, created_at, rendered_html) FROM stdin;
\.


--
-- Data for Name: care_circle_patient_profiles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.care_circle_patient_profiles (id, family_id, created_by_user_id, display_name, stage, access_state, timezone, delivery_time, delivery_days, auth_image_keys, preferences, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: care_circle_provider_catalog; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.care_circle_provider_catalog (id, provider_key, label, icon, category, enabled, display_order, patient_visible, family_visible, source_app, created_at) FROM stdin;
1	weather	Weather	☀️	core	t	1	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
2	joke	Daily Joy	😄	wellbeing	t	2	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
3	nostalgia	Time Machine	🕰️	memory	t	3	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
4	puzzle	Puzzle	🧩	games	t	4	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
5	brain_booster	Brain Booster	🧠	games	t	5	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
6	sensory	Sensory	🎵	wellbeing	t	6	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
7	ai_trivia	AI Trivia	💡	games	t	7	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
8	daily_quote	Daily Quote	✨	core	t	8	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
9	dog_photo	Furry Friend	🐶	memory	t	9	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
10	cat_fact	Cat Fact	🐱	memory	t	10	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
11	gratitude	Gratitude	🙏	wellbeing	t	11	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
12	gentle_exercise	Gentle Exercise	🤼	wellbeing	t	12	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
13	daily_affirmation	Affirmation	💛	core	t	13	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
14	nature_scene	Nature Scene	🌿	memory	t	14	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
15	simple_recipe	Simple Recipe	🍳	lifestyle	t	15	f	t	daily_newsletter	2026-04-06 21:00:27.905555+00
16	this_day_history	On This Day	📅	memory	t	16	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
17	riddle	Daily Riddle	🤔	games	t	17	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
18	missing_vowels	Missing Vowels	🔤	games	t	18	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
19	finish_phrase	Finish the Phrase	💬	games	t	19	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
20	odd_one_out	Odd One Out	🎯	games	t	20	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
21	word_scramble	Word Scramble	🔀	games	t	21	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
22	song_of_the_day	Song of the Day	🎵	memory	t	22	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
23	complete_the_duo	Complete the Duo	🤝	games	t	23	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
24	spot_the_difference	Spot the Difference	🔍	games	t	24	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
25	pen_pal_letter	Pen Pal Letter	✉️	wellbeing	t	25	f	t	daily_newsletter	2026-04-06 21:00:27.905555+00
26	gridless_crossword	Gridless Crossword	📝	games	t	26	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
27	world_news	World News	🌍	core	t	27	f	t	daily_newsletter	2026-04-06 21:00:27.905555+00
28	hobby_spotlight	Hobby Spotlight	🎨	lifestyle	t	28	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
29	family_greeting	Family Greeting	👨‍👩‍👧	core	t	29	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
30	local_history	Local History	🏛️	memory	t	30	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
31	personal_affirmation	Personal Affirmation	💪	wellbeing	t	31	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
32	activity_suggestion	Activity Suggestion	🌟	wellbeing	t	32	t	t	daily_newsletter	2026-04-06 21:00:27.905555+00
\.


--
-- Data for Name: care_circle_provider_patient_configs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.care_circle_provider_patient_configs (id, patient_id, provider_key, is_enabled, schedule_expression, custom_parameters, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: care_circle_provider_run_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.care_circle_provider_run_logs (id, provider_key, patient_id, family_id, status, error_message, execution_time_ms, created_at) FROM stdin;
\.


--
-- Data for Name: care_circle_provider_session_outputs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.care_circle_provider_session_outputs (id, patient_id, provider_key, run_log_id, output_json, session_date, created_at) FROM stdin;
\.


--
-- Data for Name: characters; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.characters (id, name, gender, species, description, personality_traits, backstory, image_prompt_definition, image_blob_path, world_id, current_location_id, placement_note, current_image_id, importance_rating, relationships, core_motivation, core_motivations, physical_attributes, key_relationships, genre, genre_specific_answers, generated_narrative, is_ai_generated, next_quest_scenario, first_meeting_message, age_category, profession, short_backstory, visual_prompt, narrative_filter_results, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: chat_messages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.chat_messages (id, session_id, role, content, full_context, element_type, element_id, cost_log_id, created_at) FROM stdin;
\.


--
-- Data for Name: chat_samples; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.chat_samples (id, title, prompt_text, category, is_active, sort_order, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: chat_sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.chat_sessions (id, world_id, user_id, title, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: credit_packages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.credit_packages (id, name, description, credit_amount, price_usd, bonus_percentage, is_active, display_order, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: cta_contents; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.cta_contents (id, title, subtitle, content, "position", sort_order, style, background_color, text_color, icon_class, features, primary_button_text, primary_button_url, primary_button_icon, secondary_button_text, secondary_button_url, secondary_button_icon, show_for_anonymous, show_for_authenticated, show_for_admin, is_active, created_at, updated_at, campaign_name, utm_source, utm_medium, utm_campaign) FROM stdin;
\.


--
-- Data for Name: forum_categories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.forum_categories (id, name, description, slug, sort_order, is_active, icon, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: forum_posts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.forum_posts (id, content, content_html, thread_id, user_id, parent_post_id, character_id, location_id, upvote_count, downvote_count, score, edit_count, edited_at, edited_by_id, is_deleted, deleted_at, deleted_by_id, deletion_reason, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: forum_subscriptions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.forum_subscriptions (id, thread_id, user_id, notify_email, notify_in_app, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: forum_threads; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.forum_threads (id, title, slug, status, category_id, user_id, world_id, story_id, view_count, post_count, last_post_at, last_post_by_id, is_pinned, is_locked, is_deleted, deleted_at, deleted_by_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: forum_votes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.forum_votes (id, post_id, user_id, vote_type, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: generated_images; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.generated_images (id, image_uuid, blob_path, prompt, revised_prompt, element_type, associated_element_id, aspect_ratio, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: job_statuses; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.job_statuses (id, job_id, job_type, state, status_message, result_message, user_id, world_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: location_connections; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.location_connections (from_location_id, to_location_id, path_description, reverse_path_description, is_bidirectional, dm_notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: locations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.locations (id, name, description, atmosphere, significance, image_prompt_definition, image_blob_path, scale, parent_location_id, map_x, map_y, map_z, dimension_x, dimension_y, dimension_z, dimension_unit, current_image_id, geography, cultural_context, importance_rating, connected_elements, world_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: lore_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.lore_items (id, title, description, category, image_prompt_definition, image_blob_path, world_id, current_location_id, placement_note, current_image_id, importance_rating, related_elements, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: prompts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.prompts (id, title, prompt_content, reason_to_use, comment, is_active, prompt_type, age_target, user_id, last_updated_by_user_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: published_stories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.published_stories (id, story_id, user_id, published_url, filename, title, description, word_count, is_public, is_featured, view_count, like_count, comment_count, average_rating, published_at, updated_at, search_vector) FROM stdin;
\.


--
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.refresh_tokens (id, token, user_id, issued_at, expires_at, revoked_at, ip_address, user_agent) FROM stdin;
\.


--
-- Data for Name: scene_character_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.scene_character_associations (id, scene_id, character_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: scene_location_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.scene_location_associations (id, scene_id, location_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: scene_lore_item_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.scene_lore_item_associations (id, scene_id, lore_item_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: scenes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.scenes (id, scene_number, title, summary, ai_summary, content, characters_present, plot_points, mood, image_prompt_definition, act_id, story_class_id, current_image_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: social_share_daily_summaries; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.social_share_daily_summaries (id, user_id, date, total_shares, coins_earned, max_coins_reached, facebook_shares, twitter_shares, linkedin_shares, reddit_shares, whatsapp_shares, email_shares, copy_link_shares, pinterest_shares, telegram_shares, image_preview_shares, published_story_shares, ai_public_chat_shares, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: social_shares; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.social_shares (id, user_id, content_type, content_id, content_title, content_url, platform, shared_text, shared_hashtags, ip_address, user_agent, referrer, coin_awarded, coin_amount, created_at) FROM stdin;
\.


--
-- Data for Name: stories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.stories (id, title, short_description, ai_summary, user_id, world_id, story_type, image_prompt_definition, image_blob_path, current_image_id, story_genre, story_tone, primary_conflict_type, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: story_character_association; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.story_character_association (story_id, character_id, role_in_story) FROM stdin;
\.


--
-- Data for Name: story_character_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.story_character_associations (id, story_id, character_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: story_chat_messages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.story_chat_messages (id, session_id, role, content, full_context, story_context, target_element, target_element_id, cost_log_id, created_at) FROM stdin;
\.


--
-- Data for Name: story_chat_sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.story_chat_sessions (id, story_id, user_id, title, description, focus_area, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: story_classes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.story_classes (id, name, description, color, world_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: story_comments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.story_comments (id, published_story_id, user_id, parent_comment_id, content, is_approved, is_deleted, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: story_location_association; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.story_location_association (story_id, location_id, significance_to_story) FROM stdin;
\.


--
-- Data for Name: story_location_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.story_location_associations (id, story_id, location_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: story_lore_item_association; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.story_lore_item_association (story_id, lore_item_id, relevance_to_story) FROM stdin;
\.


--
-- Data for Name: story_lore_item_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.story_lore_item_associations (id, story_id, lore_item_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: story_ratings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.story_ratings (id, published_story_id, user_id, rating, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_act_character_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_act_character_associations (id, act_id, character_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_act_location_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_act_location_associations (id, act_id, location_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_act_lore_item_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_act_lore_item_associations (id, act_id, lore_item_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_acts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_acts (id, title, description, act_number, act_summary, ai_summary, writer_notes, image_prompt_definition, system_prompt_id, story_class_id, story_id, current_image_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_brainstorm_favorites; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_brainstorm_favorites (id, user_id, session_id, concept_id, concept_data, is_selected, created_at) FROM stdin;
\.


--
-- Data for Name: storytelling_brainstorm_sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_brainstorm_sessions (id, user_id, interview_response_id, session_name, generated_concepts, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_brainstorm_stories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_brainstorm_stories (id, user_id, favorite_id, story_id, title, three_act_structure, created_at) FROM stdin;
\.


--
-- Data for Name: storytelling_characters; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_characters (id, name, gender, species, description, personality_traits, backstory, image_prompt_definition, image_blob_path, world_id, current_location_id, placement_note, current_image_id, importance_rating, relationships, core_motivation, core_motivations, physical_attributes, key_relationships, genre, genre_specific_answers, generated_narrative, is_ai_generated, next_quest_scenario, first_meeting_message, age_category, profession, short_backstory, visual_prompt, narrative_filter_results, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_location_connections; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_location_connections (from_location_id, to_location_id, path_description, reverse_path_description, is_bidirectional, dm_notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_locations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_locations (id, name, description, atmosphere, significance, image_prompt_definition, image_blob_path, scale, parent_location_id, map_x, map_y, map_z, dimension_x, dimension_y, dimension_z, dimension_unit, current_image_id, geography, cultural_context, importance_rating, connected_elements, world_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_lore_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_lore_items (id, title, description, category, image_prompt_definition, image_blob_path, world_id, current_location_id, placement_note, current_image_id, importance_rating, related_elements, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_published_stories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_published_stories (id, story_id, user_id, published_url, filename, title, description, word_count, is_public, is_featured, view_count, like_count, comment_count, average_rating, published_at, updated_at, search_vector) FROM stdin;
\.


--
-- Data for Name: storytelling_scene_character_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_scene_character_associations (id, scene_id, character_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_scene_location_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_scene_location_associations (id, scene_id, location_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_scene_lore_item_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_scene_lore_item_associations (id, scene_id, lore_item_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_scenes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_scenes (id, scene_number, title, summary, ai_summary, content, characters_present, plot_points, mood, image_prompt_definition, act_id, story_class_id, current_image_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_stories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_stories (id, title, short_description, ai_summary, user_id, world_id, story_type, image_prompt_definition, image_blob_path, current_image_id, story_genre, story_tone, primary_conflict_type, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_story_character_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_story_character_associations (id, story_id, character_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_story_chat_messages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_story_chat_messages (id, session_id, role, content, full_context, story_context, target_element, target_element_id, cost_log_id, created_at) FROM stdin;
\.


--
-- Data for Name: storytelling_story_chat_sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_story_chat_sessions (id, story_id, user_id, title, description, focus_area, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_story_classes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_story_classes (id, name, description, color, world_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_story_comments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_story_comments (id, published_story_id, user_id, parent_comment_id, content, is_approved, is_deleted, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_story_location_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_story_location_associations (id, story_id, location_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_story_lore_item_associations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_story_lore_item_associations (id, story_id, lore_item_id, roles, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_story_ratings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_story_ratings (id, published_story_id, user_id, rating, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_user_interview_responses; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_user_interview_responses (id, user_id, interview_id, json_response, completed_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_world_collaborators; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_world_collaborators (id, world_id, user_id, role, status, invited_by_user_id, invited_at, joined_at, permissions, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_world_roles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_world_roles (id, name, description, world_id, created_by_user_id, is_predefined, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: storytelling_worlds; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.storytelling_worlds (id, name, description, short_description, world_builder_data, user_id, image_prompt_definition, image_blob_path, current_image_id, is_free_chat_enabled, is_shadow, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: uploaded_documents; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.uploaded_documents (id, filename, content_type, blob_storage_path, status, error_message, uploaded_at, updated_at, processed_at, user_id, world_id, source_element_type, source_character_id, source_location_id, source_lore_item_id) FROM stdin;
\.


--
-- Data for Name: user_accounts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_accounts (id, user_id, current_balance, total_spent, total_credits_added, currency, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: user_activities; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_activities (id, user_id, action_type, action_category, action_details, endpoint, method, status_code, duration_ms, ip_address, user_agent, request_id, request_data, response_data, extra_data, error_message, error_type, created_at) FROM stdin;
4b3d1f1e-0421-4284-9146-90d530f6edf8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.424333572387695	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:00:39.995088+00
3d4d8b7f-40a7-4c08-a728-f302a2466b35	\N	get_request	general	GET request to /ui/story-wizard/health	/ui/story-wizard/health	GET	500	10.825634002685547	172.25.0.1	Mozilla/5.0 (Windows NT 10.0; Microsoft Windows 10.0.28020; en-US) PowerShell/7.5.5	[no_request_id]	null	null	null	'dict' object has no attribute 'encode'	AttributeError	2026-04-06 21:01:01.219854+00
cb94c32a-4d6f-49eb-a38c-df8d0c11c708	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0017623901367188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:01:12.772663+00
ad37d1c4-45c9-4af0-815d-2015550082dc	\N	get_request	general	GET request to /ui/story-wizard/health	/ui/story-wizard/health	GET	500	6.59942626953125	172.25.0.1	Mozilla/5.0 (Windows NT 10.0; Microsoft Windows 10.0.28020; en-US) PowerShell/7.5.5	[no_request_id]	null	null	null	'dict' object has no attribute 'encode'	AttributeError	2026-04-06 21:01:22.345816+00
617be6c4-e72e-4917-8eab-ad2a268cdb5d	\N	get_request	general	GET request to /ui/story-wizard/health	/ui/story-wizard/health	GET	500	7.327556610107422	172.25.0.1	Mozilla/5.0 (Windows NT 10.0; Microsoft Windows 10.0.28020; en-US) PowerShell/7.5.5	[no_request_id]	null	null	null	'dict' object has no attribute 'encode'	AttributeError	2026-04-06 21:01:22.372562+00
7e755746-d72e-4aed-b6ca-5fd4e891ad56	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.908468246459961	172.25.0.1	Mozilla/5.0 (Windows NT 10.0; Microsoft Windows 10.0.28020; en-US) PowerShell/7.5.5	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:01:32.875478+00
0fc57908-ca96-43c6-b790-cb818a83cd75	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6853084564208984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:01:45.559231+00
f50db7a1-5fbe-4f8f-9284-056f05c198cc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5746822357177734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:02:18.364315+00
7cef8150-b2f1-4a4c-88b9-21f466e9e41d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9750595092773438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:02:51.144664+00
e5c9975a-08b7-4b0e-a86c-dfd3067b9d63	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.083301544189453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:03:23.931667+00
1b24126d-e48e-4145-93c4-e5ae11fc0e73	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1572113037109375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:03:56.705112+00
5a29f7be-815d-44a6-b68e-f034d8bc15c4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.062082290649414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:04:29.493223+00
9d1965cc-6332-4567-b9d2-9d30c969e844	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.126455307006836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:05:02.284202+00
bed33ae8-7bf8-43e3-924e-6a070d4d53f1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.490852355957031	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:05:35.066491+00
3979fbe2-eb0f-4439-bc44-3803cd10328b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7971267700195312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:06:07.857541+00
b2c3575b-9823-4195-9f80-706f77d67a9e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3953914642333984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:06:40.645719+00
4749dd85-b88a-4132-a172-4e58f5caea7e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0978450775146484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:07:13.425798+00
11384056-a8bb-4815-8b64-cbafd2828f09	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2661685943603516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:07:46.221605+00
281d8f12-423f-4733-95e4-7431827e206f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.8160552978515625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:08:19.03599+00
f6fefa8d-e04d-41cc-971a-2928912d7760	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.260446548461914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:08:51.846788+00
e5962271-5866-4505-9029-f39c927fb906	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9500255584716797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:09:24.620128+00
1e001244-59f4-4c39-af58-d0b6f7ee2552	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.243135452270508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:09:57.425573+00
541a946c-a95e-4ee6-85f8-2a232b73690d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0754337310791016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:10:30.210337+00
2111b7d0-5777-4d06-b8af-0150eb84bb8b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.878499984741211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:11:02.98903+00
c45e5f7c-433a-42bf-85ca-7505c8d516da	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8646717071533203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:11:35.763119+00
cffbba2e-2355-4333-9aa6-66e3a817356c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.932165145874023	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:12:08.54759+00
5d0f59c7-1a1a-48e4-b64e-dc3899120a98	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.519845962524414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:12:41.324922+00
92742f9f-20ca-4d61-9295-92c71e7c79de	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8769969940185547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:13:14.107837+00
c2362163-4984-4ff9-b803-0d9a2ff7be4e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5413036346435547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:13:46.897489+00
3618f2c4-5874-426e-897c-9815858de75b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	10.415315628051758	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:14:19.686502+00
5dd5fc8b-16e1-4aaf-aeed-49988806c0a5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.115964889526367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:14:52.526142+00
f686f8e1-721c-4901-a3b4-6e4abbd5d718	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7638206481933594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:15:25.306877+00
0458f32e-e271-4a3b-baa0-8e05170c3ffa	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.851652145385742	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:15:58.093965+00
3b28ea6f-134f-47ae-8fd8-65e0ea93b770	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4237632751464844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:16:30.879831+00
44f6bb4e-0076-480c-9ea4-4ab75aadbe50	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	213.1967544555664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:17:03.875683+00
ae65c1b0-6721-46f0-9d3e-a11bb7acbe65	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.458333969116211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:17:36.665825+00
c98f9d90-fce1-47e6-979e-03e44f78262b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3622512817382812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:18:09.44987+00
7870cd66-c17b-4899-a28d-6cc6f53da771	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1104812622070312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:18:42.22572+00
195ed7ce-89aa-4f75-864a-3a1154fe0def	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7290115356445312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:19:14.998587+00
2f48865a-1915-4d6a-97d0-939c5c3199d3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8987655639648438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:20:20.58622+00
7dc5bcd3-2405-448a-a2c0-5b1011d3107c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3746490478515625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:08:38.548401+00
c9d2c79e-a87a-4a0d-ab57-16a08c11c6cc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6056766510009766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:09:45.318541+00
609bad48-2d22-494a-93f9-460c8baeb89b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.935720443725586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:10:18.701713+00
9f4d0045-3c42-4392-8f55-bce943ce8756	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0678043365478516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:11:25.469285+00
14ea2c0f-766b-454f-b00d-be00132b177e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8849372863769531	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:12:32.240802+00
c07fcf90-fa61-4ffa-a6d7-c40bc1a08266	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.553224563598633	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:13:05.630614+00
a188ecc4-025e-4f51-bd65-92f2b8abe5fd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7995834350585938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:13:39.049119+00
4bcb29cf-f033-466f-9416-5898699d7f72	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.251314163208008	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:05:42.23384+00
b8d1d96d-5d38-4bf5-8e73-d1284e3fdb9b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6209354400634766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:06:49.009385+00
2d4aeef3-c1e3-4454-94a3-271ad62302df	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.928567886352539	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:09:02.564037+00
c3b48663-bb54-4438-a0dd-c0a0aa15ee64	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7311573028564453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:09:35.954566+00
ee635231-ce2a-4b89-8130-2185d858127b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7654895782470703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:10:42.724095+00
843cb2ff-11a0-4b63-9e42-117281099828	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7871856689453125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:12:22.86996+00
68c32f87-d6a9-4472-8d7b-65759a9190fe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8124580383300781	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:14:03.068936+00
3aa0a0ff-744c-4c8f-8464-dc21234de78b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8274784088134766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:15:09.891763+00
c2210340-1863-4304-9805-97453bc29cf6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8818378448486328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:15:43.274891+00
b8bcf1f3-b98e-44cb-b43b-1629b8633ae2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.871347427368164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:14:31.105893+00
377f624d-1341-4ac3-ba30-9a2268da22fd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	13.350963592529297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:31:35.174095+00
edd87c99-6f29-4478-9526-769e98e4afdb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.121448516845703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:32:35.319081+00
636a8ddb-1f37-4a0a-adbc-3d3d58a56d9a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.016305923461914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:36:35.961417+00
dcdd870a-1a19-4e80-81c7-d5aeb98cdd87	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1877288818359375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:37:06.041584+00
23490cee-6dfe-49b0-b1af-1383b9d502c1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.785205841064453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:37:36.154499+00
ebacfa3c-382d-4231-8424-34b2d3155d40	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.096414566040039	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:39:06.40146+00
f632b45f-83b6-458d-994c-06c351d625c5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0895004272460938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:40:36.657698+00
9a9b1218-6afa-4319-bf0f-9100ec6d9b3c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.633810043334961	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:41:06.740306+00
59503b85-9cdf-4cef-81ad-05c38283863f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.472400665283203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:45:37.44296+00
5edc1794-d88d-43e9-bd6f-9853a6846ba1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.731800079345703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:49:08.150663+00
14442281-8820-4375-b78c-3c82caace37b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.228975296020508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:51:38.556826+00
6574ecc9-ad07-4161-8934-af8c69cc2e95	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	533.4265232086182	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 22:04:00.652711+00
d3377254-69c3-4f8f-9790-2e77ae5054a8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.702951431274414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:19:47.78794+00
a5a985c9-5ff7-41a6-9970-8667960cda91	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0530223846435547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:20:53.367563+00
671d8660-816d-4411-959e-631d590b16a9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7848014831542969	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:21:26.182869+00
02998490-719f-4332-bfe4-ceb1b8c6a694	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.025604248046875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:21:58.964275+00
07128781-ae4c-4ab6-b64b-e2b5d82c84ba	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.943349838256836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:22:31.747678+00
d62d9085-7552-4f9a-9a9e-864e83cd7217	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.009153366088867	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:23:37.318907+00
ae2b0eed-5774-424e-9945-dd1d1cead9c1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.531766891479492	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:24:10.12401+00
a5f1827e-69d3-4c83-9e09-ab9a15fa32d5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7538070678710938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:25:15.670007+00
cfa86fc0-4a64-4da9-9ddb-ca44ebf8243c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9295215606689453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:25:48.443687+00
50f2ffe2-ee75-441e-b974-92889d8c856c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8813610076904297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:26:21.222763+00
79c4716f-7a13-44c0-8041-77d9fcfae8cd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8429031372070312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:09:11.932875+00
a07d1af5-f61e-4b58-9ead-173b1eba3a95	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9066333770751953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:10:52.085829+00
b1d2da30-b42d-4b88-94ec-b529e965dee8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6603469848632812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:11:58.853723+00
96f352aa-04ca-4776-a66f-7167df131376	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9977092742919922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:13:29.684128+00
9ab8c620-d6f4-4bff-85b8-a310796b533b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9145011901855469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:19:03.614349+00
e0bf6933-c74b-46e1-af2c-0262f899e9d7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.263784408569336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:24:37.537932+00
fddea675-22a1-4f40-a8e3-45a4451e8ccf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9528141021728516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:25:44.359594+00
4fd0dd7f-f4c8-4308-86fd-9a9bdec21af0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.533435821533203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:28:31.320712+00
59f1f6c4-5b1c-4e46-9022-8918ea75c8f8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9524097442626953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:31:51.673965+00
80b6af21-c3cf-4010-b431-3b4904634939	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9533634185791016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:36:18.77632+00
fdc97266-5402-4fda-baf4-948c5f0993d2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9838809967041016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:39:39.102992+00
05a08da0-8590-42ac-9f96-5ac935c5ccbf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1255016326904297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:42:26.015806+00
58e8dbff-92e7-4a7a-ae14-b6e65f0fee14	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8122196197509766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:15:37.867628+00
fbf29680-7f64-48ba-a840-f8b811cb235f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9445419311523438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:17:51.414052+00
9306a861-06f1-416f-afcf-70f1709f9b83	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.264738082885742	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:19:31.564535+00
a90c76e4-72e3-496e-bb6d-6a703fda26fc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1927356719970703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:25:05.467077+00
0cdc3a45-e890-420b-b7a5-247a0bcca5f9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9598007202148438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:27:19.03544+00
59eec1eb-5751-454e-a066-3d02e73ec17a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.369403839111328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:27:52.428508+00
dc0f86b0-8a2b-48fa-809d-6ee7022dac5c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6667118072509766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:28:25.8163+00
48a46887-8182-410d-8ec1-1caaa378cb2f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.749277114868164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:30:39.391217+00
910ff4c0-ca46-410b-9021-c48907a68ce5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9865036010742188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:31:12.779466+00
4a108652-6f3c-433b-ab5a-3ae2b9a91bce	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8377304077148438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:36:46.60955+00
02c0991b-9959-4303-a901-857632367d18	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3436546325683594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:37:19.998649+00
fc3e947c-01a9-476c-8754-06f649cd1ad9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1381378173828125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:34:05.560795+00
2910707b-066f-4e67-af74-330004b8d479	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.06756591796875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:38:36.314838+00
1834057c-810f-45ca-9308-3b269fb14860	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.149820327758789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:47:37.884212+00
1f10db4a-a567-49b3-8801-87f6b843241e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2120.860815048218	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 22:04:00.638999+00
cf61cd1d-a1de-49bb-9c0c-bcc1720c10f6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	34.70873832702637	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 22:20:55.148702+00
97aea9cd-a632-4042-be92-317f2aeafacc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.321813583374023	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:23:04.53672+00
084058e5-13a4-442b-929f-491c56f16856	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.852273941040039	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:24:42.89573+00
0b410a76-3729-4780-bb6e-5988ea6145ee	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.045869827270508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:26:54.040887+00
988c7361-b9fc-4e3d-80af-d818588ab705	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7828941345214844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:27:26.814071+00
cbaa684a-6558-4f7f-bd27-1b48ab28867b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7900466918945312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:27:59.600557+00
20d76969-0890-46cd-b8a7-6efa9e43ae41	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0132064819335938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:28:32.887937+00
39a01c61-807e-40c3-9d01-19add1cc387b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.595186233520508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:29:06.279923+00
9f50cce0-6f65-4153-bec0-1472571f54f0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.132415771484375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:29:39.66779+00
4694d4e5-635f-43bb-a79c-b92d4f0ceadc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	242.36273765563965	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:30:13.297346+00
70939265-fc72-4a81-be16-753185789478	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.429485321044922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:30:46.71003+00
48c404ad-0a99-4f5e-9274-9b81bdef5ffe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1431446075439453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:31:20.134214+00
0d82c652-92ed-4a3d-b5fc-f2bbcfe84b26	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8205642700195312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:31:53.520807+00
02a4f500-ac22-4b79-ab7e-fb3b0ae8c78a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9481182098388672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:32:26.936099+00
234b46f9-df90-4973-ab84-bd4bbbdb85fe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5217533111572266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:33:00.321547+00
ac4a3512-1b9d-4931-98e6-c5eee5839948	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8544197082519531	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:33:33.703666+00
d2348ee8-4d5c-4912-ba78-eb2990eb9249	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8973350524902344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:34:07.09053+00
b545ed2c-710d-4ff3-b067-bfd0577b56cb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.683401107788086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:34:40.478319+00
41eac1d4-beef-44ae-b527-cd13c21e8bd1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	7.734775543212891	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:35:13.874519+00
34175f96-729f-4077-90e5-770661447f05	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0012855529785156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:35:47.276493+00
d01d535c-fb13-493a-8c3d-b690ed54a496	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7387142181396484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:36:20.649388+00
feade9fd-28df-4ed3-8f36-85f791e7115f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.034902572631836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:36:54.049276+00
363e771a-2dc0-4f8e-bd15-48181901d7fc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7657279968261719	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:37:27.43623+00
6d8fabc4-f08f-459f-950c-a9e66e07e425	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9505023956298828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:38:00.823225+00
afe99b4d-c518-4644-a667-68609393cd17	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9723644256591797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:38:34.206616+00
59248614-ec93-4017-bc6a-21b3de65ef4e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.034830093383789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:39:07.597164+00
f94fc3cc-a0a9-4b4d-922e-388e64dd8d2f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.93023681640625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:39:40.981644+00
3946c721-4b54-406d-9879-3b76c5564654	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9314289093017578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:40:14.368008+00
61319de9-bcbc-44be-b77a-6afd60d9dfb1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8405914306640625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:40:47.747486+00
93d05cb6-62aa-4dc5-a03f-1825cd1ea8bf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.089262008666992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:41:21.135822+00
112d2451-9daf-413a-885e-95a83647e7ab	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.052783966064453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:41:54.515345+00
bddcac59-16df-44f0-abdc-b7c6174bcb9e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4824142456054688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:42:27.883578+00
8aa16b6d-7d75-481a-bf68-43c1c3afb974	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1173954010009766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:43:01.270283+00
df0c813f-a108-4748-aa04-2e124ce6a803	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0444393157958984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:43:34.648134+00
4742e4b9-640b-45ef-be74-2939712e5db1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6693344116210938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:44:08.055295+00
ffc6811f-2ecd-4613-a770-ea5fe0dd6144	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.245664596557617	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:44:41.457069+00
1529fb0c-e42b-4826-8a07-ed0e48f50c27	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8222332000732422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:45:14.839791+00
9149f708-6bce-4645-9774-791750d5a88b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	8.749008178710938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:45:48.252891+00
79e2407c-e28e-43a1-a8bd-88f0bcdddc24	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1691322326660156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:46:21.642141+00
4719e556-1329-4276-9ff5-a66ff7ce61d8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4036.159038543701	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:46:59.058078+00
281ecd1f-2086-4a28-90f4-571c8bbd3a24	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.013683319091797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:47:32.444659+00
4b6b17bb-2d64-4b2f-9e07-4c3668bdd3e5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.41851806640625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:48:05.826752+00
e824525a-3b46-44e5-a660-3c6ebabe09b5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7049312591552734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:48:39.202732+00
bc7305b9-4944-4406-b7bd-4857decc7695	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7108192443847656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:49:12.626075+00
9d80b0a8-b800-403d-b19b-a10f28a843a6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0678043365478516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:50:19.399844+00
c7db0fd5-4011-4c99-9609-6846c6dab754	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7580986022949219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:51:26.190752+00
d73090dc-2818-410a-a18d-eaa4de3e7cf2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7228126525878906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:51:59.560023+00
0b181dc4-db26-4386-816f-2dd004c9e143	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7707347869873047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:52:32.945484+00
66b93e26-4480-4d99-abaf-80c2e9be4734	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.370119094848633	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:53:39.718778+00
7f43ff92-e7c1-4350-8223-71514cdb5686	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.026081085205078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:54:13.106079+00
531dc7ce-60ae-4d83-a7d7-08d80a06ac8b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8281936645507812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:54:46.489673+00
ea31385b-a788-4b9e-97a0-1cdb84813f7d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.032756805419922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:55:19.879052+00
df998510-ded4-46ba-b172-1c3e8a5a9787	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.645254135131836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:55:53.265954+00
d5a44520-85ec-4794-b2e8-025cf5ff4f81	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7299652099609375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:57:00.022102+00
66165540-7d7d-4006-927f-10f2b2cd8b2b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7504692077636719	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:14:12.451561+00
fa2018ad-fd83-4f65-8348-56a13ff8211a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8703937530517578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:15:19.265867+00
b9c5db70-ee00-47e0-83cd-db8f2af9ce7e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3365020751953125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:16:26.03752+00
27a77e62-b0bb-4c37-8e50-54bdf671507e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5424957275390625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:16:59.427912+00
6a0d89cf-476d-43b9-9d94-8bab674c5878	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8799304962158203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:19:12.99783+00
79af8d8a-4684-4c68-91e6-d12ae914ef59	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7380714416503906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:20:53.172867+00
fce084bc-b18a-45a3-a8ec-4dc9107a4342	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.353191375732422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:23:06.740266+00
19566349-117e-4634-9abd-41881f5fccc0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9688606262207031	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:23:40.113736+00
9a35f8dc-4a61-41e5-b4fe-07303227d4b9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9021034240722656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:25:20.24884+00
8ee43e7f-578c-4547-b50f-088bbc6055b9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.733541488647461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:25:53.624011+00
a99a5558-6896-4a52-9eed-77d24a6e5f11	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.407073974609375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:26:27.017047+00
6426e8c8-9cee-408e-a13a-581ff3baa108	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.050161361694336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:27:33.78061+00
3cb5cf00-489e-40d9-8789-7a670229149f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8968582153320312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:28:40.537412+00
e15e1745-26f1-4232-ac0d-942d4c0f2fa8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7008781433105469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:29:13.922386+00
fa67748d-b735-4a95-abfc-239d53199e68	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7609596252441406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:29:47.29417+00
1313d404-e7a5-44d9-998c-db66c029c25f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9702911376953125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:30:20.672038+00
393e41cd-1b88-46dc-b08d-be66d1c6d8b1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7597675323486328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:30:54.053978+00
9c312b21-d869-4169-ae0c-a44d84947f6b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.470731735229492	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:31:27.456734+00
31cc522e-6409-43bf-a24d-188ee9a26624	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.39508056640625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:34:14.475095+00
62b0ece6-e307-4364-aa71-4d72c6b69be0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0852088928222656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:34:47.877269+00
d23834a8-6b38-4389-86ec-ade2e12a38cb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.989126205444336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:35:21.261558+00
04e3b786-a533-48b9-90ad-125f2846a074	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.972841262817383	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:14:36.503268+00
94a99ecc-5774-4677-a7be-974a98bd6b11	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8181800842285156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:16:16.663259+00
68a8a494-46aa-4972-ae66-bd59091f9b1a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7824172973632812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:18:30.23006+00
879d7512-5b8e-4f26-88c6-25ae672989cc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8794536590576172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:21:50.547862+00
62b9d8c0-d014-4877-aed0-0d25dbb6fc10	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6237964630126953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:22:23.942699+00
5f4c167b-0d60-426f-bcd4-5814c1ab1664	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7823448181152344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:24:04.128935+00
f3aafcb2-2a99-4dc7-b37d-f25e6b77801e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7447471618652344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:34:38.629263+00
c8042c91-9b65-47cb-8591-a117220faf25	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7545223236083984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:36:52.162274+00
596d8c79-945f-4058-b59e-1bc1bfd16e7a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1893978118896484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:49:46.011211+00
6bf939b0-5100-40e8-ae68-c4206a69e8a0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2308826446533203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:50:52.807912+00
44d79c48-41de-46b5-a991-860e1c649352	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8756389617919922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:56:26.649728+00
fedd5e48-793c-4615-aa05-336262cb909f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0797252655029297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:57:33.405533+00
e6d1cae6-d1a8-452f-9d02-83082e881f3f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8892288208007812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:58:06.783739+00
f482c78f-a18b-4f2b-a84d-ba2941b2e8af	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8999576568603516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:14:45.889432+00
6d9c8067-235b-42dc-9ff3-801c978b476b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7313957214355469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:17:32.812698+00
16de5b6c-d88b-45b2-b5e5-7e1e47799012	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4383068084716797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:18:39.610907+00
944a7924-5e7b-4882-906a-54a4ac592d35	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.438068389892578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:27:00.406149+00
8e65066f-4bf3-4f6b-be10-ee891cc59e3a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.567291259765625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:33:07.630099+00
97eb8155-a883-4de2-a74f-7cf08374638a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3355484008789062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:33:41.001897+00
305523a3-645c-45da-b9e8-07a03c1f25c1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5577545166015625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:16:50.075941+00
869beb1a-9cb4-4483-a5fd-303a5e372a92	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.390623092651367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:17:23.46501+00
ae7da699-20d3-48c2-b62d-62a3433d3bc2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.4437179565429688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:19:37.012583+00
1601c8a6-8f42-4db9-b67d-6ce642d43d80	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0172595977783203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:20:10.390874+00
4fecc6e3-c1f4-4f78-8cc0-662df3ed8045	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.840829849243164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:20:43.77752+00
95b410ba-abdc-4096-9a53-7af14b698cca	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0437240600585938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:21:17.161172+00
d6235f3c-20e9-4551-b23a-c3f03199684f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.027273178100586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:22:57.335624+00
ca74fc7c-7dfa-4bac-a8a0-95c675afd2a6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7235279083251953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:23:30.718303+00
fae1321e-607c-46fb-81db-fffc75e33417	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8815994262695312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:26:17.749627+00
1165d66c-2c57-43d0-89bc-5a3b721aab8e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2614002227783203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:26:51.129098+00
832849c3-5f4f-4318-8f67-0dbdc9ab9918	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8274784088134766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:27:24.54515+00
97c96ee0-6526-4c94-8964-7cfc72a3b23b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8768310546875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:27:57.937952+00
579cb97a-17be-40f7-bd15-acc1d4018ff9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2890567779541016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:29:04.710203+00
20602402-832d-4a06-b945-4c80e90d27b0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9381046295166016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:29:38.101245+00
84878c6a-93d6-4fa8-8213-3058c4e5981a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8544197082519531	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:30:44.885169+00
26180d28-cc31-4151-af93-3347ff010be2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7595291137695312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:32:25.061074+00
cfe555e2-71f9-4e95-ad02-bfe3d638ead1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0275115966796875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:32:58.447093+00
53826376-d163-49aa-896a-e3fc651de177	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7175674438476562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:33:31.81865+00
d9df7bf5-7c4f-4e12-bb5a-b436fa35bc49	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1834373474121094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:35:12.007518+00
14daa769-ded8-40a6-9ae0-927f7fab75f7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8968582153320312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:37:58.929305+00
d1901ca1-c148-4b08-a3c4-7a39d96a19f8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1665096282958984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:38:32.320161+00
6bf6a451-261b-4f31-a866-7fac064d93d5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8568038940429688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:41:52.640163+00
131ab0f9-eb91-4d21-907f-1947120859b4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9490718841552734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:42:59.405317+00
88e6ae49-91e3-4a9e-a01b-ec94701cf094	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.017974853515625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:43:32.792465+00
06155790-68c6-437e-a449-d55bf26c7812	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9938945770263672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:45:12.967834+00
085a47ed-851b-478b-b957-a82564408e4f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6756057739257812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:45:46.359163+00
33f183f8-805d-401e-9e2a-b503e6ea27b4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0093917846679688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:46:19.7495+00
1842ffd1-bddc-4981-b84a-a76fec5b2ffe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.837015151977539	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:16:11.253462+00
aebcccef-3ee1-4b27-987c-069bffb5cba0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9104480743408203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:16:44.639869+00
8a9a4ac3-30de-4ccf-b182-57f696d2e5d3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7066001892089844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:17:18.02402+00
f6cfcd4b-1f89-454c-8e5f-a0af3f5376ba	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8825531005859375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:53:06.329894+00
27eb2b43-6d63-4a26-82ed-dc7b01d08b35	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.282857894897461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:58:40.16784+00
0ed9d736-22e7-46d1-a246-0496b5ef6761	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8911361694335938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:59:13.540364+00
74122f12-0c4e-4640-bfa5-e6f34a51af44	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.046823501586914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 21:59:46.930473+00
ae1e558e-a0cd-4e35-8dc3-3aaa5c82915b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8391609191894531	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:00:20.306475+00
bc5c6a2f-1165-4bc8-ae27-8fae14dc7389	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6373863220214844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:00:53.690235+00
080d9f21-0d93-4125-9de3-37ae801e8049	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7731189727783203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:01:27.063181+00
080d7434-4b32-4f5a-a15a-94e91084a3cb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9707679748535156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:02:00.472605+00
4a4c692d-43cb-4748-8ad9-cf4c0ab4002c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9683837890625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:02:33.854797+00
d33da969-4abe-443e-acc2-e9faeb83ffd2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.315998077392578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:03:07.265202+00
5b6fd10b-7b91-4dfa-bb16-f90ad6d90617	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7538070678710938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:03:40.640901+00
ba342f59-d5b6-4ca3-8b16-002fe77bfd95	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9710063934326172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:04:14.027778+00
7e5cace3-2758-4ac6-94c3-8acb3891ede3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1202564239501953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:04:47.412561+00
5cc39539-c32e-4b8e-9d72-aa346b614e6e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.274751663208008	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:05:20.797719+00
63f452d2-b52d-4c1e-b987-d97224a599fa	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8825531005859375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:05:54.198016+00
3d49d1c6-0fe0-45fc-bb8e-f1d01b4c9bc8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.344846725463867	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:06:27.584308+00
8dc0f662-3b80-40f8-b97e-08ad7f43b685	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.087831497192383	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:07:00.966188+00
004f45bd-3666-4117-b2f0-c826e3766b5f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8186569213867188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:07:34.353907+00
f4d89e54-2c62-436e-91b3-9f3f008d647b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5305747985839844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:08:07.722647+00
cfd9ecf4-b7ef-4fca-8109-4c0614c18c29	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7850399017333984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:08:41.115587+00
f2cb6bd0-c4b6-4e48-92ad-e30686af023d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9674301147460938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:09:14.498652+00
72e4a5f9-b435-4c6f-af67-3965f91ca6a7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9190311431884766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:09:47.881372+00
27097e8a-fadd-4081-8c3a-c8f2718df70d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9390583038330078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:10:21.264286+00
1e823d9f-2092-4aa9-8906-71374c03a12e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.710653305053711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:10:54.647831+00
22573a96-b5c3-4083-bb37-e5ca9745810c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0089149475097656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:11:28.030306+00
c43478c7-e9a4-43f4-9688-28d6ddd86679	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7571449279785156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:12:01.412717+00
dde2eb21-6c4c-4253-ad87-67576edb6d43	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.277374267578125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:12:34.801592+00
c6a7f689-7eec-4623-ad48-271a7950748c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8703937530517578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:13:08.188206+00
821c5ea0-ef8c-4b9a-a509-c806da1caabc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0723342895507812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:13:41.571881+00
e718c347-bc46-4832-976f-0515d0791fc2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8694400787353516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:14:14.954474+00
ff43df9a-1914-4f1d-9d96-243b8f58baeb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.389120101928711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:14:48.344141+00
85ce2996-1734-46e9-9316-c468fe70cb7d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.05120849609375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:15:21.764018+00
0ec23953-5aed-47bc-991b-b89b39a8bb8e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.7412643432617188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:15:55.227171+00
776a99ac-eae2-439f-a46f-517b64b3f82a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9571781158447266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:16:28.616481+00
096cd18d-80b0-45f0-a46c-bbb495b9efe2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.176046371459961	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:17:01.997405+00
0a3d0197-7d13-40b7-84d9-7db11481e1f5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8260478973388672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:17:35.383098+00
2a316af8-ceea-4a29-8b12-2f2c20797546	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.122163772583008	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:18:08.769463+00
a23182b3-77d0-4b98-a3b5-00765f8f796d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8265247344970703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:18:42.15524+00
94f43082-0c84-442c-9bed-a426651e6c32	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.661321640014648	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:19:15.555207+00
2395f6c1-dcc9-45be-83c4-d4fca4d8387a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9903182983398438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:19:48.970828+00
c282557a-ef82-4a7d-8889-c240e35d088d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7771720886230469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:20:22.342756+00
8319897a-6b4b-4848-a8dd-c2beb58b5e1a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2857189178466797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:20:55.732781+00
12bcc9d6-338a-4f08-bdcc-ee114116bfdc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8038749694824219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:21:29.120115+00
8ba21258-91a5-4530-a502-4b9483e2659f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.008676528930664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:22:35.886994+00
3be80afb-1707-4e64-8a67-cbc7c951509a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7852783203125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:23:09.262585+00
aa3c6fd4-7592-4fba-9490-9565c7cc3532	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8756389617919922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:23:42.646345+00
e194bd45-0b5e-41f9-91c5-feab92c38dbd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1572113037109375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:24:50.193149+00
a717d371-6db4-4cca-9807-890f33c9345d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9462108612060547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:25:23.576392+00
6ed7c87a-2e5a-40fc-a852-2ad729508a82	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7330646514892578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:25:56.965976+00
971d6b2f-7ed2-4d62-a953-15ad5806089e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9254684448242188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:26:30.346984+00
af4ad378-dc03-4d5d-8605-cbb4b42a8a61	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7712116241455078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:27:37.159122+00
e02f333c-4e59-4275-99dc-cd6898a7124f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2537708282470703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:28:10.545554+00
c468d71d-9430-4ed7-ad57-75eacd1260f1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8379688262939453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:28:43.932061+00
b158155c-e13a-42d1-bc34-85b773799da6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0210742950439453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:29:17.315139+00
8104e641-0857-4ca3-a208-75374cf38c83	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9431114196777344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:29:50.699848+00
d6fb0edf-4647-485d-9fad-7cad7e0c7b19	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.765178680419922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:30:24.089707+00
7c93bdc8-2fb4-44ad-945c-dc2649973974	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9049644470214844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:30:57.475101+00
98d74ff4-5214-45b8-bb03-d4c8194e9cbb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.163410186767578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:31:30.846691+00
36356772-8031-4b0b-8bd8-b3c9ce5b71ab	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9335746765136719	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:15:52.651967+00
1da19f7e-3269-4a56-8d8d-af15d921ef3d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2635459899902344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:34:05.231747+00
a36ab0e2-b267-4426-aa33-fa285a9c21f5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2132396697998047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:35:45.390474+00
013c0d7c-e94d-47ed-ba67-50553d9c4973	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2644996643066406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:37:25.546812+00
d4486893-a9b3-4bfd-a07b-60b748a29d3d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7527809143066406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:39:05.715227+00
458a662a-751b-4b06-9046-92a87821fab9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9910335540771484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:40:12.478405+00
8ec23af9-fc69-4cdd-bb09-63516da3033d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.08282470703125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:44:39.590319+00
e511d812-e05a-4f10-a53c-336d2e92f713	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3975372314453125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:47:59.935276+00
d7fc4334-17ba-409e-ab4f-bc29cb7479e1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.683950424194336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:48:33.321409+00
7c1c5ca0-0e0d-4a7d-989d-e48998070212	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8222332000732422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:51:20.282325+00
fd59ae58-b787-4541-8f48-3cbcc09cc6b1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.206563949584961	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:53:00.458467+00
616bbc75-7483-449d-8d05-653c359612c7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.71661376953125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:56:54.189871+00
41ed02b5-d9db-46f6-803f-e1cabf5c450d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9876956939697266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:01:24.604219+00
3189bdae-5c09-432c-aa61-6ba95114ae70	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8343925476074219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:01:57.978923+00
12b8ac98-0e01-41fc-82f1-52901de2b882	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.018451690673828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:18:24.801304+00
f8667855-6734-4022-9aff-7b57af5fb6ba	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8463134765625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:18:58.178413+00
b6a1201c-bbfb-4fae-b56d-c126907b60a4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0837783813476562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:39:36.482558+00
c963fc25-edce-4c99-90c2-11e48d45795c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3114681243896484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:42:06.897473+00
70bcdc19-a7ad-47f1-9036-165d0455f719	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.218961715698242	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:42:36.98372+00
0f0e3d56-38a2-40ea-be57-de3837b31d07	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	475.6045341491699	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 22:04:00.753014+00
df756bf8-2596-415b-88ca-4bf4b7c79246	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2459030151367188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:22:02.506212+00
60567d33-785c-4da3-ba66-a63a5452b681	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.811981201171875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:18:06.222872+00
2a3a002e-cfda-445b-8bc3-d5a52833524a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6841888427734375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:20:19.782642+00
a06aada1-2f75-4b30-ba72-ca62b44b1ce8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.5845298767089844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:21:59.947828+00
a9a2b4ed-2fd1-4244-96bd-784daa92e544	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5115013122558594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:24:46.873378+00
4c3f470a-4438-4d15-a703-37df80cb6cd5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7998218536376953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:28:07.153693+00
ed1a4b5b-e182-4b01-89d5-2975c65b355a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9631385803222656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:32:00.830894+00
a936478e-2845-4c02-95f2-b0625018257c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8197765350341797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:32:34.222576+00
05f817f3-16d7-4dce-bff5-4434f7093bcc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4292469024658203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:40:45.867784+00
5886dcbf-01d4-4af0-8d73-924fc5bc8942	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9326210021972656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:41:19.253953+00
09dacc54-3bb3-47b3-b1c1-b421761d7a05	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0093917846679688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:20:04.949362+00
1b9b696c-a18e-4718-9442-c890f4883e1e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8329620361328125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:23:58.676387+00
317a47c5-b99f-4124-b23d-0e81e4b60959	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1054744720458984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:34:33.096177+00
e1a810b0-4128-44b7-9b3d-04baae46611d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.954793930053711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:38:26.759138+00
1a4e58b3-8d9c-4d3c-8a1d-fa8a4d495df6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2916793823242188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:40:06.888192+00
3b7ae1dc-37b7-48e1-ad86-c09dd2d294fc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.9072036743164062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:46:37.721703+00
cf71f125-8add-483c-9265-b710f77ebdfc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.509593963623047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:48:07.963168+00
a43e29e9-11fc-438e-a497-2f3839707a00	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2161006927490234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:50:08.311603+00
b534d70b-a0f2-4beb-afcb-e7012ac74c46	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.262115478515625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:50:38.399885+00
7c7d416f-0f6a-472c-89e4-59e85ed84054	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.268552780151367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:55:39.301283+00
834d8e2d-70bb-40e1-a16d-6b418996ae37	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0601749420166016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:57:09.604145+00
d97d1e3b-c5db-4df2-b843-5a2854941f21	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4797916412353516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:05:41.052529+00
24294e8b-4f9a-464d-adf1-d9e0c2c2a234	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9867420196533203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:06:41.219164+00
13028db6-1ea4-4304-9ef1-84c088ab396d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3870468139648438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:12:12.157365+00
e5409e6c-0be5-472a-ae38-3ed93f9a917e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.166271209716797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:13:42.386892+00
a04f2983-382b-46ee-84c5-a41f64dad532	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.292156219482422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:14:42.556293+00
d6ae4a9d-8840-4237-9916-0001c841c4e1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	85.62612533569336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 22:04:23.228259+00
522ae115-5daf-4113-b6f0-842d47b370f4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	16.451358795166016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 22:04:56.483842+00
62a51d7f-4d93-4a31-9027-0e8af9f0c255	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6121139526367188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:24:16.809348+00
4e645bcf-a5ba-4325-82da-c82c0580ac8b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8398761749267578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:19:46.407572+00
b938f2a3-b604-457f-98a0-5ce2beb748d9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.633810043334961	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:21:26.560696+00
9bf756c4-2a76-4a9d-8749-15bd22a2ae99	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0308494567871094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:22:33.355496+00
b0794322-a3c8-4da8-b030-7c3f569d56dd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.468585968017578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:24:13.485444+00
69cdce75-4171-463c-8402-9aa03fa7df30	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.113819122314453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:44:06.20122+00
fdbba73c-a841-4380-a5b0-b5c7044f276d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0198822021484375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:49:40.093739+00
0698a199-b957-4e7d-a8a7-fd797d970c66	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8553733825683594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:55:47.403499+00
9eced9a1-0cd7-4e4f-91a1-c333841e222b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	10.843276977539062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:56:20.796602+00
396eb874-6660-4b1c-a794-90ddca6080da	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9083023071289062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:58:00.961081+00
9d26648c-4ed7-4a8d-bf45-99339706e09b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0568370819091797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:00:51.220845+00
83f6ebf2-2a46-4178-b944-207fadf1a818	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.050565719604492	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:03:38.123885+00
8aa599fd-52b5-4dac-b5b2-7c8ca0365e18	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4878978729248047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:06:25.022663+00
0ae2b064-111f-4299-871a-b9e94cd985a3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.002239227294922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:07:31.799639+00
def90da5-a515-43c6-8f8b-ab0afacdf094	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.909494400024414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:20:38.363668+00
7da3f86a-0588-4209-b050-b6e817c49fcc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9147396087646484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:21:11.749987+00
68aa0b03-b7af-400f-91ee-6db859b4d7b5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0935535430908203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:22:18.515696+00
077dc837-5516-4571-8493-c2e2ae6da385	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0139217376708984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:22:51.902488+00
d6141ca4-c062-4339-b087-204f109e15c7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7883777618408203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:23:25.287453+00
a6c9c5d8-892e-4e2d-832d-1afbd72b192d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9216537475585938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:24:32.066016+00
a3d031e0-8f22-4e90-980b-c09b14705c3d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.901388168334961	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:25:38.880456+00
dc582d31-7738-451e-8ecd-8be17992ff46	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9710063934326172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:26:12.269378+00
6cc90d86-151f-427e-89e1-a5d16fc021eb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.515554428100586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:26:45.655499+00
dc20050f-d2af-439f-a5c2-cbe4da8a3f3c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8842220306396484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:29:32.621971+00
47e8a09e-4b53-4beb-bcf6-90238f8ee516	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.743316650390625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:30:06.005627+00
21c6ec9d-ecdb-422d-9917-c17bc41ee011	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0165443420410156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:31:46.165487+00
32939357-4313-4f72-8c80-577740734ba1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8916130065917969	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:32:19.562402+00
8f03a4f5-8f77-45c6-8a15-57a974e8f703	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.692056655883789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:33:26.330179+00
6d8a0b75-5e56-4880-a1e3-7e6f3a0d73f3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8239021301269531	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:33:59.718438+00
7abb29c4-77ef-4c13-8023-cd3f8cdafdd6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.93023681640625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:35:06.483276+00
6727b996-946a-44c8-8988-db0db226ede4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9214153289794922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:35:39.857607+00
6e690fbc-9b6e-4565-b8d5-a937e5dcba18	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8656253814697266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:37:53.372054+00
9d07b664-6c39-4d03-a313-a1076ce642e4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9273757934570312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:39:00.13573+00
fa8e89bf-e010-49ed-b2d3-06d7a85af66a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.022266387939453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:39:33.510966+00
271685eb-01d7-44c1-9754-31eb8afb705e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.154827117919922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:40:40.27116+00
39c0e526-0892-4a61-a8ef-ab5a0ea7f7a1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.092123031616211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:41:13.675476+00
19b097bb-a200-403d-bf95-e9e2d031aad6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2106170654296875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:42:53.840402+00
84e8c2d4-c074-42d5-b85a-f0dabf3ffc77	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9605159759521484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:44:00.598604+00
35183ce9-456b-4e43-94d8-2b1c38cc45d5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0020008087158203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:45:07.349445+00
75303125-719e-4659-873b-ecdfaa198621	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.819610595703125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:45:40.745534+00
1bbc400a-8e6d-45aa-8ba9-d971ee24330e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.791881561279297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:46:47.556415+00
90811bc8-08d7-4781-8e33-4c0a813ccc9c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	8.855819702148438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:27:03.769343+00
19031c3f-eb26-45f0-b9e1-9407bb4d3a29	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.724170684814453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:32:04.237789+00
8738b970-0384-46fc-be71-949077693ca6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.106904983520508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:32:37.627575+00
ce0a03dc-1dc3-4bd8-a840-3e586de612fb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.869844436645508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:33:03.394511+00
9dd747e2-8d2b-4543-91cc-b4ce01c4fe2c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7931461334228516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:33:36.803104+00
94e09153-3967-48a6-9406-bd47842779b5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8334388732910156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:34:10.186197+00
45cf472d-5d49-4c92-ad55-0a1814eca666	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9516944885253906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:34:43.562229+00
0eb4ce70-4bc5-4659-a91d-2588546e42b6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8362274169921875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:35:15.598358+00
72fc6735-cb1c-47ad-84b0-c31862c7b20a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.526521682739258	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:35:47.237393+00
acb32e80-1528-4458-a0aa-9d9b1d0be715	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9647350311279297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:36:18.54695+00
714087fa-c027-45ba-bfbd-b8d25c849479	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1975040435791016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:36:50.130185+00
888ab0ba-38fc-4ad0-b5c6-80c70035da8a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.761363983154297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:37:21.286107+00
51dd1266-b08d-4ac5-b0ca-65df7299e1b4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.171754837036133	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:37:52.672218+00
5117071d-e1c3-44dd-a998-dd5a1dcaa1ca	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.109527587890625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:38:23.990879+00
1cd02352-2dc9-466a-80fa-279b7831be54	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6965866088867188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:38:55.281314+00
feace48b-217c-46ee-a88e-b3e857f01bb4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.244234085083008	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:39:26.353235+00
0524cfb6-93e5-451e-bde3-dc5c620439de	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.4542083740234375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:39:57.57461+00
1dcfa72c-dfa7-4161-835f-b2d6a08571d1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.989530563354492	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:40:28.889869+00
a5f1c657-2d7d-4b24-abaf-2905162a1d3f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.193927764892578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:41:00.100401+00
76c3f894-09d8-4e2f-9a9f-3196d81cb7bd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8954277038574219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:41:31.222296+00
9909aa28-a565-44a8-be4d-d88118540c14	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.118825912475586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:42:02.370251+00
fff6d83d-46b4-4fdc-b785-3377304a5f66	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3360252380371094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:42:33.661112+00
3791c8a9-e6da-4b38-9e61-d969604462a2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.4134387969970703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:43:12.667893+00
2e77ae70-f560-4ce5-a9e7-ab7a31ae1934	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0599365234375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:43:45.748658+00
19e4bcec-c7d7-40a2-9eca-d47e180f183e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.134561538696289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:44:18.783495+00
2e3f15fa-b724-4f45-91df-0a7fa470ed14	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.15911865234375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:44:52.160947+00
9e90436b-3abd-4d64-8495-ef31c585d5ce	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7637481689453125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:45:25.53814+00
9c46b18e-fac9-49be-be7e-6c5c26bac715	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2230148315429688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:45:58.922594+00
c978019d-28ea-4909-baac-b5ebf3a8231a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5289058685302734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:46:32.318811+00
1d3cece0-73ff-4d2b-be4a-9e3b2b973878	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0542144775390625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:47:05.708692+00
8ed244da-0638-4e2f-b98d-3cbe1463ae14	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2242069244384766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:47:39.100744+00
3283262e-5927-4e7b-a503-bbd00d1338e7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2253990173339844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:48:12.51359+00
3e018f14-3358-4e0b-8dae-8494ae38a1bd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2268295288085938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:48:45.916381+00
5c331c89-89bc-4aec-add4-611e2a774ef5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8221607208251953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:49:19.296867+00
979a62fc-3151-4d6b-b384-2121e7f3721e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.548860549926758	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:49:52.682844+00
370d202f-3bf3-441f-8735-476f9823aa4e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6552677154541016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:50:26.134415+00
d217eb2d-90a2-4150-a0d3-6f472d9c3c35	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9276142120361328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:50:59.534253+00
bc98d328-5a91-4806-85fd-26f0a2df06ec	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.559185028076172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:51:32.92004+00
7b2d5750-4e2d-44e2-b84c-c84dcaa66c37	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.210378646850586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:52:06.306655+00
b5143e41-4a19-4ab8-97d0-7066685c3348	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.146005630493164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:52:39.690162+00
38b37b53-7dcc-4f05-9dae-0a5ab8d23037	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4161338806152344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:53:13.080162+00
753b11f9-9c5c-43cb-94f5-f25982de47c4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.912832260131836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:53:46.45621+00
b41fc637-a3c4-4b5a-bc8a-371967d7c3f8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9350051879882812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:54:19.827565+00
5cc6c25e-429c-471b-8777-4b34b84afe29	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.737833023071289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:54:53.212601+00
c50d9c43-55fc-4fa2-9885-c04a34a5c1cf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8894672393798828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:55:26.585047+00
5f570f85-017e-4013-9e74-09f5085dce8d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9296875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:55:59.996869+00
c1be66cc-3467-492e-9b0e-f235f8f0544b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8868446350097656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:59:53.695567+00
1ad3e8cd-109a-4498-b01d-50f2425325d2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8799304962158203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:00:27.079166+00
3ae1650b-1816-4267-b91d-0d7f1fefb151	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9040107727050781	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:01:00.467515+00
cd605274-c24e-4fb2-a5f0-4e1fc8809cd0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1359920501708984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:01:33.889422+00
5b4368cb-3fd7-4197-b8c0-81654dd83a89	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1860599517822266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:35:54.664891+00
4c58885e-1341-4d38-baaf-71c753661cf2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.042531967163086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:36:28.063045+00
affd5373-a805-448c-942c-26d911e72008	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.702474594116211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:37:34.842893+00
ed97e4ca-99c5-4fa7-87b2-e11de9e68e5c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0875930786132812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:38:08.238066+00
be017ad6-3e22-4b69-bc8b-cb98e30a37ee	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8184185028076172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:41:28.540241+00
1bfaeb2b-8d9f-49c6-932c-7a0623ac88aa	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8002986907958984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:42:01.915202+00
deddfe90-ab67-44ed-94f0-257e78861580	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7087459564208984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:43:08.674532+00
6f91ceaa-0e17-4d1f-8616-b0d70d0c8300	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.97601318359375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:46:53.161846+00
6179bc5e-fed2-4840-997c-b056135706ed	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7123222351074219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:47:26.549401+00
cf939c31-638c-4215-a2fb-f4d9a1015829	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9652843475341797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:49:06.709686+00
275aac12-eb46-4f94-a5d6-d98ef0416655	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8968582153320312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:50:13.480787+00
c013ff9b-4512-4983-8a8d-e806e35ad381	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3496150970458984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:50:46.897005+00
02d52565-dbd6-4c8b-8917-ae9e7ce95f90	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7082691192626953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:52:27.078756+00
382b7b4b-c791-468f-b158-94175bf45d0a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9137859344482422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:54:07.226437+00
a0eb3910-502b-4251-8b00-bedf415d0d6f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.983642578125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:54:40.619057+00
5f329e9c-7c21-4571-a60d-922d6c709a3a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.131938934326172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:55:14.018714+00
9148ba54-52bc-4fa3-adc6-05a48de65664	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.072572708129883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:57:27.576008+00
0e8ad110-35f9-43df-b5da-4d9ce453e8ee	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.068758010864258	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:58:34.339158+00
455183bc-a886-4dca-b020-2d15458a8c8f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7590522766113281	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:59:35.974102+00
c4401c22-92b6-4b13-be0c-d52db6b7258b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8496513366699219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:00:17.826202+00
3d766769-fbf0-4377-be5a-b0791ded0508	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7120113372802734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:02:31.357281+00
96b8ea70-cebd-455f-9583-86249ec1a159	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7247200012207031	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:03:04.749132+00
13e67615-7bbc-46af-8b42-208a079f7b9f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0186901092529297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:04:44.884405+00
1d8caec2-8e7c-46c1-9e1f-663599a8bba8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.798391342163086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:05:18.257822+00
10c9b38d-27ea-47c9-a16d-c1d0874bc502	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9993782043457031	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:08:38.56448+00
3aa92102-a410-4016-89c4-355c7f62ae8e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.197742462158203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:10:18.706809+00
04458f66-2d10-42a7-8467-5a8f936edcba	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1064281463623047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:11:25.454673+00
4d826e6b-53d5-4050-a6a0-ea30af89c1cf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7812252044677734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:12:32.233156+00
0628aa84-b537-4cfc-ae76-16ebcaa8f7c6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.328561782836914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:13:39.010567+00
b8de24a4-45ef-46fd-b6bc-d7af28201bd2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.110719680786133	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:14:45.801344+00
ad1ca5b6-cb8d-44dc-a452-4d1da11b0a78	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.951000213623047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:15:52.594245+00
c23fa713-31ce-4835-9d4e-99cccabde3eb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8796920776367188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:21:45.127083+00
a5480e8c-061e-4fa5-b9a7-fafe6fe9e812	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0360946655273438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:56:33.383758+00
f920a550-2559-42e5-ae1d-a3ba2c761b63	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0558834075927734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:57:06.777431+00
4a2b214e-0931-4d9e-8184-881b49827da7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7096996307373047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:37:01.439085+00
e0d5f62d-9126-4afa-9bf6-a18242b8186f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7092227935791016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:38:41.621025+00
a3fb337a-2a36-40c3-aa2b-8186d1d78dac	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.228975296020508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:40:55.153048+00
aa6d256a-2bc1-4b2e-b4dd-b499f9274177	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.158641815185547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:42:35.288342+00
6d9838a0-a85d-4c07-a138-b82bfe5d328e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7368793487548828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:43:42.070447+00
3e8b3867-3c67-4a8a-a4b5-c7f8a9d973df	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.076387405395508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:51:53.692147+00
3ed617d1-09c9-4219-a040-bfe543306752	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1741390228271484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:53:33.842702+00
1ad14b9f-8646-4e16-8d1f-e3616619b685	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8782615661621094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:59:02.586702+00
ce0d680a-d02d-47bd-8e4a-8ca42b34ff71	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1708011627197266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:04:11.506661+00
9a15b83e-87bb-4b88-98ca-82a3ba347d20	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7557144165039062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:05:51.634077+00
d2e8b993-fb85-4742-b43b-b77c960fca61	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.095460891723633	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:08:05.179156+00
8cb9a1b1-5c70-47fb-84ba-526432b2d72b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8198490142822266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:11:58.838691+00
3cf4f6ee-cd50-4442-8e8b-099a32f8b9bb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2776126861572266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:28:59.230363+00
1429b23d-1686-4535-901e-bff4a31bdfb5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7771720886230469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:32:52.94604+00
a18f1f37-7d14-4041-95e6-90d6e541a67e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.798868179321289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:36:13.233086+00
4c959d46-77e7-4459-aa01-d25df657ea1d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7457008361816406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:43:27.212791+00
068f8781-cae1-4579-92e6-48de92705ba5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.002239227294922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:44:33.971069+00
7681e6bb-2f5b-4861-b291-3e8707384e33	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1038055419921875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:49:34.537543+00
9bc25ae9-6864-48bc-8f2a-8cad4ce6757f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.647016525268555	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:53:08.841796+00
0d686c7b-edf9-4a1a-8d88-496e51acb42b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.864360809326172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:53:38.942133+00
6f1bb199-4922-4e5c-b2eb-9fe5a17622f5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5801658630371094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:54:09.024009+00
9042576e-d3a4-4982-ad74-e9dc99e5b050	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.899169921875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:54:39.133364+00
b05363d1-374b-401f-a756-e2993320fc46	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.164125442504883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:55:09.219506+00
2f4cec19-1620-45aa-a2e9-7f7000e7246c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.243518829345703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:56:09.388137+00
309f7e74-6ed9-46a4-aee0-f2ce8ed0ac24	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3527145385742188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:57:39.685305+00
521b2d6f-6ff8-497c-b5e7-cc66aa665eef	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.098560333251953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:58:09.761214+00
bdb64ee6-e01e-4c5a-996e-81c4d2e35014	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.501964569091797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:58:39.835385+00
7364b252-8203-4ff7-bf05-83fc28b50e95	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.329587936401367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:00:10.08939+00
a13e4a15-190c-4510-801e-dba8392aeaa7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.283811569213867	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:00:40.173058+00
ca256354-7421-4a0f-8436-09a03fa137a9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1181106567382812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:01:10.256032+00
f5c3f6ae-3db9-4bd1-b516-6d3b902550ca	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0401477813720703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:01:40.339731+00
0e58a106-d72f-495a-9f04-d6cf0d0d0b74	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1283626556396484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:02:10.419838+00
a7d2ec64-8081-453c-b5d5-0cced2e60fff	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.979827880859375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:02:40.512876+00
7c26454d-f045-4168-b824-a142c20ab90d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9817352294921875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:03:40.708587+00
d1e00cab-ffb3-4769-88a3-eb399f5b71cd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5773048400878906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:04:10.791778+00
e8e15f83-0900-4a71-aafa-b8077ea932da	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.221822738647461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:06:11.133477+00
0921fdb1-d38b-4b54-bef8-df0f87ebc9a4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8600692749023438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:07:11.290385+00
6e4a7632-09e4-47a9-ad1e-0760596d0904	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.123117446899414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:07:41.391047+00
df746166-b8a1-406d-9b4f-bcd9f1cec26c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.387523651123047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:08:11.463284+00
3e96aec9-bddf-4f02-9985-fadbab3a8b2a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.920461654663086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:57:40.154224+00
0cb92b19-f136-440d-ab23-85691e3b2d43	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.262115478515625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:58:46.928385+00
0db77374-9583-41d2-a5ba-a698aafd8fb8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.372264862060547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:59:20.307742+00
3d75fce8-2692-478c-abd4-fa8c1a444a9c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.318859100341797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:02:40.657202+00
483e5af0-852c-454e-913b-3269df58a0aa	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1369457244873047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:39:15.006914+00
97a3196f-3747-46e7-bb68-4a206dd171b5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.218008041381836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:40:21.777187+00
5655e9bb-081f-423a-84cf-1840e97412bc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.928018569946289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:45:55.656175+00
5ffe73b9-f6ea-4839-a305-310aa0e2ac24	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8744468688964844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:48:09.234812+00
db3dd3a0-9f90-4cec-bd3d-ec7e7b4da300	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9581317901611328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:06:58.423364+00
11411c62-675c-4bd2-beff-b1fc82847bc0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6955604553222656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:09:11.944825+00
bda3f797-e9d3-4a8f-a782-2d0bbc7254c4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9278526306152344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:09:45.331882+00
f6d51f99-907f-45ef-a2f2-0e9638fed998	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9314289093017578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:10:52.080464+00
317ef65d-6001-4d49-867a-1bfea14416b2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9924640655517578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:13:05.626777+00
90c71113-37e8-41c0-ac09-29fadc4b7e77	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0704269409179688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:15:19.188388+00
50906391-c758-4d8d-aa50-aba700b6168d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8093585968017578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:16:25.979111+00
c1cb6854-b726-4650-bef6-a885a01eb0b0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.14385986328125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:25:53.625635+00
0df07c48-811a-487a-b8e6-ac88a57ea02c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.207517623901367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:27:33.785824+00
e4fa5f99-3269-4843-8cce-0d146339557b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8315315246582031	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:41:47.088029+00
0c2eba85-2ae9-4f41-9416-174185e79445	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.828908920288086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:42:20.463464+00
e9cbe068-0fc5-43d9-812b-44af9259b3e1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1622180938720703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:47:20.941214+00
e04ba6e4-a93e-4bfb-8fdf-18a791196e3b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.958536148071289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:50:41.330109+00
106c1f3c-a1f5-4d7a-9aff-dbbc6a34064c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9831657409667969	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:58:35.93264+00
83d947f6-3f94-4a11-b155-3eb7229a54cc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0678043365478516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:02:47.631023+00
e544f3e3-9853-4a8d-8413-c43365cd17b5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0034313201904297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:56:39.50436+00
c48c919f-7b26-4951-bea7-69fe5a01d716	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4912357330322266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:59:09.913545+00
be237bd9-fb7a-4d6e-971c-9bd11fd4cf56	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3336410522460938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:59:40.007082+00
807160b7-2119-476d-862e-bd00bbd90d64	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9671916961669922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:04:40.885914+00
7fbc0d3a-14d2-4969-9305-088279c49291	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.046823501586914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:05:10.967217+00
f7033432-df4a-4394-a27e-12c8f8a2e3e5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8756389617919922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:09:41.718426+00
158ebf44-9f63-4936-a742-afeba77b1dc0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8668174743652344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:14:12.481213+00
cb0f960c-2b52-4d33-a55b-261bb636e630	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.122163772583008	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:16:12.822756+00
66cbfc8f-82be-4b41-b7c1-5cb36800d7bc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0859241485595703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:20:13.529893+00
1d588ef8-97c2-4369-b5f6-e63562e93688	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	19.59824562072754	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 22:05:29.524809+00
c0219930-914f-4af8-a861-ae8fc49cbb1e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8243789672851562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 22:58:13.545085+00
24307020-d798-4f23-a969-c6aae96b8a62	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7850399017333984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:02:07.278153+00
ed0e1784-af5a-4fd7-9354-0be36e7483d8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.716541290283203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:03:14.05602+00
5de3f173-e3df-4d31-96a9-151444cf38cd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4106502532958984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:03:47.445098+00
64aa3be8-3c18-414a-af24-048ac2e87227	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.75421142578125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:04:20.851065+00
20c106a9-f083-40c3-966e-d2f1cad01a07	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0537376403808594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:04:54.240506+00
25bcf36b-3678-428e-a597-7f6429c336b7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.966714859008789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:05:27.625523+00
a2f1cdbc-108d-4335-a378-364becbfa037	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1507740020751953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:06:01.012289+00
8fa26784-d385-42f1-a006-64b070cdf5ba	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8520355224609375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:06:34.41874+00
7d415ba7-4ee9-4af2-9d20-d9955488a8aa	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3729801177978516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:07:07.845655+00
79db3873-2883-4e13-aaf1-e67a26123a83	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1054744720458984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:07:41.223482+00
eb2546ba-5732-4f8e-8321-8f02010142da	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.4842491149902344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:08:14.612609+00
c6560090-e5d1-4458-8778-703cfacfb171	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3584365844726562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:08:47.998922+00
2c22c5fa-c6a0-4ed1-82e6-09293981fc8d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9404888153076172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:09:21.387211+00
7426ed0d-e2eb-4318-90cf-7babd23e711f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.124309539794922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:09:54.771234+00
80dcb3dd-5460-4ba9-b878-b278ddea584f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.013299942016602	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:10:28.165013+00
df8a687a-85fe-481b-8efc-2df5dab123eb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8188953399658203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:11:01.54047+00
f20bd310-1223-4661-b852-07af450b403d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7735233306884766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:11:34.926047+00
57d6aca9-e576-447c-b971-e7c297e22d68	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7452239990234375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:12:08.296579+00
bfba2adc-fd20-4015-ba66-8e27f44c728c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9103755950927734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:12:41.696069+00
7c9487f1-2d65-4771-b20d-e5f724cabe89	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3992061614990234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:13:15.093861+00
9c583cfa-dbe2-4d79-973f-6ac9de598529	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6340484619140625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:13:48.521493+00
85ba362b-6cc1-4b8c-a2cc-c07ee85f1dcf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9137859344482422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:14:21.910665+00
75e8b8d4-8397-4cfd-a4f3-860e2ad342e1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.852273941040039	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:14:55.300928+00
2c35d1c5-9cae-45f7-a01e-f3d85f5e7400	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4042129516601562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:15:28.688014+00
118bb089-8dd9-465e-a98f-8fd860752799	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.283334732055664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:16:02.072203+00
80b45669-ebc5-4428-911c-2ed9b359e92d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6543140411376953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:16:35.460551+00
5b34c7ee-d510-4a5f-a238-926bd3702d36	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8215179443359375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:17:08.845173+00
8419c3e3-74c9-4c04-9ba9-62eb97c64b79	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9214153289794922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:17:42.230998+00
1a831f10-b217-40b2-9443-adc3c0514836	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.28826904296875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:18:15.621598+00
1d0228cd-bf4d-444d-baa4-349dbef2115c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8305778503417969	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:18:49.056213+00
db373f3e-f325-43d6-b710-02e1db6549c3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.104520797729492	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:19:22.431553+00
6210d90b-7318-438b-bc32-f2408acea0f7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0875930786132812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:19:55.817774+00
f890c172-65b3-4502-add8-5d07f2104c99	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.769947052001953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:20:29.239755+00
e1c90050-1320-44dd-b546-8b2582db538c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.96783447265625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:21:02.640303+00
1e2e5008-17d7-45a2-bab0-9b72a7914078	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0225048065185547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:21:36.029937+00
1718df2a-7940-43c0-a221-95a55e74ad2d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.027273178100586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:22:09.416781+00
8dac0ad4-6e1f-418a-a38a-64594e437995	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	13.19265365600586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:22:42.846476+00
70306440-5a92-4b5d-8323-369cf4076e3b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.144502639770508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:23:16.241389+00
818a1224-0416-4d89-a907-11472c59b555	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0232200622558594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:23:49.625843+00
7ab3d43f-afba-4aca-b8eb-4d7fe665847f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	5.93256950378418	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:24:23.034288+00
9f469070-7c45-4ff2-96e3-1fddecd71c98	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.445863723754883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:24:56.43572+00
a35d9d24-019a-4985-97e5-b431fff2a8f8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.8099288940429688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:25:29.851162+00
756e2a9a-cf3a-4a2d-9a6a-4ece34f10281	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5506019592285156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:26:03.229189+00
fd337bf4-8435-4555-a3cd-7258974d4c5c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6564598083496094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:29:57.176486+00
9f1b5acc-d954-44f5-b543-b48e2a885e43	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.048969268798828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:30:30.564566+00
0b6c6d57-2f25-4a10-980b-c2b96d1935b3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.824544906616211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:31:03.958433+00
149a272b-8a28-4973-9a63-f92bfc2b1e2f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	12.311697006225586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:31:37.347069+00
67324a61-0a84-4c70-b8d2-2e58ea53eeda	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5932788848876953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:32:10.709011+00
586e4e9a-20ed-4504-99bd-c4c7adfa555f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.236532211303711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:33:46.793655+00
a70b2949-81a2-41b6-bc8c-4aefd050b7b4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9831657409667969	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:34:17.948946+00
8e1947f8-6412-4c5d-b92b-4b861f8354a2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7466545104980469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:39:48.394189+00
61b6fa01-68b9-4f20-832f-217578fa2a8b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7669200897216797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:44:48.867875+00
2a0899fa-988f-4230-8a5a-e45cc9a0d8a3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9905567169189453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:46:29.048672+00
e127a4ae-85d6-402a-9322-9ecd57a26495	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8696784973144531	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:14:12.425304+00
bc792518-2176-45ab-822d-dc6b78d4ae86	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0139217376708984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:19:12.899809+00
0227b864-1cb1-4c2d-b962-2ae1bff9b17e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9571781158447266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:26:27.0108+00
b657aa4b-2e86-4251-8320-ec12c78acb2c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.058267593383789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:28:40.544868+00
492c39a9-2d8e-4c56-8c97-070a10d27f9c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.966714859008789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:41:28.572812+00
3f2a6110-dacc-4b92-a001-a8d5a5e4ac45	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9004344940185547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:42:01.948853+00
481ce031-e578-46ab-ac16-0f0cb6bb5089	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9240379333496094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:42:35.333155+00
225d036c-c97f-482f-bb7b-68b55cfbbe67	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0618438720703125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:46:14.159843+00
fc5d7c4f-1534-47c7-90aa-13a1e89f6228	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9135475158691406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:47:54.319032+00
eafe9057-9bcb-4663-ab72-917dde51b946	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1812915802001953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:52:48.268972+00
e7cbd1ed-3646-4278-a992-6abe967ec35a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9652843475341797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:56:29.836325+00
ce6a656e-e396-46d8-8e23-45456f605980	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.028226852416992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:57:01.251219+00
3e7200b1-cacf-41b0-92c3-fbc384ddc5f2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0563602447509766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:59:07.389132+00
88459f7c-81e6-4c95-8ea8-aaf8e1ef3ed2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9202232360839844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:01:44.83667+00
c431deed-6680-4612-9a43-fd39456e5ae4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8596649169921875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:03:19.132012+00
9e764df3-cd8d-4966-aafb-77885b4589b6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	11.564254760742188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:07:29.796784+00
5f5b31c0-daf2-4b04-a43e-883f4e16940f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2585391998291016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:14:46.639391+00
4ccaeb8a-d22a-4296-8a7a-e83698116403	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9369125366210938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:15:17.170738+00
fa3d0918-dda3-4a2a-a459-028a6fcab779	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.016305923461914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:15:47.813058+00
ee16e454-4775-4d66-9c59-161fdbdba1b5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1233558654785156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:03:10.623188+00
bef21396-9408-43d2-a129-cadbc03d35a2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9488334655761719	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:10:41.891812+00
5211a8c6-6401-4966-b0a5-b910e46beca7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.305269241333008	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:16:42.918217+00
51188a60-4358-409e-a43e-86793a28bfbf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1347999572753906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:18:43.255904+00
9fa681b3-d3f8-4b7a-8fad-02bd680420dc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.260923385620117	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:21:13.698783+00
8da32673-690d-4d66-95ff-53c1ac82e0e7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.483844757080078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:23:44.193174+00
43a9eff5-f539-4356-bb85-d699b19aeb8c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0079612731933594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:24:14.28413+00
c654abe1-2e6b-4cd8-97ef-9ec4d8baace0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1238327026367188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:27:14.814609+00
96040c48-87a8-4a25-bbbc-805c1dff63cf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2575855255126953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:30:15.374274+00
bda5b631-d9bb-40fb-b541-14047ad69d2c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4721622467041016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:26:36.62651+00
84bb854d-2fc8-4854-bf92-5e8987f2ff67	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4971961975097656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:27:43.402109+00
1f8784f5-ab1b-4104-b616-e9c3bf3f082c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9152164459228516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:28:50.1787+00
a1216440-a71f-4537-9e88-76783873b723	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.406597137451172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:33:15.315592+00
a8a65f28-d881-4f70-9d1f-1cb8df4a3aca	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9555091857910156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:34:49.262911+00
9c2d18b5-598c-42f9-9cfb-830f1a22f866	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3055076599121094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:36:22.53788+00
3c19bf13-4385-448d-b1bf-a8cf025b74cf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4726390838623047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:38:26.423507+00
ea5bce37-21c7-4e79-8f93-db22e551b5e9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2118091583251953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:40:30.211512+00
0a51c975-5d83-421c-bd4d-2aa5e136e11f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9655227661132812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:42:02.98496+00
c05e6cc7-4281-4fde-9548-454c0458ae81	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6192665100097656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:44:15.481568+00
cf360f16-2ae1-43e9-82d2-ac3fc78c7d02	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0363330841064453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:45:22.241003+00
2b12c8ae-f325-4a53-aa73-063247869942	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8320083618164062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:47:02.433878+00
9dcaf0bd-1eb0-434f-addc-a6439b9edb9f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.531766891479492	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:47:35.851959+00
31f622da-fc63-43a3-95ed-9e4f90d1fef9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9583702087402344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:48:42.620209+00
541ad54f-dd18-49c9-9ef6-a30f0d290097	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9347667694091797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:49:16.006544+00
c1101da0-be84-4831-9393-58285a491420	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7991065979003906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:49:49.391467+00
e9c8cf08-b4d2-47ab-bf06-287dd5bdde6f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9619464874267578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:50:22.773938+00
83e6fb17-320e-46ec-9fb1-bd0021178f44	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7650127410888672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:51:29.585822+00
fd8c1d54-3bfa-4483-b37f-ced606badb52	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9657611846923828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:52:02.968535+00
43539e24-7a71-4e09-90c1-69cd7fa8633e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9485950469970703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:52:36.352416+00
7abe4c08-9819-470b-9399-5a728cdccbd5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1333694458007812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:53:09.725155+00
0c719a36-6e4e-4e15-8920-587d7755379e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5420188903808594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:53:43.11076+00
7af864b3-1855-4f6e-b609-b36784a13c80	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6438236236572266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:54:16.52226+00
96f1b519-029c-42eb-8a17-4e007dd183d3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7626285552978516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:55:23.328467+00
d2611975-b7f9-4fb0-b588-f8986a40e28c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8072128295898438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:55:56.715555+00
afe9c1fa-badf-4344-b5f6-ee99ff92125a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1839141845703125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:57:03.50538+00
d109d857-38f0-4f8b-98a2-a054c551aaae	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8589496612548828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:57:36.890447+00
b4394e86-170b-488a-945e-d1d353b224f1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8699169158935547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:58:10.274891+00
9ee70f11-3a12-4387-9fbf-b830520d76b6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9297599792480469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:58:43.656971+00
0ccd2ec5-7d16-45e3-ba85-aa23881f84f7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.973867416381836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:59:50.426466+00
d265c20a-8d18-4543-856f-4f4db3df4706	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8467903137207031	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:03:10.69486+00
b1d1e364-981d-49b8-8e16-8770de1523e6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8508434295654297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:03:44.071307+00
fa8b4886-d678-4f3c-96e9-2681388076e7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9011497497558594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:04:17.452255+00
5bd525c0-e440-4102-ae31-c208f6eaa0e6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.752065658569336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:04:50.834611+00
7b2f7807-f6c9-47ae-b833-51a1a915e904	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8355846405029297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:05:24.211969+00
a1a2d735-89ed-4b94-a610-318c602e34f3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7871856689453125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:06:30.975642+00
4d6f14b0-5eeb-4eea-b9dd-d1aa0ffd6f97	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8050670623779297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:07:04.358113+00
b7f7b2af-cc5d-4a75-84fa-9b36cebab388	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9633769989013672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:07:37.728842+00
167d4bf7-ccf5-4287-973c-8581a534632c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9028186798095703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:08:11.102574+00
82e3a009-d4c3-43bb-b1da-2aa06763b4d3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8520355224609375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:08:44.48615+00
3832058c-6d27-4a00-8388-34b069d1b574	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7735958099365234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:09:17.872263+00
5ed64448-0387-4da3-ac05-d32e4a2ee3c2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.271818161010742	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:27:10.015911+00
fd1ece94-9ba1-4980-8c3f-7dd014f86067	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7502307891845703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:28:16.768904+00
a7d162c8-d7e4-458e-8e5c-cd8581144831	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.139568328857422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:29:23.558097+00
16760cf8-3378-4364-afc4-71fe9c9a6d55	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3474693298339844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:32:43.712413+00
ab8225f5-0de7-4e77-9055-a7c790af22f2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.941131591796875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:37:55.522798+00
822af706-efd4-4705-b5bf-5cff311b8541	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.333402633666992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:41:01.185672+00
d09accd6-408b-48b3-bef4-ffb24ed81ed7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.349853515625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:48:13.212809+00
800f2801-0e32-47ec-ae99-a30d49e6e29e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.3974647521972656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:50:56.196558+00
e911321a-9b10-415c-8a5a-10cd536585ff	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8155574798583984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:00:23.811566+00
fa9c2a32-3333-4c00-a4bf-695756172728	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3925304412841797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:00:57.186784+00
1634b229-2315-4c30-bbad-c57bc2b7b6ff	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8360614776611328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:01:30.562945+00
d18e3001-3c0d-49ef-a6b0-bd4077c50753	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.040386199951172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:02:03.936203+00
81846140-bda7-4481-adc7-2f58dc1b1706	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1843910217285156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:02:37.316585+00
6eb5a77f-b5f0-4241-89e2-1152cfff6f2e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.962900161743164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:05:57.601683+00
2707e4f6-4da2-495c-9156-dbf555dbb3ef	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.766204833984375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:09:51.243893+00
7c934221-ae9b-4086-b942-f9500a813599	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.795053482055664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:11:31.400882+00
2b8a2a3e-5175-4b14-87ea-ba14beb69795	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.909494400024414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:13:44.94389+00
5b860f88-3180-4361-9ae1-bffc5b374c2e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.920938491821289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:14:51.716356+00
70ed5dae-d9d3-4f9b-8ce8-77d5dc40c51d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7733573913574219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:16:31.874969+00
09201e4d-a12c-4ecb-bf85-90f8a4c5101e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7971992492675781	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:17:38.650784+00
20fe74c2-86c9-4eda-bd71-535a325a43ab	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9922256469726562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:18:45.420749+00
f77f205a-0c2c-42aa-acf4-7e549097de40	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9652843475341797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:16:59.373976+00
36bb7d30-3af9-447d-a5f0-b2b934dbbe39	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7805099487304688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:17:32.767977+00
86ed614e-a6a1-47e8-9554-b830a96b8db4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8243789672851562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:18:06.138497+00
88780d95-1e16-4abd-b6c4-a87ee577d315	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.973318099975586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:18:39.516298+00
112f31c3-8f51-44d8-b85a-6d94fb8f4bfa	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8587112426757812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:19:46.286615+00
8f59a510-5aae-4676-b4d2-1ba44a784cfb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.492666244506836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:20:19.731127+00
e8b12671-d4ca-4d51-8def-917d53e90abd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0360946655273438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:20:53.121136+00
f1804481-4b1c-407f-a30b-5449c56656b0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8339157104492188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:21:26.493896+00
e5de1f47-fc5b-451f-813f-b69bcefaa3bf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.498149871826172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:21:59.910583+00
5995ea04-faea-44b1-9bcc-5e48bc90f04a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9822120666503906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:22:33.287592+00
592884f5-f68d-476a-afac-18b6860c7996	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9352436065673828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:23:06.677509+00
8222c34a-e8c9-4954-ab35-765624772269	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5548934936523438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:23:40.065239+00
82c39b5f-541b-4242-b5ac-bc7ce7b20ff6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.017498016357422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:24:13.448879+00
b8abe0d5-ab4f-4ab5-988a-ce4723239387	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9581317901611328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:24:46.833753+00
afc8c39f-f509-477b-827e-f465fa336496	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9338130950927734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:25:20.221049+00
7276d88f-b027-4f60-ae00-095a922618f7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.922607421875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:27:00.394091+00
817151c3-0c5d-4e97-86b5-d7ebba2137df	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7993450164794922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:28:07.162059+00
5c8375e8-c093-4c02-af9f-4bef5fda841d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0241737365722656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:29:13.950707+00
a717df5d-4d9e-43ec-b6df-f1eb13f1b259	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4204254150390625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:30:54.151387+00
66db1d95-91b8-4bbe-abe3-c4904fdfa06b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.324342727661133	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:31:27.541112+00
21e50247-d868-4776-b445-fd1d255ecad5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7658939361572266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:35:20.484987+00
ef2642ae-aa92-4554-a93a-39e7a174df4a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.195119857788086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:35:51.523584+00
812379c0-a9de-42c3-9733-55ad3ed2f08b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.249479293823242	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:36:53.681964+00
7f9fa0d1-64de-4c43-b39b-9870b13fe0ba	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1066665649414062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:37:24.571331+00
06a18754-bea5-4e2e-bad8-553caf425394	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1750926971435547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:38:57.347631+00
bac0101c-0501-4a3b-b135-7587ed4e4704	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.0074119567871094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:39:28.353841+00
27d8552d-39e2-4b91-ac30-31ea7ebfb33c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.512859344482422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:39:59.306464+00
87900af4-dc35-49c6-960e-d0f0e80465dc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0835399627685547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:41:32.144852+00
e9b812a2-a033-4255-ae45-04a0cbf36321	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8894672393798828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:42:33.830065+00
9f0f2c6e-64e2-474f-9639-55cfc2d7b182	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8682479858398438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:43:04.816016+00
34c03bdf-b2fb-44ba-81a3-4eccecc48b1a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3527145385742188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:43:35.799883+00
73cacc62-5ec9-4be5-824a-8dbb95920c3d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.637624740600586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:44:06.593375+00
f48c8a9b-c9da-4626-a636-37b680d107aa	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9619464874267578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:44:37.46657+00
e4a31361-3243-4eeb-ad9b-d5b5fbeac851	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9764900207519531	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:45:08.412544+00
0962aca5-36ef-410f-a828-81c0068dfafc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	6.056547164916992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:45:39.386998+00
3e665fa5-2def-460c-8ce5-622c0b7ba3a6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.79180908203125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:46:10.213653+00
391da471-fbbb-4ff7-aa29-3c5e7ad6b02d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3660659790039062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:46:41.064476+00
ca52405b-c1ce-49a2-aa07-d47b42ba702d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.377748489379883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:47:12.01699+00
282438f4-e34d-44f3-a477-d3923c4f1a75	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8672943115234375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:47:42.505416+00
abdf32c0-97b5-4d26-91fa-2f05ca5eb0e8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.432107925415039	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:48:43.985347+00
6f878e0c-f489-4deb-92fb-6c3104857a16	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2008419036865234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:49:14.31244+00
1a2506e5-7377-4bc6-9395-c40e7059ab18	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7654170989990234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:49:44.88571+00
64e766d8-2c5b-4067-b4da-f5d4493397e4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5930404663085938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:50:15.222816+00
1294a512-6d85-4388-b66e-3bf0b73e1728	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1631717681884766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:50:45.428139+00
21d44dcd-c221-4136-91fc-cac1857e4a7f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4826526641845703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:51:15.644956+00
604f10b7-2693-444b-ab36-b39c7edb04b2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2554397583007812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:51:45.972099+00
d786dbfe-43ee-4ab6-af46-be08d437a3f7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.821134567260742	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:52:16.406697+00
47607936-de33-438f-885b-62d9b669e1f2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.027677536010742	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:52:46.636623+00
1782d22c-d9f4-4cef-a820-84980e580310	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1796226501464844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:53:16.87306+00
fcbafe07-2c5c-4076-89a6-afe3dcc05273	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0542144775390625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:53:47.227851+00
9e38302e-6f58-41d9-9804-d3542902e112	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.283262252807617	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:54:17.46494+00
72ca0d0d-7936-475c-9618-6228165d202b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8259754180908203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:54:47.680103+00
b3ef0bd3-eafd-4fef-b255-c0af4a6bff2c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2330284118652344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:55:17.891523+00
2e18d14f-c106-429b-92bc-88e7ffcd01f6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1092891693115234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:55:48.081343+00
9707b970-516d-4ec0-b680-158421af6625	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.369403839111328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:56:18.296528+00
ef3efc93-9e17-4e5c-aafc-2a3b109a52a7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0122528076171875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:56:48.46507+00
4d8a8360-2fe0-4dab-83f4-6c819afcdd59	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3789405822753906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:57:18.628006+00
f807deac-4819-4ef2-a77c-550c82b1e09a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2368431091308594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:57:48.749135+00
14c4ab1d-c2e3-4db3-81fd-2e445471c70e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.6253929138183594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:58:18.853536+00
c528d0cd-f3c6-4124-8827-58bd2d097f30	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3469924926757812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:58:48.953957+00
14069fe6-73a4-41fe-ad3a-04d3c56ac7cb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7570724487304688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:59:19.043676+00
0c7d9b7f-2b4c-4ea8-8eb5-dd1912aad42d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8723011016845703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-06 23:59:49.112434+00
65b20a0e-f34f-4779-b84b-57d0cba6ed4a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.525806427001953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:04:49.891483+00
8447c5df-e752-4096-8b60-3c098604a9ef	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8856525421142578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:08:50.423879+00
29140f06-9455-4b5c-9494-99052e50a6a5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8529891967773438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:54:49.938426+00
e8f14f8e-d0d9-4387-8ccb-bdf974d68d65	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2575855255126953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:13:11.562964+00
15533a4e-343e-48cc-bc68-092b64970fbf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9164085388183594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:19:18.806535+00
cba7bb68-4e9f-495e-8349-207913e357bd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.006053924560547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:29:47.356121+00
913e41e2-7e95-4c60-a69a-3d25b66edc33	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7852783203125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:30:20.75234+00
3d28aabd-a8b8-4b90-92a6-6dae0ade5477	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8248558044433594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:32:00.929948+00
f8ea3eec-947a-4dcc-a78d-2946b277ffa5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	12.410402297973633	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:33:41.102709+00
512dac6f-c0a5-41d7-9320-52a62fd3f008	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0575523376464844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:35:54.6652+00
f99b0f5b-c67a-49bd-a82b-03733af24ea0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.339601516723633	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:45:55.635935+00
8baeba51-4469-4ab9-ab41-871f1ab0896b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9392967224121094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:47:02.417957+00
c8396925-0848-4d7d-9fff-ed5f4f533ac0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4704933166503906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:47:35.806896+00
766ecf2d-1efc-40b1-9753-80909ce01e75	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8112659454345703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:48:09.19458+00
94f0a8fd-c63a-4296-b094-c96c936c428d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9748210906982422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:49:16.010759+00
948cad44-945d-4a02-a714-3b9a9f4668e8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7669200897216797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:50:56.166202+00
dc5fd566-79ed-49ae-acde-e4fc0ad6f226	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8246173858642578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:53:09.73905+00
95033ee5-ba61-435d-b764-2e84a437d531	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4368762969970703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:54:49.89625+00
1cfcc576-97da-4788-b107-e205e2f8ae53	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.223491668701172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:59:17.07735+00
ddf9cdd8-1b25-46ea-bfc9-d6a2076f2c88	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6137828826904297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:48:27.745401+00
5da6a2bb-d58a-43cb-9dc4-4dd284d9030b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7409324645996094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:49:01.13872+00
fb95620c-2463-4ffd-9ec7-0730affc7e72	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.406452178955078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:50:07.951173+00
1746d60b-8da6-4f2b-ac68-5cdb3a4b730e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.382516860961914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:08:41.559481+00
44315daa-2f7b-4ffe-bac1-731c1b52052a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.270936965942383	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:09:11.627842+00
5f126490-4fa1-4d47-9b0e-49301db31eb2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.120494842529297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:10:11.803811+00
e820e4ca-d0fd-4041-9910-44a46c645cd9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0411014556884766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:11:11.979019+00
565ccb54-15fb-40ba-b433-0723f9ade86e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.213716506958008	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:11:42.06036+00
5fc0409f-3801-40ea-8d15-2757f3d08f04	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2172927856445312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:12:42.235718+00
2403203e-c9ba-4b99-9b2a-5cffd511663a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5174617767333984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:13:12.315194+00
9c001367-1249-4bfd-913d-96ab27486d5b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1049976348876953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:15:12.637835+00
0fadf9f1-d39b-427d-8f4c-38973b4a2ba2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5796890258789062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:15:42.729709+00
e62b2f4e-8be2-4cde-9422-e39a33f3e212	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.228260040283203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:17:13.002194+00
a57d0ca3-7950-4950-a9fc-a6af45c312ec	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8575191497802734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:17:43.088652+00
ee8f7280-a0b8-4151-8565-c76941aeff90	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8694400787353516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:18:13.162854+00
d88f7e69-84d7-487f-bf24-48b85a84e9e2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1932125091552734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:19:43.452598+00
e4b7fe8d-f6d3-42ca-b000-b804ca277516	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3200511932373047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:20:43.615879+00
100b85df-4304-4a5b-af7a-983ffa89d9b2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.135753631591797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:21:43.788922+00
0904aaa5-f9fb-47a6-a0be-6ebedcf31552	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.783060073852539	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:22:43.980406+00
81b42288-ad9f-4e8c-ab14-f672f329422a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	15.72108268737793	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-09 01:49:17.341055+00
77d25f17-f903-432e-963b-42d6724d2be8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	18.671035766601562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-09 01:51:35.333224+00
585813b6-d9d2-4233-8f20-f0aad920e697	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6531219482421875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:00:19.189366+00
5443dd36-3f2b-4921-a6f4-ec84a730161f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9931793212890625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:01:19.352735+00
4ce126f5-49a4-44cf-bdc0-84005796a125	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4499893188476562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:01:49.427408+00
a872b09c-1aed-4367-892d-129aaa54b7b7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2428035736083984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:05:19.965171+00
2edd27ce-b645-48e9-b838-1c8ca1d6130d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.052783966064453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:11:20.811519+00
54319914-6718-4df0-a93b-c4bcceb752c3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8129348754882812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:56:30.111803+00
c39a45cb-e566-4442-8840-94ed1ab87522	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7819404602050781	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:59:17.04193+00
ee6cf8f7-52e7-4de8-9451-e82b694aef3f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0904541015625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:10:24.628244+00
4bbfda7a-5396-46ef-8c43-e9bf72af450a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.072023391723633	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:14:18.337948+00
6c56d7bb-4e73-4cd6-89e3-cea678fc1f06	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1779537200927734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:18:12.03694+00
10fd71f5-f619-4766-abbd-8c9d4992be93	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2623538970947266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:19:52.180322+00
ef21a92b-126b-43e8-9a77-08bdea437fdd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8742084503173828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:20:25.56392+00
4cf0e0cc-937b-4767-8cfe-bfcaee306612	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8842220306396484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:23:12.562077+00
d5059405-b3bf-41d4-b57b-53fe3bfe33b5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0236968994140625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:32:34.319086+00
43b2a273-f4b2-4688-8e5e-7f220c72ef66	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.981496810913086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:33:07.706288+00
878f7cca-811f-4f1d-93e4-fd042865ba1a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5594234466552734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:34:14.493898+00
98ef97f1-c64d-47f8-a978-3fbb1dec0810	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8053054809570312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:34:47.876734+00
2150f2d0-55ca-4cec-8e0d-b6d6e062db02	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6667118072509766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:35:21.278368+00
e069bbf8-b3b2-476f-81cb-44f087c689d8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.775979995727539	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:36:28.051698+00
74b88512-66d1-4241-8617-69c9c510d135	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.314329147338867	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:37:01.440407+00
7b4da513-63b2-4b1c-bde2-e4fbe87620d7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.844167709350586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:38:08.238809+00
20391ead-b519-4fb5-bb1f-1c5b80914473	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.042055130004883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:39:15.019993+00
faa063ed-3d93-449b-b0ae-77a2e5821895	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0599365234375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:40:21.793291+00
63a85082-8329-4e71-b203-6efe145769ae	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7048587799072266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:40:55.18779+00
8ea34058-964f-4e8f-aedc-d8aa01686c19	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.087116241455078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:43:08.717983+00
a74994a0-fb91-49b3-8b81-02750593b5f3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7938613891601562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:43:42.097272+00
b03b5a5f-f82a-409f-aac3-772b13c25652	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7986297607421875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:44:15.481847+00
5c7af225-a2ef-47f9-bb24-63e654b72c6a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0093917846679688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:45:22.245604+00
5ba13dc3-6f7b-4e3c-ac81-e5d1395b3ed9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9540786743164062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:46:29.01559+00
658de820-0acd-4e98-ab5f-a20f54af9956	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4628639221191406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:51:13.108931+00
1e0e364d-5cb4-4952-94a1-3ccf9087bf5d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8718242645263672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:51:45.253476+00
37e5b4f0-7445-4bdc-a582-c5f09684cf22	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7986297607421875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:52:16.773313+00
b5a942e8-db9c-4d96-b76a-fc25f42dafd4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	5.617618560791016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:53:20.134766+00
95b413be-ba75-49c0-bbd6-74edec417947	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0160675048828125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:53:51.612868+00
213d1eaa-36e8-4e12-a02c-5bc248c88026	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.928091049194336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:54:23.258974+00
6d81e894-ddbc-4be6-8302-49c20dbb3cf0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.454519271850586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:54:54.88445+00
008cb645-2284-433a-8a28-68c6cd510962	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.947164535522461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:55:26.516515+00
479a2748-08bd-4e09-a7dc-814a60a3dc39	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8925666809082031	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:55:58.235475+00
c8a5f072-b494-4c68-9c96-e3bf208854c6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	11.890172958374023	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:57:32.866902+00
c3fa7e45-1486-46da-a321-acc07b15c351	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.886606216430664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:58:04.406028+00
6e2a8c1f-983e-46ce-85e6-dbe762371f58	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.015352249145508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:59:38.917601+00
9c9ee71b-2fb8-402e-8955-7288d9e476da	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.092599868774414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:00:49.275543+00
4acceb81-c999-4e19-a29e-f1684d71e817	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6254653930664062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:02:19.499164+00
73a306ab-5b7a-4b1c-a86f-f9d757af8879	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4569034576416016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:02:49.560134+00
d3f48a66-32dd-47c8-8d4f-0cd2f0a3199a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4404525756835938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:06:20.11163+00
3f9f5249-7894-473c-aa2f-2e99be8ff981	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.146482467651367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:06:50.172029+00
42f0b7e8-ac3d-4139-ad48-5eb6812e3a1f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9048919677734375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:10:58.01858+00
e6b1e6a7-3511-43db-ae56-319520db9c0d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8227100372314453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:12:04.782375+00
13408497-67b6-42e7-9ae0-08c6712efbaf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.422332763671875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:12:38.179834+00
be9a13ed-06b0-4218-8230-e552bc390956	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.018451690673828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:37:34.85395+00
53731d02-9aed-48b3-8a62-b5a4ac2b9a41	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8420219421386719	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:38:41.625484+00
62c7d172-65ee-43b6-9785-2df87e3a40a1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.325296401977539	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:39:48.405124+00
5d4f468d-7f03-4bac-be1d-ac2920b1b259	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3088455200195312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:44:48.860576+00
46abf2da-e4d6-4242-aa0d-c21ef0a82c79	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8012523651123047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:50:22.7831+00
e1dfaab5-7854-4630-a878-7bd49cb773ac	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0904541015625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:58:10.310123+00
9c4c07a6-a06b-459f-bb42-d022884447ca	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.171754837036133	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:00:10.411525+00
fefae832-32fb-48d8-94ad-38d61bd28963	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9345283508300781	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:01:13.380503+00
6970025a-c5aa-4a11-b5dc-699d44111878	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8801689147949219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:02:16.197514+00
740206cd-85aa-478c-b1a9-7e3072b56a45	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4106502532958984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:03:50.574671+00
ca78c5dd-04bf-4d33-a51c-937ec98b9f2c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.062082290649414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:04:21.683395+00
90b6b72a-4278-41a7-8ace-788c70a24a64	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.755403518676758	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:04:53.091599+00
fcd6f73e-e39b-4284-9118-f91519f8fc40	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8639564514160156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:06:27.156141+00
2e8b21a6-524c-4c03-bb33-2b9187edb7ce	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8987655639648438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:06:58.535515+00
2b38f42a-e3d1-45e2-94f8-1f83ae79c3b0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.972126007080078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:08:01.254396+00
dc5902b4-561e-4f1e-bae4-0c04925be8c6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.237558364868164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:08:32.690637+00
7f055a91-cea3-42f0-976e-23dfff5ce21b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.086639404296875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:09:35.346758+00
8fd5359f-6b4e-47e6-897d-1d09f54d6ad5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.901315689086914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:10:38.141316+00
930b97b6-8b3e-44a5-b783-362dbe61b8f0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.0510425567626953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:11:09.457748+00
07d19584-3e7a-4190-ac85-ced924a8434d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.034902572631836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:11:40.752284+00
9df7506b-4f5a-4e5f-9611-2e68bce8e056	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.254009246826172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:12:43.353756+00
36b63080-6d14-4826-af67-f5502e9670b8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1147727966308594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:13:14.246174+00
abaa91e3-e9e0-4289-b7e9-b7b64ec90e67	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2208690643310547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:13:45.286802+00
fdade893-d2b1-457e-9d4d-96f96a141bc6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1409988403320312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:14:15.984867+00
c9045c48-c73b-45db-a4ce-2512a4556af0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0766258239746094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:17:49.866183+00
9c0a55fa-afd3-497c-b44e-655d1099428b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1924972534179688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:18:20.347615+00
646a21da-3212-4e8e-b2f9-e43c141dda89	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7475357055664062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:18:50.943113+00
5c6ba4e7-bca6-4dc9-aa1a-a6196038a82b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.0629634857177734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:19:21.461787+00
a55f6759-c384-49c1-b1b7-324983349689	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.162456512451172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:20:22.254266+00
e6fc2f7c-791d-41e8-baeb-612a0e74295a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9108524322509766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:19:13.37268+00
41bf6d1d-8287-4d65-ae1d-ffd8be38ee08	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3953914642333984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:22:13.878926+00
f0f67cdc-7400-47f5-a659-aa443f792536	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9350051879882812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:23:14.108805+00
3460546e-0f88-404c-ae44-24ca103a08d0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9675960540771484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:30:45.468698+00
aa8b1448-34f4-4941-a3e7-aa6e52ac0b98	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1886825561523438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:03:19.672781+00
28fe700f-af58-4b39-908a-2bde1549f886	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.000570297241211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:03:49.733706+00
c1b54b28-9aa2-4b25-a523-e9c598d95863	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.255678176879883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:04:19.820849+00
28b2ea1c-f505-4b29-afc8-1585196430c2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2051334381103516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:05:50.028732+00
1c0080a5-4af4-48e1-aa5c-578588a0e846	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9958019256591797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:07:20.235817+00
ab907578-7601-4956-965f-5dcf0ef30dde	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.076387405395508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:07:50.293962+00
2bee308f-5fdc-4687-a273-acde5110319e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.001047134399414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:08:20.354821+00
5cbcff79-0b24-4b2f-a997-8087ebcc37e1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.040241241455078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:09:20.535796+00
c8366eed-058c-44fc-a601-54739b9e045b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9729137420654297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:09:50.601729+00
477b74c8-a24f-4009-b06b-a5647d3b6f0f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2020339965820312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:10:20.668116+00
60d071a8-2add-4a13-9942-e701ae935f3c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9710063934326172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:10:50.737907+00
7ca5bcb0-f306-4498-b298-42cae049172a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2547245025634766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:11:50.86437+00
761f68c5-6cbc-44d0-8615-2e0c4673c1fe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3109912872314453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:12:20.934187+00
24b3669a-f4a0-4878-af33-faf5720f2950	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.555370330810547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:12:50.999363+00
cc6d2322-5b82-41f5-a002-24eb4ae8c693	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8879642486572266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:13:21.083074+00
b24863d8-cd41-457a-b669-82cc99bb18c2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.531290054321289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:13:51.183919+00
3ca0dff4-e380-4e6a-9213-9392f6969c45	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.44903564453125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:14:21.258808+00
b2005394-d993-4fc3-862a-aca92caf39d9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8949508666992188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:14:51.3208+00
e4f99915-1e35-4b15-99eb-ada737dbbb6f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9009113311767578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:15:21.383065+00
73cc802f-e88d-471d-86ff-456d4e4aefc2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1774768829345703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:15:51.436428+00
9a624097-3df6-49b0-8144-d5809d55961c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2041797637939453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:16:21.488303+00
fef9791f-68a7-42d6-94e5-4a50b6d5acf6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8258094787597656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:16:51.539424+00
c3fff9eb-8a1a-45b9-914f-bfd937b85117	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3202896118164062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:17:21.602+00
53157b4b-444e-4ed2-af3a-72b6c8691d24	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9931793212890625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:17:51.680917+00
126b37f2-9bff-4941-8dd9-6345e9ad97f3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2912025451660156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:18:21.752665+00
f4079dd8-1747-40c8-9460-b302a9fddc9c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.886129379272461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:18:51.81449+00
87c4f24e-68a6-4583-b53e-ede20c72aac3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6764869689941406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:19:21.900013+00
e9bb102e-6b1a-4f13-89b1-a05e86e77087	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0399093627929688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:19:51.956471+00
01d78b64-aff0-41d7-a0cf-0534457d74c9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6824474334716797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:20:22.031297+00
42a8cf08-f15d-4030-bd55-834303962bde	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.078533172607422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:20:52.094496+00
58d81556-9913-462b-b302-8a9e9d06baaf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.154827117919922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:21:22.15827+00
97b869cd-2514-43fb-87c3-32614ee24ee5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1371841430664062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:21:52.237265+00
0115d104-1ef1-4fff-8352-30a4909739f5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2284984588623047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:22:22.30773+00
68569018-ae9f-4c0f-a8c2-e9e8688bdbd8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9614696502685547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:22:52.376694+00
bb813bac-d0ca-457f-8a13-73c3294e765a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.371000289916992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:23:22.456422+00
7aa0137f-8813-431f-819c-1fa8d581a958	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3183822631835938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:23:52.52202+00
578cf7eb-7ff8-48d3-8c22-0fd937997e5d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.225637435913086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:24:22.57033+00
a9c6f117-735f-4b95-b55a-371564ecc540	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3050308227539062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:24:52.622164+00
ea6c0f7e-e5cd-42cc-85f5-322b6fd774e0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.270936965942383	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:25:22.674274+00
caa0facb-0a07-4f32-83f2-7839972df7c5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9402503967285156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:25:52.729963+00
8d1406d5-a1c2-4ea2-848b-aa541cd11d7e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.972198486328125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:26:22.793096+00
8fd481d5-810f-4d40-9d82-01efd488b1bd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.185344696044922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:26:52.880881+00
79ae46d2-c8c8-4346-a7bf-df81a956ea45	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1524429321289062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:27:53.002889+00
8e957350-6881-4d90-9fe1-4c1224d9ee8a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.840829849243164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:15:25.115914+00
713db438-579b-4b2a-8768-5cecc681fa3c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.435445785522461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:15:58.501317+00
e0646b0a-5b7d-4321-b87a-b97a4afd0f12	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7116069793701172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:17:05.258431+00
13120565-79d1-47b9-b777-0ef84e2944d9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.735687255859375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:21:32.385015+00
aa0767ed-c313-47ca-8f02-c2f953bfe067	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8792152404785156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:22:05.769012+00
0bfc9172-5849-48f6-b402-c8feabc74db4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.867055892944336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:22:39.156742+00
71c54fde-53f1-43a0-9e50-dae22d53169f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6040802001953125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:24:19.336462+00
67880aec-b6b1-407b-bc42-13b22cd89679	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9314289093017578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:24:52.725022+00
c8e6aac8-2c5a-4b0e-87d8-13fc5dbbc926	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7032623291015625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:25:26.109422+00
ee317c10-d049-4724-b9b2-30f6a9832d94	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8393993377685547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:27:39.723627+00
fec5f23a-10e3-476c-a953-60f94bb67a3e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8825531005859375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:28:13.108335+00
7ce8db3a-1307-4cd6-9ae6-eeeda838839a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0034313201904297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:29:19.885343+00
619b6b12-dce4-4435-a4dc-512a5438e52b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.829385757446289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:29:53.267261+00
5f8bd116-d317-4d80-9c31-90e7b8452ebc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7752647399902344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:31:00.184982+00
5d2af2b5-f0a4-42cd-9694-21a3b00659f5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8684864044189453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:32:06.945715+00
41822b16-5c24-4114-893f-364b3ea1d6f7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8603801727294922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:33:13.718531+00
19b67aa6-d669-4052-a99d-a6be9997956d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7840862274169922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:36:00.635333+00
a612d79c-35cb-494d-a776-a6720e32fb64	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.850128173828125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:38:14.166571+00
85b03977-5e39-4d97-9cc4-2639f4b93093	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7919540405273438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:38:47.537566+00
4f8468da-e326-494c-8c72-1e3693a306a8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8458366394042969	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:39:20.920671+00
59eb2a8d-5fb8-4766-83c6-60e77c00b64b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.806020736694336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:42:07.841449+00
1ae7ee0d-14ea-4168-b49d-8f92eb83e9ba	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3660659790039062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:43:14.622484+00
bc5a7202-0286-4347-8537-1402d5b1dce3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.025127410888672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:43:48.007935+00
ad175c52-08f1-4769-a6b5-62eb1c77555c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9106864929199219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:44:21.394885+00
e4de2dfb-cead-470d-ab26-45cc82e2ebdb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7631053924560547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:44:54.757594+00
eb5017ef-2d5b-40f0-9dc4-cf8e31563e18	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8763542175292969	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:48:42.592277+00
408dbc73-c146-4e7f-8659-122b5bf7cd0f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8703937530517578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:49:49.399566+00
d3a38a10-1f31-4956-a5d5-26d1956811a1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.197265625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:51:29.567013+00
9a50ee57-4a88-4433-a201-58d11d68e76e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.471923828125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:52:02.95872+00
18d0ae97-2028-4819-b258-4384a64d13e7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9502639770507812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:52:36.34325+00
797dee8b-59a2-418c-b5b6-9020cde32b47	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6677379608154297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:53:43.12568+00
e5de0d3f-78bc-4f1c-b363-63adfe4dc930	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7709732055664062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:54:16.510212+00
657d6c42-09d3-4e7f-809b-c98f3b132a34	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8458366394042969	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:55:56.749794+00
be4328d2-4a7e-4276-ac0c-87ef530f3b76	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2461414337158203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:56:30.133766+00
aa2b4620-27b7-4b0c-9b97-6754e69db445	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0475387573242188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:57:36.921825+00
cd4660a8-1f6d-4f09-b3e4-7ab575343067	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8818378448486328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:59:50.462813+00
efaea990-c573-49ee-a505-57fd609135c2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.000570297241211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:00:23.845118+00
3feb2e48-e4a1-44be-8c9b-4f8cac0d1a5f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6603469848632812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:00:57.229713+00
03de7d9f-023e-41f9-8e78-47776341706e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9831657409667969	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:01:30.611701+00
0b794333-eaff-44cb-b978-ab860cc15d3a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0151138305664062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:27:22.948618+00
8e99fd51-5503-4a4e-b28c-2c2025a57d8e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.155303955078125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:29:23.20447+00
761f9fe3-1112-483a-8706-f362be7868a6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2263526916503906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:29:53.267423+00
abb56d47-5d03-4e02-a9a0-3742b3f25378	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9257068634033203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:30:23.338237+00
9027e59b-0f7f-4e43-acf1-4e2a11f55f06	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.132892608642578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:30:53.408197+00
f27aa13d-53b9-4e98-af42-03aa2e885cf7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.026796340942383	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:31:23.47775+00
fa5150d1-f08b-49e9-8ba9-ee8a2e7a4e13	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9381046295166016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:20:58.962335+00
054fbc6e-dfce-40d7-9112-3a0b08d9068d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.124309539794922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:23:45.948309+00
f9ed3935-1407-47c0-a5da-8b55c84065f5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8362998962402344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:26:32.916715+00
1f5edde3-9a52-4c7c-b276-cfa6e47d4f0f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	5.868434906005859	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:28:46.490979+00
75f48866-d326-4de3-a808-6adbb5241cb8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7917156219482422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:31:33.570946+00
7d379249-317f-45ec-9f36-f7ad7855fc73	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.076864242553711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:32:40.348122+00
5d016a76-0f0b-4e86-9444-4fa88c20a0af	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9671916961669922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:33:47.100218+00
6b8a6015-73d8-493a-8fa7-beaf83b335f7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7380714416503906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:34:53.868079+00
200639ea-9ef7-447d-b297-e79487eee45d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.214193344116211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:36:34.01969+00
157cf70f-34cb-4b18-a994-9a887ae9c8fd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9783973693847656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:37:07.396038+00
7f9e3043-6d7c-41bb-b61b-13b9d6daeda5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.434253692626953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:41:01.083883+00
a3818b41-2537-4637-a4ab-2eafeb034a6f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7447471618652344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:41:34.469652+00
ef4bc50b-614c-4f78-8a34-89d0615b905e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8987655639648438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:55:23.315688+00
4979df05-65a7-43f0-a2c5-835793f791fc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8603801727294922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:57:03.534816+00
489ad46d-f945-43d3-bc08-a7f9b97ca9e1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0630359649658203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 03:58:43.689537+00
d09f23c1-5582-4f2f-b448-181ef27d8fed	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7731189727783203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:02:04.006735+00
be122c7a-27a5-4005-8852-c935b2ad3a68	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9345283508300781	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:02:37.391196+00
ac841b5f-cd78-4f94-9681-2e44e26d8d9b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9199848175048828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:00:41.960523+00
03a1593d-402b-4332-93c9-0d2a33299b45	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.918792724609375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:05:24.289195+00
e81e4501-9748-43bd-bc93-d717f169aa42	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9669532775878906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:05:55.757924+00
838318f5-e8c8-4c4a-933c-e4443023c18c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9564628601074219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:09:04.065139+00
201dcaea-f4ed-4f80-8c9d-e4d8d8c9e575	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8362998962402344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:10:06.752196+00
404ca7c9-956f-4fbf-be1c-12ccd93059b6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.386331558227539	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:19:51.81178+00
d323e317-4595-4850-b3c7-1a101afa2e39	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0780563354492188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:21:53.351896+00
9dc0a012-d678-48ea-855b-cc004001098e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5053024291992188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:22:53.832429+00
48d93cfb-0832-409a-9093-cbecb8a8debb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8877983093261719	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:24:24.423155+00
e063a43f-f4e4-4a03-bffe-af17b9a94930	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2225379943847656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:30:25.930173+00
d623f696-f078-4b87-a5ae-25ff3b74a415	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0978450775146484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:24:44.400745+00
47c2285b-0d0f-4517-bd01-c3132af8d62d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2716522216796875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:25:14.490447+00
ba77ae4c-4167-43f6-a440-efcc371ca124	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.754688262939453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:25:44.581841+00
603e4a19-609e-4a6c-91df-1b1ada35fa3a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1867752075195312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:26:14.659369+00
5dbfc365-7671-41be-89db-a2b40bd7dbee	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9893646240234375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:26:44.732676+00
ed9f7abd-47c8-4f21-ae41-83920dffbc20	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2842884063720703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:27:44.902485+00
6fd5377b-ebc1-465c-9935-aecc6832dfe3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0661354064941406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:28:15.002442+00
4e0046ea-b993-4f66-ad0a-3323cbba66c0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0363330841064453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:28:45.088397+00
89fbbf8a-51bc-4728-82a0-326e77ba2463	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0666122436523438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:28:23.069061+00
70023e96-6ea2-4b4c-97ca-055d8df0bf06	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.756906509399414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:25:59.529219+00
a46df1e0-5df2-4e7f-94a8-d1318e30c436	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9942989349365234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:30:26.803869+00
d4853289-910a-421b-80cc-d806dc65137d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7826557159423828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:34:20.484686+00
640a34e3-5dfb-43b2-ad4c-f20f8f931669	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7085075378417969	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:37:40.782855+00
373759c4-e4cc-4322-8810-101e96dd7357	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7888545989990234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:39:54.304682+00
fbf13ecf-09bb-44b8-a890-03b245329105	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9397735595703125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:40:27.701429+00
ed3ae9b5-e2cc-464d-bd5f-22bd5261fa99	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2521018981933594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:48:48.485472+00
47f67ed2-9407-427e-977f-e206502e17a2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9237995147705078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:49:55.279386+00
9a0de303-2233-407b-b0e1-c7c044ba693e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.499103546142578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:03:10.790693+00
ecef1b9c-6023-440a-9a3d-e8b2472d0e1e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3593902587890625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:12:12.070423+00
a460ec6f-72fd-4aeb-861c-b12ce9fe747d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1822452545166016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:40:27.338617+00
fd30ebab-e4b7-4b31-8ff1-4c19426c139b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8121471405029297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:29:15.180286+00
2f670007-a2e5-4a02-840d-af84aa650851	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.01416015625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:29:45.276107+00
0bcce2b7-e424-4e31-8b58-d51f87a54346	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1643638610839844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:31:15.557179+00
732731b5-ddd6-47de-a849-6c13f5150041	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8383731842041016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:32:15.797223+00
95e626c6-923a-42f5-b509-754f319bf6da	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.085447311401367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:34:16.153318+00
27101700-5f10-4e78-bac5-b6630fb44933	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.371072769165039	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:35:16.340043+00
a26bf3f5-9030-47d0-b96a-0171d2b5d792	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.956939697265625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:35:46.449211+00
01f7bb16-2105-4ab6-90e4-446e6eef0db3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8978118896484375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:36:16.542801+00
c1f9c8a3-5443-4db2-982a-25fd0a4ac27c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.953125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:37:16.764151+00
d0d2b116-5b59-4d47-a16e-1e007e804027	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9859542846679688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:37:46.862817+00
d0b45e90-878a-4201-ac47-b59e18d5be73	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9872188568115234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:38:16.964243+00
1dfead71-1cff-4ef2-b723-f1bf34bc8423	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2127628326416016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:38:47.057353+00
de1597f3-4ed6-469e-bf8c-cc21f71d5604	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1038055419921875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:39:17.134929+00
08dabd10-21e7-479a-8ea5-6a754b06bc93	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.378702163696289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:39:47.216664+00
e089aafd-d9c7-4ce6-b2e5-e770b62f7fa5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.041339874267578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:42:17.702406+00
fe155454-0fc7-47ed-a923-b00b5d206ee1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1245479583740234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:43:17.890119+00
ee4fcc72-6c34-4434-92fa-cfbc647b58fe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9638538360595703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:44:18.085723+00
c6ddae8c-6a73-4160-a9b2-48550f07c9ee	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7801990509033203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:46:18.510887+00
c4c089a0-f23a-4fa5-99a3-0835fb2c1073	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.0307769775390625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:46:48.668208+00
d553f5c9-d2d5-4160-aa88-be87ab948b5f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.735614776611328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:47:18.800261+00
09e479eb-ce87-4c18-ac0c-27b648b94087	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.985788345336914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:48:18.978594+00
1dbe4467-9a2a-4064-98e9-51ff352f2622	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4602413177490234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:48:49.085128+00
112cb7bd-2404-4c7b-96fe-8b01e4da85c0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9257068634033203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:50:49.5211+00
da2a5dda-2191-4885-8ea8-f2f1fde9756c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.894163131713867	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:51:19.614706+00
210f0def-85a1-41c3-a8fc-abcf37d2e091	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.465486526489258	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:51:49.723187+00
e421c5fb-4d7d-46ef-b395-23a1f8cdd4a3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7408599853515625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:52:51.238109+00
952f3b1c-97c7-4660-9402-bd294ca703e8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	87.70179748535156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-09 01:49:48.898303+00
1c6a52b2-ced0-4f51-ae60-37f7b24730bf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	34.21783447265625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-09 01:52:07.712965+00
6809614e-054a-4377-b888-269bc0bdab45	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	5.810976028442383	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-09 01:52:40.779903+00
304f948a-3a20-47e1-9098-1b1867020663	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9478797912597656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:28:53.13823+00
f4cb0129-3b9a-42c5-bc50-ad360a7bba7f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.496004104614258	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:31:53.558005+00
60d62e27-3465-4ea3-b646-9bed973c0c47	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9724369049072266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:32:23.626027+00
821fc2b3-0d8b-452d-9b5f-640cf4be529f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.420663833618164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:32:53.697385+00
ebfe182d-33df-4bf5-9803-1976e14bf758	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7599334716796875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:33:23.791484+00
7f772ef9-a632-415a-a0c1-cc79144f1076	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8525123596191406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:33:53.851459+00
60b37fe9-2ea6-4663-bd0a-c21ce6846404	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9688606262207031	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:34:23.907869+00
f80af50a-fd1b-4f06-979c-ace66fefabd5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1469593048095703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:34:53.974009+00
137b8933-be0f-4aeb-b598-71e2de5280e6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4030208587646484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:35:24.045638+00
13564ccb-b074-4dc6-8802-d83bb3fdeb72	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0265579223632812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:35:54.113291+00
e529086e-e391-49ab-9476-7d17638e2e3c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.06756591796875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:36:24.194647+00
df8840fb-6885-47bd-afdb-d760ef1d1a10	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9376277923583984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:36:54.268035+00
8acc560b-6ccd-4a23-9747-b149f89877f1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5606155395507812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:37:24.330001+00
6291e9b5-4216-4cfc-a1ee-f204dc93dee8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8801689147949219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:37:54.395913+00
9e5b0d8c-da77-4b51-b245-163d10e8660f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9085407257080078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:38:24.44981+00
02640d36-1619-4609-b8b7-cca927445972	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3050308227539062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:38:54.515091+00
c43d9b08-2eca-438e-9d80-396f74323db2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3288726806640625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:39:24.57231+00
2a652ee3-72eb-496a-9845-28d380a28bc4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3975372314453125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:39:54.642255+00
f894522a-ce07-4850-9717-41d07a6566e6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.792835235595703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:40:24.725457+00
1224511e-f7d9-45a1-954c-7f23d96bca95	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.105712890625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:40:54.787588+00
bdcbe1b0-1eed-41aa-9a20-ebfde7290e36	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.061605453491211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:41:24.846286+00
98fbef04-e6da-4697-a8ad-b602761d2782	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9388198852539062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:41:54.912045+00
9dfd4690-67a2-4022-aa85-c5b2fb6ad753	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0360946655273438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:42:24.964028+00
54cf75f4-3b16-4140-944d-f14371ab5201	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0399093627929688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:42:55.01842+00
5ead0174-8543-4c3c-b34d-98847892a0fc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4099349975585938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:43:25.075274+00
3bb1c99c-098a-42a2-a10a-d6db91c24cbc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.074718475341797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:43:55.148106+00
1d222deb-98ce-473c-91a4-480eab9212b8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.0393600463867188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:44:25.217764+00
27bf3c79-3e0b-48aa-a1db-c40ce78b46d3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0792484283447266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:44:55.287869+00
96b0306e-4677-43b9-b376-af41657b1add	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8934478759765625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:45:25.36379+00
cc27214a-615d-4aac-8337-d3f052958d16	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.99127197265625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:45:55.429578+00
93a7d7c1-1fd1-48c5-a433-3d158640f569	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1893978118896484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:46:25.502471+00
5308714c-0cd0-4d45-a083-a505df351c34	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.028942108154297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:46:55.569878+00
c9282ae7-3a33-41de-9855-546a9f0e779a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.956939697265625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:47:25.633037+00
380718a9-569e-4d3a-a92b-dfa4487acc56	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.318859100341797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:47:55.709348+00
fd8fad3c-953f-4425-8f4c-90b5ad266954	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.198457717895508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:48:25.791105+00
2a916b09-6562-4347-b0c9-b6451ad6e8b2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3348331451416016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:48:55.862003+00
8fc51891-ea3c-4739-813a-687aface76d1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6197433471679688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:49:25.933929+00
1f662a07-dfbf-42a1-bc4f-640b0d15e329	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.943349838256836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:49:56.003066+00
eef2bd3d-78b5-46ad-96d0-aad74bebb0eb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8165111541748047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:50:26.073773+00
528952a1-3dc9-4938-a588-e645aec391ee	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4423599243164062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:50:56.148679+00
6b51ea03-895a-48b7-8387-4ee0282f2bc6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9557476043701172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:51:26.205635+00
ae2718c4-1a08-42c4-8ce0-5b863de1c1ed	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9733905792236328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:51:56.263317+00
ad8c32e6-dc02-447a-aea4-d6cb19c4eb8a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9276142120361328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:52:26.329452+00
879e34e5-5d88-4824-a553-c413a809ea81	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3374557495117188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:52:56.399281+00
93538194-d91f-49e6-b0eb-2b090cd5eabb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.080678939819336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:53:26.469011+00
0956ad32-39a9-42da-80a4-6045a4b9e154	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.924753189086914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:53:56.538965+00
4c85679c-5dac-46f7-859e-049d84a8084f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.00653076171875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:54:56.700673+00
b8338ed4-ae75-4495-bf23-b1cef7e22128	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.190113067626953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:55:56.881593+00
1ef45f40-2a86-4181-890a-b9d01e0c5bb5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9540786743164062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:57:57.215687+00
5c0d9c43-9d45-4a76-8c3a-cde317a7f10f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2497177124023438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:58:57.353397+00
4500d0a2-b426-424b-a7c1-8d0822c8afb0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.039670944213867	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:59:57.475552+00
37bc162b-1c78-4ce1-9c41-9e3b2c169752	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1507740020751953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:00:57.625692+00
c5ff7a07-4b17-4661-ba7d-c8c9de69d401	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0551681518554688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:01:57.767301+00
c21c3eec-432c-4145-a031-13268fa66ce9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.979827880859375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:02:27.862997+00
104f137a-26fd-40df-b3be-5fae901f6c39	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.352476119995117	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:03:58.070857+00
f5ef823f-b5f2-46c6-9bf0-4642bb62b62e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1812915802001953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:04:58.21974+00
7880729c-0de1-463b-a8cc-cf996bdf23ce	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8966197967529297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:05:58.404944+00
8f9ab312-6b4e-4b1d-82c8-a0ff82f3da4b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.069711685180664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:07:58.668452+00
f8f014fc-5ba7-4cc8-a27d-848d8c56c701	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4564266204833984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:08:58.81817+00
81d22657-a2dc-467c-bc61-2eb5aa21c217	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7209053039550781	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:27:06.327235+00
49df273a-8a48-45cf-a0ff-a4c08f606601	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7621517181396484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:35:27.25215+00
ac72af27-d241-4357-9621-3a00b0685994	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8286705017089844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:42:41.237396+00
acfc5f39-6131-441d-beda-389585b0815b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0618438720703125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:52:08.843628+00
0b89025a-2272-4a40-a2f6-e826783030d5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8799304962158203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:56:35.921105+00
07072ede-15f7-4bb9-8a28-7d787fa6e5e1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.092599868774414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:03:44.185633+00
36c9d650-79e6-4fa1-9d5f-b818c66dc9be	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.852273941040039	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:04:17.571828+00
d1782409-9b27-4093-87ba-3952f1210816	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.99127197265625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:05:57.731141+00
363173c8-0f47-4248-9301-926fdde9ea4a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8930435180664062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:06:31.105108+00
83d7954e-050a-436a-a11a-6b9649017361	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.901388168334961	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:07:04.490892+00
c3f06a99-bcb3-4b60-9c1c-7b0a873142a7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9140243530273438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:07:37.876142+00
a3906764-2de2-48c6-89b0-6274f6d61491	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.09808349609375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:08:11.258157+00
31af7ba2-2cb9-47f7-86bb-87bc174cd445	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0689964294433594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:09:18.032226+00
2bfdb551-d199-4be7-8264-50d95d34761e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8610954284667969	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:09:51.413778+00
34bc24ce-c750-4ac7-b433-4852c6abac86	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9450187683105469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:10:58.219101+00
3a1b9ad0-2b30-41e9-82b9-81cb81ba21fa	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9369125366210938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:11:31.604944+00
956dc130-b145-4202-80a0-d728553da508	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7919540405273438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:12:04.992906+00
159eb7d3-a93f-4938-a470-a280b996042f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7867088317871094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:12:38.384158+00
a8226766-bf46-44bf-b2b1-3aaf2c3f88da	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9638538360595703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:14:18.586983+00
7f844c83-7018-4c79-aa77-4d0143ecedcf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.2770633697509766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:14:52.012366+00
2e86ffd4-92ef-4b0f-bd2c-4b800b5e9844	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8460750579833984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:15:25.401837+00
77d3136e-32b1-4d96-97c6-24838c786799	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6111602783203125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:16:32.192622+00
79888323-fcb3-4aa7-be12-7ea5e3d05c6d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1882057189941406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:17:38.999323+00
d79da919-08cc-4785-859c-bec88a24aa25	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.182483673095703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:54:26.616844+00
d8eedc1f-3d86-4877-b8b9-ec68be3dfb96	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9271373748779297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:55:26.804968+00
73a2e4ad-cb65-46e8-834b-7e0110b3626b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.276897430419922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:56:26.957411+00
86bc0ff8-4d8f-4544-bfa9-d53dcd094ad5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.023458480834961	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:56:57.067619+00
b4b516dc-1da4-4ec0-8310-7fc2bea0c8f1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8985271453857422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:57:27.142794+00
1d0f2c50-00b9-4af8-ade8-ee9214d42923	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0911693572998047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:58:27.290352+00
248c423a-b68d-4492-88ff-e0ec38042adb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.179384231567383	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 00:59:27.413842+00
e738d0dc-3b9c-44f5-ac38-cb0f0a7c8eb5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2673606872558594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:00:27.547884+00
848e09f0-e3a2-46fe-8e2a-365923c0db82	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.082347869873047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:01:27.698931+00
af525569-121a-4aa7-9957-3e932b23eaca	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.696990966796875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:02:57.938392+00
d8da07f1-72d0-4851-b4b2-d1ff1d48a106	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.167224884033203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:03:27.998543+00
d2a504c6-eccc-41c0-8918-d78ad7e2116d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0699501037597656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:04:28.14241+00
e629b154-2b84-4def-a600-93be4be1b222	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2211074829101562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:05:28.327706+00
0f423693-b957-4952-a79b-1254ed50e411	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.005338668823242	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:06:28.487743+00
bbc6a06b-62a3-409a-bb35-f43e506906cf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0945072174072266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:06:58.548329+00
5db61e64-64b8-4a97-bf40-58cf2e351b7b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2912025451660156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:07:28.607397+00
a680d818-efe3-4026-8d8c-e37bec426ccc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2590160369873047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:08:28.744695+00
415ac9ec-73e1-4002-852a-448546407c72	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0203590393066406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:09:28.899531+00
aab9ad62-d13a-46ff-8068-2439d742b5cd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5742053985595703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:09:58.967075+00
d08e1664-cea3-449f-a17f-813093bb3839	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6786327362060547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:10:29.099108+00
abb62431-3cdc-4aa9-8d4b-dbadf952c470	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	12.9852294921875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:10:59.194541+00
10f28493-6fda-42c4-95c1-507298978029	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.334688186645508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:11:29.305346+00
3e305a2a-3919-49bd-a79d-b91dc99467c2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1181106567382812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:11:59.404446+00
10bc6410-db87-454b-b7a6-4d373d943df9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.1213760375976562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:12:29.484103+00
cb584d6c-4e10-497f-b8f1-fc2769e16e3d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0673274993896484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:12:59.562973+00
7521c344-d247-4205-9a82-ea652b875400	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9958019256591797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:13:29.633871+00
a1eceb28-2559-4e0b-86d3-d8c82a966ffb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.598451614379883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:13:59.724358+00
332358f1-74db-44f4-a1b7-fc8a0f037315	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.775430679321289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:14:29.820994+00
a3a1311d-93f9-4595-9111-bcb43c904fa2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9614696502685547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:14:59.881004+00
85006e3e-3d97-46a1-8795-2c334466d064	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.2584667205810547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:15:29.943817+00
98167072-4185-4a83-87d8-006898be584b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.233743667602539	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:16:00.020064+00
c4d667b0-23bd-4743-9b1c-1096ab18dbbe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4023056030273438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:16:30.106327+00
e87e12fe-d573-4854-8573-ee5f99de5219	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9588470458984375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:17:00.16872+00
175faf3c-7758-4b72-8bc9-eae46b6ffbfa	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5262832641601562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:17:30.232599+00
86a17228-4c18-4fe7-8317-720ed1582614	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.132415771484375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:18:00.31345+00
764a8a70-e3a1-485e-8e18-38ff2e2de2da	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.203702926635742	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:18:30.388208+00
8eca4f3d-d09a-46a6-9805-eeb46a3562ed	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.178192138671875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:19:00.451905+00
707a777a-663e-402e-8dec-71d3532beba2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.343416213989258	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:19:30.512438+00
827f682c-4294-41b9-b141-1457a191afed	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2258758544921875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:20:00.608333+00
4adc8bdc-369e-4427-aced-a625289938a9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.992940902709961	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:20:30.69466+00
fe10c5ff-b8ca-41d6-bbc2-e8fd4f7773b0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0318031311035156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:21:00.771799+00
6f8f4bc5-c5cf-4a2c-bafc-11290ce7ebef	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2881031036376953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:21:30.838859+00
d8c4a935-67d0-4dbb-9b59-49c35c9e08c5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.50244140625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:22:00.927851+00
3ebf5734-82af-4157-ad50-e909e7ce2fce	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0062923431396484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:23:31.1448+00
682bdc73-776b-4d10-be98-516d64a14c2f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.0715465545654297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:25:01.379764+00
dea96b95-6df1-4ed4-b900-24e451d7e44e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0346641540527344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:28:31.992052+00
c7c5b892-3c94-4f03-a5fb-95a48127d292	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.208709716796875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:33:02.81826+00
33704431-8923-47ab-b668-4152244da989	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0995140075683594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:35:03.155489+00
392d4f1c-b885-4a60-b3ca-64e95647027e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8749237060546875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:45:28.183457+00
645d3bb1-c900-4988-bbe4-f3ceab4087f6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8703937530517578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:46:01.569411+00
e3ffd75f-055a-4030-9efc-f669f56b1490	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.804351806640625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:46:34.953785+00
6c3157f3-bba8-42c1-920d-4e2e7c5931af	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9092559814453125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:47:08.336936+00
04733841-81fb-4657-a083-80ce53f8d1a5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.796722412109375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:47:41.724012+00
220a632d-993d-4e91-8f5b-3cad42255aec	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.817941665649414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:48:15.098915+00
8e2df386-fed1-4e91-9a71-e5ff596f9793	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	6.552219390869141	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:49:21.896588+00
80c5af27-d1cb-4b3e-a2fc-4eaa4f1e6d0e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7440319061279297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:50:28.664093+00
0590c800-c3b2-4bc5-9deb-84137ad5c88c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7697811126708984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:51:35.459103+00
5c96bfdb-1e37-4b08-bc01-08837e9bac23	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.687765121459961	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:53:48.995723+00
1399c167-f348-4afe-be1b-58a62ce44069	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.444744110107422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:54:55.771849+00
68a4e5a8-57a8-48b7-b344-e6a59b2a6c78	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7383098602294922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:56:02.539049+00
bd44565b-ad2e-4ba5-bdff-45fc3acf9f7e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9576549530029297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:57:09.297981+00
16e2d816-6110-4e24-8260-3fd528e4b72b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6467571258544922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:57:42.68165+00
21e3b999-f539-4171-a61f-31526b55db26	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.940011978149414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:58:16.064554+00
c59e1613-5195-47da-9b18-393ec1c1ae0e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.800537109375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:58:49.449786+00
e39d83b0-d3f5-446f-8a15-e4e46be014e8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9180774688720703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:59:22.821545+00
a3968b7b-bb9e-4818-a19b-5d954dd5d4b6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.907991409301758	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:59:56.21672+00
3edc953b-f452-4353-bd81-ef51c07b395d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7430782318115234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:00:29.592579+00
21b6b203-7673-4883-8668-f2afebb76b01	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7082691192626953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:02:09.763633+00
ff34ebda-3f69-4de7-82a3-7aec69c0e836	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0711421966552734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:04:23.323105+00
79992115-82eb-41a4-9f44-16cec56b0475	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7209053039550781	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:06:03.509195+00
631fb654-8741-4812-a5e6-4c4c1e66eeab	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8596649169921875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:07:43.65381+00
fd087145-11f8-4472-a156-be674e4abf2e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5644302368164062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:08:17.029714+00
d7b6f7c3-3060-4393-9faf-fdf55e5ac0b3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8262863159179688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:08:50.400066+00
631e6f6c-a648-491f-9752-ec00da5f202c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7468929290771484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:09:23.775124+00
936b7c3b-e50e-4486-ae09-0207751cf210	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7974376678466797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:09:57.149479+00
05c5532a-82d6-404d-abd2-17a6cc175215	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8146038055419922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:10:30.522656+00
57bdbc0e-0e29-418c-b4b7-b9efd154586b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7561912536621094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:12:44.031548+00
94b0b1b4-42c8-4cf2-b85b-321b25eb086c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7735958099365234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:13:17.418838+00
adca0c89-e78b-412e-8747-f69a6f18e373	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.03704833984375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:04:50.960344+00
28d3a0fd-46aa-419f-8ed7-c67dd25ddab0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9218921661376953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:05:24.346857+00
d42e4d23-61fc-4d78-8e85-6e53c5691809	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1533966064453125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:16:18.306955+00
678235cd-e359-41e8-9c37-a735ecdecff8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.099275588989258	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:16:48.869307+00
2728d3a8-b2d2-4a5d-b175-6b8ca575bc76	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1300315856933594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:22:30.997502+00
ca556eb1-ccf1-469b-863b-2c7bc53ebd35	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.351045608520508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:23:01.063817+00
b58164a3-1326-472d-9377-98633e2b001b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.020597457885742	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:24:31.291052+00
e37ca4b3-3740-4a46-985b-0a33a183fc19	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6509761810302734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:25:31.448368+00
adb0d790-6d47-47fa-a780-52b6a7849c0b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.6649703979492188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:26:01.526257+00
b73db75e-dd8a-4d6c-a199-7b31e6e5e1d9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.974344253540039	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:26:31.604161+00
43650f9f-9f9e-47ad-b387-c1dcbef4d8b4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.180337905883789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:28:01.90407+00
df28cc3e-2241-4cd6-b1f8-e7610961166f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.444671630859375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:29:02.130205+00
bb84da74-1006-48d9-950f-36707da24e59	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1414756774902344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:29:32.212854+00
0295b0b5-5cab-46d7-8df2-0991c3eef3cc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.2393932342529297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:31:02.466305+00
621bb35a-5714-48d9-b729-5ea1d9e96694	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2809505462646484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:32:32.721352+00
ce18140f-e867-4245-91c4-3ce975900c70	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9042491912841797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:34:02.995064+00
576e0730-5889-416d-bd89-1958baf58341	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2058486938476562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:34:33.075492+00
e3e96331-cbc0-40ea-b0b7-dc50d978230c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.446817398071289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:35:33.248771+00
cd560d0b-4446-4109-9ce1-124d13599e84	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.371072769165039	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:36:03.354237+00
ff9d2f03-bffc-4f12-8cfc-807368e22fd9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.178192138671875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:37:03.524188+00
d469ba4f-b54d-44ae-8c1c-e94afc13c53b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0751953125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:37:33.603701+00
aa3170c8-8a62-4701-930e-15dbfc901e0d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0143985748291016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:38:03.696333+00
a22515fd-d43a-46b4-b501-66c29f84a6fa	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0046234130859375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:39:03.848428+00
09624b41-f96d-44ad-a849-c110bd5ab249	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.300739288330078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:39:33.932131+00
0687b47c-d826-4c16-add7-5bf6ca4a795b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.496957778930664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:40:04.026659+00
c4e983c6-b868-4c50-9336-7c5765d65cfc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8689632415771484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:51:02.071574+00
4251c696-0299-4a19-a059-7e346cb155b6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7986297607421875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:52:42.226437+00
a58ed870-56a4-4836-b892-5cb088b902b0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8491744995117188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:53:15.611576+00
45b73e03-c2a3-45dc-8958-9fb0c2ff0f15	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8935203552246094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:54:22.379155+00
8523be10-1d8a-4726-982e-b3277b8b0b3a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7838478088378906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 23:55:29.155243+00
cc52d63f-2f06-40c9-bbd8-deac6186d0a0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7344951629638672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:01:36.385752+00
72376330-646e-43b5-b71f-5436c7659eed	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9745826721191406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:03:16.55383+00
b0aafb72-7278-4c31-8c4c-dc592f412bc3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3941993713378906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:04:56.709496+00
2784332b-bb95-4693-81ac-6caa6bf9427c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8333663940429688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:05:30.125577+00
af850568-2efe-4d5d-8014-f4e91681734a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8460750579833984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:11:03.908326+00
299d2689-b477-49f0-b9a2-8afa27319408	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.276897430419922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:12:10.65961+00
ae5ca90f-bc96-4ca9-ac11-4afdfa144b40	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9347667694091797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:14:57.540571+00
591a377b-0fef-4f83-b7a3-24d558122266	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1140575408935547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:08:44.647571+00
be17450c-242d-4376-adba-aa88f582ba2c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9621849060058594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:15:58.784096+00
c0a123d8-04b3-4a5f-a483-30c24c35070b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7292499542236328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:17:05.610347+00
c81115eb-8343-47a2-abf1-d35d173eac5f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.866029739379883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:17:19.391901+00
d3769c6f-fbbf-451c-9035-86992d5db706	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.392292022705078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:20:52.645717+00
7cdb6941-e772-48b9-865a-6cd32ae8dc4d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5789737701416016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:24:54.622828+00
15b3eb73-1301-4e60-93ab-7837f1de99ef	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.107381820678711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:28:25.55383+00
b93f359e-c16e-4641-8f9d-f40f949c82f5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8620491027832031	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:31:26.069129+00
82551ea4-f195-4145-a548-bcdf5ff81e7d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.760648727416992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:24:01.216002+00
0b7ae828-e8eb-49f1-b92e-9773a4596f6c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2585391998291016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:27:01.715298+00
9aca737e-c9f5-405f-9f27-b7102111188d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2859573364257812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:27:31.823694+00
ba9798e6-e1d0-4b0f-a6e8-37a94c6ce444	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.817869186401367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:30:02.289168+00
89c6a56c-a025-4b9c-b24b-c147e9470e78	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1622180938720703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:30:32.368815+00
f7e74049-a592-4bde-94b9-a97fc1fe72fe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.824544906616211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:31:32.556236+00
31021b11-38bd-4702-93a5-ba99d7382b15	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4628639221191406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:32:02.640743+00
c6cd943b-f528-4ff6-8a6a-d773f470f4d5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8307437896728516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:33:32.905748+00
e6214afb-d78f-490a-9b14-406f75cce383	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0117759704589844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:36:33.452832+00
d3b628d9-a9d0-4df8-b9af-dbe7cc270ed1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0711421966552734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:38:33.775445+00
a7f94811-375c-4316-ac90-455987dd3bc5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9559860229492188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:40:34.098323+00
116197f5-8704-4999-8af8-c582e5defda7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.310514450073242	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:41:04.171921+00
1f374000-6e91-4ca2-b082-1fe25eb46715	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1514892578125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:41:34.25911+00
110a2caf-eb69-4e3c-8f7b-1115d4b6e614	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9474029541015625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:42:04.378828+00
d7300b08-d13e-4848-a276-d7a3692987ae	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9862651824951172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:42:34.454931+00
e23607a0-dd41-4a0d-bf9f-5af3d4930f3a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9664764404296875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:43:04.558711+00
9e440938-89d3-4aa3-b5de-55890bd43080	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1610260009765625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:43:34.63358+00
d137f027-45c6-49dd-9a66-7c74fcdb04da	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5005340576171875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:44:04.712253+00
933f1b18-54fa-467d-af36-7c2a7b885bdf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0685195922851562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:44:34.798332+00
74559fd0-8b25-4301-80fb-8dbec0d58cb1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.166271209716797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:45:04.883361+00
5c26bf3e-3337-4cb6-ad77-094936baa003	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9786357879638672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:45:34.966035+00
a914c919-576d-45f5-9c44-6d2fa3e2c3b6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9583702087402344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:46:05.053097+00
bd1b2ac0-19b4-4c1d-b03a-ce56bfbe8c43	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.901315689086914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:46:35.156964+00
5b465ef9-1179-4bb9-bc32-f161e2e89955	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1200180053710938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:47:05.248576+00
89b89196-dcc9-40a0-83eb-0bcf1a0e4b47	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0613670349121094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:47:35.339959+00
55dd9caf-87a0-424b-99a8-b48ce1d91d34	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.161264419555664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:48:05.424131+00
c7ed4866-7b24-4ecf-82fb-05d5b0f0f654	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3314952850341797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:48:35.51084+00
f2202329-d1fa-4857-8471-ca15cbfaf81b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.256559371948242	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:49:05.615755+00
36d8ef2a-bffe-4dcd-b39c-fcd854a818a0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.184152603149414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:49:35.743227+00
b63ef34d-fa0d-4290-8fbf-95d1b9934870	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.149820327758789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:50:05.817731+00
4dac2771-58e4-40d4-9bb7-4305b2307fb3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8429756164550781	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:50:35.89809+00
9363e8ee-c6d5-44be-a6a8-0bc608aa1034	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.284454345703125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:51:05.977686+00
c058ab42-1236-42fa-9c8b-3cf501dd8f18	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8987655639648438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:51:36.071332+00
44a208b4-ce0a-4995-92d2-5cb338660ba8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.1757354736328125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:52:06.163739+00
11e397f8-7861-4b0b-8601-51f1f8370b73	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.660036087036133	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:52:36.245371+00
a26a60e9-14a0-4a2d-99aa-dde59fbe4dd9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.346515655517578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:53:06.339294+00
6fa28127-3cb1-4c0a-9a53-ffac7028e7ef	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5310516357421875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:53:36.41897+00
839e2a80-2dc4-4ff5-839f-45bf378fcbf7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9402503967285156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:54:06.507086+00
1c629fc1-4507-42b7-8273-cf1b3a440663	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.474069595336914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:54:36.593731+00
3589d0fb-8dc4-41dd-8717-95486f188d45	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.013683319091797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:55:06.686648+00
ce4fe52e-4f0d-427c-82a6-1bbb67cd0b60	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.391815185546875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:55:36.774615+00
02d151f0-2fc4-48d1-87df-039ca5be58e5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9757747650146484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:56:06.865179+00
a57195a3-6dfc-4bb4-90fe-a6b6811893e4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1102428436279297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:56:36.948505+00
bf700d21-80bf-46a1-a722-fcab53ac6898	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2192001342773438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:57:07.031384+00
9aea845d-96c8-4e4b-9b5f-4ebbd7b47b47	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.196788787841797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:57:37.136862+00
c8705bcd-f998-43ef-8b58-5436003809cd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0012855529785156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:58:07.254361+00
d1f348cb-4353-46fb-84cc-2cbfe52c9ecb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.062082290649414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:58:37.345002+00
4d625cb2-75b2-4ca9-925b-b2c10d9947a0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	6.003856658935547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:59:37.555679+00
26017022-68b7-4e04-9307-21c7dc595c17	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1448135375976562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:00:07.643325+00
07b3d7a3-4d18-4dba-9f04-e95d21601bae	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3288726806640625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:00:37.729078+00
15339f2c-60d8-4745-b18e-487dcbfd8380	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	13.719797134399414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:01:07.831716+00
6f28c168-99f4-45f7-a1e5-155a67185565	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2284984588623047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:01:37.914576+00
f9f255a6-8825-466d-b9db-a8b3b8f3a867	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.341747283935547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:02:08.021293+00
2382998d-68a8-40a8-b84e-fd2f18874d41	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1848678588867188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:02:38.106433+00
f6f6188f-f8a4-4641-b87b-3cadaa9d1be4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9786357879638672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:03:08.18507+00
aec05513-8c4e-4d67-b12e-8713cd0cf540	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.443552017211914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:04:08.350295+00
add48fd9-68d1-4a4a-939c-3bd1328011d3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0046234130859375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:04:38.427282+00
54d9b175-1f4a-4292-b458-8db753f6b2d9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1941661834716797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:05:08.515423+00
f07c136d-d11a-4cfa-adff-ab863177f3c9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.115964889526367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:05:38.591452+00
0210da0e-1432-47f0-b807-7c3bbf8e5c28	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0487308502197266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:06:08.673011+00
1aef81ff-82d7-4606-83e3-5c99bc902b1f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4857521057128906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:06:38.764116+00
d5dc4032-dbc4-4199-93bb-e95a6390ac57	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.221822738647461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:01:02.999468+00
e1bef507-90b0-450d-b579-63738e0f3d3b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8506050109863281	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:11:37.282478+00
901a7e0e-9d19-4af6-910d-d361e1c071d8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7528533935546875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:13:50.793312+00
87788de3-df79-47be-a414-fceb64ea6a74	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9237995147705078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:14:24.166659+00
36a19f76-91d2-48ef-bd3e-bda848e591e7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8677711486816406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:10:24.829732+00
aaa7ddb5-7fd9-4f9c-8ad9-782c08072ebe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	15.267372131347656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:13:11.809425+00
efe0ba8b-8c23-4604-98b7-4fd2eace9581	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2237300872802734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:13:45.199103+00
cf954c67-0d0f-4b28-9cf0-bee0ff17fd28	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.063751220703125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:18:12.390082+00
bde3f21c-e460-4c4f-9689-bad739401258	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.825571060180664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:18:45.790428+00
9fb50f21-1d13-4409-ba7a-8f8fa42ddc8a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2110939025878906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:22:06.17069+00
07743644-c829-462a-a3d4-a2c3eff7f020	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8644332885742188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:23:46.304409+00
71f2f63c-aa05-425b-adda-3b480081e033	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8944740295410156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:24:53.100316+00
25821f83-9ce1-49a0-a79d-864f26ff0fe3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7268657684326172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:26:33.304242+00
5f7158b6-bb21-4bd4-847e-e0fa6035a4f8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.034902572631836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:32:40.563311+00
c58c4aca-7cad-4b0c-b0e9-96432a88c1ed	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8634796142578125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:34:54.105141+00
0adf2199-a1c9-4cbf-9875-89cb6f671191	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9996166229248047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:36:34.277018+00
47a2ad4d-ccf0-4665-84bd-5372560f7768	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.708984375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:38:14.451208+00
dc5b5c74-e135-413b-bd3d-cf5e10b355e7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9690990447998047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:39:54.600698+00
851c458d-c545-4d9b-abee-f8a3dc87a682	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2590160369873047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:21:22.994097+00
bece84ce-3ff3-40e0-9117-977da26a55da	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4454593658447266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:22:23.571606+00
7c2985f8-cf69-40ab-a0d3-e4a754c36059	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.033710479736328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:23:24.025679+00
cfaf5259-ce24-4388-8ba2-400ee5eb1d78	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2885799407958984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 01:59:07.43953+00
4147606d-d16c-40a4-a993-14830e754c85	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0301342010498047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:03:38.263763+00
13a79452-a6d4-4593-8b01-09ee7528ced9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5763511657714844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:07:08.883073+00
6930ea94-33d4-47db-a454-76ea47b1f445	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1982192993164062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:07:38.973556+00
0cd5046f-7fb7-4c51-a37c-a1c691adaba3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3539066314697266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:08:09.053038+00
2539b08f-4472-4e1d-9a63-efab67ebf018	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.200603485107422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:08:39.1427+00
66f64f3a-cce5-4385-86c1-fcc94c0a7e3d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1479129791259766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:09:09.226458+00
9efac819-ac0a-4756-96b1-86ab32eaa04a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3674964904785156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:09:39.312103+00
46573a43-2d08-496b-9b74-f634e3925d90	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.841949462890625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:10:09.401266+00
6d544957-f694-4166-9f2e-b6a18747cb94	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9156932830810547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:10:39.473652+00
e370101e-bb80-4e47-88f4-ab408f538a1f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.741647720336914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:11:09.55698+00
b8afc06b-492f-4b33-913d-fabddb6efd7a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1605491638183594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:11:39.67594+00
8d87e8b0-cd77-4d5a-ae4b-4d5fbdd2ab65	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1390914916992188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:12:09.760909+00
f88b8c58-ace0-4342-9c6d-9ca874878223	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8095245361328125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:12:39.943016+00
687c2fbc-3076-45b0-8f8f-aab339108d01	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6063919067382812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:13:10.055101+00
0463decb-6095-41e1-9e6e-4fa60cb8dbb1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4297237396240234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:13:40.144372+00
3624e61b-1772-467c-a826-82350a1f6830	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.515554428100586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:14:10.231945+00
e5eda0d3-7fbb-4bd4-b820-fd3e473ef939	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9254684448242188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:14:40.330362+00
82f9f9d9-3cfd-4367-a7e3-e7e53f478f65	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1986961364746094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:15:10.411944+00
c4325065-b24a-415d-93c3-bad9b34c7709	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.213001251220703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:15:40.495745+00
7cec6ced-6a52-499b-9bbc-73679be888e4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1262168884277344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:16:10.590757+00
3b52681d-4bc1-4809-99bf-075f3499c486	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.158641815185547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:16:40.683513+00
533deb7a-d6e3-47d4-93db-bf37384a29ff	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0198822021484375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:17:10.767792+00
1e22c022-22fc-4291-92b8-6e9601198a0a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5162696838378906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:17:40.857222+00
ba6b55c8-b1c8-4ff4-ba08-82bde65bcb1d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2296905517578125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:18:10.951503+00
5bd58fc1-061c-446d-ae21-9870a97d0a21	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1708011627197266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:18:41.043641+00
3b755e91-4459-4633-b6fd-7304e8033a7f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9309520721435547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:19:11.14403+00
06008e43-9379-43f0-83ac-8d87c686ce31	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1784305572509766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:19:41.236822+00
0a744526-bb66-47f5-b6dd-6b67ffc6ddf8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2106170654296875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:20:11.328685+00
6481042a-9924-4c73-a39c-fc3317fb8545	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0558834075927734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:20:41.424242+00
97dc0abd-f4c2-407d-ac67-2a15cda2277a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3908615112304688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:21:11.521114+00
6fe37e1f-0c86-483c-9667-aa98b67d7e6e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9886493682861328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:21:41.613317+00
f13701f7-2d2f-4eb2-8c7c-7e1bc0f84832	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.167224884033203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:22:11.737081+00
92cea33b-7e07-4ea5-960b-5739dff1b9b5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5331974029541016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:22:41.837399+00
3ec49ad0-2423-489d-87d8-c2ae61c217c3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4213790893554688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:23:11.921348+00
ba87a49f-54e6-4bd8-9ffb-1153a4bad643	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1224021911621094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:23:41.999433+00
14d6c5d0-d12e-4e10-aea1-3c17220a2b45	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9822120666503906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:24:12.076714+00
fb5f0bee-bb59-43ae-9369-a03c819ea275	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9409656524658203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:24:42.173701+00
3392fe31-2f9d-4dfc-9eb7-0b75a8b09d69	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1469593048095703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:25:12.253497+00
879fb2c6-efb5-4d33-800c-b70e2da7ef7e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9822120666503906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:25:42.343892+00
c50acfb2-3ef4-485a-a154-56eb33eca3e3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.014636993408203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:26:12.437059+00
efb624fe-3bc4-45f9-81ae-85e93ff6a8e6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0613670349121094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:26:42.532822+00
9478c4e5-981a-4ad4-93f3-75c007866fbd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8793811798095703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:27:12.628724+00
ce323d51-6cea-4fa6-995b-324438eea910	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.895904541015625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:27:42.792133+00
0ee4a55b-b468-4c06-8d13-559735514e29	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.667665481567383	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:28:12.915699+00
8e6bdc23-60fb-42b6-9e66-bd62de2fd2d6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2203922271728516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:28:43.036755+00
ebc5a44c-3915-4fa3-bdb5-af7473f605f0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.4711360931396484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:29:13.164545+00
5b0c704f-a641-43c9-85be-cf91b3119a1d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3851394653320312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:29:43.265503+00
22981cc2-a7e7-46ed-b7d5-fc3007cf00f5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.290010452270508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:30:13.370705+00
581c2080-f198-4c04-b13f-89130072db45	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0589828491210938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:30:43.463628+00
448f7910-1302-43cb-8e0d-068f349ae9d8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4602413177490234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:31:13.56595+00
f1f5d39f-3d4c-404d-8346-6bb193e98ebe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9946098327636719	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:31:43.693888+00
8ec3aeae-c834-4f40-a9b2-71e33b1a4f5b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5370121002197266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:32:13.797118+00
1ee6d510-42dc-415f-8a11-9da7db9db79f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4645328521728516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:32:43.882519+00
e7df170b-3f45-4b4c-994d-e5109e0e230d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6564598083496094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:33:13.977673+00
352505d0-6fab-4bea-960a-53898e3ff60c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3889541625976562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:33:44.07821+00
52e25b05-926a-4e7b-b294-ec43f369f252	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	13.538837432861328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:34:44.299172+00
33dcc83f-0b8c-41b6-8d2a-7c6a88a547cb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.346038818359375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:35:14.389713+00
b6cea9b7-0bfc-4872-aa7e-287ce4e4cddd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1355152130126953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:35:44.475116+00
e17672b5-90cd-411c-b517-9d8c6a184932	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7823448181152344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:36:44.67274+00
620cf31d-0828-4ba1-bf0d-267d2dca78ae	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8154850006103516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:37:14.790516+00
6b8f90bb-5d0d-4c51-a433-6ffe73150d03	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7108192443847656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:37:44.894284+00
c95e2a29-9a6f-4d79-8fa9-666db727a1c7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0873546600341797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:38:14.998801+00
e1aca074-23ab-4052-83be-7e08e357741a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8606185913085938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:38:45.099292+00
21f202e9-3a57-498e-82b8-61619942b0ec	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.478361129760742	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:39:15.191941+00
6be25674-784b-42fa-bbd6-33cad777bfc7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5129318237304688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:39:45.336577+00
df966f2a-2856-4752-a7cd-ae1df0c962d6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2776126861572266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:40:15.436585+00
2b904f11-552c-48e7-af1f-8296e20e30e1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5899410247802734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:41:15.673645+00
23a3d76e-7025-4ed1-a8bd-bdb1c1e9a43f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9202232360839844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:42:15.875301+00
2a388fa8-ae56-402e-9d1e-38f742d7874e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1696090698242188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:44:16.293552+00
ba1ffc51-22f5-482a-be31-bc5a315619d6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.644777297973633	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:45:16.494505+00
a6963b77-9efa-43e7-b15f-4d060137843a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.0295848846435547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:45:46.612065+00
d297a941-cfb5-44a3-b4fe-1b9d3dfa227f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	7.20524787902832	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:46:46.8324+00
8ddc2874-1869-48ca-a83b-6a4c96bcbd52	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	11.734247207641602	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:50:17.655727+00
ed202fc9-00f2-4944-8cf7-91d48d7c181b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	11.003255844116211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:51:47.976239+00
c7f0ceff-b366-4682-a220-f7b7c64b26de	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.402067184448242	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:54:48.586884+00
caf9c15d-0af6-43f7-8b3b-6657dc632eea	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.0825138092041016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:56:18.905179+00
37cb4981-e9a3-4540-adcf-396f672b0bd8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8310546875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:02:43.164897+00
beb5ab4a-edc3-4e8f-87ba-f2a77d24a958	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.837015151977539	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:03:49.936698+00
7b2b2c5f-3479-48cc-becf-6a7b36a466af	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7914772033691406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:06:36.893629+00
13b023d7-6f6d-420b-9253-a79d941efcf6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5322437286376953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:07:10.276959+00
e3db81ad-298b-45a6-8e50-13e5c210723c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0134449005126953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:19:19.206219+00
011ffec5-3898-4264-9572-e937c0d662cd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9388198852539062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:34:14.180215+00
ad86d55c-e91a-4c16-9d37-cf5b4c313bf9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.962827682495117	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:36:14.572958+00
06561903-6582-4774-9d94-1d57fed7d0a0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1800994873046875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:40:45.578364+00
7d851dd9-e2c9-4171-aeab-c8d5029e3ddc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.063274383544922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:41:45.765689+00
a8398ce0-588d-4ea4-b516-8f00ddc22a23	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.515077590942383	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:42:45.972239+00
97dfe104-f3c4-476d-b4c4-0c352e9bd55d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6144981384277344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:43:16.108649+00
07cf4826-2614-4fcd-ae4e-d8cce4fc7604	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.0663013458251953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:43:46.194528+00
4034c2bf-d24e-435e-96de-f09ad40bcc14	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9420852661132812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:44:46.406707+00
2f24dd43-103c-4ae1-a1c0-99c351c79fb1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.1862258911132812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:46:16.723582+00
d4cfd931-9a94-4e6a-91c0-4ffc780b2956	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	12.431144714355469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:47:16.957635+00
36c4bf88-c864-4609-8d15-5e23de0768cc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.257108688354492	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:47:47.06547+00
a09565b9-4982-49d6-81c7-798d639265b6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.1032562255859375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:48:17.182985+00
bbcb1105-4527-41c5-8453-f6fb54c3d652	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.5474300384521484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:48:47.289947+00
3f9532a4-b01a-43a8-a77b-241cf51ff962	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	12.078523635864258	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:49:17.44672+00
5dd919b7-8674-4cb1-9a2a-b61648aed809	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0351409912109375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:49:47.544049+00
75e541ff-5829-411a-9afc-61da8a68e720	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.459287643432617	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:50:47.754847+00
7c353a0b-5872-48bf-8c33-88fea4ae7243	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.245187759399414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:51:17.851646+00
fb226169-b12f-458e-8f15-2d929459ebcc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.683328628540039	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:52:18.106974+00
34726307-d262-474a-8740-82d8dd2a13e5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2051334381103516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:52:48.19595+00
55e309a2-a675-4a13-b253-042c4ae31add	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4230480194091797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:53:18.291749+00
07fd2af1-a4e3-4ad3-b473-b645ab70a753	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.00653076171875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:53:48.389863+00
6a3d53db-f519-4c68-8ed9-53e0a38a8397	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.119779586791992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:54:18.480292+00
1cd608e3-9454-440b-a7b1-39052a87dc37	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.519845962524414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:55:18.695288+00
11ed28e1-9dc7-456b-a312-3f652ceff2df	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0639896392822266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:55:48.798245+00
de82e2e0-2b08-4221-b58d-6a2125507363	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	6.723880767822266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:56:49.034738+00
2a2eca9b-bdbd-43be-a84c-1e9a5abaf9a5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.866029739379883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:57:19.178022+00
eeaac237-70bb-49db-8af5-135f3c4bb07d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.505229949951172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:57:49.3223+00
70dccdad-a3f1-4849-a773-1fcf73c51f62	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4862289428710938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:58:19.45547+00
a9f3c42a-f730-4621-bd9d-422fc8dc89a6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.267122268676758	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:58:49.553285+00
259e99ce-92cc-47f1-9171-21ee1d89d7a3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.286123275756836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:59:19.664855+00
7f88b592-7d96-43fd-854a-7c4628960d44	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1028518676757812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 02:59:49.772263+00
758d34a9-0dc1-4716-b476-fab91b25b1f0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.374338150024414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:00:19.875179+00
67b3bf4c-bef9-467e-ac82-c092c7e401d4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1436214447021484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:00:49.974343+00
b4e03e11-6e83-4b49-b310-08181ec821bb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0186901092529297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:01:20.082148+00
56123542-f2c4-4e79-9a47-73b7c9e925d8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.468109130859375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:01:50.193323+00
75a8752c-8892-43f1-843f-17cf9e1fb51a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.283811569213867	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:02:20.327163+00
e55e208a-b7ee-4094-a494-de0a79fd4131	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2068023681640625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:02:50.446617+00
3dc8048d-7c6c-4e8b-895d-67352fe208d5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6695728302001953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:03:20.555018+00
67bc44f3-6bdd-4df8-9c85-6e406088d628	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.027273178100586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:03:50.646953+00
83e57089-9320-4434-8eeb-09c8389f258d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.245115280151367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:04:20.738544+00
e4abd90f-e06e-40fd-9902-680c8172c844	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.74658203125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:04:50.848434+00
1b1eee14-54cd-4ec5-91ce-ea558c29804c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5315284729003906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:05:20.949586+00
d1311e00-21d2-466d-b388-4edcb116ff82	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.035856246948242	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:05:51.054213+00
4105b1fa-8825-4301-bcf2-01cc5c659f03	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2401809692382812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:06:51.279976+00
cc13a7a2-47e3-4fc6-a328-5dfd68f1248b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.250194549560547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:12:22.515173+00
6c8e5523-b824-4f4a-b5ac-62c8ec404270	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.656698226928711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:14:53.131961+00
f089b3be-798f-4584-95a0-2919ae0df5e5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.512216567993164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:16:53.552143+00
45e67302-3516-42ee-aaeb-d2355be2596b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.134561538696289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:24:55.239611+00
fddb8e13-dbab-45e8-8c8d-e419b1a127f7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0601749420166016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:25:25.344904+00
1b217230-4ea3-49d3-be2f-2d496180fc2b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2220611572265625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:26:25.567441+00
702bfcae-de91-4e98-9f5e-254124eb06ae	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	9.321451187133789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:27:55.934291+00
760a86d6-d417-413d-95d6-caa852a78ddc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9931793212890625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:15:30.952563+00
4bf2d6f0-3349-4902-bc3e-dfa02b42d627	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8329620361328125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:16:04.378759+00
9a760449-820a-4f5a-a87e-1c111c511c81	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9113292694091797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:17:11.154054+00
50ca8360-25bb-462f-a514-6d4c3c7e92be	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7325878143310547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:17:44.531603+00
96721997-f6f9-4bf7-86db-62fd0b118e12	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2630691528320312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:18:51.290589+00
3b3ec0dc-c7df-4039-8184-2931c47ea53b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.82342529296875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:19:24.661427+00
9941fa25-33ec-433d-86c8-a3d17df035e0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8336772918701172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:21:04.812393+00
2da15754-653f-4a05-bf93-9ccd18387b77	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3717880249023438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:22:11.615676+00
4e3e59be-5e14-417a-acae-36337891439e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7418861389160156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:24:25.153501+00
be32ef45-1dca-45fd-801b-a2b3be4575cf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.697467803955078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:24:58.5353+00
0d5de2ef-c2aa-49cd-84e9-258b8bcc0674	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.661539077758789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:25:31.910905+00
1a1cd300-a8be-4705-9cbc-79147902c906	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7124881744384766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:26:38.679929+00
3f1e03cc-f9de-443a-bc95-a9024a4cf366	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.844644546508789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:27:12.086983+00
b1c8259a-2076-4516-b14c-30f3a844f384	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.063274383544922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:29:25.723313+00
35db90b6-6bc2-43f8-8167-46f985e1a21d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7463436126708984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:29:59.146269+00
ad0d910d-35a6-45b7-a28e-181778ed4eb4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8093585968017578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:31:05.910051+00
bdd7a1de-fb08-4420-b7a6-be3e255d26ee	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7650127410888672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:31:39.285245+00
6938d94d-6b5a-4c6c-9b5a-17f2bc82dd28	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8596649169921875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:32:12.669786+00
0a6c74a6-5405-461d-835a-d24a0a78a890	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9259452819824219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:33:19.433169+00
ebf1d885-c825-4305-9927-fdca58133ed2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9538402557373047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:33:52.816393+00
6a699fdf-3f99-4c95-9bcb-e962757ae3ab	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.104043960571289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:35:32.998767+00
a6528cda-6f95-4c56-b5bf-19d8cac56d4d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1276473999023438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:36:06.37259+00
476272ad-d21d-4553-8955-3662136cafc3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9307136535644531	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:37:46.541355+00
abd76baa-7a08-4d1c-bdab-cc097826e779	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.970052719116211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:38:19.920006+00
81a5dab3-0bf7-47b4-8e38-697d3088af1f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.836538314819336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:38:53.307396+00
a304fc8f-d11a-4a9f-a27e-31ad8e1bc584	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.760171890258789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:39:26.699447+00
e6a9fba0-aa78-4371-886b-3119cfbbb6f4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7714500427246094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:40:00.076403+00
3ac15b45-f122-41c5-bc87-6430b0f8a16a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0766258239746094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:40:33.446304+00
2a220944-fd74-42f2-841a-220817557f3b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8534660339355469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:41:06.820535+00
a7fc6086-546f-4049-846f-71ec070258ec	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.628803253173828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:41:40.211775+00
241cca28-cc73-4c5a-866c-9f4dddbaa3e2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7628669738769531	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:42:13.584774+00
9a3cb20c-b060-4774-9c7a-e5aed15a1b49	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0270347595214844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:06:21.163339+00
7b0a6c35-8ea5-4660-9bc8-fa3aba29a090	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.239704132080078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:07:21.38433+00
71b29a27-7754-493b-b9a8-4b16e55e57cc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0880699157714844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:07:51.485383+00
cbdcdc44-5966-43d0-bdd9-89e5532c7ad6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.2379627227783203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:08:21.652156+00
cc202415-99fb-4f77-a182-1af6bab12b48	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.584218978881836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:08:51.769386+00
4281ab62-45a1-458a-88ce-897568e6b86e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.346515655517578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:09:21.877835+00
de455707-21a8-4e47-a74b-9ad391dba9e0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8285980224609375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:09:51.976558+00
3575e177-bf73-48be-b241-91b64c6b784b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0685195922851562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:10:52.184232+00
c076acb8-02d2-476b-b4d3-f051f5b0cae4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7379989624023438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:11:22.302175+00
545f6f69-0589-4858-b5df-259beb1b6a24	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.112865447998047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:11:52.407666+00
eebed4a1-7d04-4c35-8650-6129e93d7734	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.282857894897461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:12:52.624405+00
bb998c63-e40b-4b9f-a71b-844ba3554f95	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0301342010498047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:18:23.858512+00
713fa790-30d1-4c2c-84d6-e88c66134ab3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.0820369720458984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:27:25.775786+00
613df443-b2c8-40de-afb2-028f1a3304ea	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1631717681884766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:30:26.549007+00
30f6ffbf-3c07-4eb6-99b4-885f12207590	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9938945770263672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:34:57.570208+00
96c7a4b2-85aa-4bc9-bcac-05a6edeee1c8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0744800567626953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:35:57.791539+00
dd11296c-a798-4f2c-8746-b0dcc8e2d228	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8680095672607422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:16:37.762199+00
2332b366-bc71-425e-a944-30be473494c8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9557476043701172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:19:58.043618+00
a3bcf00f-30b6-4555-9418-8293d250f7cc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8038749694824219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:19:52.595372+00
b659d86c-d12a-4bad-b7bc-a8cde7c52fe5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.534627914428711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:20:26.016813+00
759dcd5a-f064-4ba7-98e2-01ef3168dbab	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7943382263183594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:20:59.414387+00
54ba45e5-8209-4bc1-89e2-e1e457af18f2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.552509307861328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:21:32.793974+00
09fa0850-7524-4958-8e6c-f91c5fee73d6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.137899398803711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:22:39.545768+00
a2f9c343-6627-4497-96ef-94bfd4b376f6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.750946044921875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:23:12.931085+00
67c95e0d-d935-4234-a835-039d3f6342fe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9686222076416016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:25:26.506676+00
3422ef4d-ca8e-4e21-ac48-2442dd1229d0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.547740936279297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:27:06.694106+00
f5a2174b-2b43-4f55-9de9-125cc74e4d14	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8498897552490234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:27:40.097545+00
caa0690b-9af8-4828-a9bb-2bf6d7ca9f99	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.737356185913086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:28:13.484+00
ce1630e7-b5a7-4a8c-8ce0-a4018b4bc0d8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9030570983886719	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:28:46.863756+00
c853d36a-5469-4169-a7c1-c5eb44e6ddfc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6942024230957031	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:29:20.251913+00
6824aad4-6d5f-46b4-af22-3bd742bf91df	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6521682739257812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:29:53.638234+00
72dbd28d-40eb-4164-979d-f6f599b8a98f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.771688461303711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:31:33.79252+00
87e0b602-dfbd-451a-8342-662726a603f0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0532608032226562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:33:13.949468+00
68b8b3b8-fc46-4101-a560-b69ae012a29b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0461082458496094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:34:20.718374+00
18e6a70a-bf95-48fa-9d12-1672cd6882a5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.440929412841797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:35:27.508783+00
91f51fe8-52a4-4fc4-ab81-a3bcc43211a8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8510818481445312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:36:00.891883+00
fdf5d54a-9abe-4d97-802d-90f849679244	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.898050308227539	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:37:07.660954+00
682fca05-dbbe-4ae1-8174-1a27c4e25bbe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9769668579101562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:39:21.220214+00
f9a3acd3-f127-474d-802d-67f10e176166	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.649545669555664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:40:27.987857+00
7f431040-bb00-48cb-ac18-33c6ca01f8ce	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9297599792480469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:41:01.370266+00
801357af-c4a5-4339-8ff0-17141bbea30b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1066665649414062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:41:34.755722+00
903cdcd5-fe76-4bef-b58e-8e892baa5ce3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.404451370239258	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:10:22.084828+00
e2e07076-f47f-46aa-8a59-f3cd1c25a4bd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.149343490600586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:13:22.770211+00
348aa7b2-8209-4f4e-8483-0d763cf0e807	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9006729125976562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:13:52.879409+00
786c6165-3366-4c74-83f2-8ea8e3bdd931	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.804994583129883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:14:23.019016+00
cc8c90c5-36ff-4638-add4-93d1768ccdb6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.256631851196289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:15:23.238987+00
0b66cf07-98cd-42de-a90e-62f7ee1da62f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.311229705810547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:15:53.346611+00
4efb4826-1b44-4698-ad08-e9fe7ce6149d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.101421356201172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:16:23.453566+00
eb03c8cb-7270-4a49-ac9d-6506f129b080	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.790689468383789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:17:23.661818+00
99ff511c-7dc5-4b1f-b6c7-b02729a7ead7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2475719451904297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:17:53.761382+00
ffac391e-e120-4f28-ad71-88571304224b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9671916961669922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:18:53.971373+00
c4ae422b-d25d-4ade-b078-a8124172b9c5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0627975463867188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:19:24.076075+00
8cf1b15c-dccf-44c7-a4a7-a95f92415bd2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9762516021728516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:19:54.18234+00
6aeeb6db-d190-4d5e-897b-b1a96c5e653b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.720355987548828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:20:24.279616+00
bee66c6e-7267-468e-8f98-d53087cee94b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.874685287475586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:20:54.383946+00
59e273cf-7dda-4514-b260-a67410ae8020	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9602775573730469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:21:24.478291+00
9acbf511-a45c-4957-a3b5-84cb85f967fb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9650459289550781	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:21:54.585898+00
40bbcc9c-ddb1-45e2-80e9-f5d379990702	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8382072448730469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:22:24.695514+00
9d7efe46-7726-486b-94f1-c6b6c438966e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4726390838623047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:22:54.812418+00
9573a887-cb76-4b25-89a9-a78b34db3e6d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9838085174560547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:23:24.907804+00
25973154-c9c6-4ec5-8612-6b9a6274508b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.084970474243164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:23:55.017888+00
3f41a34f-42b0-4ee3-8c6f-3e47da74cb35	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9359588623046875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:24:25.127384+00
bf82d388-ccdf-4bcc-b035-81308f444ca6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2382736206054688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:25:55.457686+00
e7c45642-7917-45e2-aee7-8a075e6005b9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4614334106445312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:26:55.671399+00
8ab91724-9348-4b3b-b168-13928e05c0a9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.392292022705078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:28:26.090633+00
c90332c9-5aaa-4472-988b-abd7e5bf220e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0554065704345703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:28:56.205273+00
43f1a6cf-6c3e-4c93-a4a2-b3e4d938303f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.30352783203125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:29:26.32342+00
a6ba40bf-9fcd-483b-8185-3d6ae4c3532f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.170562744140625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:29:56.430789+00
74afab88-2228-4ca4-a7b4-b8a440359c56	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8973350524902344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:30:56.678491+00
5b6c3b3b-b003-4dce-9043-0e223497ee09	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3183822631835938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:31:26.78319+00
e224a7cc-1b59-4b20-b4dc-fa73bbd538b7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.786397933959961	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:31:56.902388+00
3018e7f3-1c05-4340-a0ae-c1c01cceb509	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4242401123046875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:32:27.009109+00
8bedd72a-7a69-4844-bd83-557e06f0dbe2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0360946655273438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:32:57.13152+00
94a1d61d-a7dd-4a92-b4ad-54334a3fe1bf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0873546600341797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:33:27.244928+00
2a320ae8-9377-4ed8-a2ae-32adb06e208d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.024412155151367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:33:57.3365+00
8ce991f7-c3c2-405b-935d-00dd78400f1e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8990039825439453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:34:27.45024+00
558091ca-0428-4330-877b-42b0f3bf364a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1753311157226562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:35:27.679716+00
4c0fb084-6025-4531-976f-a3a2b1b04ea5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3374557495117188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:36:27.933678+00
6fb5464b-65bb-4685-b603-b4fc1b4fb552	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.96075439453125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:36:58.047219+00
7f865274-64d2-40c7-91ad-5d6e476eaeb8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.059459686279297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:37:28.147094+00
18115bb3-85d4-4065-b211-7a7d386c6d55	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.936197280883789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:37:58.243848+00
e11a3060-7413-40d1-924e-24cbb54d5582	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.8678646087646484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:38:28.371601+00
819eab4a-3588-4c82-839a-1dcbc5e17057	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1674633026123047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:38:58.487652+00
d8b83f14-a10b-47ba-9277-ebb340a100e6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.064228057861328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:39:28.637566+00
e261b15b-ebae-4597-b38d-e53a4c1dfce9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	8.566141128540039	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:39:58.836826+00
f06ef048-77ef-4972-94a2-5b717891b8eb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.368927001953125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:40:59.08667+00
04fea7f5-f2cd-4cc5-b571-0eb90b904900	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.683401107788086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:41:29.209742+00
8888b768-4eb6-4c3c-a5f3-e22b3451a7ad	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	7.207155227661133	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:41:59.335424+00
a322972f-710a-4919-b335-e6bb62db082b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.429485321044922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:42:29.439803+00
2df45a0c-a52d-4a30-8512-ba83d0c07bf3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2382736206054688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:42:59.550835+00
0af06b13-b139-44d0-91e1-d6fd62f66080	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.620697021484375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:46:30.430619+00
a7c2c8a3-9849-49a1-9c0b-d5805c8b9d8b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.27301025390625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:55:02.567833+00
26a6e3c3-5ef1-4723-aa99-3b938a53a510	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2919178009033203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:56:32.9701+00
502246f2-9e6f-4dd2-9791-a9345d3b72da	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7478466033935547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:18:17.904472+00
d37d15a9-f51c-4d0b-b56f-2f1c50bbf61a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8990039825439453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:20:31.428924+00
1e28502b-12a9-41a3-bc95-4a0f538a7476	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5374889373779297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:22:44.990411+00
c8853dd5-14e8-4a04-a686-35350c80443f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7015933990478516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:23:51.767623+00
228e0fd7-4ca0-4527-8315-ec3b66266a00	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.267599105834961	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:24:19.716203+00
d5065a12-fd04-4c8a-8c66-f7db9b44b8a2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1734237670898438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:31:00.407756+00
ff203f41-6b44-43c7-84a9-caca593c6d7b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.178192138671875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:37:41.063644+00
4e3e5b82-b654-47b0-9cd3-fdabcde30282	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.802206039428711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:38:47.834789+00
9f5e88f9-39aa-4057-af2b-d053ef3838a2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9626617431640625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:43:48.324246+00
50cc3ecc-29c2-4f25-b7a7-73218722dd53	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7246475219726562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:46:35.3128+00
e089dd10-ca22-4e6d-b87d-5cd1d2d2933c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.74713134765625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:49:22.247506+00
b21239b9-a859-4a0b-9818-fbdaafbbb218	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2068023681640625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:23:54.237358+00
3f974722-99de-47f8-a05a-4c63e228f8a6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2230148315429688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:25:24.795601+00
7e100355-7a01-4b74-a7fc-42d1aae72262	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3169517517089844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:25:54.956692+00
9f4236fc-8da5-4487-82d7-cf7520546f02	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2268295288085938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:26:25.091673+00
71e1e7bb-f75a-47a7-a8fe-5354f9671974	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.969503402709961	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:26:55.247087+00
c6988efb-dd0f-4d25-aed6-4065eb9981c4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0139217376708984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:27:25.361454+00
eb6b9a5b-860a-4dd7-83a1-4bf1bf43464b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5107860565185547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:27:55.464676+00
5e9861f8-8334-4fac-b3e8-73f5e6db5088	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.241849899291992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:28:55.644548+00
5573c2c3-415b-4f0c-af2e-63e3f86b58ac	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5703907012939453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:29:25.75908+00
e14fed13-9c6e-4353-aec9-27251fb25f13	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.521038055419922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:29:55.842121+00
a4a2e048-14a2-4a41-8632-1a6d2066b76d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6922225952148438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:30:56.007007+00
6cbc8302-d867-4d91-bb3b-609d629d4ef8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.180337905883789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:31:56.145081+00
87306913-240d-4d09-ba21-98fc235668f6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7599334716796875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:32:26.238268+00
b62dc622-49c9-4a59-bc27-4e83362efb05	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2461414337158203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:32:56.311245+00
ceed4c18-1a37-411d-b779-10fec45637d1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8157958984375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:33:26.385277+00
c9d8d1d9-7a76-420a-8a7a-c98018cf8e3d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9190311431884766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:34:26.523186+00
5da84668-3197-4e01-a392-f1cfc936deba	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0606517791748047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:36:26.784964+00
97bc8548-1222-4aad-97c1-fdf7494872d0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.017974853515625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:36:56.860462+00
8c6d9025-26f8-48a2-b2fa-3640aaa73e9d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.229928970336914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:37:26.92145+00
cb628c69-26b6-492b-bbe3-e84679484d2b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	8.328437805175781	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:40:28.954755+00
61cb8878-4e88-40d5-bb1b-5b7fe5309c77	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0568370819091797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:43:29.699301+00
3f9836a4-6ace-4d23-b4d8-69a0d335098d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8508434295654297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:44:29.945025+00
99e15089-c23c-42e0-81b2-5e505ddbdc75	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0112991333007812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:45:00.056161+00
eae03ecb-47f3-49e3-b9a5-a3bcead63c19	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.179384231567383	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:45:30.171435+00
ed871d9e-a6d2-48aa-93ee-3d0818312ad5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.946138381958008	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:46:00.309195+00
f53c38b7-de58-45db-ba9e-85f2a7a6388c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.917123794555664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:47:00.543934+00
20cf2dcc-3ecb-4d84-bbe9-88b59c56bc83	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0685195922851562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:47:30.651031+00
92e4409a-5693-4d65-9178-923da7991701	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.016782760620117	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:48:30.945021+00
8e1c4ce6-cb85-44fd-a35f-7ab601a4a278	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8777122497558594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:49:01.069107+00
e765f00f-d6d5-4ffc-9d19-0202faaf8417	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.185344696044922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:50:01.302064+00
b5152b6f-2606-4501-8572-b207128342fe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0530223846435547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:51:01.540679+00
1be5a1cc-e18d-441a-883e-3fcfafa8261b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.113819122314453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:51:31.664948+00
a5b221d7-40cd-4970-b6be-a5d75aa827c2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9986629486083984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:52:01.802213+00
3a55e9de-87b5-48d6-92e0-d1efc32c947d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.332925796508789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:52:31.927016+00
f28fd416-a9db-4305-8a38-c8ef80c4e426	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.848386764526367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:54:02.299621+00
95fb8617-a6e1-4b9c-afe6-c896bd8cede8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9617080688476562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:55:32.675896+00
46c44904-4c73-4667-945d-b5d557b45d31	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2428035736083984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:56:02.808205+00
3e62592f-f58a-4eae-9639-88400fa0235e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3283958435058594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:57:33.205886+00
991def4a-f4e7-42a0-97f6-7000ff16cc94	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9490718841552734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:58:03.314479+00
bb135e70-95b5-45d3-8623-8b38328b69ca	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1142959594726562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:58:33.440382+00
09563bf4-a67a-4e9b-9368-f731cfbd0a16	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.094268798828125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:59:03.560252+00
71c316f5-08be-457c-99d6-f07e8a706e4d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.012491226196289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:59:33.679901+00
485f88f0-43c6-4dc2-bb52-b5bc5c30e970	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.301454544067383	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:00:03.804965+00
3ffce8b2-4bf7-425f-908e-14a0ae0b6713	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.131223678588867	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:00:33.931822+00
155641a5-9793-436e-8510-6cd622df4bac	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.985311508178711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:01:04.060006+00
b9801545-a203-4ed2-971a-0a239507de5e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.103090286254883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:01:34.182689+00
cc187e9b-4d08-4377-97fe-82a971bdb18f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.221273422241211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:02:04.329357+00
7a7bc49f-ee8e-4316-a518-ff870cc23edc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0074844360351562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:21:38.221408+00
f877da48-1a9a-4854-8330-04c1f3a805b9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.99127197265625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:26:05.286677+00
139cd97c-e7f7-4510-80c6-8e27fcbbf1ec	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4433135986328125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:28:52.320309+00
c128c478-4ef5-4e65-b41a-9e6f8ecfca02	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7740726470947266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:32:46.040152+00
2ffc55da-8df3-4e60-8de6-b3751e50c49a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0177364349365234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:47:14.020688+00
c382cae4-c413-46f9-b2ce-2735bb9e8dff	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.307415008544922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:25:59.919+00
6e3a983d-a1f4-4140-9b39-57c6cc6f0cf5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9595623016357422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:30:27.021765+00
d3510a1c-ae16-433a-9934-77b5739b4306	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4881362915039062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:32:07.174629+00
3cc5a235-fedd-46e3-962f-e0fde3361bbd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9512176513671875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:33:47.334717+00
98718244-293d-49d5-b59a-d2fc2137c51d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8148422241210938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:51:02.431776+00
9ea69e85-cfab-4db5-b34e-ae4e8910fae0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.386808395385742	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:52:09.222655+00
38b5d496-3d8c-40bc-83a6-e69d087f7b04	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.084970474243164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:52:42.626639+00
c91cca3b-8f4b-4d2b-9e54-9d4a4f0a9f4b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.043008804321289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:33:56.459175+00
05d1d5f1-758a-4b9a-989e-396cd4372ae7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	7.018566131591797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:43:59.823967+00
5076832f-a8a0-42a2-aa07-d6b262ee9f8b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.083301544189453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:48:00.792279+00
b2aa06a3-1874-4e35-bf35-f2555c32d5fd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.28118896484375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:49:31.184071+00
9f75eb69-45da-4f66-a0a5-4dcdde223761	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7921924591064453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:50:31.426912+00
0e7b3efa-1417-4a64-a715-39188621bad5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1619796752929688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:53:02.032384+00
3465b7d9-c817-4fbe-9848-2d3907e4939f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9736289978027344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:53:32.135873+00
d77628eb-53d1-4abe-aff8-47fbed0ea7ee	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8665790557861328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:54:32.45336+00
ecf8516c-2dc2-4987-b339-5a3f3c23c30d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4123191833496094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 03:57:03.091301+00
8d76a5cc-2c9d-44bc-87d7-545384b2d109	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.274036407470703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:02:34.468011+00
57df9bde-2fd8-4fe7-866f-a3402d46fdb7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3450851440429688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:03:04.578541+00
bc66502f-6841-485a-867d-c6a353f7fa99	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.1540393829345703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:03:34.732629+00
0683422b-c586-419c-a785-fa3b160b962c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5260448455810547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:04:04.857671+00
51e3630e-1eea-4cbf-ac03-0d72f9d15414	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8062591552734375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:04:34.983204+00
067fbac3-b6ef-4766-b030-2f4ada36a7cd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9686222076416016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:05:05.111862+00
1f39b57c-7224-4129-bdf5-5a5c40097a56	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2017955780029297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:05:35.2445+00
93f145c8-0c36-41b0-a652-26c4b760c6af	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9519329071044922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:06:05.361373+00
83bb73a0-7c39-4da1-9e4d-be80232b42a8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.015352249145508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:06:35.488915+00
bffd96f9-e9ac-4f70-a443-3f828c320fae	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2089481353759766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:07:05.61236+00
06e7055b-e2a7-4ba2-9898-e019343fa6d7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.457857131958008	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:07:35.76543+00
e1cd48bf-bb99-4919-aea9-831c123a7379	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9640922546386719	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:08:05.888738+00
b1f95b72-757d-4abb-b93a-a7070b7b8499	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9447803497314453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:08:36.010042+00
4e06d4a7-52d8-445c-85f0-80b6a58e4358	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.221822738647461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:09:06.126586+00
fe33af40-43e0-4f32-85be-c71baa57f541	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3627281188964844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:09:36.23658+00
bdd67e46-2194-4df9-a482-79d066ab9252	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9664764404296875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:10:06.351595+00
de480de1-3b1d-469a-90c5-aef13f0b95b7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7086734771728516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:10:36.476465+00
26359f5e-8b61-4fd9-be45-21cc4ce791af	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1202564239501953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:11:06.605638+00
b15376fd-473f-4090-bd5d-8d6f20762a44	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1042823791503906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:11:36.7638+00
3de14b8d-aa80-4cde-be47-8775c1e05fc8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.30352783203125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:12:06.920112+00
5f1a65e1-5b78-4ac0-97dc-ababcbfdc421	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4962425231933594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:12:37.035762+00
a13b8a17-d932-43c9-ae90-864b9866414d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9175281524658203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:13:07.148909+00
42f7b3c3-1b3a-4e65-8bea-b0f5fa05c796	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.6122798919677734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:13:37.277892+00
dca33bc3-826b-417d-9328-fbef46e78089	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.074003219604492	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:14:07.438299+00
225e9cff-b1ba-4e79-87e0-7b4d6206f527	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.874685287475586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:14:37.564051+00
b3f8e573-d362-432b-b407-34f361ed3f56	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.414703369140625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:15:07.693094+00
86c29f0e-393d-4b4e-932f-ca3163f6139a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3317337036132812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:15:37.821189+00
0d1e247d-61fa-4590-865f-99fb572bddc1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.854585647583008	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:16:07.961569+00
549c0784-f41e-4dea-883f-249b95fe926f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.306699752807617	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:16:38.086801+00
f3054044-9ae1-4060-b721-04220013356e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.24249267578125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:17:08.285662+00
de711094-eb5a-4eaa-a2eb-01e4f5e2bf66	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1376609802246094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:17:38.421712+00
18245e48-f607-42e0-b5c7-a1ec2f68a4dd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1507740020751953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:18:08.555066+00
0b98a46c-1335-4107-a6de-df4659d1554a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2945404052734375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:18:38.685279+00
d0b2dcbc-c6a6-462a-8f08-9000f4f3046f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.079010009765625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:19:08.81229+00
34e8ffdf-e6b7-4a60-a6e5-8d88de66b97a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.359628677368164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:19:38.944794+00
cdacc2a4-b1b7-40e6-a97b-7a0691bcfa38	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0151138305664062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:20:39.213176+00
e60183f7-7a55-4f06-805b-a82068444c86	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.082347869873047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:21:09.336463+00
f4bbe706-d9a2-4d84-8f37-06e0c6ce678e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0744800567626953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:22:09.646125+00
ba0f335d-b70e-44a9-925f-180a4a44dadb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2673606872558594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:22:39.773761+00
0316d7c9-57b9-420c-af61-6f65d2b6f922	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2606849670410156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:23:40.029582+00
ac4cea37-7629-49c7-b96e-404799182d7d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9502639770507812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:24:10.168238+00
316f7ebf-3ea2-4d11-bbd2-0bdf1c2ed4da	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.038240432739258	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:24:40.292163+00
6693dd47-3c31-4c6b-ad89-fe2cae297037	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.874135971069336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:25:10.420061+00
089bae7c-3036-42ee-b2fd-5707178c56f2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.157377243041992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:25:40.562959+00
cb824db4-f7d0-4cc9-b3fa-c55f2a45a696	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.019166946411133	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:26:10.690028+00
3ea4eacc-712e-4725-9890-3a92cb817b0e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6237964630126953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:26:40.842732+00
b8ae33f5-c111-4c89-af6c-3578997316b7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8023719787597656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:27:41.109493+00
1bd18266-27be-4f53-bd55-7348063074f7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9371509552001953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:28:11.226161+00
4ada1f1f-3b08-46ae-92fc-f5e2f6fb8cbe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.170490264892578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:29:41.630981+00
3689327e-c6f6-4515-b025-8c6c6bfb08ad	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5091171264648438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:30:41.917698+00
77fe9d91-2a28-4744-9452-c497eb3165fe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5069713592529297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:31:42.172649+00
6f276fe0-d9a5-4b52-8a09-0450e038c45e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4280548095703125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:32:12.303927+00
21efc364-ddcf-4521-8d38-27544fdef682	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.813577651977539	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:32:42.463758+00
68abd292-2e51-4ce4-a5d0-944d56e7f10f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7472972869873047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:33:12.589929+00
9eb8f7f0-571a-478b-936f-6e8f8eb867a1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1212100982666016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:34:42.99354+00
2b29eb1e-d670-4c38-92da-abaf3cb2c332	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0792484283447266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:36:13.398612+00
ca5cca65-e48a-4282-9d22-56e751bc568f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9114017486572266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:36:43.528056+00
8c0469e0-2584-46a2-ab06-3b5f470cd460	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.346515655517578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:37:13.656245+00
e46157f5-e609-4a9e-ab2f-57515f6b19cb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.282381057739258	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:37:43.792506+00
6d40cb59-1ce9-4dbd-a349-ced8df5d2aa6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9571781158447266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:38:13.923597+00
5272c43d-c4a9-4503-907e-9826e2bceb7f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.144502639770508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:38:44.085696+00
512bb558-c056-4c51-8884-497b28859fb3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	5.783796310424805	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:39:14.249939+00
bde492a2-274d-406d-9ce9-0b0b3729322b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1295547485351562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:39:44.388174+00
e2ee72ca-a4e9-499a-962e-041c6e169b42	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.1518936157226562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:40:14.52381+00
a460d9ab-7f98-4196-983e-bc020bf416a8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.166748046875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:40:44.648863+00
68a5bbf6-83c9-479e-9c0e-6d36165546fd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.281665802001953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:41:44.934465+00
b22769ea-60af-4cdb-89ce-317ef139c4ba	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9450187683105469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:42:15.055448+00
065011e8-8968-4e45-88b3-0613417755e4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5835037231445312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:42:45.188606+00
bb660048-2148-4267-99aa-cc4b5d8ba283	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.25067138671875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:43:15.312048+00
e360f323-f083-4836-a416-f2b4241406c7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9931793212890625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:43:45.439461+00
6787362c-c2bd-4a3b-8690-9649aa60db33	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.637624740600586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:23:18.376243+00
13f68a75-84ad-4489-bada-47f5c83952aa	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.269268035888672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:27:45.473896+00
d7db40ff-43fb-438a-90eb-0af5bd5626e9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.552509307861328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:28:18.923535+00
c6a1dc8d-d832-4d08-a3f6-8bc102f4cff5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2144317626953125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:30:32.524409+00
c8dec902-d386-4350-b0c0-75c08edba689	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0406246185302734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:20:09.081018+00
ee75a098-df81-49ee-a7b6-000800d77588	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0372867584228516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:21:39.492845+00
3e1571f1-d47f-41a9-8fcf-0354f311680a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0999908447265625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:27:10.965903+00
ec830e8f-13b5-4e91-afac-23b9a76269e8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.221822738647461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:29:11.484106+00
064514ff-9fd2-4c39-93e0-8746d9295155	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3391246795654297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:30:11.780022+00
bbb29c12-aedc-4d3b-a5d0-a1a25ec5e9ed	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.576040267944336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:31:12.050299+00
079516ca-ce88-496b-9e62-f0d47c01f778	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.080202102661133	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:33:42.722181+00
292135b8-a835-496a-9b84-8bad6cc08e18	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9235610961914062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:35:13.124392+00
1021fada-e373-43df-a90b-630a42095376	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.64630126953125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:47:46.563593+00
7cc63f54-317d-4371-9442-b32322060997	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.955270767211914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:49:47.118295+00
218df083-55a5-45f2-95cb-d84f19f0b8d0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7380714416503906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:34:26.225111+00
1e6ca689-7aef-401d-8179-f76b2fff6e81	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.859426498413086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:34:59.61294+00
77a12057-2c62-4e65-b6d5-b0845dd94e06	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8963813781738281	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:45:00.468102+00
9c42aed4-4043-4d78-8deb-c686a57b99d9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7745494842529297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:46:07.218123+00
bf1924dc-afa0-494a-9623-98691a0f9e44	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.615690231323242	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:48:54.174612+00
7514b99d-edfb-42dd-9d5c-c9598f2a8f74	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6913414001464844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:50:34.322203+00
887559b1-769f-4d16-961c-2ab5f3204d99	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9266605377197266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:51:41.099241+00
948a1524-d345-47b3-b8b6-6f8fc2af368a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.1785964965820312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:59:28.561125+00
ecdb8431-52b7-425e-b872-41a5596876cc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9805431365966797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:02:48.898755+00
933fc6ec-083d-4076-b053-1572a0f778ae	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7430782318115234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:42:08.141656+00
c804569e-828b-4060-ac2c-124e0d34ec2f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3412704467773438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:43:14.939691+00
842d65f4-16e2-4d69-b734-9d2d87500e6d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.848459243774414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:44:21.696914+00
5288270e-dd38-40b7-b194-6b577efd12f6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8570423126220703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:44:55.084072+00
dc363ae1-a54a-4e16-b7af-a266e249e781	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9085407257080078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:45:28.498219+00
062c2c9e-271b-4c6f-834b-7ce6f65e7006	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.3066272735595703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:46:01.905833+00
3759a2ba-c53e-47c7-816d-1e08b9f37fc6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8470287322998047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:47:08.702348+00
64efa85a-53ce-4964-9ddb-96660d35e82b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8763542175292969	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:47:42.085286+00
945900b7-1e3b-4452-bc04-918d71a9aa13	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.527952194213867	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:48:15.475271+00
1b9ae146-8357-42fb-ae1f-c21a449cd5a4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2161006927490234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:34:56.595365+00
8fd9bb6d-ecd2-4090-bf48-92e1c1824a59	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1827220916748047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:35:26.65952+00
ef909a5e-3a2b-4416-bb17-9848c49181bd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0303726196289062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:35:56.722854+00
153e3672-ad26-422b-8cc8-200f869fe6d1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.042531967163086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:39:57.268494+00
d63d40a1-9d56-4191-afa4-54ec38696af9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9440650939941406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:31:45.683313+00
2790f619-c914-457f-9701-dc805e522459	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1665096282958984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:33:15.961883+00
ee95addc-e07e-475e-90fe-8211c5f9c01b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8761157989501953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:33:46.054607+00
c78f3c31-c2ca-42fe-8b29-790cefcff31a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.358675003051758	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:34:46.244106+00
1be0cf05-dde1-43b0-8c66-7c29e0af8ed7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.027273178100586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:42:47.793637+00
b7f5a798-cbb6-4060-a25d-bc57aab4a249	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.14385986328125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:50:19.416691+00
1be1b718-4dee-463c-b113-b5470756ebde	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.332542419433594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 10:01:23.085262+00
f4fa44a9-ab96-4504-aea5-ae0b3563ce5d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	9.437799453735352	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-09 01:53:13.707271+00
8ec61a2b-b711-439b-b8b8-9c773ed8b488	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	7.0400238037109375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-09 01:54:19.644724+00
356041f5-0a86-493b-bac6-b48996af1d17	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.325296401977539	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:23:09.900323+00
a8f7a64f-2fe8-4562-a852-7d45f4484162	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.140045166015625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:28:41.34908+00
44191487-23a8-4512-9275-cafcd63b30a8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9838809967041016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:34:12.860554+00
316389f8-b9f7-4900-a400-f26afe77b0d9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.901792526245117	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:35:43.280425+00
44c7cfc4-adb7-440b-8633-5821f1338b0d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.62794303894043	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:41:14.793673+00
d2548dc8-a939-4be7-82c9-dcba410870c8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0797252655029297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:44:15.601721+00
ecd45eac-ead9-423a-9beb-7f0ab0a97403	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2182464599609375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:44:45.761982+00
741aa15a-359f-4033-b380-f4ae16048567	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1457672119140625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:45:15.894403+00
ab78a89f-730a-4276-92d8-1442a2b3a45b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9304752349853516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:45:46.024014+00
3cb11a04-96a8-455d-837a-0289afdbe34a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1359920501708984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:46:16.158695+00
7c8b0faf-e1f8-4480-82c7-64dc533ad1e8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.050638198852539	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:46:46.291135+00
670ac4b9-f829-4cac-84cc-14f93c22d061	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9452571868896484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:47:16.425545+00
fc59e83c-525e-4447-9f4f-5b948bc467a3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8341541290283203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:48:16.738339+00
820f60c5-1e45-463f-b794-7cef7a3c5833	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2966861724853516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:48:46.866104+00
f5c533bf-6198-40c0-b38e-c3b0e1e9086c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.323150634765625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:49:16.990764+00
66a4de9e-925d-4f1a-9228-0315a7910234	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2478103637695312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:50:17.249004+00
d3abb845-b4a7-446d-b0b9-c6309a45dc09	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0627975463867188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:50:47.387956+00
5ff53791-8e2a-4eaf-a6c1-169ac38f06fb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.039194107055664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:51:17.516133+00
ec6f7c12-90af-4d4c-beb3-4df4fdf20e6e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1212100982666016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:51:47.636198+00
e72812dc-373f-44e1-b653-c3ebfc0baa7c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.993988037109375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:52:17.809413+00
3c4317bb-bd6a-41fa-a470-bd551c7c53c2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4063587188720703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:52:47.94091+00
4fdc5ae2-b979-46c4-be3f-16787437dbfe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9898414611816406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:53:18.078058+00
22ed2f7e-d99e-4941-92b9-fd38228c1724	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.081632614135742	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:53:48.213833+00
fef4dee3-7d19-4ed1-a798-4119b08ef1f5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2039413452148438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:54:18.355059+00
29da4280-7ea2-4a0d-8d07-71724e4941fa	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9948482513427734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:54:48.4818+00
09ba6469-9082-4a3b-9174-0b92ffc08252	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8448829650878906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:55:18.619994+00
8ccd00b6-2955-4cfd-bd53-30b054290a38	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.057313919067383	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:55:48.759406+00
34b48f61-c177-47f7-a487-df2df9b05567	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.571582794189453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:56:18.898743+00
dffd1c96-b7a5-471f-8a2f-a0d033cbf8dc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.051830291748047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:56:49.068298+00
08008746-0b1b-42be-9d69-9f5be82b4bb0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2912025451660156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:57:19.216818+00
2978e7de-6ee0-4a73-a08f-4259ced9dfe4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.167940139770508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:57:49.342335+00
42ae2806-b2d2-48ee-9fb5-ed072a9f05de	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.103567123413086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:58:19.472844+00
cf147ee6-8c99-470c-ac47-5649c4389bbf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9431114196777344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:58:49.614307+00
0451e6d7-4e36-4895-9a90-dbf88b38c5bf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.947092056274414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:59:19.743593+00
4194c441-080f-4989-bdd5-9ee1761d5b38	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8780231475830078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 04:59:49.879238+00
9b1b1e7b-f9c2-418e-a2b6-33f13b22f7fc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3353099822998047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:00:20.016271+00
f188c792-6755-4536-9029-fe666ae62d4f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.651214599609375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:00:50.158099+00
27df85d6-2044-42ad-aa86-383c136dac08	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	6.57200813293457	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:01:20.361183+00
b977795d-a60a-4140-bf0d-3cc6401613b4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.62451171875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:01:50.523343+00
bde54f7e-8d31-48d0-82b8-b3094a0b51f0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.016305923461914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:02:20.658668+00
ab0c4940-164e-49df-8144-28291c6a77bd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0110607147216797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:02:50.795053+00
39f03ac2-9ae5-435d-8b64-b7185b04d881	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9199848175048828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:03:20.945092+00
07a5b129-17bb-42b9-afd5-d20fe44ed16e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8312931060791016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:36:39.786098+00
1303f4eb-7885-441f-941a-b87f5b79c8be	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0132064819335938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:37:13.160456+00
ae2d5a93-d089-43c2-b108-5df33e6f6f27	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0895004272460938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:45:33.845137+00
acdbfa07-da40-4c0d-b3c0-68d80956e995	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1386146545410156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:52:14.496158+00
f2cec38f-7281-474c-adce-2f19732586a9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9085407257080078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:53:54.656129+00
20ef022f-38ee-4ef6-83af-c805596e6a7f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9505023956298828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:02:15.513558+00
49dd1f8a-f0d3-4944-93f1-05d3c3cb542d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7151832580566406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:05:02.457681+00
4f8275cf-b6ac-4e8b-89ed-df17cdbee489	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1483898162841797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:42:41.562509+00
c42168da-e748-415a-8985-69953557309a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6187896728515625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:48:48.8637+00
8e12580a-18a7-4827-882e-91ba24d1a55f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0093917846679688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:53:16.016258+00
0e3c847c-4a06-44da-850c-641faf4f86d3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9009113311767578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:58:16.537483+00
50e0e049-d4e9-4c08-a060-70c6ae1d49b2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.911163330078125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:59:23.309123+00
4caf51d6-f62f-42bd-a17d-9a205d5745bc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9545555114746094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:59:56.695136+00
c77574ee-3207-4fd1-945c-2b8d9243f4ed	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8010139465332031	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:03:50.379268+00
223937ef-efab-456e-ab1a-b8f882f4c531	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.436399459838867	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:06:37.426955+00
8e0f7e6b-01c9-4341-aa3b-2429d62a3a53	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7740726470947266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:08:50.992208+00
16fb4a2f-259a-448e-89ac-ad1eb16e1ff4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9443035125732422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:37:56.985196+00
1f6e9465-3c83-43a7-a25b-41382071bcd7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.748727798461914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:38:27.059712+00
698db02c-6b99-431a-b512-df8fe4012b31	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1817684173583984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:38:57.12941+00
3f6b4a26-2019-4e2c-b91a-5004a47f3379	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.366781234741211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:39:27.199105+00
7e24294e-b4a8-4426-b83c-b5e104badf4d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0973682403564453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:40:57.418635+00
6e5d4df0-de3f-42e2-bbd7-f68397879e26	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.778219223022461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:41:27.487333+00
730ef56d-344b-4e23-957d-77cd37dd1a81	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.292633056640625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:41:57.558499+00
1c76769b-bfc3-48a1-bd0c-737a38e8d02e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.507925033569336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:42:27.63051+00
18f81c7f-4ec4-43c6-a9e2-756798c5157e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9964447021484375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:43:27.793075+00
a95bdb7e-7b55-4fee-adda-baf15f052bc2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8968582153320312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:43:57.851391+00
b0c8a6bb-cf5a-40ac-9be0-95ad1eb15208	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4704933166503906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:44:27.919767+00
a07a0bcd-4463-4a32-8bd9-1c158f623781	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9237995147705078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:45:28.063293+00
578331bf-5c2c-48ae-a43a-39f5cd42ecd0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7290115356445312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:46:58.354451+00
10403aef-4ce9-4ca6-8c06-679ffc20ca9d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0143985748291016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:48:28.556532+00
fcc72716-d066-4802-864f-3d8413bd4c1e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.058267593383789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:49:58.788885+00
e05c4730-6f49-4396-81ed-5285d6d2261c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9392967224121094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:32:45.883217+00
e99212ec-4f9f-4642-9832-286ea99c070f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	5.567789077758789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-09 01:53:46.656979+00
b3f101aa-d87e-4b6b-bd0d-21c419edb3c6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.024267196655273	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-09 01:56:31.688648+00
998ef908-6628-4fa2-9806-b3e6c5f05035	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	5.362510681152344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-09 01:57:04.608549+00
45930fea-6a60-4c2b-8773-aec672413b77	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9829273223876953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:03:51.073201+00
1c312739-f712-429b-9165-fa2c1d385780	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.104520797729492	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:04:51.359269+00
392a5338-0141-4372-9447-337a09f33461	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8956661224365234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:05:51.64247+00
60f0eb09-498a-4481-88af-d62b90fda7c4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.81524658203125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:08:52.49436+00
2739a774-de04-4035-b712-f1c4d54d5469	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8677711486816406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:09:22.631607+00
821d107b-17c6-4dd0-9404-6d66b57fb354	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4480819702148438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:42:46.967255+00
d68f82cd-4551-4493-a7c3-2772c209b4cd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6140213012695312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:43:20.347409+00
24de51b9-0e68-4b8b-90fd-360b64ab3cb7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9173622131347656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:43:53.722122+00
6df387b8-7ed9-4a60-8877-98bd1bd391f3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.102375030517578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:44:27.095163+00
8243204a-7d09-495c-9362-e74907b9c81a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9469261169433594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:49:55.659807+00
24700075-11ad-4b32-a056-654e3f2cfa4b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0940303802490234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:50:29.050685+00
bf8d6973-7172-4e03-a60d-aa4f5f493adc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0606517791748047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:51:35.819153+00
b0074f52-edf2-49af-a01d-9bd31f93ceb8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7919540405273438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:53:49.404408+00
524c752b-a5ad-48df-acbd-07866f593168	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.873016357421875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:54:56.194853+00
2149ad82-fe09-4bfd-ab8b-ab21b5bd0451	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.404928207397461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:56:02.99553+00
8c017dd4-b152-4825-9b55-0600367d5cbd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0246505737304688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:57:09.766576+00
5e532167-5893-45a9-9c89-8ab19c73eb3d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9481182098388672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:57:43.153543+00
e9ad5687-578a-4a8e-b7a1-8e282ddc87e1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9664764404296875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:58:49.923512+00
73602516-0aee-4ec6-bdd9-7f2b06d7e13b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1109580993652344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:00:30.078114+00
5d246f5a-5b11-4783-afe7-178d2c56f993	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6810894012451172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:01:03.46335+00
dfcfa07d-6988-4876-8674-a0a92ee1959e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8267631530761719	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:02:10.232676+00
0fc9e92f-1979-4db2-9d11-4b02b5680cbb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9304752349853516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:02:43.619887+00
22ab6460-3841-4e1b-a30d-78c3d3b3e894	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9545555114746094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:03:16.996412+00
a5e2d8e0-6c14-4f96-a1e3-a872b423da64	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9810199737548828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:04:57.212986+00
142f8483-4d2e-4c7b-a6df-8b89716b92f1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.039670944213867	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:05:30.596225+00
ab4d59b3-1963-49d1-ad4f-8935d6e95c39	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.477407455444336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:06:04.029916+00
90fd5538-9192-4912-8c31-4a93be90d812	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.424001693725586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:07:10.81052+00
21661e1b-2a4d-4378-9fef-e6897099e014	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.588033676147461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:07:44.214189+00
e56f0742-7415-44d0-a686-623f88052ca2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8100738525390625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:09:24.370109+00
7f2bc855-fee8-41a3-b4fb-3f0575fa4212	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8634796142578125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:09:57.742747+00
c574983a-2006-4e60-8ef8-136b6dde7c6f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.783132553100586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:11:04.514159+00
7816cfab-661a-4c5c-8063-e3cfb88c7d1a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.425670623779297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:12:44.715144+00
b6f481ff-48da-4f77-9183-bce762c18071	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7981529235839844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:13:18.101899+00
a08b9620-7afa-4162-89b4-42cd034dd763	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	12.268543243408203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:14:24.909576+00
790f998f-30a9-442d-b9d8-c8085d05cfd1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9006729125976562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:16:05.041153+00
7bb6a0c1-14c5-4cc8-85be-b76cc0aeaa7f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1543502807617188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:16:38.431394+00
4e0cf593-ba7f-46ae-82f8-a374434439c5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9354820251464844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:17:45.20408+00
a5983d1d-fb43-4fdd-9110-2367eca058f5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.156972885131836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:18:18.599762+00
26f3afdb-b63f-407f-bfb6-3f8359e6a867	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0084381103515625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:42:57.718944+00
a87d8141-0e4a-4bbc-9a1c-1ca5a394c465	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.981351852416992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:44:57.998841+00
e8e1f1cb-3b6a-4142-9660-61916a0f2f09	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9690990447998047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:47:28.422921+00
204a7561-9ff5-407f-89f1-a4d927357e97	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.095388412475586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:04:21.217836+00
aa58dd2b-ed97-4e50-ba37-444452cc5ea9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.485990524291992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:05:21.508063+00
354b075b-debc-40f2-b5fd-ef6bb886da54	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3276805877685547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:06:21.784679+00
ed87a0a9-244f-40ff-831b-6b0b13aca725	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.992940902709961	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:06:51.939412+00
ec5cda72-e189-405b-87ca-cca292b85468	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6559829711914062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:07:52.206616+00
ae37fcea-76fc-41bb-a863-c0cbc933e1f9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2978782653808594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:08:22.339084+00
ce5b263b-e333-4e38-8515-389929f4c175	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7852783203125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:46:40.633375+00
fa203652-bb24-4d47-9aa4-fed4fdc00859	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0656585693359375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:47:47.400444+00
7048ccd9-917b-481e-9f16-a8350b766d63	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0780563354492188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:48:20.785656+00
7c4fc93c-5bab-48d1-9ab7-07463d17eb94	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8420219421386719	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:49:27.555696+00
1307b516-3fe1-4145-9bf6-8892704e880d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.828908920288086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:50:00.947876+00
fa5bd988-c992-4a76-a849-dfbf90154b59	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.461671829223633	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:51:07.719317+00
f1a6be1d-2139-4afd-929d-02b84583f8a5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.201080322265625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:52:47.883773+00
a094010c-a4f4-4979-8e0f-73ca766aa7df	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0132064819335938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:53:21.267544+00
e497e8e6-c56b-4b17-b15e-18ce6c051988	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9795894622802734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:54:28.053675+00
d8f9e272-8257-4009-8ec7-7b7e644dd7dc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.631664276123047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:55:34.867075+00
6a0bf941-1a0d-4bb1-940e-29c17604aa3d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.009868621826172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:56:08.243368+00
ae3b27d7-5a70-4e7c-938e-f3f4d5e0059c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4259090423583984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:56:41.637762+00
4187272a-a4a9-45ac-827b-301ce53a4a48	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8455982208251953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:57:15.01653+00
6363ad81-89d6-4f2a-b0ee-282112b52143	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.819610595703125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:57:48.39528+00
411f1ec3-892d-4b00-961e-0773ef3b1821	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0678043365478516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:58:21.779815+00
7dc11b0a-57c3-466b-8da0-3541b1172451	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8146038055419922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:58:55.167067+00
97c9f614-83f3-4f53-9140-a3cbf1a94824	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9011497497558594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:00:01.948576+00
63133d7d-e07e-4579-85c2-194586213f57	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8148422241210938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:01:42.112308+00
afd007d6-359a-4e07-b056-69139b9bf032	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.173900604248047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:03:55.68238+00
673c2944-78fe-4d2b-87f2-e94dff145f39	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8024444580078125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:05:35.858946+00
0faba87d-176b-4540-95a8-620465c90799	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4306774139404297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:06:42.658194+00
492e3724-e1e9-402b-9af1-97622a0b2312	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9237995147705078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:07:49.471355+00
aa10b3db-9cee-4663-92c2-e37f3fecbc5c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9772052764892578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:08:22.856876+00
98b3abd5-f9d9-49b7-bc76-6c205e9a34c6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9865036010742188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:10:03.005988+00
6e849746-19ff-4206-88b8-fd9c34dcd0ee	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7516613006591797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:10:36.405592+00
f22ef867-ab8c-45a2-9e66-a76f08610404	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8460750579833984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:11:09.797345+00
c79525b5-3545-4bf6-8823-9aa37d021a2c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.131938934326172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:11:43.189251+00
fa1ea60a-c329-49a1-b448-1d5131d70473	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.289295196533203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:12:16.587472+00
9c2eaca2-c0dc-4ba7-8dff-bdaaf533c139	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0380020141601562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:13:23.309738+00
1ea974ec-2fab-42c5-9428-bb43f6fadadb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2459030151367188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:13:56.737504+00
7b078425-6574-4293-82ba-0f906156bf9d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.086639404296875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:14:30.121483+00
db8303e5-3f98-4152-b95f-a110c4ba1fad	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.76239013671875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:15:03.499258+00
14499735-a0f3-43b5-8598-8496e07d5813	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9922256469726562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:16:10.274099+00
86ec7a63-5c73-46d9-8e33-2f66d5b1dc7c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9550323486328125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:54:22.805532+00
384e80f3-30c3-4126-8f27-27b380de37bf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7092227935791016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:55:29.608583+00
bbd764ae-6c9c-4a8d-8e3c-d4a1f2574a61	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.045154571533203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:07:22.066604+00
c514b57e-2f9f-4a69-8e3f-fb28b3e51c82	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2118091583251953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:09:52.801209+00
6bbe6c83-4430-47fa-a510-f9f6b3cfb4dd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5119781494140625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:10:22.931996+00
2cd3bd10-87dc-4c4f-8995-7c06a70a2806	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0186901092529297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:10:53.063634+00
316d37a1-87cd-4508-8ca2-afc90c7c83b6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.972198486328125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:11:23.193805+00
0bb79b06-45c0-4ead-b37b-cda0cc486e86	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.146482467651367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:11:53.339475+00
e140b1b8-d829-4cff-9d04-2deca4b32f46	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.555370330810547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:12:23.478493+00
0798c12d-93fc-448d-9a6e-bef05636a503	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.191305160522461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:12:53.615637+00
e5616e41-f035-4d08-9ef7-07e7b45744d1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0227432250976562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:13:23.765177+00
21dab530-8be5-4ce8-94a2-cc04a4530f2f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.505064010620117	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:13:53.911216+00
0403345c-6459-45e5-853b-8c6e20d9f655	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	13.214111328125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:14:24.096698+00
9404280b-e0fc-4ff8-9bd0-f15393542f3c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1827220916748047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:14:54.24427+00
64ca5a2e-5a85-4ef1-9007-ed348b008e7a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8085708618164062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:15:24.391072+00
bb280141-10b9-4f2f-869f-28e1851bf47c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0303726196289062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:15:54.528933+00
ce76ca02-fcf9-43e8-b5f8-c2c7ea326786	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0601749420166016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:16:24.680671+00
7e86eb38-ae7d-4050-85a1-33dd9b2aff76	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.057790756225586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:16:54.823875+00
316e0b16-13c7-4852-9c58-0ad6b62dd5e8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3453235626220703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:17:24.958155+00
45f21c2d-c4ed-44e9-8486-1c90ed85f5d3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.902984619140625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:17:55.126925+00
5ce719de-ad3b-4055-b8f8-7b8e06708ecf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5446414947509766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:18:25.316601+00
0e0b6fc7-8d34-4071-b0fb-4e63c9a616e9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.190113067626953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:18:55.472181+00
b70874ca-24be-4b56-af53-cc0f6acfedb1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.924753189086914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:19:25.611188+00
578bcb0a-987f-4f47-a070-3fa2d324bf05	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.103090286254883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:19:55.755621+00
81c8acdd-e42a-408a-a278-58008e5092f3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.202749252319336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:20:25.906518+00
eea40d66-7093-4a13-bc62-49de9a1d6474	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9278526306152344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:20:56.05886+00
667a9a7e-4e4f-4c60-8a96-73551f038be0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.971172332763672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:21:26.214295+00
7551b6af-28bc-460e-a026-97aabd3b21ba	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9330978393554688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:21:56.356039+00
b70df4ca-93c5-4d1c-a605-c464e8473564	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0973682403564453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:22:26.532172+00
cb908d79-ab81-4b88-ba54-9a857688df12	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.070903778076172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:22:56.68461+00
9cb647cc-dcda-4720-8de9-b2cddf37fae8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8777122497558594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:23:26.832143+00
5c0289de-9dfc-4450-bca3-7a5a483011de	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.09808349609375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:23:56.987879+00
36047a5b-5967-450a-b446-6b47e4d076fe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.992940902709961	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:24:27.134967+00
bdbda124-5e37-4e37-9a8c-df1e62f9e8fe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.122640609741211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:24:57.274602+00
3d8e9705-faf3-4783-9c6d-88792f1201ce	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0897388458251953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:25:27.414879+00
63072073-5f68-416f-ba9e-16cad7ab8729	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9979476928710938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:25:57.559602+00
6901f9ce-5d55-4073-bfae-cde9cd8a4877	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9021034240722656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:26:27.70738+00
ea8e82da-19e9-4c77-85a0-5e4acf72dab7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.271413803100586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:26:57.866607+00
0af7a2b5-14d3-48f5-84e6-58a13ffa146e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8906593322753906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:27:28.009269+00
0f1db336-4d32-429c-ac74-4fd31e945ddc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.049684524536133	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:27:58.146725+00
4b999231-e947-4ab5-a415-ec55902fa683	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.168416976928711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:28:28.289219+00
ac3f6c80-2319-41f3-bac4-0b6e97331b84	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.778768539428711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:28:58.441557+00
eabb8c16-2264-41cb-bf5f-d4827e97fc9f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1753311157226562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:29:28.603694+00
efeba320-b5b4-4e0d-a7b2-df95482721fa	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8799304962158203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:29:58.752446+00
4b17b7ea-ba8e-45df-81ab-5a20e29d1a9e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0952224731445312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:31:59.338935+00
f13d8ada-df0e-4739-8a34-b1a47c055066	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9614696502685547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:32:29.473552+00
6f54cb15-de50-4115-83b5-a7e6af86db79	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.075672149658203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:35:30.360311+00
5377d92b-f524-41ab-88ac-f48b0bcd47f0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9295215606689453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:36:30.670971+00
c5c71b4a-c026-4d7a-b5f7-7bb3411aa643	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.603147506713867	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:42:32.540432+00
fefa06b2-796e-4d96-a043-6f745699fc34	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.855611801147461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:50:34.940902+00
4f7d5cc1-c6bd-4c23-9d09-558b7a80a513	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1741390228271484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:55:36.616532+00
f10c035e-472c-4ae8-a320-438152ef0172	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9011497497558594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:57:07.120016+00
668df244-e7e1-4e5e-a169-28a6043886b8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9631385803222656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:58:07.450796+00
9aec25fe-e3f8-44fb-8e1a-aae05e955e12	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.656698226928711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 00:55:01.469155+00
5d7b828e-0df2-4d4e-b1d8-8b6f2acf1a81	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.466917037963867	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:00:35.339242+00
8d2aea9c-79eb-4578-aabd-a019f8281be6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7008781433105469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:01:08.724764+00
d7aeab71-cee7-4d8c-847c-1163dc4f2cc3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1219253540039062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:03:22.292951+00
3b980b32-63d4-46c9-a9ab-f5f66bc554ce	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9307136535644531	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:04:29.066137+00
958a60a0-c1c4-46a0-8d5d-6c0ac26a9ba9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9283294677734375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:08:56.234541+00
06f822e7-14d8-4c12-abbb-d4f17ce58137	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9669532775878906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:12:49.959351+00
d48ef996-848d-4472-85b0-7f15ca56c4c0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.321481704711914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:18:23.863981+00
f0c766ed-45a2-46b5-9251-6631575af4ef	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9304752349853516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:20:04.030665+00
5747f765-070d-4af5-bd7a-a4dd695b28fe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7588138580322266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:22:50.953928+00
220beac0-6865-494d-abc5-ee882766084f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8546581268310547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 04:56:36.376538+00
0362d7e9-4cd4-432c-bbea-7ab62c72c3d9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9960403442382812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:01:36.851726+00
fc234d75-f70d-4db5-ab2e-6e6c966c2d24	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.460956573486328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:08:17.605357+00
06cc1ec3-b2ff-4bdc-b0f6-b70ad1234f33	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7728805541992188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:10:31.127795+00
38de19c3-5b28-4df0-85a2-cd89e09abaad	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9431114196777344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:12:11.283372+00
457e8c20-8919-4ae9-bf18-1fe5a7eda252	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8503665924072266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:14:58.284222+00
efaa2293-77ae-42fb-93dc-77c960e11c06	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7621517181396484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:17:11.812833+00
5242ee64-abcb-4ad9-9fb4-0e2090a2e750	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0444393157958984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:22:12.321385+00
9c3ea2ca-d2e7-4f83-ac4e-5ebaa24ccad5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9764900207519531	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:45:58.160579+00
a6748c0a-bb41-4f1c-9a89-d6690874cc55	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.561330795288086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:59:30.163847+00
9e1c22bd-baba-44fc-993b-94adedc7c1f0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0012855529785156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:01:30.430746+00
6a9b8d8b-0b09-4338-9d15-86c5d408fc8b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.098560333251953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:04:30.842093+00
63331887-4eda-41e7-b526-023cfc653d86	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8727779388427734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:12:01.881113+00
04390acf-cdfa-4a42-a297-35530864fa91	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8541812896728516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:14:02.214676+00
5686af82-fba7-4432-9dff-ac133c600d9c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9931793212890625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:36:46.671686+00
84dd35bc-9d94-4bb4-b3c3-23c53c8e86b1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2809505462646484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:40:17.319349+00
03d855c9-1cc1-4ebf-b546-86cda28d379b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	13.577699661254883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:41:17.515634+00
8cf7eec6-26fe-4b11-b548-928d00b61ce4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8073787689208984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:45:18.287384+00
14e4753e-a49b-4c86-9a20-e64c8c3ec8fc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.1952857971191406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:45:48.385723+00
84b5074b-1053-4d66-9f93-b6e0dc93625f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.947164535522461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:47:48.895996+00
bded5da9-396e-452e-927b-8a177f758e3c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.073049545288086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:49:49.303808+00
97f1b0d2-b876-44b5-99db-4a943838a48f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	13.47804069519043	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:30:28.906933+00
a0930e75-4807-43e9-8927-a85e727e4333	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9259452819824219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:31:29.193438+00
be569f5e-581f-4b65-82a6-c77e476a6891	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.227306365966797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:34:30.055084+00
9d9c33ce-d5ba-4836-916b-0239ee452804	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0525455474853516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:35:00.211984+00
d7fabbb2-c8b0-4e32-bafc-c790ef4ddae5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.6678314208984375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:37:00.82514+00
7dda3634-ee55-46b5-b3c1-2baf8ea40ec2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.871274948120117	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:38:01.117256+00
7b345d0c-bb82-4c3b-99a4-4f25f8e11262	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1915435791015625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:38:31.281481+00
75a12529-a321-4696-93a5-951c537cf7cc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1979808807373047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:39:31.580716+00
73b38cbd-48b8-420b-bd75-7fa75294078f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.084970474243164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:40:01.730051+00
11cf2f33-3dd9-428b-9ab2-721d01921997	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.134084701538086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:40:31.89289+00
f2952315-e996-41ff-8ff3-de809e39598b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.7071704864501953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:41:32.196621+00
51dd1671-05fc-4c92-b496-e1c9bc0bbe72	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.615140914916992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:42:02.359261+00
9bbbb374-7636-426f-b1b1-fc8a44b7c941	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.232789993286133	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:43:02.683541+00
3031d125-1871-4370-a1b9-8d9e561adacd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0148754119873047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:43:32.829889+00
19b4c620-547b-422e-ae36-e3b4c75d70ea	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9545555114746094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:44:02.986824+00
96859464-3ec8-494e-a896-f915ef03a1d7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7261505126953125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:06:09.269762+00
af4f7f97-e91d-45f6-869b-445a5d691b7c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7690658569335938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:15:36.889622+00
c38d3cec-3bd6-40f2-8e3b-7a1f62074291	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6696453094482422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:17:17.080244+00
e703b770-ff4d-4339-981d-44587340019c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4194717407226562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:18:57.24787+00
fe67213a-adc8-4e84-b02d-e694daabca03	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2554397583007812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:21:44.180591+00
e97cf4a6-529a-4b07-985b-4f4c80b742ec	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7628669738769531	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:24:31.131114+00
cae370d1-a75a-4fed-8a61-6c601f4d6412	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7878284454345703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:04:23.827353+00
ebfde466-9064-4443-9988-9264e1b02b05	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.89971923828125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:11:37.90032+00
ef49d99c-be8a-485c-a494-051b21225d85	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8165111541748047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:18:51.984238+00
fbdbd3a1-5268-4b17-a175-9d1bc2431c7b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9276142120361328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:20:32.167696+00
aa281d27-8fa5-4983-954d-9e454a5eb09a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7969608306884766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:22:45.706606+00
5cae89b9-cfbd-4c8a-b356-4f1dd97c33fc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9075870513916016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:24:59.238848+00
1ff2e339-5bc0-4802-830a-9851336c2bee	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0034313201904297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:32:46.724905+00
78cea422-8c98-4b08-8ae6-e72bbcf54786	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2563934326171875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:46:28.282998+00
24995df4-4f3a-4ba4-9810-538cd3140abd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9996166229248047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:47:58.490498+00
eb3c8685-6548-43ef-9f13-c4673142e622	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.966714859008789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:48:58.628534+00
a85055d2-a8cc-4e40-80d0-d37cbe353664	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2649765014648438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:50:28.859124+00
4c2f3a7c-4b15-42a8-b678-a91895d67251	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6268959045410156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:50:58.923537+00
060e811e-887b-4e2d-b74e-6e0ac902c55c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2079944610595703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:52:59.214814+00
261e0176-c5ea-48ef-9db2-ae8318ba6cbc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1054744720458984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:56:59.814407+00
72277cd9-9e24-4070-a85a-ad787eb1f642	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.22015380859375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:57:29.874312+00
9b2708e8-32ad-4d60-9ec6-6115dfbe6cc8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9609928131103516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:05:30.985232+00
d5b3dbf6-811a-40c8-babd-24de31963bce	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.381563186645508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:07:31.247907+00
01ec60ee-4366-4d06-b511-adb48101fc3b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0971298217773438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:12:31.971081+00
38009363-0106-4e34-a158-7e0acb3991bb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8551349639892578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:40:47.413097+00
1e6b986b-330e-46ca-aa90-55cc615bcb3c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1088123321533203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:41:47.601136+00
fb5a784f-b2bb-4d95-9962-274dc73374ed	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2406578063964844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:30:59.043828+00
3629bd76-8a3f-4f34-a4a4-741db9ecfecf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9904842376708984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:32:59.623273+00
678295c7-dcf1-4056-ba48-835637658431	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0503997802734375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:36:00.51423+00
6acf0f40-cf87-4832-b5b2-85b4524d0b9a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.763437271118164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:46:33.762036+00
8ec93209-5b5b-401f-80d3-571676ce6f2b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8451213836669922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:07:16.073258+00
017bd1fb-63f0-4914-a545-a73b7b117552	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0210742950439453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:09:29.620106+00
80a2ac8b-122b-4bc7-9672-04ede2aa8974	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.007007598876953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:21:10.802433+00
95e9ba2a-c221-4854-8adf-239ecb82d066	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9097328186035156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:23:57.746435+00
e36ad968-7873-4a27-8490-0ed237204366	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.96075439453125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:25:04.520255+00
3436232c-d56e-4d18-845b-5b25e0bb1816	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.77655029296875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:26:44.728828+00
ead43b17-030f-482c-8373-5547111e2ec1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7397403717041016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:30:05.135955+00
1d0ed307-1dfd-4591-95f4-c1313666a793	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	5.074262619018555	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:31:11.917853+00
facb9b93-b6ea-4cb0-8fa1-d8d0c7f74e0a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0325183868408203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:36:12.480268+00
def937bd-1acc-4b8b-885a-b3984644d22f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8591880798339844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:13:51.510488+00
be6170db-5b24-44b6-8894-661909c6cd5f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.993417739868164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:15:31.65629+00
f849dcb7-086f-494c-a0b7-969033cdd9a7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8017292022705078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:19:25.366019+00
a6878e00-c557-4e79-8147-d77f0d7543e7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7516613006591797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:26:06.040412+00
a80a9854-b80a-478a-a1f8-aaecc345ba5c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1789073944091797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:27:12.806335+00
e1a740a1-d605-4e68-ab0f-67edc3cec564	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.072572708129883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:28:52.992514+00
c16b7cce-fd9c-4cdd-b1d7-be3a354cb255	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8124580383300781	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:31:06.563085+00
19502818-51c1-4dde-b525-5c34f0fb4773	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0215511322021484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:33:20.111689+00
9ff98fe7-7f9f-4ccd-a34e-6e61f5d5701c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9097328186035156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:42:14.358479+00
9ccfd269-1b9f-4da9-b297-609aa24d526e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1080970764160156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:49:28.693458+00
4828acda-fb55-4185-874b-823b54984720	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9745826721191406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:51:28.983208+00
151e4024-4674-416e-b12a-f3f442dcde20	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.175569534301758	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:51:59.049413+00
3d7f91ff-ed21-406d-a13e-5004ff7e8c6a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9989013671875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:55:59.642686+00
c9ebd36f-19f7-475b-8ee0-e4ef3dcd42cc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5594234466552734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:02:00.499635+00
c29fb72c-b228-4eff-a5fe-4c70cc160732	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0678043365478516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:06:01.055824+00
fdae6ac2-defb-48a1-a6d2-0731102e4bcd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9538402557373047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:10:31.664092+00
1c2b8856-65f5-4457-8092-7c9edd77964d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3643970489501953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:11:01.733677+00
15ce842c-ed73-4a19-84a3-265707aa4ca4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.197265625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:11:31.809054+00
b3676a16-cd00-4558-a169-4182f08eb72f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0749568939208984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:43:47.992959+00
34da2f1d-3463-4cf9-bd93-d866edd15ef0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8992424011230469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:44:48.181712+00
4659078b-49f9-4878-b2d8-eb6fdde8c07e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	6.247282028198242	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-09 01:54:52.728698+00
08348ec2-1758-4082-b6fe-2f80dc6a684e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.009868621826172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:33:29.769003+00
601b72dc-5b79-41fc-98eb-ceb57101824b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9059181213378906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:33:59.904323+00
6d05a30d-f685-4a8c-992c-3ad52a66ff3f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.591299057006836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:37:30.977814+00
f5b62e99-4655-4e70-a975-5f5358391347	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.116680145263672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:39:01.429014+00
b141170d-2b7a-496e-bcd7-6ea930b7fcc7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0399093627929688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:41:02.042053+00
0e300f19-5c29-460b-abe8-a46c1fc077eb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1736621856689453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:44:33.13723+00
c081d20c-775f-4a74-baa3-f62572689b5a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8908977508544922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:45:03.320316+00
6d88292d-1e0c-4521-bbb4-8fc6fa62d939	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.073526382446289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:45:33.475346+00
0e353e4b-f00f-4dae-a0a5-7aabafa46ba4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0856857299804688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:46:03.616083+00
417a7d7c-0d5f-4f97-a506-8f748160aa71	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2928714752197266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:47:03.913111+00
35353a89-9d13-4fc5-abfd-df18ff38f204	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3140907287597656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:47:34.048335+00
403d26c2-61a4-471e-8f1b-e38ffa98364e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1152496337890625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:48:04.181684+00
bbc3083b-2601-49fb-a393-40d8cd8163ab	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8324851989746094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:48:34.332807+00
fa781a8b-9c50-4bac-8b0f-561b0303294a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3620128631591797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:49:04.487152+00
f9531d65-6fe7-4939-88af-42344b3f49b2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.332925796508789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:49:34.638847+00
fe89721b-3708-478c-9f77-8b2b640ecaf3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7960071563720703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:50:04.795974+00
c8a093d2-183c-4504-bc1d-4b461f99e563	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1028518676757812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:51:05.132777+00
db543759-8a6f-4178-80ce-65c67453b388	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.992391586303711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:51:35.307729+00
f3f832bf-0102-4ab6-8408-24cfe883825c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.000570297241211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:52:05.463727+00
049534b9-c241-44fb-aba0-f0d5ab4c3bce	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.439737319946289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:52:35.614416+00
8bbd13c7-0175-48d2-864a-9f1fd2b6780f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.015352249145508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:53:05.800462+00
af756a51-0b51-4d60-8bd7-73f3a684fc14	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1660327911376953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:53:35.95799+00
92b0aec6-1456-46dc-82db-f904dbacd184	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9996166229248047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:54:06.113159+00
a9626ba5-51ff-4257-8e53-18820149c747	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6657581329345703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:54:36.299077+00
7e1ca36d-c1ae-4b2f-8b76-c971184a6f4e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.221822738647461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:55:06.461968+00
5fd26831-ef83-4973-a242-a78f57eea798	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.964569091796875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:56:06.788053+00
3923eff6-0abb-42c7-8bdb-06341788b746	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.291440963745117	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:56:36.969784+00
fc102493-c81e-47d2-9d2e-599f670ff862	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9717216491699219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:57:37.292478+00
3011b85a-c13c-4d0b-88cb-8ce9e7a67a54	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.671480178833008	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:58:37.612611+00
9277318f-7875-4797-8662-1b3370cc2c8c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.130270004272461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:59:07.768754+00
8ea8d547-8e82-48f7-8eb9-333783df8506	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2170543670654297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 05:59:37.932404+00
96b67d95-e714-4d9b-b826-e7b83d21fe6b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.748250961303711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:00:08.083718+00
dd00d262-f687-4026-a60f-f127eeaf7b6e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.251863479614258	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:00:38.243704+00
a3b072e1-f40c-4d75-af24-cdef31bfa91b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9729137420654297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:01:08.39862+00
2a52560f-aa04-4a23-baed-a83eb8d0f357	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1948814392089844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:01:38.602435+00
fe4b4aaf-23cd-4a9f-9bbd-f4ea36eb0f0f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.418994903564453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:02:08.754322+00
b6bfc0e9-e560-488e-a699-850829283ca6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.1223297119140625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:02:38.907701+00
164bedbf-3417-4c2e-99d4-52ea7a358672	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9381046295166016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:03:09.063364+00
fc553abd-4c18-4a0e-8626-96fd10396f11	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9483566284179688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:03:39.220063+00
f830f735-8ebb-40b4-9c01-a598514d2113	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2804737091064453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:04:09.383382+00
2eeb95b3-864c-4a41-b9c9-f509de23be44	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.1070709228515625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:04:39.542151+00
335fa804-17b9-4739-9309-53844300b452	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.001523971557617	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:05:09.699096+00
32fd3f77-40ab-479c-beb9-f93b65b70239	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2192001342773438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:05:39.862737+00
2817c075-9fd9-4ab6-809d-2857b7795e81	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3622512817382812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:06:10.015088+00
181e8547-29e0-49a9-a547-2decb37d25ca	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2792816162109375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:07:10.318231+00
26fff82c-bdb7-4cbd-a10e-7d879a402831	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8775463104248047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:08:10.65634+00
15f0c0df-f86c-42f2-a7b8-7d739d051389	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8885135650634766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:08:40.82055+00
46475208-72bb-457c-b131-74667b4102a0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0186901092529297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:09:41.135781+00
e8337fe8-621c-4db0-82f7-67c5bcb1e873	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9376277923583984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:10:41.430295+00
615e8823-bf37-43d6-a41a-7fac8150e425	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9979476928710938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:12:42.066938+00
fbd0231f-5f48-4e24-af93-1f8a29000731	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.001523971557617	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:13:12.213596+00
dd88b0a1-dfc8-4133-afb5-933369af5bbe	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2101402282714844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:14:12.552149+00
ca515640-0872-4f6e-b6fd-1898ad5bb3d2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4085044860839844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:14:42.701416+00
d163f9a3-82c2-4959-81e0-b71ea114e4bc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.212047576904297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:16:43.69273+00
e20dc8b5-923c-4b64-a1a7-d6fea228a25f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9788742065429688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:17:50.468455+00
a3ebddce-65a8-49ce-9847-cec367fa03a2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9328594207763672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:19:30.637724+00
e570290d-5a45-4333-aac7-fa402f73a083	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6510486602783203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:20:37.415333+00
c608bf47-9597-46ba-bc2f-281567368d12	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9688606262207031	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:22:17.567494+00
65d38419-ddde-4506-bcb9-adfa5ccaef9d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8813610076904297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:23:24.366035+00
a5ede5bc-2d62-4295-98c2-8ff69bbf1bf2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1452903747558594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:25:37.905986+00
683c5836-b843-4e26-ae79-e38c0f4d41dc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.327297210693359	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:27:18.125155+00
276cc1bd-079f-4273-852d-a4e142142281	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8290748596191406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:27:51.510692+00
866bd2a5-7033-4f3c-85fb-90f26da47f81	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4204254150390625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:28:24.915698+00
3bfbceba-714b-49c8-be94-cce4584d812e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0880699157714844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:28:58.293711+00
74aecef6-f44d-4252-8994-59d73afaa14a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5780200958251953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:29:31.745079+00
779e2b28-82b9-4d65-ac42-0718aceb7be5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8515586853027344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:30:38.522649+00
f236a9f8-2706-4560-8a09-5ef35882c54f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.054452896118164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:31:45.303566+00
a4ba53c0-7bcb-412f-8707-a57f731348de	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.903533935546875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:32:18.692555+00
de58da94-1602-4509-82c8-13893d06146e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7740001678466797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:32:52.100582+00
c72040f3-a76d-4a81-8725-eae790512242	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.597808837890625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:33:25.503996+00
7eae63ab-c4c2-4064-a172-1125b938f362	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8918514251708984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:35:05.683685+00
91422999-4e52-475f-ac47-0638ba33fa96	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.584789276123047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:35:39.093837+00
adbcd859-d314-4356-90e2-bea5e6249de9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.078533172607422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:36:45.883942+00
360cb701-0ffa-4777-9f38-7976ac22ab90	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9006729125976562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:37:19.267954+00
778b1d00-7819-42b1-97ee-338c9e956e37	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4008750915527344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:37:52.670775+00
99a414c7-0673-48fb-a274-3876acc04e6e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8224716186523438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:38:26.065548+00
e0644969-c74c-4836-b014-d958e0c8558d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7379989624023438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:38:59.446363+00
10cb6765-96c8-4fa4-92a1-c88e5f70bc94	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4077892303466797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:39:32.828477+00
42fbbc1f-efc7-4811-ada1-d1fc3767f8b9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.123594284057617	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:41:12.996222+00
97d13591-80b4-41c2-9da6-f4cd00af9b44	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.170013427734375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:42:53.182455+00
742d5eca-add3-44c9-af61-169159b47eae	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1979808807373047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:44:00.002549+00
b551b579-4d35-4ed7-a788-91f6ed77b7e6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.344369888305664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:44:33.390949+00
c7df4a5b-26a9-4bf8-b249-6e515484cff1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9993782043457031	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:06:40.160987+00
61f6815c-53e4-4398-9379-b71b06d312b8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	19.154071807861328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:07:40.49446+00
089e0efe-a4f9-4c8b-b7cd-f53c506a77d5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2263526916503906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:15:43.026237+00
754bfa46-e82f-49cb-8f86-40783d46b8fb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1872520446777344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:16:43.519903+00
7809f255-6efb-4d8d-a422-bce43c75e5bc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9557476043701172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:19:44.559889+00
96d4b085-3e81-4522-9fc9-7186e10efa93	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3000240325927734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:21:45.232431+00
d5e1cf66-1192-47b2-a81d-2b086b357c2e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.4646987915039062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:26:11.324741+00
4eb891c7-fca7-4d95-882b-1ffdf54f2b8f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8846988677978516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:33:58.908682+00
4391eef2-a32d-4c4d-8fff-162dda6a2087	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9788742065429688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:34:32.295401+00
10774243-fdb5-4936-b5f0-2e472b7badc4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6984214782714844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:40:06.222256+00
3f38ca9c-dafb-481d-834b-dad304bba293	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.050161361694336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:40:39.611646+00
e70356ab-09cd-486c-9794-8a4e09683ffb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8320083618164062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:41:46.37258+00
73aa0dd5-51ac-4e47-b695-b10797c9cb48	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8036365509033203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:45:06.777801+00
0f46898c-68a9-41bb-b41b-0b9906a8ac6c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.123117446899414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:50:07.356244+00
7e9563ff-589b-4818-a7b0-373c1811c817	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.315998077392578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:50:40.735899+00
af33d97d-682b-432d-a972-4e0063b79556	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.498626708984375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:54:34.445514+00
1bc25e61-65eb-49d5-9a41-b73124b50cd5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1636486053466797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:19:58.77993+00
03bd80c0-c42a-4705-a853-30668745f355	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7480850219726562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:21:05.549745+00
99b60932-a565-45f7-99fe-503bd774d2fc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9423961639404297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:21:38.939749+00
a87528bb-cbf5-4cdd-9226-d985ee7ed4af	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2089481353759766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:23:19.082877+00
89f6ce11-977f-41e2-9415-f85ea9e3e003	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7053356170654297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:23:52.470507+00
ec305bc1-3dd4-46f1-a0c6-3f86e6c6b4bc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8339157104492188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:24:25.854727+00
89c3b53e-4287-4d78-807a-413e5ffdabe5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9807815551757812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:26:39.421402+00
c34423ca-e430-42d7-aa55-844111488339	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9268989562988281	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:27:46.192964+00
cb6c6463-e944-4967-8fbe-1c053f31b4b7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5663375854492188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:29:26.37831+00
c70856bc-160b-4617-afcd-e1a81117e8fb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.25067138671875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:29:59.76299+00
e89aaea7-8b55-4f84-a16b-f5a66e6a9002	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.016305923461914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:30:33.149411+00
fcb6d9b3-a632-42de-868b-411faf46e34d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7254352569580078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:32:13.33712+00
a017b90f-ca6f-4b02-83a9-7854b53547e4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4042129516601562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:33:53.49094+00
2b799b2c-62fa-4053-a4e8-f3ec90c5aaa6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8680095672607422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:34:26.874225+00
2f2cbedd-4e26-4ca5-95d1-2c50a817c72e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9140243530273438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:35:00.259369+00
543026cc-f8c4-4cf2-92c8-bf41301114e2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8701553344726562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:35:33.64725+00
cd3d0aec-2b57-4636-823a-fa986db8fc58	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.101898193359375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:36:07.06357+00
8e03667a-9e8e-44e1-bf69-8ff129864ed8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.069234848022461	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:37:13.849934+00
876a1de0-5420-4228-a1b9-46a36c7cf837	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.148151397705078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:37:47.225491+00
737a1492-f632-4f6d-a18f-f885334abfb6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8756389617919922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:38:20.618539+00
fdc530f8-e58c-49e5-8874-8ff1e7e55268	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9502639770507812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:38:54.015335+00
7eb05d98-8421-4911-a0e8-d0bf9ea5fe8c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.912832260131836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:40:00.804118+00
aaf91726-95c0-4a52-bb8b-1cc3e48d0465	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5784969329833984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:40:34.194891+00
7b3b4018-8350-4eba-981c-670c819a43a3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8734931945800781	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:41:07.588167+00
e824f7a4-d698-4bbe-8eeb-2e05eac13a7a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8460750579833984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:41:40.971891+00
130399c7-5ac8-4b78-ab90-f10178d8ef96	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9271373748779297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:09:10.980448+00
6020c02f-9a39-433f-bb84-603426a1e106	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9309520721435547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:10:11.278987+00
1cbb4903-2f41-4a4d-a365-06686e8b83c6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2776126861572266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:11:11.590487+00
a50d0cd1-b2e3-4ae5-8960-b8150d23163f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8992424011230469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:12:11.906282+00
496b60c7-04b7-4334-8bb7-5d6f9026c96f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	13.559341430664062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:20:44.881871+00
f1ba0393-f018-4730-a818-c70141664d71	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.672050476074219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:42:19.778076+00
72d42d41-3518-4712-9f6a-be14322aa5f6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.893758773803711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:45:40.152689+00
d589e8f8-0191-42c1-a638-788a49065c45	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.394437789916992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:03:28.691715+00
9438ee34-7ca8-4bc3-9a39-08b6601616f7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9443035125732422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:25:32.65301+00
a4eed9e3-5421-453c-9ca9-fe053ab966ca	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1495819091796875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:28:19.608086+00
5b2d930d-cb27-420b-baf1-e8bf990187b4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.311229705810547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:31:39.951427+00
c476e851-41ac-4c16-b921-40d4301bd565	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6667842864990234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:36:40.463176+00
4f934c43-f361-48ee-bba0-398cbacffd48	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.834869384765625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:46:41.462378+00
b238b37f-adfb-4a41-ad88-5118a0f12171	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9528865814208984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:47:14.84837+00
717296ff-3ba3-4b70-9456-1c277a767b21	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.116680145263672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:55:02.285509+00
6e42665e-9143-4518-bb46-cd55bce3cb89	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6569366455078125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:52:29.153403+00
3dcbaf58-68b8-4f75-a58c-2a342911ff27	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7463436126708984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:53:29.284732+00
22031d01-9711-48a5-b262-f2231061ebb4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.268003463745117	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:53:59.355462+00
29553964-a4cc-4862-949d-70685377dbd2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.794981002807617	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:54:29.433694+00
0a09542c-f8ce-4900-b7a3-8df8574a1a60	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.546548843383789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:54:59.505942+00
3335301c-f5a5-4b82-b09d-099a7d0f7458	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.357959747314453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:55:29.573558+00
6d909661-082c-4c91-a7fc-740a9c4553c1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2993087768554688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:56:29.716805+00
51eff7d8-c861-4115-891f-1c21ebbdf6d9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3925304412841797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:57:59.944362+00
da99b6f8-3702-4596-9958-f3a478ac849f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1533966064453125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:58:30.045943+00
b80e3a6d-0913-47d1-9100-7a0217352f75	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.117633819580078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 07:59:00.106166+00
536c59d0-0c2a-4429-9d1d-63c706599dcc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.125978469848633	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:00:00.236454+00
2aaf5d9c-2b61-4169-a994-61193e363b6a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9831657409667969	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:00:30.303132+00
d41e6aff-b264-4981-b509-383d33a213f6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1233558654785156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:01:00.373644+00
dea0079d-5a13-4ebe-ab26-701886816d55	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2575855255126953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:02:30.568036+00
d811da57-ac01-495a-8291-9459797eb17b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.917123794555664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:03:00.63458+00
fef07207-99d3-4ac2-a966-ef5bccbfec9b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4178028106689453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:03:30.706109+00
feb23c4c-c600-4b76-9ce7-1fb3fe4559f8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.348661422729492	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:04:00.77359+00
e2ab1fae-57ae-4338-8f74-33f6d2f5f282	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.315998077392578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:05:00.914025+00
815fe707-1dd3-46b9-8b00-e51d5587aa9f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.02178955078125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:06:31.12583+00
d9c08698-2541-4838-95cb-52c4f21769c1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.149343490600586	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:07:01.190591+00
cd5bc57a-7a91-4a50-b23c-04f32eae4f8a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.344369888305664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:08:01.311757+00
37fda7d9-f394-46e4-9b43-bb3f93edf279	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1190643310546875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:08:31.376805+00
4d2d09cf-2035-4df8-8add-cce55d05f35d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9609928131103516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:09:01.448779+00
2404390b-b2af-44d4-a3ed-0b59bac993c6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0842552185058594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:09:31.518463+00
fa0de2f9-8003-4298-9b1f-8c5a06ce31f6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.007007598876953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:10:01.589861+00
d5939210-1b5b-4184-b836-2a12d4b82fc3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7723312377929688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:13:02.044212+00
aec4fd1b-3a5e-44d0-a598-3f5776c89b72	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2978782653808594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:11:41.749642+00
cfcae028-0147-43bb-88ef-217b35747ca5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2058486938476562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:13:42.406759+00
f0f847dd-3136-4146-bd03-4415cac73e9d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2246837615966797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:15:12.86258+00
252515f4-1dae-432a-8a41-8a22369dd579	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9142627716064453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:16:13.282055+00
97dddbbe-0899-48a6-9f54-8769854f73d5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8755664825439453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:17:13.687491+00
52cb401b-2bb6-4944-a9ed-022a28b06b5b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4063587188720703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:17:43.855001+00
bd8d4b0a-d1d5-469d-92cc-2392f0b26d04	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.225564956665039	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:18:14.020513+00
bc53520a-37ed-4690-b937-1db0b7b25c9f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.804994583129883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:18:44.223075+00
ee48b14e-8811-4550-8bef-d5effba4a61e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2149085998535156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:19:14.38918+00
01f6b336-d6ad-4efb-8988-30b2f2958f3a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.897573471069336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:20:14.709894+00
02996042-9ac5-4a1c-9b14-c214465db341	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.235889434814453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:21:15.048682+00
be46db3d-f64f-494f-b583-e7a610c139ea	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9550323486328125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:22:15.380825+00
e3c055a0-65f2-4fcb-a3a7-dc21b51b8ac6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3355484008789062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:22:45.522016+00
2592a73b-53f4-4c81-9d07-a3488ec9394d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9724369049072266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:23:15.68473+00
658d9b81-d348-448b-af57-8212d1d3a9ea	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	14.167308807373047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:23:45.872161+00
4276d426-483c-4cb3-9e95-68bdb9a63e62	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0232200622558594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:24:16.033408+00
c9ce28a3-fc70-4506-b76f-02416376b3c7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9116401672363281	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:24:46.194956+00
30c3ed78-8fa1-468b-b8f9-8ab62fd7bac4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.172708511352539	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:25:16.474778+00
b7ef1a36-8f1d-4a6c-b64c-8dbf7f361a98	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.178192138671875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:25:46.655865+00
c3f63d9d-e38e-4147-91fe-21acab850729	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	13.948917388916016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:26:16.820352+00
d45516d2-c2b8-4fc5-a6d9-a5523bad4189	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5968551635742188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:26:46.978249+00
cba98b9d-9527-47f0-96f2-d410098426d0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.407550811767578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:27:17.145701+00
427e8233-311d-4eda-bb49-8b6387999b07	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.103494644165039	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:27:47.311181+00
128d93f1-c922-4c40-8ae4-920536cee7f8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.923250198364258	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:28:17.518758+00
ef2d0ecc-036b-4915-a489-fd0c09b7342d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.100229263305664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:28:47.681782+00
61ec98ee-cce1-4eda-a10e-eb465dce4516	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0461082458496094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:29:17.846756+00
de087fed-f8ef-4540-bf01-fd5992df4188	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3512840270996094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:29:48.015624+00
903e1019-aed8-4152-b51d-de19e5eef543	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.521991729736328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:30:18.201963+00
eb344df5-72dc-4bf8-aebf-3dd6af753335	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9354820251464844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:30:48.361423+00
089beb49-9be5-4210-bdaf-ed776feaab80	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.292156219482422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:31:18.532807+00
3df91ed0-6d59-45dd-a556-23e7296aa3ef	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3119449615478516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:31:48.709262+00
66647401-2e22-40ee-aede-ef201630572a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2652149200439453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:32:18.88524+00
c817e8bb-12e5-4342-b4b3-6e3328caa789	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8968582153320312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:32:49.03714+00
71a69798-34bd-4415-9ffb-9bb0ae8665c5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9955635070800781	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:33:19.223848+00
81eca671-a899-4b7c-bb1d-5bb4f013ce0b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.125978469848633	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:33:49.372736+00
744ca116-618d-48cb-8c47-8f10f61d2e22	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1195411682128906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:34:19.523825+00
3f936f52-481e-435b-82c6-a65eb5fe0c00	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.987457275390625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:34:49.68118+00
f836c1d2-b8b3-4fbc-ab9a-5e21ab6300cc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.3898353576660156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:35:19.866052+00
513ed779-72cf-4158-b0d4-1730ef1a6548	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0036697387695312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:35:50.048498+00
9291ce61-829d-4014-8ee5-b61319f8f00b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8045177459716797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:36:20.210293+00
325541d6-d5ae-4df5-903a-fb8b0f3926d7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3796558380126953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:36:50.383762+00
52828168-cfab-4824-b2e0-fe93e2ab996a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.287626266479492	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:37:20.561702+00
d47b66db-049f-462c-8db3-0bc1aa1d173b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.510547637939453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:40:21.560212+00
6ee0f699-847e-4995-a1dc-c3cdf549b61f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.254962921142578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:41:52.097476+00
aea3737c-ae50-4703-a062-b46ea059c0f8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.713535308837891	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:42:52.471066+00
c72953e2-0de9-43f3-87bd-53712abbdfe2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1104812622070312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:50:55.502562+00
d5600471-0b21-44ea-b495-1076608c14ef	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.482175827026367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:52:26.078188+00
1ba93c24-6ead-408c-a026-cbcae69905ff	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.5164356231689453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:52:56.248691+00
49f39b56-54e6-4aa0-8125-06b4c566ae20	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5234222412109375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:54:57.144752+00
408e1c40-ef27-4fbe-b1d6-5e5c38d41c0a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.57110595703125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:43:26.610259+00
8d347556-dbba-4e9d-a078-e57229bf65c2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.1125545501708984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:47:20.399411+00
a454c8ba-e215-4f96-a690-9ecbafafd5d4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.133607864379883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:47:53.783411+00
47f37500-470b-4843-993c-47ac4cf71d92	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.146648406982422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:49:33.970059+00
26005e32-6e03-4f2e-89bf-c4d30a8c0bec	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4747848510742188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:55:07.843264+00
df72241c-31e9-4fd0-a26b-717a2bc0c3e9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.750396728515625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:57:54.80244+00
a82ba398-ddad-4d2c-aae3-0046a37b9e7c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8219947814941406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:59:01.574946+00
9092f76d-4cbd-4dc8-b06a-aa8a48c561de	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.063274383544922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:39:27.421976+00
5d1cb124-84ea-4447-a384-547d7e45f396	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8131732940673828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:43:21.132226+00
4ded8ec2-a288-436e-9293-cbf7bbf46622	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2246837615966797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:52:15.374042+00
5dfdce71-3a74-4ff6-abe0-603ecd6765e4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.720355987548828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:55:35.664659+00
5d435d9b-1b60-4691-aa73-e032afb54247	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2187232971191406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:01:43.045939+00
16a986ca-086f-463e-a72d-2d37c58a0224	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1948814392089844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:02:49.832309+00
ea7b903c-ec17-4d2b-b945-b3553e0a7e92	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1440982818603516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:07:50.3836+00
9c0d9999-aeff-4445-bf6f-e16903cb0dd7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1567344665527344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:13:32.135594+00
81d54f06-2e31-4dc9-b933-029cabb7fc3b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.375364303588867	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:14:32.288468+00
c6df17fc-56cc-4a95-b58d-6151ad271a42	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4933815002441406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:16:02.504693+00
7667e483-aae2-4010-9a80-dfb125d5da32	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0847320556640625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:22:33.533128+00
576c7d9c-07a1-421c-9e85-2d980fd9e28c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.521991729736328	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:24:03.786258+00
d9ad4b2c-758a-422f-8a10-2b2c54d22c5e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2025108337402344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:26:04.092571+00
8a22eab5-0d0b-442a-b43c-d9ce81d6918c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5839805603027344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:49:19.214121+00
10d1835d-9910-4bfb-9dc1-953b25a2a5a5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.0994415283203125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 10:01:53.189893+00
c03be650-86b1-4231-8450-4e8a235232df	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	10.726451873779297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-09 01:55:25.658154+00
555edd04-cbc9-4d98-9446-8b44c20ec21b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	43.39122772216797	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-09 01:55:58.74756+00
86682782-b8ad-48a2-bdab-eb34ef9b974c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	10.993480682373047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-09 01:57:37.603676+00
b7d2b539-1328-4b83-9b3f-ff3f33feeacc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0427703857421875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:37:50.721331+00
405081ca-2c39-4e30-94e2-da5c93675ef3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.053499221801758	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:38:20.887254+00
952e58c8-1adf-424b-ad6e-90aa5a64d87c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	4.530429840087891	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:38:51.058314+00
770ba4e9-26a5-4f3a-9375-d474019fafd4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.928567886352539	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:39:21.235228+00
0a64744c-4196-44ef-841a-7a3b5168aa45	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9211769104003906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:39:51.400022+00
ca1e0270-51ef-4922-a052-400c7e9eb136	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.47955322265625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:41:21.90556+00
0feb5a58-0f18-40ab-83ec-22f710e6fa24	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.8101673126220703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:42:22.275809+00
c811f894-16d3-4098-b926-40e61cfc1532	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2192001342773438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:43:22.649461+00
118edacb-b193-482e-843a-5cff106c67ce	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.955270767211914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:43:52.803416+00
7e65563c-b05b-4789-8057-f42bd5603d18	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9922256469726562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:44:53.143165+00
957277a9-f827-4984-ac13-c84c46380e78	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.201557159423828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:45:23.320893+00
17e19569-9f21-4700-a0a3-ee6c957a3cc2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9104480743408203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:45:53.493571+00
c78f7af4-85ab-4b6c-8086-b26ba8e4f984	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8548965454101562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:46:13.571512+00
9ea284ea-cb0a-4633-81e3-8fdbe52ddb18	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7322769165039062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:42:47.755789+00
5f5a202c-3173-4696-a735-ebdbcc401d55	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8563270568847656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:44:27.938501+00
d97f6952-650e-46c7-b47b-7a0c90edfa78	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7457008361816406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:45:34.704902+00
3053f89e-b406-4fb3-95fd-e6a9f3e4c13d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.932382583618164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:46:08.093084+00
72e77c40-6a91-43dc-a8cf-16ff105c5977	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0608901977539062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:48:21.621604+00
d08ab977-b0b8-49ab-8268-aec909febe7c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8668174743652344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:48:55.006272+00
b716c44f-ca88-4b25-b2b0-a73ff1363cdc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0089149475097656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:15:02.363673+00
82b8536f-2b28-4d00-89c7-209b015b5e29	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9724369049072266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:15:32.436312+00
a82da299-f069-4b1c-8c78-6cd5bacbe6af	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3741722106933594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:16:32.572859+00
c49726b9-db3c-41c8-90db-e8562732f111	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9295215606689453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:17:02.646582+00
25101d01-1275-4e04-a427-06542badc199	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9714832305908203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:17:32.739995+00
c58ffa3a-4a7f-4f52-9e0a-435cfa3933a0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3767948150634766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:18:02.813363+00
da8db5a5-de3f-4872-94e7-35ed7482a551	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3016929626464844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:18:32.888417+00
4ea66bec-1f31-4f7f-92da-9c6b39081e66	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8606185913085938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:19:02.958565+00
57e6a3e5-9824-477e-b6b9-4c4a80a0ed5c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.646207809448242	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:20:03.142439+00
81043118-f5a9-4517-b087-7c036ac7628b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9268989562988281	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:20:33.212851+00
648f73b0-8e80-4c9a-a419-9364fbd6a8f1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0487308502197266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:21:03.281258+00
509720af-4890-40b5-ae4f-8473581aa6bd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.246379852294922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:21:33.3557+00
be3ac0fc-7ff8-4ce2-b246-e8943e5f11b4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0885467529296875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:52:19.816298+00
e6ed2f75-f353-42ea-98dd-758246b7d116	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.819061279296875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:53:21.385983+00
e1bfd360-c863-46e6-b913-fc4cff38caae	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7565956115722656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:53:51.496283+00
61976a1d-ec74-4c34-a903-1b32ade3a77e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.150297164916992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:54:21.588613+00
1895c7b1-2fbd-4727-97d2-0b1adb77428a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.842426300048828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:56:21.986865+00
853b80be-5ea6-46df-9055-c2e82a0b3811	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.720355987548828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:57:22.202424+00
4f0b3f53-2b12-4dd6-82dd-b449db45e16e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0482540130615234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 10:00:22.849696+00
5f307b4e-414f-4ebe-8fb6-06b6009e3103	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1469593048095703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 10:00:52.973078+00
0e22baf6-a148-4a71-91f0-8da092dbbbde	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8529891967773438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:40:51.733048+00
5ea75d02-7a7e-48c4-97f2-5717ff20c72d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	21.620988845825195	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:51:25.703472+00
8febe568-0cc0-4929-b648-e2811a7c8d67	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9244422912597656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:51:55.908028+00
249385d5-a898-49d8-a31a-ba4656c35995	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.188444137573242	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:56:57.855895+00
dd4cadd2-00fa-4cff-8a6f-83ff78e03c2b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4979114532470703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 07:00:29.069916+00
d071b56f-116d-48e3-a767-34184388d3d6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1562576293945312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:46:47.000784+00
9a95a255-2bcb-4dab-b8d8-9c90fe71cb40	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.137422561645508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:48:27.17345+00
5fa0a595-bb89-4ab6-9799-1ac9ced3d647	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.108335494995117	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:49:00.587703+00
13edb101-1716-423a-bf04-393919dfe7a5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.043008804321289	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:51:14.125665+00
f1a39dc1-092f-4da4-8950-30077968447a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.9706954956054688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:51:47.525891+00
8e16c549-b734-4d7e-9376-1a88d1d797ad	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.684354782104492	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:52:20.916456+00
6b81bd6c-a780-4be5-b6c5-dd23b97d3870	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.039194107055664	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:52:54.304331+00
95789eb4-d860-4022-b3b2-a39504979577	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.316713333129883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:53:27.68836+00
a7bbab1c-88b4-4884-b83b-27463a15da41	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7507076263427734	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:54:01.072971+00
4143be8f-d822-4614-bf28-3eca643af144	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9609928131103516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:55:41.227547+00
0c99010a-165a-41ed-bbd8-a123a618add3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9125938415527344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:56:14.619365+00
d40f5393-05a1-41a2-ad1d-985cf0abe2b0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.888275146484375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:56:48.004275+00
51f6dbbe-5a39-4ffa-b485-544ea75d09d4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6846656799316406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:57:21.421454+00
1365968e-baf6-4702-b37a-80531cfea5b1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9595623016357422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:58:28.190202+00
b51331a4-4939-4de6-8dea-ef652f9e15bd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.079010009765625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 01:59:34.960981+00
48340632-9105-4154-b980-0b476ec2bbab	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4483203887939453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:00:08.348607+00
5084e67b-2852-4192-89b8-88a53d12b9f9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.959085464477539	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:00:41.734105+00
d25869e8-6b1d-4e52-93a3-3f1739093fd4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8258094787597656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:01:15.11995+00
31162e11-3fd8-4131-94cd-5a030b2a8fb5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.019643783569336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:02:21.921252+00
bef5aae4-bf52-4cdf-8fcc-4617801658a1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.695394515991211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:02:55.304071+00
2e7a3e1e-cd22-4e2a-8ef7-f9460bd5ac0d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.804994583129883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:43:54.542479+00
b95d04bd-c3b4-4b3a-a091-49070c941249	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.071380615234375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:45:01.320903+00
cf89cf2e-39e2-46f2-991f-c8defc13a7cb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8849372863769531	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:47:48.247961+00
2d0cc241-1b9f-4744-b5c1-a20300dada8a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.943349838256836	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:49:28.434042+00
3ba7ef8d-7a9c-4b6c-9a26-61dca9b9ae00	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4640560150146484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:50:01.822727+00
73594c51-6f8c-4da6-bbc4-5378f41a68b2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7900466918945312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:51:08.622039+00
cb17d7be-ce61-477e-804e-3872ad3a1cbd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9810199737548828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:52:48.749408+00
f0fc5355-ac95-4d9b-ac87-805fc76151fc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.038644790649414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:53:55.520108+00
bca8bc53-34e3-4ff6-9edf-697d0af865dd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7163753509521484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:54:28.901735+00
6e6bb997-f651-4fb1-b4d3-58cf4fac7c7c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8308162689208984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:56:09.066321+00
eb6c328c-5827-49c1-a44f-69eaa9ed826d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1479129791259766	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:57:49.279966+00
0d7b8bd2-6284-4d65-a7fc-66aa194701b1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3660659790039062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:58:56.106308+00
b3f1bb9e-4e25-4b0f-87a1-89e117ffdc8e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.434968948364258	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:59:29.507035+00
6baa3359-2126-45bd-aa23-03d6eee52e96	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.458810806274414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:00:36.268+00
44324791-bc4c-4ea9-95f6-935d8d9918ec	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1982192993164062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:01:09.660098+00
3fd0b5b8-a0f4-4819-894a-64c194a3e234	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.939535140991211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:02:16.435243+00
a2c8b92c-42b5-49f9-9573-44c3b9f456a9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.3676624298095703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:44:22.972819+00
db39e1ba-3afd-49df-9438-de94c311dd2d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.071857452392578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:46:23.705515+00
0425f8c8-7786-4874-bb8a-a382d82381af	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.290010452270508	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:46:53.878067+00
d03680ff-f478-47a7-b30e-9625dd1e2950	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.299785614013672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:47:24.049159+00
e33699a4-ba4a-4e83-a95b-86fb084737e5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.184152603149414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:47:54.213851+00
1af6fc61-042c-468e-873b-0ed76b9698b0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8377304077148438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:48:24.858374+00
74edbce6-724a-4ca6-aac5-13b9b32ab1c5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9233226776123047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:48:54.819024+00
85ee760a-41e7-4042-a40b-34e6c97d0fc8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.0965805053710938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:49:24.991016+00
ebe86e51-6155-4baa-bb34-636f9b16f11e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9235610961914062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:49:55.165998+00
8346ce30-267a-4836-a369-52d44eff46b6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1653175354003906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:50:25.339716+00
eead9396-e2cf-400f-bbb2-fb69b556296d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0651817321777344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:53:26.424686+00
f3803396-26e1-431c-8325-416bec40b5e9	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5925636291503906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:53:56.601743+00
f560ef89-78d8-4386-b752-64b910117af1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.723217010498047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:54:27.018992+00
ff7da45c-db8b-4f87-bdf8-00ce933e9718	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0775794982910156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:55:27.317629+00
d874c963-9db7-45ae-807c-a0fdb5a0343f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1538734436035156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:55:57.516151+00
e3ce66e5-ee85-4180-979d-9cc56e9c5fac	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3674964904785156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:56:27.685118+00
78bb8ca0-46cc-4507-80f1-a9c90a1a7f47	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.025531768798828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:57:28.020545+00
27f92148-0136-42c8-9f85-2ce7ae67f7cc	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.0260086059570312	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:57:58.182108+00
52fa30be-94ab-45f9-a8a1-5e0667dbfcd3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8679370880126953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:58:28.360146+00
4c90f12a-85b7-40ea-8fff-3427209acc26	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.180814743041992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:58:58.535506+00
ab53878e-0571-4d9c-9d99-6fa378058555	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.047300338745117	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:59:28.712184+00
00bceb1e-c711-4a5b-81ec-fc07b97f3685	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2809505462646484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 06:59:58.894268+00
aa61e7ec-09f5-41e9-ab4a-d8f23d45816e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1028518676757812	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 07:00:59.232715+00
8a404adc-df36-46ed-83a2-ddb9e05a33d0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3949146270751953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 07:01:29.507714+00
b2a4e70c-1ede-49f2-b898-6144c2e29a7e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1407604217529297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 07:01:59.679507+00
519ddbe9-20cc-4c11-ab26-3f467d8d3043	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.185344696044922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 07:02:29.855223+00
26f65036-435a-4504-998a-37a3131125eb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	51.767587661743164	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:43:15.902661+00
075cee2a-4b4b-4a01-a548-1454c359e922	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	10.881185531616211	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:43:47.84219+00
dfcf9900-6368-45d6-8e49-bf45c230c2e4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	24.645090103149414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:44:20.74566+00
4858285b-704d-4bdb-814f-f614b0f34a79	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	13.783693313598633	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:44:53.584099+00
466f5fd4-dbeb-4d7c-b2d6-febc2250c69e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8489360809326172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:45:26.360052+00
5106f60b-25d3-40c0-8e39-354f9194a465	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	12.792110443115234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:45:59.179622+00
5c2d7e00-17e2-45d6-ad39-a4ac87741c0c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0079612731933594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:46:31.957728+00
abddc4e9-ed39-4cd0-91e7-ddbe0e344cd1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.025127410888672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:47:04.738065+00
eaa0b58b-bbd5-45ba-8299-69eb3882800b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8870830535888672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:47:37.519278+00
f0284dff-dcfc-4661-a190-b04b4aade8b6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	12.789487838745117	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:48:10.316348+00
36cb23d7-e6de-4c89-9cdf-ebac11c85744	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8322467803955078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:48:43.102815+00
295fa006-fcf7-48f0-a687-e55c14ce8a2c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.026796340942383	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:49:15.87903+00
c9c79a16-d27b-4df7-ac48-9d62120328ef	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6865005493164062	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:49:48.668291+00
e6d9e1d0-2394-4935-86a2-fdad0c31f62a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.294301986694336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:50:21.443238+00
d15914f6-1786-4158-828d-2a27f1fe41f1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3055076599121094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:50:54.231736+00
9042f0e5-ec40-4692-b8c5-66c8d3321c9e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	13.077259063720703	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:51:27.010145+00
b85a0817-ceaa-4fc3-92ec-b9e0ebf1c348	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.133607864379883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:57:30.891357+00
a7ce37e8-b4fc-44dc-800c-3c49fbb01809	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3708343505859375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:58:37.639667+00
b17f8c9b-3af1-455b-a8f3-99930140da94	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0020008087158203	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:59:44.396363+00
c27d58e8-899c-4548-8518-8b8f39cdac01	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.676321029663086	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:04:11.48113+00
86ed6f82-aad0-4ece-a4c2-3302eb541130	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7459392547607422	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:07:31.788855+00
dac855b9-4650-45e3-96bd-1026e07a76a1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3589134216308594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:01:48.532995+00
13d2777f-f8dc-4d2a-ad54-7b875fec339b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.796722412109375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:50:35.234147+00
7ef26d18-8ba3-4cd7-85c8-e351b8092066	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.74713134765625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:51:41.996335+00
cb3691bb-fa92-45cb-9cd7-b7879808570a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7840862274169922	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:53:22.134935+00
d89c1430-9cd9-4321-9f39-1295bc08e2ac	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8877983093261719	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:56:42.443166+00
f2f46744-3f7b-4864-9c97-9a679de63649	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7494430541992188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:57:15.889472+00
a9a0269a-1e3c-4215-ae38-72699d527c5e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1162033081054688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:00:02.890987+00
8867d51e-49e7-4ff0-9d47-2e8c0b525dba	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6674995422363281	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:03:23.216283+00
490448e4-97fb-4822-8bb1-816bb56c9433	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	12.941122055053711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:06:10.228646+00
07f1a350-8f68-415c-9b85-57f09deb0fe6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7757415771484375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:06:43.61312+00
9af15a4d-d141-4960-abef-4984e319f0d0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7132759094238281	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:07:16.995326+00
c7603781-cc51-4a9b-a11a-390666760bc4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8184185028076172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:09:30.544494+00
df28d764-0810-435c-b9da-63c5f8720660	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9145011901855469	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:10:03.919149+00
03a3a9b6-442d-4a3d-b28f-eb9ae3ad996f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7559528350830078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:11:10.689776+00
1427cd1e-a17c-4577-9b95-ac65c958ce15	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0360946655273438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:12:50.894335+00
154d1d18-6e74-43ad-8243-656b533e7d7a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9536018371582031	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:13:57.65458+00
5b7e14ff-09bf-48ce-b011-57abfd740ba0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1643638610839844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:15:04.484772+00
12e1dd2a-383e-44cf-8f2c-731efc52d092	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0215511322021484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:19:33.061992+00
5ab99903-04fb-4603-b56c-42fa32285082	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4878978729248047	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:28:34.494767+00
61825285-281b-4f55-9382-ca14bd852058	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5365352630615234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:54:51.706501+00
38df04b0-ab7a-4d2f-ac45-e8301a07d655	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7532577514648438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:55:21.804135+00
1cf59e95-f4fc-4be0-a977-1067e4b39baa	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.970529556274414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:55:51.899238+00
d63e8084-9ceb-4d49-ba02-ad5a994304f6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.029346466064453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:56:52.1042+00
a2e6af12-0af7-4a6d-839f-b8fba86db65a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.5827884674072266	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:57:52.288234+00
8c43c80b-327c-4766-ae0b-168854db6c7b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2068023681640625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:58:22.389829+00
a8479e67-8829-4f7d-9214-e0b5c09ddd3f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0508766174316406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:58:52.509414+00
dc53faa3-0868-4026-97bc-f33bd37ffbbd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0825862884521484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:59:22.644301+00
dcc20bbf-4f20-43b4-b2a7-755310a122cd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6395320892333984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 09:59:52.751178+00
d3cbfb7c-1e9e-4ca2-babf-6b106e8990eb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.019166946411133	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 10:02:23.284796+00
1ed5fbdf-f181-4d3a-8214-c39b743c2bc6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.894235610961914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:51:59.780193+00
c4ebad57-c24e-4e74-ad2f-d9b2240da044	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7979145050048828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:53:38.10867+00
c807b866-fe46-4382-90db-5381258952eb	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7895698547363281	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:54:10.877692+00
39d5fed4-c4b0-4835-8cf9-b2aadaeffc20	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.110719680786133	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:54:43.951013+00
4c202b48-81c2-4903-85e5-50bfa9cb32ba	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	5.690336227416992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:55:17.340695+00
f67a3918-8873-4123-94e6-aa9a8115aa66	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0313262939453125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:56:57.503398+00
a8505f53-eacb-4207-b868-62c82def7f74	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.718282699584961	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:58:04.265122+00
0891eec7-8228-4c51-b6ed-5ea554da3531	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.001047134399414	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:00:17.772066+00
b4b9ad6b-014c-45cb-b892-285b67956780	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8339157104492188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:00:51.162211+00
1ec3371b-5714-413b-b68f-3f8784f733d5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7718544006347656	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:01:57.945176+00
d528a132-bcbe-44f0-9e25-260beb7b9cfd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8661022186279297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:02:31.334785+00
3504eb83-66a7-47ef-a0ef-f6548ab5e11b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9636154174804688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:03:04.719768+00
40464288-add6-4919-bc24-d4c255baeac1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8477439880371094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:03:38.10434+00
7d825741-088d-4fe8-a505-6b2a75e0b606	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2187232971191406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:04:44.866101+00
f5bf6b4f-3ceb-457d-ab21-d85d8a15faf2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8551349639892578	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:05:51.630762+00
b1dbb9b5-7d75-499c-8cf3-01851b518e1e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7421245574951172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:06:25.019841+00
674092ae-cd86-4f75-a771-201a249afc2e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.987457275390625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:06:58.406787+00
8ea58c00-a499-4ed8-a11c-f96e8460d770	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7528533935546875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:04:02.078337+00
69343c7e-df14-4e5d-8865-a9a560284a7c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.180265426635742	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:08:29.189276+00
39f6255e-1b59-426b-a42c-b44a8c26f6bf	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.644134521484375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 05:58:22.687861+00
9c8e4322-eda8-4c8c-9ffb-4668a0de718a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.048492431640625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:05:03.385469+00
1beed553-6025-4874-b458-c6a1cbad6b07	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.6770362854003906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:08:57.153002+00
49fb7257-d027-4ff8-a4dd-6e08fedba37c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8138885498046875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:13:24.268419+00
dd6b9c0a-9417-4edc-89fe-cb5fd5975680	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8475055694580078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:22:03.456383+00
5fd5d57c-29a4-4d8b-b5ae-dce00f65a426	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.6178359985351562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:24:33.880856+00
2080ac72-53f3-463c-be01-b20eb360a4af	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.168893814086914	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:25:03.951381+00
e6e9db47-e3c2-4bee-bf0d-01010558f9aa	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.85284423828125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 19:01:10.771273+00
031e5e60-9e39-47f5-abe5-9f6dd383882e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	461.43174171447754	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 22:03:59.069522+00
7fcba369-c1c2-41ad-bb73-a2806a28dfff	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.219676971435547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:52:32.566229+00
0a59883f-cc39-474a-b146-9f0de86372e5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.084016799926758	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:55:50.73184+00
133c79c1-c886-4f57-bd75-6e3465de40ae	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7828941345214844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:59:11.022118+00
6ed0de11-857c-4df1-9b60-91f51b509e19	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8143653869628906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:01:24.546358+00
1b21fd55-a8ba-42da-a6df-94c913090013	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8267631530761719	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:04:35.467094+00
1241930b-3560-407e-bbe0-256993fd7e0a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.7114620208740234	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:07:55.804582+00
4ff085ce-9f5d-4efe-a39a-6c7d8ec130f2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0165443420410156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:11:16.111145+00
13e84814-061c-4440-be30-b05c85a4a5ea	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7991065979003906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:17:56.847287+00
5ee8e0ad-e5c1-4ad1-ad31-d81352c050cd	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8815269470214844	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:25:10.92278+00
24d9724d-90cb-416d-97a2-4b576bb45275	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9869804382324219	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:30:11.49837+00
5cf42280-c959-400b-98b9-fbc34220bc66	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.537250518798828	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:31:18.28697+00
4e1934ad-58f9-4c3a-82fd-e0f9bd2733a7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.266407012939453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:03:56.605889+00
4e3a31e8-d248-4d56-942f-d7aec8b8587e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8668174743652344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:04:29.995889+00
69977222-ef33-437f-b5c9-eaa26c6ea8db	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8720626831054688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:05:36.769393+00
4fb0b810-533b-4dc7-904e-2ad3b43895a1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.324819564819336	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:08:23.767887+00
0de401f4-63ec-4e72-9f7c-653612844e75	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	12.217998504638672	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:10:37.314513+00
2111e2dc-b663-4d20-ba3d-20e754e98fe4	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1200180053710938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:12:17.522414+00
0a7282ad-8233-467b-bd82-e4565723f6a2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.8917789459228516	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:23:03.663583+00
fd0ce591-42ad-47ba-8c77-9546b2dc7dc8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2649765014648438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:23:33.727531+00
131a7c4c-d29c-4e3f-9166-6e65f882003d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9085407257080078	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:25:34.01737+00
7e821379-3ae8-4bc0-99a0-1dd843a0ebce	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0055770874023438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:26:34.167501+00
cb0e345c-e2da-4601-ad24-7bafa960f66d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.7923583984375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:27:04.263832+00
28aa1a35-68cf-461c-8cb2-f38ed4cdece0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0389556884765625	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:27:34.343412+00
b5462d28-9f40-43d2-8c1f-6d0f6ea808e2	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.096891403198242	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:28:04.417066+00
8d53691d-a7a8-488b-b782-81d0a13f307a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.020597457885742	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:29:04.576659+00
248c1264-8b4e-488a-b7c4-bd384189b6e6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	3.0999183654785156	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:29:34.682485+00
56faa453-6dcc-4d75-a444-e1f0e613afad	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	13.196468353271484	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:30:04.823677+00
5eff61a1-89c9-4e1e-b195-1063ce9db3d5	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2128.1256675720215	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 22:04:00.515154+00
8c3f1cbf-ff90-4107-a8e9-b10272807da7	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9216537475585938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:53:05.341595+00
05e3b2b5-578f-4124-991f-7c15af6ef8a1	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8227100372314453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 21:56:24.118679+00
0d70c492-949a-4f0c-9318-c5158639490c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9228458404541016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:05:18.251685+00
ca3267d2-4e10-430b-b863-d6e668a625a6	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.8749237060546875	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-07 22:08:05.175501+00
e22b59b0-574a-45d8-86f5-828b5ef8746b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.7919540405273438	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:05:08.853463+00
fbc4e1c5-f195-468a-a22b-e67e7d2d254f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.3734569549560547	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:06:15.622684+00
1d717dde-21b1-4982-871c-e5ee56775380	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0661354064941406	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:07:22.387259+00
0c5b0556-dd73-47dd-82a7-82eb9424ed83	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9955635070800781	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:10:09.338172+00
8b3e9bf3-1f2b-43e1-9414-ec04b4ac376c	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.063751220703125	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:11:49.4961+00
01574745-845f-4a6b-8fdb-a4802f2b9a8a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.604246139526367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 02:12:56.272446+00
ffdbeace-0d9c-4d60-afc2-4bbb4800d7e8	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	12.36271858215332	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 06:11:44.109184+00
dfb5b42a-f3d6-47c6-bb33-c060c564d826	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.900838851928711	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:30:34.94321+00
510576fa-8802-463c-98ab-c4b544eb91ba	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.873659133911133	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:31:05.070958+00
17a8aaf6-a5ad-44e6-aa3e-241c8581c5ce	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4111270904541016	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:32:05.24148+00
6deed96d-7ade-4bec-b8ef-9dae52969773	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0627975463867188	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:33:05.398522+00
cbec850e-1fca-4ed4-92a3-f9f15f821e46	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1805763244628906	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:33:35.48788+00
51b9840c-ba76-4eb5-b759-d3e825c6d6ac	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.4261474609375	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:34:35.640376+00
ab6f2867-3c85-4baf-829e-212f678c3dae	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0155906677246094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:35:05.726225+00
2469f8f3-fe70-47a9-9e50-259307ebef20	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2275447845458984	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:35:35.804609+00
b6d3a5ad-46e5-4169-9e25-3c1acaa1b64e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.042055130004883	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:36:05.882796+00
a1ce3327-e974-42e9-b600-6a78023fe46e	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.238035202026367	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:38:06.23267+00
8d4aa193-8ba3-4ba4-a23b-fa7aae427f65	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.797365188598633	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:40:06.578288+00
9fc96e1a-a5cd-445a-91f1-2b0d04defa9d	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.241849899291992	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:41:36.82277+00
40a5fb65-b3b1-4a6b-8b16-af1105a3a44a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.541065216064453	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:43:07.06141+00
8c337d33-e9dd-4105-ba53-4239f6b73e36	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2363662719726562	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:43:37.138764+00
fbdac357-37be-4c92-b7a4-915d71e3d854	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0797252655029297	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:44:07.211567+00
f8b795f7-c952-4f92-85f3-c132632a8be0	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.0134449005126953	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:44:37.288762+00
32e175d8-2a1c-4820-92ac-7dc7c9a8786f	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.241373062133789	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:45:07.35808+00
7ffe4c47-4a9f-4bb2-b869-0f1c8cbfbbee	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9316673278808594	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:46:07.510051+00
e27eed66-26c4-4a47-8d8e-7c50b054a400	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9369125366210938	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:47:07.805335+00
5a349bb9-f60f-490b-bb96-b926e5e36e0a	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.803325653076172	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:48:38.062192+00
16882d16-0c8b-4dc3-bca5-ac564c6b7e85	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	1.9888877868652344	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:49:38.232125+00
e43c7451-6c7f-4cc4-bb32-76eb87cd1f1b	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.1924972534179688	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:51:08.485522+00
3b1ec1ad-2712-4906-adc4-49d15ef1b7da	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.328157424926758	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:52:08.623203+00
ff2951c1-7a95-4515-8d7f-c4d8fdcd48e3	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	2.2139549255371094	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 08:52:38.704122+00
ddc92d87-7877-4590-b6b1-1b9cdfd7a010	\N	get_request	general	GET request to /robots.txt	/robots.txt	GET	200	489.154577255249	127.0.0.1	curl/7.88.1	[no_request_id]	null	null	null	\N	\N	2026-04-08 22:04:00.491477+00
\.


--
-- Data for Name: user_interview_responses; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_interview_responses (id, user_id, interview_id, json_response, completed_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: user_transactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_transactions (id, user_account_id, transaction_type, amount, balance_after, description, ai_cost_log_id, credit_package_id, payment_reference, transaction_metadata, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, username, email, hashed_password, display_name, auth_provider, provider_id, provider_data, profile_picture_url, is_active, is_admin, interview_data, bonus1, bonus2, bonus3, bonus4, bonus5, bonus6, bonus7, bonus8, bonus9, bonus10, referred_by_user_id, referral_count, reset_token, reset_token_expires, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: world_collaborators; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.world_collaborators (id, world_id, user_id, role, status, invited_by_user_id, invited_at, joined_at, permissions, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: world_roles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.world_roles (id, name, description, world_id, created_by_user_id, is_predefined, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: worlds; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.worlds (id, name, description, short_description, world_builder_data, user_id, image_prompt_definition, image_blob_path, current_image_id, is_free_chat_enabled, is_shadow, created_at, updated_at) FROM stdin;
\.


--
-- Name: act_character_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.act_character_associations_id_seq', 1, false);


--
-- Name: act_location_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.act_location_associations_id_seq', 1, false);


--
-- Name: act_lore_item_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.act_lore_item_associations_id_seq', 1, false);


--
-- Name: acts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.acts_id_seq', 1, false);


--
-- Name: ai_call_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ai_call_logs_id_seq', 1, false);


--
-- Name: ai_model_configurations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ai_model_configurations_id_seq', 1, false);


--
-- Name: anonymous_user_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.anonymous_user_sessions_id_seq', 1, false);


--
-- Name: blog_analytics_summary_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.blog_analytics_summary_id_seq', 1, false);


--
-- Name: blog_author_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.blog_author_profiles_id_seq', 1, false);


--
-- Name: blog_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.blog_categories_id_seq', 1, false);


--
-- Name: blog_comments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.blog_comments_id_seq', 1, false);


--
-- Name: blog_content_links_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.blog_content_links_id_seq', 1, false);


--
-- Name: blog_follows_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.blog_follows_id_seq', 1, false);


--
-- Name: blog_likes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.blog_likes_id_seq', 1, false);


--
-- Name: blog_post_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.blog_post_associations_id_seq', 1, false);


--
-- Name: blog_post_tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.blog_post_tags_id_seq', 1, false);


--
-- Name: blog_posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.blog_posts_id_seq', 1, false);


--
-- Name: blog_subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.blog_subscriptions_id_seq', 1, false);


--
-- Name: blog_tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.blog_tags_id_seq', 1, false);


--
-- Name: blog_views_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.blog_views_id_seq', 1, false);


--
-- Name: brainstorm_favorites_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.brainstorm_favorites_id_seq', 1, false);


--
-- Name: brainstorm_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.brainstorm_sessions_id_seq', 1, false);


--
-- Name: brainstorm_stories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.brainstorm_stories_id_seq', 1, false);


--
-- Name: care_circle_families_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.care_circle_families_id_seq', 1, false);


--
-- Name: care_circle_family_memberships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.care_circle_family_memberships_id_seq', 1, false);


--
-- Name: care_circle_patient_content_cards_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.care_circle_patient_content_cards_id_seq', 1, false);


--
-- Name: care_circle_patient_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.care_circle_patient_profiles_id_seq', 1, false);


--
-- Name: care_circle_provider_catalog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.care_circle_provider_catalog_id_seq', 32, true);


--
-- Name: care_circle_provider_patient_configs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.care_circle_provider_patient_configs_id_seq', 1, false);


--
-- Name: care_circle_provider_run_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.care_circle_provider_run_logs_id_seq', 1, false);


--
-- Name: care_circle_provider_session_outputs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.care_circle_provider_session_outputs_id_seq', 1, false);


--
-- Name: characters_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.characters_id_seq', 1, false);


--
-- Name: chat_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.chat_messages_id_seq', 1, false);


--
-- Name: chat_samples_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.chat_samples_id_seq', 1, false);


--
-- Name: chat_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.chat_sessions_id_seq', 1, false);


--
-- Name: credit_packages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.credit_packages_id_seq', 1, false);


--
-- Name: cta_contents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.cta_contents_id_seq', 1, false);


--
-- Name: forum_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.forum_categories_id_seq', 1, false);


--
-- Name: forum_posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.forum_posts_id_seq', 1, false);


--
-- Name: forum_subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.forum_subscriptions_id_seq', 1, false);


--
-- Name: forum_threads_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.forum_threads_id_seq', 1, false);


--
-- Name: forum_votes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.forum_votes_id_seq', 1, false);


--
-- Name: generated_images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.generated_images_id_seq', 1, false);


--
-- Name: job_statuses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.job_statuses_id_seq', 1, false);


--
-- Name: locations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.locations_id_seq', 1, false);


--
-- Name: lore_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.lore_items_id_seq', 1, false);


--
-- Name: prompts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.prompts_id_seq', 1, false);


--
-- Name: published_stories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.published_stories_id_seq', 1, false);


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.refresh_tokens_id_seq', 1, false);


--
-- Name: scene_character_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.scene_character_associations_id_seq', 1, false);


--
-- Name: scene_location_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.scene_location_associations_id_seq', 1, false);


--
-- Name: scene_lore_item_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.scene_lore_item_associations_id_seq', 1, false);


--
-- Name: scenes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.scenes_id_seq', 1, false);


--
-- Name: stories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.stories_id_seq', 1, false);


--
-- Name: story_character_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.story_character_associations_id_seq', 1, false);


--
-- Name: story_chat_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.story_chat_messages_id_seq', 1, false);


--
-- Name: story_chat_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.story_chat_sessions_id_seq', 1, false);


--
-- Name: story_classes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.story_classes_id_seq', 1, false);


--
-- Name: story_comments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.story_comments_id_seq', 1, false);


--
-- Name: story_location_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.story_location_associations_id_seq', 1, false);


--
-- Name: story_lore_item_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.story_lore_item_associations_id_seq', 1, false);


--
-- Name: story_ratings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.story_ratings_id_seq', 1, false);


--
-- Name: storytelling_act_character_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_act_character_associations_id_seq', 1, false);


--
-- Name: storytelling_act_location_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_act_location_associations_id_seq', 1, false);


--
-- Name: storytelling_act_lore_item_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_act_lore_item_associations_id_seq', 1, false);


--
-- Name: storytelling_acts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_acts_id_seq', 1, false);


--
-- Name: storytelling_brainstorm_favorites_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_brainstorm_favorites_id_seq', 1, false);


--
-- Name: storytelling_brainstorm_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_brainstorm_sessions_id_seq', 1, false);


--
-- Name: storytelling_brainstorm_stories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_brainstorm_stories_id_seq', 1, false);


--
-- Name: storytelling_characters_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_characters_id_seq', 1, false);


--
-- Name: storytelling_locations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_locations_id_seq', 1, false);


--
-- Name: storytelling_lore_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_lore_items_id_seq', 1, false);


--
-- Name: storytelling_published_stories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_published_stories_id_seq', 1, false);


--
-- Name: storytelling_scene_character_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_scene_character_associations_id_seq', 1, false);


--
-- Name: storytelling_scene_location_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_scene_location_associations_id_seq', 1, false);


--
-- Name: storytelling_scene_lore_item_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_scene_lore_item_associations_id_seq', 1, false);


--
-- Name: storytelling_scenes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_scenes_id_seq', 1, false);


--
-- Name: storytelling_stories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_stories_id_seq', 1, false);


--
-- Name: storytelling_story_character_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_story_character_associations_id_seq', 1, false);


--
-- Name: storytelling_story_chat_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_story_chat_messages_id_seq', 1, false);


--
-- Name: storytelling_story_chat_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_story_chat_sessions_id_seq', 1, false);


--
-- Name: storytelling_story_classes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_story_classes_id_seq', 1, false);


--
-- Name: storytelling_story_comments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_story_comments_id_seq', 1, false);


--
-- Name: storytelling_story_location_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_story_location_associations_id_seq', 1, false);


--
-- Name: storytelling_story_lore_item_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_story_lore_item_associations_id_seq', 1, false);


--
-- Name: storytelling_story_ratings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_story_ratings_id_seq', 1, false);


--
-- Name: storytelling_user_interview_responses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_user_interview_responses_id_seq', 1, false);


--
-- Name: storytelling_world_collaborators_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_world_collaborators_id_seq', 1, false);


--
-- Name: storytelling_world_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_world_roles_id_seq', 1, false);


--
-- Name: storytelling_worlds_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.storytelling_worlds_id_seq', 1, false);


--
-- Name: uploaded_documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.uploaded_documents_id_seq', 1, false);


--
-- Name: user_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_accounts_id_seq', 1, false);


--
-- Name: user_interview_responses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_interview_responses_id_seq', 1, false);


--
-- Name: user_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_transactions_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: world_collaborators_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.world_collaborators_id_seq', 1, false);


--
-- Name: world_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.world_roles_id_seq', 1, false);


--
-- Name: worlds_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.worlds_id_seq', 1, false);


--
-- Name: scenes _act_scene_number_uc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scenes
    ADD CONSTRAINT _act_scene_number_uc UNIQUE (act_id, scene_number);


--
-- Name: acts _story_act_number_uc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.acts
    ADD CONSTRAINT _story_act_number_uc UNIQUE (story_id, act_number);


--
-- Name: act_character_associations act_character_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.act_character_associations
    ADD CONSTRAINT act_character_associations_pkey PRIMARY KEY (id);


--
-- Name: act_location_associations act_location_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.act_location_associations
    ADD CONSTRAINT act_location_associations_pkey PRIMARY KEY (id);


--
-- Name: act_lore_item_associations act_lore_item_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.act_lore_item_associations
    ADD CONSTRAINT act_lore_item_associations_pkey PRIMARY KEY (id);


--
-- Name: acts acts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.acts
    ADD CONSTRAINT acts_pkey PRIMARY KEY (id);


--
-- Name: ai_call_logs ai_call_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_call_logs
    ADD CONSTRAINT ai_call_logs_pkey PRIMARY KEY (id);


--
-- Name: ai_model_configurations ai_model_configurations_display_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_model_configurations
    ADD CONSTRAINT ai_model_configurations_display_name_key UNIQUE (display_name);


--
-- Name: ai_model_configurations ai_model_configurations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_model_configurations
    ADD CONSTRAINT ai_model_configurations_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: anonymous_user_sessions anonymous_user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anonymous_user_sessions
    ADD CONSTRAINT anonymous_user_sessions_pkey PRIMARY KEY (id);


--
-- Name: blog_analytics_summary blog_analytics_summary_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_analytics_summary
    ADD CONSTRAINT blog_analytics_summary_pkey PRIMARY KEY (id);


--
-- Name: blog_author_profiles blog_author_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_author_profiles
    ADD CONSTRAINT blog_author_profiles_pkey PRIMARY KEY (id);


--
-- Name: blog_categories blog_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_categories
    ADD CONSTRAINT blog_categories_name_key UNIQUE (name);


--
-- Name: blog_categories blog_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_categories
    ADD CONSTRAINT blog_categories_pkey PRIMARY KEY (id);


--
-- Name: blog_comments blog_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_comments
    ADD CONSTRAINT blog_comments_pkey PRIMARY KEY (id);


--
-- Name: blog_content_links blog_content_links_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_content_links
    ADD CONSTRAINT blog_content_links_pkey PRIMARY KEY (id);


--
-- Name: blog_follows blog_follows_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_follows
    ADD CONSTRAINT blog_follows_pkey PRIMARY KEY (id);


--
-- Name: blog_likes blog_likes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_likes
    ADD CONSTRAINT blog_likes_pkey PRIMARY KEY (id);


--
-- Name: blog_post_associations blog_post_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_post_associations
    ADD CONSTRAINT blog_post_associations_pkey PRIMARY KEY (id);


--
-- Name: blog_post_tags blog_post_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_post_tags
    ADD CONSTRAINT blog_post_tags_pkey PRIMARY KEY (id);


--
-- Name: blog_posts blog_posts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_posts
    ADD CONSTRAINT blog_posts_pkey PRIMARY KEY (id);


--
-- Name: blog_subscriptions blog_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_subscriptions
    ADD CONSTRAINT blog_subscriptions_pkey PRIMARY KEY (id);


--
-- Name: blog_tags blog_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_tags
    ADD CONSTRAINT blog_tags_pkey PRIMARY KEY (id);


--
-- Name: blog_views blog_views_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_views
    ADD CONSTRAINT blog_views_pkey PRIMARY KEY (id);


--
-- Name: brainstorm_favorites brainstorm_favorites_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.brainstorm_favorites
    ADD CONSTRAINT brainstorm_favorites_pkey PRIMARY KEY (id);


--
-- Name: brainstorm_sessions brainstorm_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.brainstorm_sessions
    ADD CONSTRAINT brainstorm_sessions_pkey PRIMARY KEY (id);


--
-- Name: brainstorm_stories brainstorm_stories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.brainstorm_stories
    ADD CONSTRAINT brainstorm_stories_pkey PRIMARY KEY (id);


--
-- Name: care_circle_families care_circle_families_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_families
    ADD CONSTRAINT care_circle_families_pkey PRIMARY KEY (id);


--
-- Name: care_circle_family_memberships care_circle_family_memberships_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_family_memberships
    ADD CONSTRAINT care_circle_family_memberships_pkey PRIMARY KEY (id);


--
-- Name: care_circle_patient_content_cards care_circle_patient_content_cards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_patient_content_cards
    ADD CONSTRAINT care_circle_patient_content_cards_pkey PRIMARY KEY (id);


--
-- Name: care_circle_patient_profiles care_circle_patient_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_patient_profiles
    ADD CONSTRAINT care_circle_patient_profiles_pkey PRIMARY KEY (id);


--
-- Name: care_circle_provider_catalog care_circle_provider_catalog_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_provider_catalog
    ADD CONSTRAINT care_circle_provider_catalog_pkey PRIMARY KEY (id);


--
-- Name: care_circle_provider_patient_configs care_circle_provider_patient_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_provider_patient_configs
    ADD CONSTRAINT care_circle_provider_patient_configs_pkey PRIMARY KEY (id);


--
-- Name: care_circle_provider_run_logs care_circle_provider_run_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_provider_run_logs
    ADD CONSTRAINT care_circle_provider_run_logs_pkey PRIMARY KEY (id);


--
-- Name: care_circle_provider_session_outputs care_circle_provider_session_outputs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_provider_session_outputs
    ADD CONSTRAINT care_circle_provider_session_outputs_pkey PRIMARY KEY (id);


--
-- Name: characters characters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.characters
    ADD CONSTRAINT characters_pkey PRIMARY KEY (id);


--
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (id);


--
-- Name: chat_samples chat_samples_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_samples
    ADD CONSTRAINT chat_samples_pkey PRIMARY KEY (id);


--
-- Name: chat_sessions chat_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_pkey PRIMARY KEY (id);


--
-- Name: credit_packages credit_packages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.credit_packages
    ADD CONSTRAINT credit_packages_pkey PRIMARY KEY (id);


--
-- Name: cta_contents cta_contents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cta_contents
    ADD CONSTRAINT cta_contents_pkey PRIMARY KEY (id);


--
-- Name: forum_categories forum_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_categories
    ADD CONSTRAINT forum_categories_name_key UNIQUE (name);


--
-- Name: forum_categories forum_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_categories
    ADD CONSTRAINT forum_categories_pkey PRIMARY KEY (id);


--
-- Name: forum_posts forum_posts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_posts
    ADD CONSTRAINT forum_posts_pkey PRIMARY KEY (id);


--
-- Name: forum_subscriptions forum_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_subscriptions
    ADD CONSTRAINT forum_subscriptions_pkey PRIMARY KEY (id);


--
-- Name: forum_threads forum_threads_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_threads
    ADD CONSTRAINT forum_threads_pkey PRIMARY KEY (id);


--
-- Name: forum_votes forum_votes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_votes
    ADD CONSTRAINT forum_votes_pkey PRIMARY KEY (id);


--
-- Name: generated_images generated_images_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.generated_images
    ADD CONSTRAINT generated_images_pkey PRIMARY KEY (id);


--
-- Name: job_statuses job_statuses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_statuses
    ADD CONSTRAINT job_statuses_pkey PRIMARY KEY (id);


--
-- Name: location_connections location_connections_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.location_connections
    ADD CONSTRAINT location_connections_pkey PRIMARY KEY (from_location_id, to_location_id);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);


--
-- Name: lore_items lore_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lore_items
    ADD CONSTRAINT lore_items_pkey PRIMARY KEY (id);


--
-- Name: prompts prompts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prompts
    ADD CONSTRAINT prompts_pkey PRIMARY KEY (id);


--
-- Name: published_stories published_stories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.published_stories
    ADD CONSTRAINT published_stories_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: scene_character_associations scene_character_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scene_character_associations
    ADD CONSTRAINT scene_character_associations_pkey PRIMARY KEY (id);


--
-- Name: scene_location_associations scene_location_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scene_location_associations
    ADD CONSTRAINT scene_location_associations_pkey PRIMARY KEY (id);


--
-- Name: scene_lore_item_associations scene_lore_item_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scene_lore_item_associations
    ADD CONSTRAINT scene_lore_item_associations_pkey PRIMARY KEY (id);


--
-- Name: scenes scenes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scenes
    ADD CONSTRAINT scenes_pkey PRIMARY KEY (id);


--
-- Name: social_share_daily_summaries social_share_daily_summaries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.social_share_daily_summaries
    ADD CONSTRAINT social_share_daily_summaries_pkey PRIMARY KEY (id);


--
-- Name: social_shares social_shares_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.social_shares
    ADD CONSTRAINT social_shares_pkey PRIMARY KEY (id);


--
-- Name: stories stories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stories
    ADD CONSTRAINT stories_pkey PRIMARY KEY (id);


--
-- Name: story_character_association story_character_association_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_character_association
    ADD CONSTRAINT story_character_association_pkey PRIMARY KEY (story_id, character_id);


--
-- Name: story_character_associations story_character_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_character_associations
    ADD CONSTRAINT story_character_associations_pkey PRIMARY KEY (id);


--
-- Name: story_chat_messages story_chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_chat_messages
    ADD CONSTRAINT story_chat_messages_pkey PRIMARY KEY (id);


--
-- Name: story_chat_sessions story_chat_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_chat_sessions
    ADD CONSTRAINT story_chat_sessions_pkey PRIMARY KEY (id);


--
-- Name: story_classes story_classes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_classes
    ADD CONSTRAINT story_classes_pkey PRIMARY KEY (id);


--
-- Name: story_comments story_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_comments
    ADD CONSTRAINT story_comments_pkey PRIMARY KEY (id);


--
-- Name: story_location_association story_location_association_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_location_association
    ADD CONSTRAINT story_location_association_pkey PRIMARY KEY (story_id, location_id);


--
-- Name: story_location_associations story_location_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_location_associations
    ADD CONSTRAINT story_location_associations_pkey PRIMARY KEY (id);


--
-- Name: story_lore_item_association story_lore_item_association_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_lore_item_association
    ADD CONSTRAINT story_lore_item_association_pkey PRIMARY KEY (story_id, lore_item_id);


--
-- Name: story_lore_item_associations story_lore_item_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_lore_item_associations
    ADD CONSTRAINT story_lore_item_associations_pkey PRIMARY KEY (id);


--
-- Name: story_ratings story_ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_ratings
    ADD CONSTRAINT story_ratings_pkey PRIMARY KEY (id);


--
-- Name: storytelling_act_character_associations storytelling_act_character_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_act_character_associations
    ADD CONSTRAINT storytelling_act_character_associations_pkey PRIMARY KEY (id);


--
-- Name: storytelling_act_location_associations storytelling_act_location_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_act_location_associations
    ADD CONSTRAINT storytelling_act_location_associations_pkey PRIMARY KEY (id);


--
-- Name: storytelling_act_lore_item_associations storytelling_act_lore_item_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_act_lore_item_associations
    ADD CONSTRAINT storytelling_act_lore_item_associations_pkey PRIMARY KEY (id);


--
-- Name: storytelling_acts storytelling_acts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_acts
    ADD CONSTRAINT storytelling_acts_pkey PRIMARY KEY (id);


--
-- Name: storytelling_acts storytelling_acts_story_id_act_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_acts
    ADD CONSTRAINT storytelling_acts_story_id_act_number_key UNIQUE (story_id, act_number);


--
-- Name: storytelling_brainstorm_favorites storytelling_brainstorm_favorites_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_brainstorm_favorites
    ADD CONSTRAINT storytelling_brainstorm_favorites_pkey PRIMARY KEY (id);


--
-- Name: storytelling_brainstorm_sessions storytelling_brainstorm_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_brainstorm_sessions
    ADD CONSTRAINT storytelling_brainstorm_sessions_pkey PRIMARY KEY (id);


--
-- Name: storytelling_brainstorm_stories storytelling_brainstorm_stories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_brainstorm_stories
    ADD CONSTRAINT storytelling_brainstorm_stories_pkey PRIMARY KEY (id);


--
-- Name: storytelling_characters storytelling_characters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_characters
    ADD CONSTRAINT storytelling_characters_pkey PRIMARY KEY (id);


--
-- Name: storytelling_location_connections storytelling_location_connections_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_location_connections
    ADD CONSTRAINT storytelling_location_connections_pkey PRIMARY KEY (from_location_id, to_location_id);


--
-- Name: storytelling_locations storytelling_locations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_locations
    ADD CONSTRAINT storytelling_locations_pkey PRIMARY KEY (id);


--
-- Name: storytelling_lore_items storytelling_lore_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_lore_items
    ADD CONSTRAINT storytelling_lore_items_pkey PRIMARY KEY (id);


--
-- Name: storytelling_published_stories storytelling_published_stories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_published_stories
    ADD CONSTRAINT storytelling_published_stories_pkey PRIMARY KEY (id);


--
-- Name: storytelling_scene_character_associations storytelling_scene_character_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scene_character_associations
    ADD CONSTRAINT storytelling_scene_character_associations_pkey PRIMARY KEY (id);


--
-- Name: storytelling_scene_location_associations storytelling_scene_location_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scene_location_associations
    ADD CONSTRAINT storytelling_scene_location_associations_pkey PRIMARY KEY (id);


--
-- Name: storytelling_scene_lore_item_associations storytelling_scene_lore_item_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scene_lore_item_associations
    ADD CONSTRAINT storytelling_scene_lore_item_associations_pkey PRIMARY KEY (id);


--
-- Name: storytelling_scenes storytelling_scenes_act_id_scene_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scenes
    ADD CONSTRAINT storytelling_scenes_act_id_scene_number_key UNIQUE (act_id, scene_number);


--
-- Name: storytelling_scenes storytelling_scenes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scenes
    ADD CONSTRAINT storytelling_scenes_pkey PRIMARY KEY (id);


--
-- Name: storytelling_stories storytelling_stories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_stories
    ADD CONSTRAINT storytelling_stories_pkey PRIMARY KEY (id);


--
-- Name: storytelling_story_character_associations storytelling_story_character_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_character_associations
    ADD CONSTRAINT storytelling_story_character_associations_pkey PRIMARY KEY (id);


--
-- Name: storytelling_story_chat_messages storytelling_story_chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_chat_messages
    ADD CONSTRAINT storytelling_story_chat_messages_pkey PRIMARY KEY (id);


--
-- Name: storytelling_story_chat_sessions storytelling_story_chat_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_chat_sessions
    ADD CONSTRAINT storytelling_story_chat_sessions_pkey PRIMARY KEY (id);


--
-- Name: storytelling_story_classes storytelling_story_classes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_classes
    ADD CONSTRAINT storytelling_story_classes_pkey PRIMARY KEY (id);


--
-- Name: storytelling_story_comments storytelling_story_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_comments
    ADD CONSTRAINT storytelling_story_comments_pkey PRIMARY KEY (id);


--
-- Name: storytelling_story_location_associations storytelling_story_location_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_location_associations
    ADD CONSTRAINT storytelling_story_location_associations_pkey PRIMARY KEY (id);


--
-- Name: storytelling_story_lore_item_associations storytelling_story_lore_item_associations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_lore_item_associations
    ADD CONSTRAINT storytelling_story_lore_item_associations_pkey PRIMARY KEY (id);


--
-- Name: storytelling_story_ratings storytelling_story_ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_ratings
    ADD CONSTRAINT storytelling_story_ratings_pkey PRIMARY KEY (id);


--
-- Name: storytelling_story_ratings storytelling_story_ratings_published_story_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_ratings
    ADD CONSTRAINT storytelling_story_ratings_published_story_id_user_id_key UNIQUE (published_story_id, user_id);


--
-- Name: storytelling_user_interview_responses storytelling_user_interview_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_user_interview_responses
    ADD CONSTRAINT storytelling_user_interview_responses_pkey PRIMARY KEY (id);


--
-- Name: storytelling_world_collaborators storytelling_world_collaborators_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_world_collaborators
    ADD CONSTRAINT storytelling_world_collaborators_pkey PRIMARY KEY (id);


--
-- Name: storytelling_world_collaborators storytelling_world_collaborators_world_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_world_collaborators
    ADD CONSTRAINT storytelling_world_collaborators_world_id_user_id_key UNIQUE (world_id, user_id);


--
-- Name: storytelling_world_roles storytelling_world_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_world_roles
    ADD CONSTRAINT storytelling_world_roles_pkey PRIMARY KEY (id);


--
-- Name: storytelling_worlds storytelling_worlds_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_worlds
    ADD CONSTRAINT storytelling_worlds_pkey PRIMARY KEY (id);


--
-- Name: blog_follows unique_author_follower; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_follows
    ADD CONSTRAINT unique_author_follower UNIQUE (author_id, follower_id);


--
-- Name: blog_analytics_summary unique_post_date; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_analytics_summary
    ADD CONSTRAINT unique_post_date UNIQUE (post_id, date);


--
-- Name: blog_likes unique_post_like; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_likes
    ADD CONSTRAINT unique_post_like UNIQUE (post_id, user_id);


--
-- Name: blog_author_profiles unique_user_profile; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_author_profiles
    ADD CONSTRAINT unique_user_profile UNIQUE (user_id);


--
-- Name: story_ratings unique_user_story_rating; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_ratings
    ADD CONSTRAINT unique_user_story_rating UNIQUE (published_story_id, user_id);


--
-- Name: uploaded_documents uploaded_documents_blob_storage_path_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uploaded_documents
    ADD CONSTRAINT uploaded_documents_blob_storage_path_key UNIQUE (blob_storage_path);


--
-- Name: uploaded_documents uploaded_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uploaded_documents
    ADD CONSTRAINT uploaded_documents_pkey PRIMARY KEY (id);


--
-- Name: care_circle_family_memberships uq_care_circle_family_user; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_family_memberships
    ADD CONSTRAINT uq_care_circle_family_user UNIQUE (family_id, user_id);


--
-- Name: care_circle_provider_patient_configs uq_care_circle_patient_provider; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_provider_patient_configs
    ADD CONSTRAINT uq_care_circle_patient_provider UNIQUE (patient_id, provider_key);


--
-- Name: forum_subscriptions uq_subscription_thread_user; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_subscriptions
    ADD CONSTRAINT uq_subscription_thread_user UNIQUE (thread_id, user_id);


--
-- Name: forum_threads uq_thread_category_slug; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_threads
    ADD CONSTRAINT uq_thread_category_slug UNIQUE (category_id, slug);


--
-- Name: forum_votes uq_vote_post_user; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_votes
    ADD CONSTRAINT uq_vote_post_user UNIQUE (post_id, user_id);


--
-- Name: world_collaborators uq_world_collaborator; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.world_collaborators
    ADD CONSTRAINT uq_world_collaborator UNIQUE (world_id, user_id);


--
-- Name: user_accounts user_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_accounts
    ADD CONSTRAINT user_accounts_pkey PRIMARY KEY (id);


--
-- Name: user_accounts user_accounts_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_accounts
    ADD CONSTRAINT user_accounts_user_id_key UNIQUE (user_id);


--
-- Name: user_activities user_activities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_activities
    ADD CONSTRAINT user_activities_pkey PRIMARY KEY (id);


--
-- Name: user_interview_responses user_interview_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_interview_responses
    ADD CONSTRAINT user_interview_responses_pkey PRIMARY KEY (id);


--
-- Name: user_transactions user_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_transactions
    ADD CONSTRAINT user_transactions_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_provider_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_provider_id_key UNIQUE (provider_id);


--
-- Name: world_collaborators world_collaborators_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.world_collaborators
    ADD CONSTRAINT world_collaborators_pkey PRIMARY KEY (id);


--
-- Name: world_roles world_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.world_roles
    ADD CONSTRAINT world_roles_pkey PRIMARY KEY (id);


--
-- Name: worlds worlds_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.worlds
    ADD CONSTRAINT worlds_pkey PRIMARY KEY (id);


--
-- Name: idx_blog_comments_author_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_blog_comments_author_created ON public.blog_comments USING btree (author_id, created_at);


--
-- Name: idx_blog_comments_parent_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_blog_comments_parent_created ON public.blog_comments USING btree (parent_comment_id, created_at);


--
-- Name: idx_blog_comments_post_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_blog_comments_post_status ON public.blog_comments USING btree (post_id, status);


--
-- Name: idx_blog_posts_author_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_blog_posts_author_status ON public.blog_posts USING btree (author_id, status);


--
-- Name: idx_blog_posts_category_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_blog_posts_category_status ON public.blog_posts USING btree (category_id, status);


--
-- Name: idx_blog_posts_published_featured; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_blog_posts_published_featured ON public.blog_posts USING btree (published_at, is_featured);


--
-- Name: idx_blog_posts_search_vector; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_blog_posts_search_vector ON public.blog_posts USING gin (search_vector);


--
-- Name: idx_blog_subscriptions_email_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_blog_subscriptions_email_status ON public.blog_subscriptions USING btree (email, status);


--
-- Name: idx_blog_subscriptions_frequency_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_blog_subscriptions_frequency_status ON public.blog_subscriptions USING btree (frequency, status);


--
-- Name: idx_blog_subscriptions_last_sent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_blog_subscriptions_last_sent ON public.blog_subscriptions USING btree (last_sent_at);


--
-- Name: idx_blog_subscriptions_user_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_blog_subscriptions_user_status ON public.blog_subscriptions USING btree (user_id, status);


--
-- Name: idx_post_parent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_parent ON public.forum_posts USING btree (parent_post_id);


--
-- Name: idx_post_thread_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_thread_created ON public.forum_posts USING btree (thread_id, created_at);


--
-- Name: idx_post_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_user ON public.forum_posts USING btree (user_id);


--
-- Name: idx_subscription_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_subscription_user ON public.forum_subscriptions USING btree (user_id);


--
-- Name: idx_thread_category_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_thread_category_status ON public.forum_threads USING btree (category_id, status);


--
-- Name: idx_thread_story; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_thread_story ON public.forum_threads USING btree (story_id);


--
-- Name: idx_thread_world; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_thread_world ON public.forum_threads USING btree (world_id);


--
-- Name: idx_vote_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vote_user ON public.forum_votes USING btree (user_id);


--
-- Name: ix_act_character_associations_act_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_act_character_associations_act_id ON public.act_character_associations USING btree (act_id);


--
-- Name: ix_act_character_associations_character_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_act_character_associations_character_id ON public.act_character_associations USING btree (character_id);


--
-- Name: ix_act_character_associations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_act_character_associations_id ON public.act_character_associations USING btree (id);


--
-- Name: ix_act_location_associations_act_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_act_location_associations_act_id ON public.act_location_associations USING btree (act_id);


--
-- Name: ix_act_location_associations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_act_location_associations_id ON public.act_location_associations USING btree (id);


--
-- Name: ix_act_location_associations_location_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_act_location_associations_location_id ON public.act_location_associations USING btree (location_id);


--
-- Name: ix_act_lore_item_associations_act_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_act_lore_item_associations_act_id ON public.act_lore_item_associations USING btree (act_id);


--
-- Name: ix_act_lore_item_associations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_act_lore_item_associations_id ON public.act_lore_item_associations USING btree (id);


--
-- Name: ix_act_lore_item_associations_lore_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_act_lore_item_associations_lore_item_id ON public.act_lore_item_associations USING btree (lore_item_id);


--
-- Name: ix_acts_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_acts_id ON public.acts USING btree (id);


--
-- Name: ix_acts_story_class_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_acts_story_class_id ON public.acts USING btree (story_class_id);


--
-- Name: ix_acts_system_prompt_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_acts_system_prompt_id ON public.acts USING btree (system_prompt_id);


--
-- Name: ix_ai_call_logs_call_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_call_logs_call_type ON public.ai_call_logs USING btree (call_type);


--
-- Name: ix_ai_call_logs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_call_logs_id ON public.ai_call_logs USING btree (id);


--
-- Name: ix_ai_call_logs_job_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_call_logs_job_id ON public.ai_call_logs USING btree (job_id);


--
-- Name: ix_ai_call_logs_model_config_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_call_logs_model_config_id ON public.ai_call_logs USING btree (model_config_id);


--
-- Name: ix_ai_call_logs_model_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_call_logs_model_name ON public.ai_call_logs USING btree (model_name);


--
-- Name: ix_ai_call_logs_object_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_call_logs_object_id ON public.ai_call_logs USING btree (object_id);


--
-- Name: ix_ai_call_logs_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_call_logs_user_id ON public.ai_call_logs USING btree (user_id);


--
-- Name: ix_ai_model_configurations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_model_configurations_id ON public.ai_model_configurations USING btree (id);


--
-- Name: ix_ai_model_configurations_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_model_configurations_is_active ON public.ai_model_configurations USING btree (is_active);


--
-- Name: ix_ai_model_configurations_is_public_chat_default; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_model_configurations_is_public_chat_default ON public.ai_model_configurations USING btree (is_public_chat_default);


--
-- Name: ix_ai_model_configurations_model_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_model_configurations_model_name ON public.ai_model_configurations USING btree (model_name);


--
-- Name: ix_ai_model_configurations_model_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_model_configurations_model_type ON public.ai_model_configurations USING btree (model_type);


--
-- Name: ix_anonymous_user_sessions_browser_fingerprint; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_anonymous_user_sessions_browser_fingerprint ON public.anonymous_user_sessions USING btree (browser_fingerprint);


--
-- Name: ix_anonymous_user_sessions_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_anonymous_user_sessions_created_at ON public.anonymous_user_sessions USING btree (created_at);


--
-- Name: ix_anonymous_user_sessions_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_anonymous_user_sessions_id ON public.anonymous_user_sessions USING btree (id);


--
-- Name: ix_anonymous_user_sessions_ip_address; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_anonymous_user_sessions_ip_address ON public.anonymous_user_sessions USING btree (ip_address);


--
-- Name: ix_anonymous_user_sessions_session_token; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_anonymous_user_sessions_session_token ON public.anonymous_user_sessions USING btree (session_token);


--
-- Name: ix_anonymous_user_sessions_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_anonymous_user_sessions_user_id ON public.anonymous_user_sessions USING btree (user_id);


--
-- Name: ix_blog_analytics_summary_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_analytics_summary_date ON public.blog_analytics_summary USING btree (date);


--
-- Name: ix_blog_analytics_summary_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_analytics_summary_id ON public.blog_analytics_summary USING btree (id);


--
-- Name: ix_blog_analytics_summary_post_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_analytics_summary_post_id ON public.blog_analytics_summary USING btree (post_id);


--
-- Name: ix_blog_author_profiles_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_author_profiles_id ON public.blog_author_profiles USING btree (id);


--
-- Name: ix_blog_author_profiles_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_author_profiles_user_id ON public.blog_author_profiles USING btree (user_id);


--
-- Name: ix_blog_categories_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_categories_id ON public.blog_categories USING btree (id);


--
-- Name: ix_blog_categories_slug; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_blog_categories_slug ON public.blog_categories USING btree (slug);


--
-- Name: ix_blog_comments_author_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_comments_author_id ON public.blog_comments USING btree (author_id);


--
-- Name: ix_blog_comments_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_comments_created_at ON public.blog_comments USING btree (created_at);


--
-- Name: ix_blog_comments_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_comments_id ON public.blog_comments USING btree (id);


--
-- Name: ix_blog_comments_parent_comment_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_comments_parent_comment_id ON public.blog_comments USING btree (parent_comment_id);


--
-- Name: ix_blog_comments_post_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_comments_post_id ON public.blog_comments USING btree (post_id);


--
-- Name: ix_blog_comments_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_comments_status ON public.blog_comments USING btree (status);


--
-- Name: ix_blog_content_links_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_content_links_id ON public.blog_content_links USING btree (id);


--
-- Name: ix_blog_content_links_link_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_content_links_link_id ON public.blog_content_links USING btree (link_id);


--
-- Name: ix_blog_content_links_link_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_content_links_link_type ON public.blog_content_links USING btree (link_type);


--
-- Name: ix_blog_content_links_post_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_content_links_post_id ON public.blog_content_links USING btree (post_id);


--
-- Name: ix_blog_follows_author_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_follows_author_id ON public.blog_follows USING btree (author_id);


--
-- Name: ix_blog_follows_follower_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_follows_follower_id ON public.blog_follows USING btree (follower_id);


--
-- Name: ix_blog_follows_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_follows_id ON public.blog_follows USING btree (id);


--
-- Name: ix_blog_likes_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_likes_id ON public.blog_likes USING btree (id);


--
-- Name: ix_blog_likes_post_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_likes_post_id ON public.blog_likes USING btree (post_id);


--
-- Name: ix_blog_likes_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_likes_user_id ON public.blog_likes USING btree (user_id);


--
-- Name: ix_blog_post_associations_association_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_post_associations_association_id ON public.blog_post_associations USING btree (association_id);


--
-- Name: ix_blog_post_associations_association_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_post_associations_association_type ON public.blog_post_associations USING btree (association_type);


--
-- Name: ix_blog_post_associations_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_post_associations_created_at ON public.blog_post_associations USING btree (created_at);


--
-- Name: ix_blog_post_associations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_post_associations_id ON public.blog_post_associations USING btree (id);


--
-- Name: ix_blog_post_associations_post_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_post_associations_post_id ON public.blog_post_associations USING btree (post_id);


--
-- Name: ix_blog_posts_author_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_posts_author_id ON public.blog_posts USING btree (author_id);


--
-- Name: ix_blog_posts_category_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_posts_category_id ON public.blog_posts USING btree (category_id);


--
-- Name: ix_blog_posts_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_posts_id ON public.blog_posts USING btree (id);


--
-- Name: ix_blog_posts_published_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_posts_published_at ON public.blog_posts USING btree (published_at);


--
-- Name: ix_blog_posts_slug; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_blog_posts_slug ON public.blog_posts USING btree (slug);


--
-- Name: ix_blog_posts_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_posts_status ON public.blog_posts USING btree (status);


--
-- Name: ix_blog_posts_title; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_posts_title ON public.blog_posts USING btree (title);


--
-- Name: ix_blog_subscriptions_confirmation_token; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_subscriptions_confirmation_token ON public.blog_subscriptions USING btree (confirmation_token);


--
-- Name: ix_blog_subscriptions_email; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_subscriptions_email ON public.blog_subscriptions USING btree (email);


--
-- Name: ix_blog_subscriptions_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_subscriptions_id ON public.blog_subscriptions USING btree (id);


--
-- Name: ix_blog_subscriptions_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_subscriptions_status ON public.blog_subscriptions USING btree (status);


--
-- Name: ix_blog_subscriptions_unsubscribe_token; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_blog_subscriptions_unsubscribe_token ON public.blog_subscriptions USING btree (unsubscribe_token);


--
-- Name: ix_blog_subscriptions_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_subscriptions_user_id ON public.blog_subscriptions USING btree (user_id);


--
-- Name: ix_blog_tags_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_tags_id ON public.blog_tags USING btree (id);


--
-- Name: ix_blog_tags_name; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_blog_tags_name ON public.blog_tags USING btree (name);


--
-- Name: ix_blog_tags_slug; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_blog_tags_slug ON public.blog_tags USING btree (slug);


--
-- Name: ix_blog_views_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_views_created_at ON public.blog_views USING btree (created_at);


--
-- Name: ix_blog_views_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_views_id ON public.blog_views USING btree (id);


--
-- Name: ix_blog_views_ip_address; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_views_ip_address ON public.blog_views USING btree (ip_address);


--
-- Name: ix_blog_views_post_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_views_post_id ON public.blog_views USING btree (post_id);


--
-- Name: ix_blog_views_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_blog_views_user_id ON public.blog_views USING btree (user_id);


--
-- Name: ix_brainstorm_favorites_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_brainstorm_favorites_id ON public.brainstorm_favorites USING btree (id);


--
-- Name: ix_brainstorm_sessions_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_brainstorm_sessions_id ON public.brainstorm_sessions USING btree (id);


--
-- Name: ix_brainstorm_stories_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_brainstorm_stories_id ON public.brainstorm_stories USING btree (id);


--
-- Name: ix_care_circle_families_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_families_id ON public.care_circle_families USING btree (id);


--
-- Name: ix_care_circle_families_join_code; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_care_circle_families_join_code ON public.care_circle_families USING btree (join_code);


--
-- Name: ix_care_circle_family_memberships_family_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_family_memberships_family_id ON public.care_circle_family_memberships USING btree (family_id);


--
-- Name: ix_care_circle_family_memberships_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_family_memberships_id ON public.care_circle_family_memberships USING btree (id);


--
-- Name: ix_care_circle_family_memberships_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_family_memberships_user_id ON public.care_circle_family_memberships USING btree (user_id);


--
-- Name: ix_care_circle_patient_content_cards_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_patient_content_cards_id ON public.care_circle_patient_content_cards USING btree (id);


--
-- Name: ix_care_circle_patient_content_cards_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_patient_content_cards_patient_id ON public.care_circle_patient_content_cards USING btree (patient_id);


--
-- Name: ix_care_circle_patient_content_cards_provider_key; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_patient_content_cards_provider_key ON public.care_circle_patient_content_cards USING btree (provider_key);


--
-- Name: ix_care_circle_patient_profiles_family_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_patient_profiles_family_id ON public.care_circle_patient_profiles USING btree (family_id);


--
-- Name: ix_care_circle_patient_profiles_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_patient_profiles_id ON public.care_circle_patient_profiles USING btree (id);


--
-- Name: ix_care_circle_provider_catalog_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_provider_catalog_id ON public.care_circle_provider_catalog USING btree (id);


--
-- Name: ix_care_circle_provider_catalog_provider_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_care_circle_provider_catalog_provider_key ON public.care_circle_provider_catalog USING btree (provider_key);


--
-- Name: ix_care_circle_provider_patient_configs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_provider_patient_configs_id ON public.care_circle_provider_patient_configs USING btree (id);


--
-- Name: ix_care_circle_provider_patient_configs_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_provider_patient_configs_patient_id ON public.care_circle_provider_patient_configs USING btree (patient_id);


--
-- Name: ix_care_circle_provider_patient_configs_provider_key; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_provider_patient_configs_provider_key ON public.care_circle_provider_patient_configs USING btree (provider_key);


--
-- Name: ix_care_circle_provider_run_logs_family_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_provider_run_logs_family_id ON public.care_circle_provider_run_logs USING btree (family_id);


--
-- Name: ix_care_circle_provider_run_logs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_provider_run_logs_id ON public.care_circle_provider_run_logs USING btree (id);


--
-- Name: ix_care_circle_provider_run_logs_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_provider_run_logs_patient_id ON public.care_circle_provider_run_logs USING btree (patient_id);


--
-- Name: ix_care_circle_provider_run_logs_provider_key; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_provider_run_logs_provider_key ON public.care_circle_provider_run_logs USING btree (provider_key);


--
-- Name: ix_care_circle_provider_session_outputs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_provider_session_outputs_id ON public.care_circle_provider_session_outputs USING btree (id);


--
-- Name: ix_care_circle_provider_session_outputs_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_provider_session_outputs_patient_id ON public.care_circle_provider_session_outputs USING btree (patient_id);


--
-- Name: ix_care_circle_provider_session_outputs_provider_key; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_provider_session_outputs_provider_key ON public.care_circle_provider_session_outputs USING btree (provider_key);


--
-- Name: ix_care_circle_provider_session_outputs_session_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_circle_provider_session_outputs_session_date ON public.care_circle_provider_session_outputs USING btree (session_date);


--
-- Name: ix_characters_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_characters_id ON public.characters USING btree (id);


--
-- Name: ix_characters_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_characters_name ON public.characters USING btree (name);


--
-- Name: ix_characters_world_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_characters_world_id ON public.characters USING btree (world_id);


--
-- Name: ix_chat_messages_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_chat_messages_id ON public.chat_messages USING btree (id);


--
-- Name: ix_chat_messages_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_chat_messages_session_id ON public.chat_messages USING btree (session_id);


--
-- Name: ix_chat_samples_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_chat_samples_id ON public.chat_samples USING btree (id);


--
-- Name: ix_chat_sessions_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_chat_sessions_id ON public.chat_sessions USING btree (id);


--
-- Name: ix_chat_sessions_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_chat_sessions_user_id ON public.chat_sessions USING btree (user_id);


--
-- Name: ix_chat_sessions_world_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_chat_sessions_world_id ON public.chat_sessions USING btree (world_id);


--
-- Name: ix_credit_packages_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_credit_packages_id ON public.credit_packages USING btree (id);


--
-- Name: ix_cta_contents_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_cta_contents_id ON public.cta_contents USING btree (id);


--
-- Name: ix_cta_contents_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_cta_contents_is_active ON public.cta_contents USING btree (is_active);


--
-- Name: ix_cta_contents_position; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_cta_contents_position ON public.cta_contents USING btree ("position");


--
-- Name: ix_forum_categories_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_forum_categories_id ON public.forum_categories USING btree (id);


--
-- Name: ix_forum_categories_slug; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_forum_categories_slug ON public.forum_categories USING btree (slug);


--
-- Name: ix_forum_posts_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_forum_posts_id ON public.forum_posts USING btree (id);


--
-- Name: ix_forum_subscriptions_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_forum_subscriptions_id ON public.forum_subscriptions USING btree (id);


--
-- Name: ix_forum_threads_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_forum_threads_id ON public.forum_threads USING btree (id);


--
-- Name: ix_forum_threads_slug; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_forum_threads_slug ON public.forum_threads USING btree (slug);


--
-- Name: ix_forum_votes_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_forum_votes_id ON public.forum_votes USING btree (id);


--
-- Name: ix_generated_images_associated_element_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_generated_images_associated_element_id ON public.generated_images USING btree (associated_element_id);


--
-- Name: ix_generated_images_element_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_generated_images_element_type ON public.generated_images USING btree (element_type);


--
-- Name: ix_generated_images_element_type_assoc_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_generated_images_element_type_assoc_id ON public.generated_images USING btree (element_type, associated_element_id);


--
-- Name: ix_generated_images_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_generated_images_id ON public.generated_images USING btree (id);


--
-- Name: ix_generated_images_image_uuid; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_generated_images_image_uuid ON public.generated_images USING btree (image_uuid);


--
-- Name: ix_generated_images_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_generated_images_user_id ON public.generated_images USING btree (user_id);


--
-- Name: ix_job_statuses_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_job_statuses_id ON public.job_statuses USING btree (id);


--
-- Name: ix_job_statuses_job_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_job_statuses_job_id ON public.job_statuses USING btree (job_id);


--
-- Name: ix_job_statuses_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_job_statuses_user_id ON public.job_statuses USING btree (user_id);


--
-- Name: ix_location_connections_from_location_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_location_connections_from_location_id ON public.location_connections USING btree (from_location_id);


--
-- Name: ix_location_connections_to_location_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_location_connections_to_location_id ON public.location_connections USING btree (to_location_id);


--
-- Name: ix_locations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_locations_id ON public.locations USING btree (id);


--
-- Name: ix_locations_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_locations_name ON public.locations USING btree (name);


--
-- Name: ix_locations_parent_location_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_locations_parent_location_id ON public.locations USING btree (parent_location_id);


--
-- Name: ix_locations_world_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_locations_world_id ON public.locations USING btree (world_id);


--
-- Name: ix_lore_items_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_lore_items_category ON public.lore_items USING btree (category);


--
-- Name: ix_lore_items_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_lore_items_id ON public.lore_items USING btree (id);


--
-- Name: ix_lore_items_title; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_lore_items_title ON public.lore_items USING btree (title);


--
-- Name: ix_lore_items_world_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_lore_items_world_id ON public.lore_items USING btree (world_id);


--
-- Name: ix_prompts_age_target; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_prompts_age_target ON public.prompts USING btree (age_target);


--
-- Name: ix_prompts_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_prompts_id ON public.prompts USING btree (id);


--
-- Name: ix_prompts_prompt_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_prompts_prompt_type ON public.prompts USING btree (prompt_type);


--
-- Name: ix_prompts_title; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_prompts_title ON public.prompts USING btree (title);


--
-- Name: ix_published_stories_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_published_stories_id ON public.published_stories USING btree (id);


--
-- Name: ix_published_stories_is_featured; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_published_stories_is_featured ON public.published_stories USING btree (is_featured);


--
-- Name: ix_published_stories_is_public; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_published_stories_is_public ON public.published_stories USING btree (is_public);


--
-- Name: ix_published_stories_published_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_published_stories_published_at ON public.published_stories USING btree (published_at);


--
-- Name: ix_published_stories_story_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_published_stories_story_id ON public.published_stories USING btree (story_id);


--
-- Name: ix_published_stories_title; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_published_stories_title ON public.published_stories USING btree (title);


--
-- Name: ix_published_stories_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_published_stories_user_id ON public.published_stories USING btree (user_id);


--
-- Name: ix_refresh_tokens_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_refresh_tokens_id ON public.refresh_tokens USING btree (id);


--
-- Name: ix_refresh_tokens_token; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_refresh_tokens_token ON public.refresh_tokens USING btree (token);


--
-- Name: ix_scene_character_associations_character_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scene_character_associations_character_id ON public.scene_character_associations USING btree (character_id);


--
-- Name: ix_scene_character_associations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scene_character_associations_id ON public.scene_character_associations USING btree (id);


--
-- Name: ix_scene_character_associations_scene_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scene_character_associations_scene_id ON public.scene_character_associations USING btree (scene_id);


--
-- Name: ix_scene_location_associations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scene_location_associations_id ON public.scene_location_associations USING btree (id);


--
-- Name: ix_scene_location_associations_location_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scene_location_associations_location_id ON public.scene_location_associations USING btree (location_id);


--
-- Name: ix_scene_location_associations_scene_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scene_location_associations_scene_id ON public.scene_location_associations USING btree (scene_id);


--
-- Name: ix_scene_lore_item_associations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scene_lore_item_associations_id ON public.scene_lore_item_associations USING btree (id);


--
-- Name: ix_scene_lore_item_associations_lore_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scene_lore_item_associations_lore_item_id ON public.scene_lore_item_associations USING btree (lore_item_id);


--
-- Name: ix_scene_lore_item_associations_scene_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scene_lore_item_associations_scene_id ON public.scene_lore_item_associations USING btree (scene_id);


--
-- Name: ix_scenes_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scenes_id ON public.scenes USING btree (id);


--
-- Name: ix_scenes_story_class_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scenes_story_class_id ON public.scenes USING btree (story_class_id);


--
-- Name: ix_social_share_daily_summaries_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_social_share_daily_summaries_date ON public.social_share_daily_summaries USING btree (date);


--
-- Name: ix_social_share_daily_summaries_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_social_share_daily_summaries_id ON public.social_share_daily_summaries USING btree (id);


--
-- Name: ix_social_share_daily_summaries_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_social_share_daily_summaries_user_id ON public.social_share_daily_summaries USING btree (user_id);


--
-- Name: ix_social_shares_coin_awarded; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_social_shares_coin_awarded ON public.social_shares USING btree (coin_awarded);


--
-- Name: ix_social_shares_content_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_social_shares_content_id ON public.social_shares USING btree (content_id);


--
-- Name: ix_social_shares_content_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_social_shares_content_type ON public.social_shares USING btree (content_type);


--
-- Name: ix_social_shares_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_social_shares_created_at ON public.social_shares USING btree (created_at);


--
-- Name: ix_social_shares_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_social_shares_id ON public.social_shares USING btree (id);


--
-- Name: ix_social_shares_platform; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_social_shares_platform ON public.social_shares USING btree (platform);


--
-- Name: ix_social_shares_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_social_shares_user_id ON public.social_shares USING btree (user_id);


--
-- Name: ix_stories_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_stories_id ON public.stories USING btree (id);


--
-- Name: ix_stories_story_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_stories_story_type ON public.stories USING btree (story_type);


--
-- Name: ix_stories_title; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_stories_title ON public.stories USING btree (title);


--
-- Name: ix_stories_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_stories_user_id ON public.stories USING btree (user_id);


--
-- Name: ix_stories_world_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_stories_world_id ON public.stories USING btree (world_id);


--
-- Name: ix_story_character_associations_character_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_character_associations_character_id ON public.story_character_associations USING btree (character_id);


--
-- Name: ix_story_character_associations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_character_associations_id ON public.story_character_associations USING btree (id);


--
-- Name: ix_story_character_associations_story_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_character_associations_story_id ON public.story_character_associations USING btree (story_id);


--
-- Name: ix_story_chat_messages_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_chat_messages_id ON public.story_chat_messages USING btree (id);


--
-- Name: ix_story_chat_messages_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_chat_messages_session_id ON public.story_chat_messages USING btree (session_id);


--
-- Name: ix_story_chat_sessions_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_chat_sessions_id ON public.story_chat_sessions USING btree (id);


--
-- Name: ix_story_chat_sessions_story_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_chat_sessions_story_id ON public.story_chat_sessions USING btree (story_id);


--
-- Name: ix_story_chat_sessions_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_chat_sessions_user_id ON public.story_chat_sessions USING btree (user_id);


--
-- Name: ix_story_classes_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_classes_id ON public.story_classes USING btree (id);


--
-- Name: ix_story_classes_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_classes_name ON public.story_classes USING btree (name);


--
-- Name: ix_story_classes_world_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_classes_world_id ON public.story_classes USING btree (world_id);


--
-- Name: ix_story_comments_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_comments_id ON public.story_comments USING btree (id);


--
-- Name: ix_story_comments_is_approved; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_comments_is_approved ON public.story_comments USING btree (is_approved);


--
-- Name: ix_story_comments_is_deleted; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_comments_is_deleted ON public.story_comments USING btree (is_deleted);


--
-- Name: ix_story_comments_parent_comment_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_comments_parent_comment_id ON public.story_comments USING btree (parent_comment_id);


--
-- Name: ix_story_comments_published_story_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_comments_published_story_id ON public.story_comments USING btree (published_story_id);


--
-- Name: ix_story_comments_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_comments_user_id ON public.story_comments USING btree (user_id);


--
-- Name: ix_story_location_associations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_location_associations_id ON public.story_location_associations USING btree (id);


--
-- Name: ix_story_location_associations_location_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_location_associations_location_id ON public.story_location_associations USING btree (location_id);


--
-- Name: ix_story_location_associations_story_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_location_associations_story_id ON public.story_location_associations USING btree (story_id);


--
-- Name: ix_story_lore_item_associations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_lore_item_associations_id ON public.story_lore_item_associations USING btree (id);


--
-- Name: ix_story_lore_item_associations_lore_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_lore_item_associations_lore_item_id ON public.story_lore_item_associations USING btree (lore_item_id);


--
-- Name: ix_story_lore_item_associations_story_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_lore_item_associations_story_id ON public.story_lore_item_associations USING btree (story_id);


--
-- Name: ix_story_ratings_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_ratings_id ON public.story_ratings USING btree (id);


--
-- Name: ix_story_ratings_published_story_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_ratings_published_story_id ON public.story_ratings USING btree (published_story_id);


--
-- Name: ix_story_ratings_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_story_ratings_user_id ON public.story_ratings USING btree (user_id);


--
-- Name: ix_uploaded_documents_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_uploaded_documents_id ON public.uploaded_documents USING btree (id);


--
-- Name: ix_uploaded_documents_source_character_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_uploaded_documents_source_character_id ON public.uploaded_documents USING btree (source_character_id);


--
-- Name: ix_uploaded_documents_source_element_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_uploaded_documents_source_element_type ON public.uploaded_documents USING btree (source_element_type);


--
-- Name: ix_uploaded_documents_source_location_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_uploaded_documents_source_location_id ON public.uploaded_documents USING btree (source_location_id);


--
-- Name: ix_uploaded_documents_source_lore_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_uploaded_documents_source_lore_item_id ON public.uploaded_documents USING btree (source_lore_item_id);


--
-- Name: ix_uploaded_documents_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_uploaded_documents_status ON public.uploaded_documents USING btree (status);


--
-- Name: ix_uploaded_documents_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_uploaded_documents_user_id ON public.uploaded_documents USING btree (user_id);


--
-- Name: ix_uploaded_documents_world_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_uploaded_documents_world_id ON public.uploaded_documents USING btree (world_id);


--
-- Name: ix_user_accounts_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_accounts_id ON public.user_accounts USING btree (id);


--
-- Name: ix_user_activities_action_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_activities_action_category ON public.user_activities USING btree (action_category);


--
-- Name: ix_user_activities_action_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_activities_action_type ON public.user_activities USING btree (action_type);


--
-- Name: ix_user_activities_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_activities_created_at ON public.user_activities USING btree (created_at);


--
-- Name: ix_user_activities_endpoint; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_activities_endpoint ON public.user_activities USING btree (endpoint);


--
-- Name: ix_user_activities_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_activities_id ON public.user_activities USING btree (id);


--
-- Name: ix_user_activities_request_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_activities_request_id ON public.user_activities USING btree (request_id);


--
-- Name: ix_user_activities_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_activities_user_id ON public.user_activities USING btree (user_id);


--
-- Name: ix_user_interview_responses_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_interview_responses_id ON public.user_interview_responses USING btree (id);


--
-- Name: ix_user_interview_responses_interview_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_interview_responses_interview_id ON public.user_interview_responses USING btree (interview_id);


--
-- Name: ix_user_transactions_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_transactions_id ON public.user_transactions USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_world_collaborators_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_world_collaborators_id ON public.world_collaborators USING btree (id);


--
-- Name: ix_world_collaborators_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_world_collaborators_user_id ON public.world_collaborators USING btree (user_id);


--
-- Name: ix_world_collaborators_world_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_world_collaborators_world_id ON public.world_collaborators USING btree (world_id);


--
-- Name: ix_world_roles_created_by_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_world_roles_created_by_user_id ON public.world_roles USING btree (created_by_user_id);


--
-- Name: ix_world_roles_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_world_roles_id ON public.world_roles USING btree (id);


--
-- Name: ix_world_roles_is_predefined; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_world_roles_is_predefined ON public.world_roles USING btree (is_predefined);


--
-- Name: ix_world_roles_world_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_world_roles_world_id ON public.world_roles USING btree (world_id);


--
-- Name: ix_worlds_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_worlds_id ON public.worlds USING btree (id);


--
-- Name: ix_worlds_is_free_chat_enabled; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_worlds_is_free_chat_enabled ON public.worlds USING btree (is_free_chat_enabled);


--
-- Name: ix_worlds_is_shadow; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_worlds_is_shadow ON public.worlds USING btree (is_shadow);


--
-- Name: ix_worlds_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_worlds_name ON public.worlds USING btree (name);


--
-- Name: ix_worlds_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_worlds_user_id ON public.worlds USING btree (user_id);


--
-- Name: storytelling_act_character_associations_act_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_act_character_associations_act_id_idx ON public.storytelling_act_character_associations USING btree (act_id);


--
-- Name: storytelling_act_character_associations_character_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_act_character_associations_character_id_idx ON public.storytelling_act_character_associations USING btree (character_id);


--
-- Name: storytelling_act_character_associations_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_act_character_associations_id_idx ON public.storytelling_act_character_associations USING btree (id);


--
-- Name: storytelling_act_location_associations_act_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_act_location_associations_act_id_idx ON public.storytelling_act_location_associations USING btree (act_id);


--
-- Name: storytelling_act_location_associations_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_act_location_associations_id_idx ON public.storytelling_act_location_associations USING btree (id);


--
-- Name: storytelling_act_location_associations_location_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_act_location_associations_location_id_idx ON public.storytelling_act_location_associations USING btree (location_id);


--
-- Name: storytelling_act_lore_item_associations_act_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_act_lore_item_associations_act_id_idx ON public.storytelling_act_lore_item_associations USING btree (act_id);


--
-- Name: storytelling_act_lore_item_associations_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_act_lore_item_associations_id_idx ON public.storytelling_act_lore_item_associations USING btree (id);


--
-- Name: storytelling_act_lore_item_associations_lore_item_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_act_lore_item_associations_lore_item_id_idx ON public.storytelling_act_lore_item_associations USING btree (lore_item_id);


--
-- Name: storytelling_acts_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_acts_id_idx ON public.storytelling_acts USING btree (id);


--
-- Name: storytelling_acts_story_class_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_acts_story_class_id_idx ON public.storytelling_acts USING btree (story_class_id);


--
-- Name: storytelling_acts_system_prompt_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_acts_system_prompt_id_idx ON public.storytelling_acts USING btree (system_prompt_id);


--
-- Name: storytelling_brainstorm_favorites_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_brainstorm_favorites_id_idx ON public.storytelling_brainstorm_favorites USING btree (id);


--
-- Name: storytelling_brainstorm_sessions_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_brainstorm_sessions_id_idx ON public.storytelling_brainstorm_sessions USING btree (id);


--
-- Name: storytelling_brainstorm_stories_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_brainstorm_stories_id_idx ON public.storytelling_brainstorm_stories USING btree (id);


--
-- Name: storytelling_characters_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_characters_id_idx ON public.storytelling_characters USING btree (id);


--
-- Name: storytelling_characters_name_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_characters_name_idx ON public.storytelling_characters USING btree (name);


--
-- Name: storytelling_characters_world_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_characters_world_id_idx ON public.storytelling_characters USING btree (world_id);


--
-- Name: storytelling_location_connections_from_location_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_location_connections_from_location_id_idx ON public.storytelling_location_connections USING btree (from_location_id);


--
-- Name: storytelling_location_connections_to_location_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_location_connections_to_location_id_idx ON public.storytelling_location_connections USING btree (to_location_id);


--
-- Name: storytelling_locations_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_locations_id_idx ON public.storytelling_locations USING btree (id);


--
-- Name: storytelling_locations_name_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_locations_name_idx ON public.storytelling_locations USING btree (name);


--
-- Name: storytelling_locations_parent_location_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_locations_parent_location_id_idx ON public.storytelling_locations USING btree (parent_location_id);


--
-- Name: storytelling_locations_world_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_locations_world_id_idx ON public.storytelling_locations USING btree (world_id);


--
-- Name: storytelling_lore_items_category_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_lore_items_category_idx ON public.storytelling_lore_items USING btree (category);


--
-- Name: storytelling_lore_items_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_lore_items_id_idx ON public.storytelling_lore_items USING btree (id);


--
-- Name: storytelling_lore_items_title_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_lore_items_title_idx ON public.storytelling_lore_items USING btree (title);


--
-- Name: storytelling_lore_items_world_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_lore_items_world_id_idx ON public.storytelling_lore_items USING btree (world_id);


--
-- Name: storytelling_published_stories_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_published_stories_id_idx ON public.storytelling_published_stories USING btree (id);


--
-- Name: storytelling_published_stories_is_featured_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_published_stories_is_featured_idx ON public.storytelling_published_stories USING btree (is_featured);


--
-- Name: storytelling_published_stories_is_public_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_published_stories_is_public_idx ON public.storytelling_published_stories USING btree (is_public);


--
-- Name: storytelling_published_stories_published_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_published_stories_published_at_idx ON public.storytelling_published_stories USING btree (published_at);


--
-- Name: storytelling_published_stories_story_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_published_stories_story_id_idx ON public.storytelling_published_stories USING btree (story_id);


--
-- Name: storytelling_published_stories_title_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_published_stories_title_idx ON public.storytelling_published_stories USING btree (title);


--
-- Name: storytelling_published_stories_user_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_published_stories_user_id_idx ON public.storytelling_published_stories USING btree (user_id);


--
-- Name: storytelling_scene_character_associations_character_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_scene_character_associations_character_id_idx ON public.storytelling_scene_character_associations USING btree (character_id);


--
-- Name: storytelling_scene_character_associations_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_scene_character_associations_id_idx ON public.storytelling_scene_character_associations USING btree (id);


--
-- Name: storytelling_scene_character_associations_scene_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_scene_character_associations_scene_id_idx ON public.storytelling_scene_character_associations USING btree (scene_id);


--
-- Name: storytelling_scene_location_associations_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_scene_location_associations_id_idx ON public.storytelling_scene_location_associations USING btree (id);


--
-- Name: storytelling_scene_location_associations_location_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_scene_location_associations_location_id_idx ON public.storytelling_scene_location_associations USING btree (location_id);


--
-- Name: storytelling_scene_location_associations_scene_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_scene_location_associations_scene_id_idx ON public.storytelling_scene_location_associations USING btree (scene_id);


--
-- Name: storytelling_scene_lore_item_associations_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_scene_lore_item_associations_id_idx ON public.storytelling_scene_lore_item_associations USING btree (id);


--
-- Name: storytelling_scene_lore_item_associations_lore_item_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_scene_lore_item_associations_lore_item_id_idx ON public.storytelling_scene_lore_item_associations USING btree (lore_item_id);


--
-- Name: storytelling_scene_lore_item_associations_scene_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_scene_lore_item_associations_scene_id_idx ON public.storytelling_scene_lore_item_associations USING btree (scene_id);


--
-- Name: storytelling_scenes_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_scenes_id_idx ON public.storytelling_scenes USING btree (id);


--
-- Name: storytelling_scenes_story_class_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_scenes_story_class_id_idx ON public.storytelling_scenes USING btree (story_class_id);


--
-- Name: storytelling_stories_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_stories_id_idx ON public.storytelling_stories USING btree (id);


--
-- Name: storytelling_stories_story_type_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_stories_story_type_idx ON public.storytelling_stories USING btree (story_type);


--
-- Name: storytelling_stories_title_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_stories_title_idx ON public.storytelling_stories USING btree (title);


--
-- Name: storytelling_stories_user_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_stories_user_id_idx ON public.storytelling_stories USING btree (user_id);


--
-- Name: storytelling_stories_world_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_stories_world_id_idx ON public.storytelling_stories USING btree (world_id);


--
-- Name: storytelling_story_character_associations_character_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_character_associations_character_id_idx ON public.storytelling_story_character_associations USING btree (character_id);


--
-- Name: storytelling_story_character_associations_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_character_associations_id_idx ON public.storytelling_story_character_associations USING btree (id);


--
-- Name: storytelling_story_character_associations_story_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_character_associations_story_id_idx ON public.storytelling_story_character_associations USING btree (story_id);


--
-- Name: storytelling_story_chat_messages_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_chat_messages_id_idx ON public.storytelling_story_chat_messages USING btree (id);


--
-- Name: storytelling_story_chat_messages_session_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_chat_messages_session_id_idx ON public.storytelling_story_chat_messages USING btree (session_id);


--
-- Name: storytelling_story_chat_sessions_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_chat_sessions_id_idx ON public.storytelling_story_chat_sessions USING btree (id);


--
-- Name: storytelling_story_chat_sessions_story_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_chat_sessions_story_id_idx ON public.storytelling_story_chat_sessions USING btree (story_id);


--
-- Name: storytelling_story_chat_sessions_user_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_chat_sessions_user_id_idx ON public.storytelling_story_chat_sessions USING btree (user_id);


--
-- Name: storytelling_story_classes_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_classes_id_idx ON public.storytelling_story_classes USING btree (id);


--
-- Name: storytelling_story_classes_name_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_classes_name_idx ON public.storytelling_story_classes USING btree (name);


--
-- Name: storytelling_story_classes_world_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_classes_world_id_idx ON public.storytelling_story_classes USING btree (world_id);


--
-- Name: storytelling_story_comments_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_comments_id_idx ON public.storytelling_story_comments USING btree (id);


--
-- Name: storytelling_story_comments_is_approved_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_comments_is_approved_idx ON public.storytelling_story_comments USING btree (is_approved);


--
-- Name: storytelling_story_comments_is_deleted_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_comments_is_deleted_idx ON public.storytelling_story_comments USING btree (is_deleted);


--
-- Name: storytelling_story_comments_parent_comment_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_comments_parent_comment_id_idx ON public.storytelling_story_comments USING btree (parent_comment_id);


--
-- Name: storytelling_story_comments_published_story_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_comments_published_story_id_idx ON public.storytelling_story_comments USING btree (published_story_id);


--
-- Name: storytelling_story_comments_user_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_comments_user_id_idx ON public.storytelling_story_comments USING btree (user_id);


--
-- Name: storytelling_story_location_associations_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_location_associations_id_idx ON public.storytelling_story_location_associations USING btree (id);


--
-- Name: storytelling_story_location_associations_location_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_location_associations_location_id_idx ON public.storytelling_story_location_associations USING btree (location_id);


--
-- Name: storytelling_story_location_associations_story_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_location_associations_story_id_idx ON public.storytelling_story_location_associations USING btree (story_id);


--
-- Name: storytelling_story_lore_item_associations_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_lore_item_associations_id_idx ON public.storytelling_story_lore_item_associations USING btree (id);


--
-- Name: storytelling_story_lore_item_associations_lore_item_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_lore_item_associations_lore_item_id_idx ON public.storytelling_story_lore_item_associations USING btree (lore_item_id);


--
-- Name: storytelling_story_lore_item_associations_story_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_lore_item_associations_story_id_idx ON public.storytelling_story_lore_item_associations USING btree (story_id);


--
-- Name: storytelling_story_ratings_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_ratings_id_idx ON public.storytelling_story_ratings USING btree (id);


--
-- Name: storytelling_story_ratings_published_story_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_ratings_published_story_id_idx ON public.storytelling_story_ratings USING btree (published_story_id);


--
-- Name: storytelling_story_ratings_user_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_story_ratings_user_id_idx ON public.storytelling_story_ratings USING btree (user_id);


--
-- Name: storytelling_user_interview_responses_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_user_interview_responses_id_idx ON public.storytelling_user_interview_responses USING btree (id);


--
-- Name: storytelling_user_interview_responses_interview_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_user_interview_responses_interview_id_idx ON public.storytelling_user_interview_responses USING btree (interview_id);


--
-- Name: storytelling_world_collaborators_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_world_collaborators_id_idx ON public.storytelling_world_collaborators USING btree (id);


--
-- Name: storytelling_world_collaborators_user_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_world_collaborators_user_id_idx ON public.storytelling_world_collaborators USING btree (user_id);


--
-- Name: storytelling_world_collaborators_world_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_world_collaborators_world_id_idx ON public.storytelling_world_collaborators USING btree (world_id);


--
-- Name: storytelling_world_roles_created_by_user_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_world_roles_created_by_user_id_idx ON public.storytelling_world_roles USING btree (created_by_user_id);


--
-- Name: storytelling_world_roles_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_world_roles_id_idx ON public.storytelling_world_roles USING btree (id);


--
-- Name: storytelling_world_roles_is_predefined_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_world_roles_is_predefined_idx ON public.storytelling_world_roles USING btree (is_predefined);


--
-- Name: storytelling_world_roles_world_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_world_roles_world_id_idx ON public.storytelling_world_roles USING btree (world_id);


--
-- Name: storytelling_worlds_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_worlds_id_idx ON public.storytelling_worlds USING btree (id);


--
-- Name: storytelling_worlds_is_free_chat_enabled_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_worlds_is_free_chat_enabled_idx ON public.storytelling_worlds USING btree (is_free_chat_enabled);


--
-- Name: storytelling_worlds_is_shadow_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_worlds_is_shadow_idx ON public.storytelling_worlds USING btree (is_shadow);


--
-- Name: storytelling_worlds_name_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_worlds_name_idx ON public.storytelling_worlds USING btree (name);


--
-- Name: storytelling_worlds_user_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX storytelling_worlds_user_id_idx ON public.storytelling_worlds USING btree (user_id);


--
-- Name: act_character_associations act_character_associations_act_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.act_character_associations
    ADD CONSTRAINT act_character_associations_act_id_fkey FOREIGN KEY (act_id) REFERENCES public.acts(id) ON DELETE CASCADE;


--
-- Name: act_character_associations act_character_associations_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.act_character_associations
    ADD CONSTRAINT act_character_associations_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.characters(id) ON DELETE CASCADE;


--
-- Name: act_location_associations act_location_associations_act_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.act_location_associations
    ADD CONSTRAINT act_location_associations_act_id_fkey FOREIGN KEY (act_id) REFERENCES public.acts(id) ON DELETE CASCADE;


--
-- Name: act_location_associations act_location_associations_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.act_location_associations
    ADD CONSTRAINT act_location_associations_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE CASCADE;


--
-- Name: act_lore_item_associations act_lore_item_associations_act_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.act_lore_item_associations
    ADD CONSTRAINT act_lore_item_associations_act_id_fkey FOREIGN KEY (act_id) REFERENCES public.acts(id) ON DELETE CASCADE;


--
-- Name: act_lore_item_associations act_lore_item_associations_lore_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.act_lore_item_associations
    ADD CONSTRAINT act_lore_item_associations_lore_item_id_fkey FOREIGN KEY (lore_item_id) REFERENCES public.lore_items(id) ON DELETE CASCADE;


--
-- Name: acts acts_current_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.acts
    ADD CONSTRAINT acts_current_image_id_fkey FOREIGN KEY (current_image_id) REFERENCES public.generated_images(id) ON DELETE SET NULL;


--
-- Name: acts acts_story_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.acts
    ADD CONSTRAINT acts_story_class_id_fkey FOREIGN KEY (story_class_id) REFERENCES public.story_classes(id) ON DELETE SET NULL;


--
-- Name: acts acts_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.acts
    ADD CONSTRAINT acts_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.stories(id) ON DELETE CASCADE;


--
-- Name: acts acts_system_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.acts
    ADD CONSTRAINT acts_system_prompt_id_fkey FOREIGN KEY (system_prompt_id) REFERENCES public.prompts(id) ON DELETE SET NULL;


--
-- Name: ai_call_logs ai_call_logs_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_call_logs
    ADD CONSTRAINT ai_call_logs_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.job_statuses(job_id);


--
-- Name: ai_call_logs ai_call_logs_model_config_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_call_logs
    ADD CONSTRAINT ai_call_logs_model_config_id_fkey FOREIGN KEY (model_config_id) REFERENCES public.ai_model_configurations(id);


--
-- Name: ai_call_logs ai_call_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_call_logs
    ADD CONSTRAINT ai_call_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: anonymous_user_sessions anonymous_user_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anonymous_user_sessions
    ADD CONSTRAINT anonymous_user_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: blog_analytics_summary blog_analytics_summary_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_analytics_summary
    ADD CONSTRAINT blog_analytics_summary_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.blog_posts(id) ON DELETE CASCADE;


--
-- Name: blog_author_profiles blog_author_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_author_profiles
    ADD CONSTRAINT blog_author_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: blog_comments blog_comments_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_comments
    ADD CONSTRAINT blog_comments_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: blog_comments blog_comments_parent_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_comments
    ADD CONSTRAINT blog_comments_parent_comment_id_fkey FOREIGN KEY (parent_comment_id) REFERENCES public.blog_comments(id) ON DELETE CASCADE;


--
-- Name: blog_comments blog_comments_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_comments
    ADD CONSTRAINT blog_comments_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.blog_posts(id) ON DELETE CASCADE;


--
-- Name: blog_content_links blog_content_links_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_content_links
    ADD CONSTRAINT blog_content_links_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.blog_posts(id) ON DELETE CASCADE;


--
-- Name: blog_follows blog_follows_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_follows
    ADD CONSTRAINT blog_follows_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: blog_follows blog_follows_follower_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_follows
    ADD CONSTRAINT blog_follows_follower_id_fkey FOREIGN KEY (follower_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: blog_likes blog_likes_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_likes
    ADD CONSTRAINT blog_likes_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.blog_posts(id) ON DELETE CASCADE;


--
-- Name: blog_likes blog_likes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_likes
    ADD CONSTRAINT blog_likes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: blog_post_associations blog_post_associations_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_post_associations
    ADD CONSTRAINT blog_post_associations_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.blog_posts(id) ON DELETE CASCADE;


--
-- Name: blog_post_tags blog_post_tags_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_post_tags
    ADD CONSTRAINT blog_post_tags_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.blog_posts(id) ON DELETE CASCADE;


--
-- Name: blog_post_tags blog_post_tags_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_post_tags
    ADD CONSTRAINT blog_post_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.blog_tags(id) ON DELETE CASCADE;


--
-- Name: blog_posts blog_posts_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_posts
    ADD CONSTRAINT blog_posts_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: blog_posts blog_posts_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_posts
    ADD CONSTRAINT blog_posts_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.blog_categories(id) ON DELETE SET NULL;


--
-- Name: blog_subscriptions blog_subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_subscriptions
    ADD CONSTRAINT blog_subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: blog_views blog_views_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_views
    ADD CONSTRAINT blog_views_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.blog_posts(id) ON DELETE CASCADE;


--
-- Name: blog_views blog_views_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blog_views
    ADD CONSTRAINT blog_views_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: brainstorm_favorites brainstorm_favorites_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.brainstorm_favorites
    ADD CONSTRAINT brainstorm_favorites_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.brainstorm_sessions(id);


--
-- Name: brainstorm_favorites brainstorm_favorites_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.brainstorm_favorites
    ADD CONSTRAINT brainstorm_favorites_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: brainstorm_sessions brainstorm_sessions_interview_response_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.brainstorm_sessions
    ADD CONSTRAINT brainstorm_sessions_interview_response_id_fkey FOREIGN KEY (interview_response_id) REFERENCES public.user_interview_responses(id);


--
-- Name: brainstorm_sessions brainstorm_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.brainstorm_sessions
    ADD CONSTRAINT brainstorm_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: brainstorm_stories brainstorm_stories_favorite_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.brainstorm_stories
    ADD CONSTRAINT brainstorm_stories_favorite_id_fkey FOREIGN KEY (favorite_id) REFERENCES public.brainstorm_favorites(id);


--
-- Name: brainstorm_stories brainstorm_stories_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.brainstorm_stories
    ADD CONSTRAINT brainstorm_stories_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.stories(id);


--
-- Name: brainstorm_stories brainstorm_stories_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.brainstorm_stories
    ADD CONSTRAINT brainstorm_stories_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: care_circle_families care_circle_families_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_families
    ADD CONSTRAINT care_circle_families_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: care_circle_family_memberships care_circle_family_memberships_family_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_family_memberships
    ADD CONSTRAINT care_circle_family_memberships_family_id_fkey FOREIGN KEY (family_id) REFERENCES public.care_circle_families(id) ON DELETE CASCADE;


--
-- Name: care_circle_family_memberships care_circle_family_memberships_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_family_memberships
    ADD CONSTRAINT care_circle_family_memberships_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: care_circle_patient_content_cards care_circle_patient_content_cards_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_patient_content_cards
    ADD CONSTRAINT care_circle_patient_content_cards_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.care_circle_patient_profiles(id) ON DELETE CASCADE;


--
-- Name: care_circle_patient_profiles care_circle_patient_profiles_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_patient_profiles
    ADD CONSTRAINT care_circle_patient_profiles_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: care_circle_patient_profiles care_circle_patient_profiles_family_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_patient_profiles
    ADD CONSTRAINT care_circle_patient_profiles_family_id_fkey FOREIGN KEY (family_id) REFERENCES public.care_circle_families(id) ON DELETE CASCADE;


--
-- Name: care_circle_provider_patient_configs care_circle_provider_patient_configs_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_provider_patient_configs
    ADD CONSTRAINT care_circle_provider_patient_configs_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.care_circle_patient_profiles(id) ON DELETE CASCADE;


--
-- Name: care_circle_provider_run_logs care_circle_provider_run_logs_family_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_provider_run_logs
    ADD CONSTRAINT care_circle_provider_run_logs_family_id_fkey FOREIGN KEY (family_id) REFERENCES public.care_circle_families(id) ON DELETE SET NULL;


--
-- Name: care_circle_provider_run_logs care_circle_provider_run_logs_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_provider_run_logs
    ADD CONSTRAINT care_circle_provider_run_logs_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.care_circle_patient_profiles(id) ON DELETE SET NULL;


--
-- Name: care_circle_provider_session_outputs care_circle_provider_session_outputs_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_provider_session_outputs
    ADD CONSTRAINT care_circle_provider_session_outputs_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.care_circle_patient_profiles(id) ON DELETE CASCADE;


--
-- Name: care_circle_provider_session_outputs care_circle_provider_session_outputs_run_log_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_circle_provider_session_outputs
    ADD CONSTRAINT care_circle_provider_session_outputs_run_log_id_fkey FOREIGN KEY (run_log_id) REFERENCES public.care_circle_provider_run_logs(id) ON DELETE SET NULL;


--
-- Name: characters characters_current_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.characters
    ADD CONSTRAINT characters_current_image_id_fkey FOREIGN KEY (current_image_id) REFERENCES public.generated_images(id) ON DELETE SET NULL;


--
-- Name: characters characters_current_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.characters
    ADD CONSTRAINT characters_current_location_id_fkey FOREIGN KEY (current_location_id) REFERENCES public.locations(id) ON DELETE SET NULL;


--
-- Name: characters characters_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.characters
    ADD CONSTRAINT characters_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.worlds(id) ON DELETE CASCADE;


--
-- Name: chat_messages chat_messages_cost_log_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_cost_log_id_fkey FOREIGN KEY (cost_log_id) REFERENCES public.ai_call_logs(id) ON DELETE SET NULL;


--
-- Name: chat_messages chat_messages_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.chat_sessions(id) ON DELETE CASCADE;


--
-- Name: chat_sessions chat_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: chat_sessions chat_sessions_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.storytelling_worlds(id) ON DELETE CASCADE;


--
-- Name: forum_posts forum_posts_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_posts
    ADD CONSTRAINT forum_posts_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.storytelling_characters(id) ON DELETE SET NULL;


--
-- Name: forum_posts forum_posts_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_posts
    ADD CONSTRAINT forum_posts_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: forum_posts forum_posts_edited_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_posts
    ADD CONSTRAINT forum_posts_edited_by_id_fkey FOREIGN KEY (edited_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: forum_posts forum_posts_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_posts
    ADD CONSTRAINT forum_posts_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.storytelling_locations(id) ON DELETE SET NULL;


--
-- Name: forum_posts forum_posts_parent_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_posts
    ADD CONSTRAINT forum_posts_parent_post_id_fkey FOREIGN KEY (parent_post_id) REFERENCES public.forum_posts(id) ON DELETE CASCADE;


--
-- Name: forum_posts forum_posts_thread_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_posts
    ADD CONSTRAINT forum_posts_thread_id_fkey FOREIGN KEY (thread_id) REFERENCES public.forum_threads(id) ON DELETE CASCADE;


--
-- Name: forum_posts forum_posts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_posts
    ADD CONSTRAINT forum_posts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: forum_subscriptions forum_subscriptions_thread_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_subscriptions
    ADD CONSTRAINT forum_subscriptions_thread_id_fkey FOREIGN KEY (thread_id) REFERENCES public.forum_threads(id) ON DELETE CASCADE;


--
-- Name: forum_subscriptions forum_subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_subscriptions
    ADD CONSTRAINT forum_subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: forum_threads forum_threads_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_threads
    ADD CONSTRAINT forum_threads_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.forum_categories(id) ON DELETE CASCADE;


--
-- Name: forum_threads forum_threads_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_threads
    ADD CONSTRAINT forum_threads_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: forum_threads forum_threads_last_post_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_threads
    ADD CONSTRAINT forum_threads_last_post_by_id_fkey FOREIGN KEY (last_post_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: forum_threads forum_threads_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_threads
    ADD CONSTRAINT forum_threads_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.storytelling_stories(id) ON DELETE SET NULL;


--
-- Name: forum_threads forum_threads_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_threads
    ADD CONSTRAINT forum_threads_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: forum_threads forum_threads_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_threads
    ADD CONSTRAINT forum_threads_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.storytelling_worlds(id) ON DELETE SET NULL;


--
-- Name: forum_votes forum_votes_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_votes
    ADD CONSTRAINT forum_votes_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.forum_posts(id) ON DELETE CASCADE;


--
-- Name: forum_votes forum_votes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forum_votes
    ADD CONSTRAINT forum_votes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: generated_images generated_images_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.generated_images
    ADD CONSTRAINT generated_images_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: job_statuses job_statuses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_statuses
    ADD CONSTRAINT job_statuses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: job_statuses job_statuses_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_statuses
    ADD CONSTRAINT job_statuses_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.storytelling_worlds(id) ON DELETE SET NULL;


--
-- Name: location_connections location_connections_from_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.location_connections
    ADD CONSTRAINT location_connections_from_location_id_fkey FOREIGN KEY (from_location_id) REFERENCES public.locations(id) ON DELETE CASCADE;


--
-- Name: location_connections location_connections_to_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.location_connections
    ADD CONSTRAINT location_connections_to_location_id_fkey FOREIGN KEY (to_location_id) REFERENCES public.locations(id) ON DELETE CASCADE;


--
-- Name: locations locations_current_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_current_image_id_fkey FOREIGN KEY (current_image_id) REFERENCES public.generated_images(id) ON DELETE SET NULL;


--
-- Name: locations locations_parent_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_parent_location_id_fkey FOREIGN KEY (parent_location_id) REFERENCES public.locations(id) ON DELETE SET NULL;


--
-- Name: locations locations_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.worlds(id) ON DELETE CASCADE;


--
-- Name: lore_items lore_items_current_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lore_items
    ADD CONSTRAINT lore_items_current_image_id_fkey FOREIGN KEY (current_image_id) REFERENCES public.generated_images(id) ON DELETE SET NULL;


--
-- Name: lore_items lore_items_current_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lore_items
    ADD CONSTRAINT lore_items_current_location_id_fkey FOREIGN KEY (current_location_id) REFERENCES public.locations(id) ON DELETE SET NULL;


--
-- Name: lore_items lore_items_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lore_items
    ADD CONSTRAINT lore_items_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.worlds(id) ON DELETE CASCADE;


--
-- Name: prompts prompts_last_updated_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prompts
    ADD CONSTRAINT prompts_last_updated_by_user_id_fkey FOREIGN KEY (last_updated_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: prompts prompts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prompts
    ADD CONSTRAINT prompts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: published_stories published_stories_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.published_stories
    ADD CONSTRAINT published_stories_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.stories(id) ON DELETE CASCADE;


--
-- Name: published_stories published_stories_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.published_stories
    ADD CONSTRAINT published_stories_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: refresh_tokens refresh_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: scene_character_associations scene_character_associations_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scene_character_associations
    ADD CONSTRAINT scene_character_associations_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.characters(id) ON DELETE CASCADE;


--
-- Name: scene_character_associations scene_character_associations_scene_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scene_character_associations
    ADD CONSTRAINT scene_character_associations_scene_id_fkey FOREIGN KEY (scene_id) REFERENCES public.scenes(id) ON DELETE CASCADE;


--
-- Name: scene_location_associations scene_location_associations_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scene_location_associations
    ADD CONSTRAINT scene_location_associations_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE CASCADE;


--
-- Name: scene_location_associations scene_location_associations_scene_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scene_location_associations
    ADD CONSTRAINT scene_location_associations_scene_id_fkey FOREIGN KEY (scene_id) REFERENCES public.scenes(id) ON DELETE CASCADE;


--
-- Name: scene_lore_item_associations scene_lore_item_associations_lore_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scene_lore_item_associations
    ADD CONSTRAINT scene_lore_item_associations_lore_item_id_fkey FOREIGN KEY (lore_item_id) REFERENCES public.lore_items(id) ON DELETE CASCADE;


--
-- Name: scene_lore_item_associations scene_lore_item_associations_scene_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scene_lore_item_associations
    ADD CONSTRAINT scene_lore_item_associations_scene_id_fkey FOREIGN KEY (scene_id) REFERENCES public.scenes(id) ON DELETE CASCADE;


--
-- Name: scenes scenes_act_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scenes
    ADD CONSTRAINT scenes_act_id_fkey FOREIGN KEY (act_id) REFERENCES public.acts(id) ON DELETE CASCADE;


--
-- Name: scenes scenes_current_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scenes
    ADD CONSTRAINT scenes_current_image_id_fkey FOREIGN KEY (current_image_id) REFERENCES public.generated_images(id) ON DELETE SET NULL;


--
-- Name: scenes scenes_story_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scenes
    ADD CONSTRAINT scenes_story_class_id_fkey FOREIGN KEY (story_class_id) REFERENCES public.story_classes(id) ON DELETE SET NULL;


--
-- Name: social_share_daily_summaries social_share_daily_summaries_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.social_share_daily_summaries
    ADD CONSTRAINT social_share_daily_summaries_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: social_shares social_shares_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.social_shares
    ADD CONSTRAINT social_shares_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: stories stories_current_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stories
    ADD CONSTRAINT stories_current_image_id_fkey FOREIGN KEY (current_image_id) REFERENCES public.generated_images(id) ON DELETE SET NULL;


--
-- Name: stories stories_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stories
    ADD CONSTRAINT stories_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: stories stories_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stories
    ADD CONSTRAINT stories_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.worlds(id) ON DELETE RESTRICT;


--
-- Name: story_character_association story_character_association_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_character_association
    ADD CONSTRAINT story_character_association_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.storytelling_characters(id) ON DELETE CASCADE;


--
-- Name: story_character_association story_character_association_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_character_association
    ADD CONSTRAINT story_character_association_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.storytelling_stories(id) ON DELETE CASCADE;


--
-- Name: story_character_associations story_character_associations_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_character_associations
    ADD CONSTRAINT story_character_associations_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.characters(id) ON DELETE CASCADE;


--
-- Name: story_character_associations story_character_associations_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_character_associations
    ADD CONSTRAINT story_character_associations_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.stories(id) ON DELETE CASCADE;


--
-- Name: story_chat_messages story_chat_messages_cost_log_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_chat_messages
    ADD CONSTRAINT story_chat_messages_cost_log_id_fkey FOREIGN KEY (cost_log_id) REFERENCES public.ai_call_logs(id) ON DELETE SET NULL;


--
-- Name: story_chat_messages story_chat_messages_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_chat_messages
    ADD CONSTRAINT story_chat_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.story_chat_sessions(id) ON DELETE CASCADE;


--
-- Name: story_chat_sessions story_chat_sessions_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_chat_sessions
    ADD CONSTRAINT story_chat_sessions_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.stories(id) ON DELETE CASCADE;


--
-- Name: story_chat_sessions story_chat_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_chat_sessions
    ADD CONSTRAINT story_chat_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: story_classes story_classes_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_classes
    ADD CONSTRAINT story_classes_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.worlds(id) ON DELETE CASCADE;


--
-- Name: story_comments story_comments_parent_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_comments
    ADD CONSTRAINT story_comments_parent_comment_id_fkey FOREIGN KEY (parent_comment_id) REFERENCES public.story_comments(id) ON DELETE CASCADE;


--
-- Name: story_comments story_comments_published_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_comments
    ADD CONSTRAINT story_comments_published_story_id_fkey FOREIGN KEY (published_story_id) REFERENCES public.published_stories(id) ON DELETE CASCADE;


--
-- Name: story_comments story_comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_comments
    ADD CONSTRAINT story_comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: story_location_association story_location_association_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_location_association
    ADD CONSTRAINT story_location_association_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.storytelling_locations(id) ON DELETE CASCADE;


--
-- Name: story_location_association story_location_association_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_location_association
    ADD CONSTRAINT story_location_association_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.storytelling_stories(id) ON DELETE CASCADE;


--
-- Name: story_location_associations story_location_associations_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_location_associations
    ADD CONSTRAINT story_location_associations_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE CASCADE;


--
-- Name: story_location_associations story_location_associations_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_location_associations
    ADD CONSTRAINT story_location_associations_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.stories(id) ON DELETE CASCADE;


--
-- Name: story_lore_item_association story_lore_item_association_lore_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_lore_item_association
    ADD CONSTRAINT story_lore_item_association_lore_item_id_fkey FOREIGN KEY (lore_item_id) REFERENCES public.storytelling_lore_items(id) ON DELETE CASCADE;


--
-- Name: story_lore_item_association story_lore_item_association_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_lore_item_association
    ADD CONSTRAINT story_lore_item_association_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.storytelling_stories(id) ON DELETE CASCADE;


--
-- Name: story_lore_item_associations story_lore_item_associations_lore_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_lore_item_associations
    ADD CONSTRAINT story_lore_item_associations_lore_item_id_fkey FOREIGN KEY (lore_item_id) REFERENCES public.lore_items(id) ON DELETE CASCADE;


--
-- Name: story_lore_item_associations story_lore_item_associations_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_lore_item_associations
    ADD CONSTRAINT story_lore_item_associations_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.stories(id) ON DELETE CASCADE;


--
-- Name: story_ratings story_ratings_published_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_ratings
    ADD CONSTRAINT story_ratings_published_story_id_fkey FOREIGN KEY (published_story_id) REFERENCES public.published_stories(id) ON DELETE CASCADE;


--
-- Name: story_ratings story_ratings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_ratings
    ADD CONSTRAINT story_ratings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: storytelling_act_character_associations storytelling_act_character_associations_act_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_act_character_associations
    ADD CONSTRAINT storytelling_act_character_associations_act_id_fkey FOREIGN KEY (act_id) REFERENCES public.storytelling_acts(id) ON DELETE CASCADE;


--
-- Name: storytelling_act_character_associations storytelling_act_character_associations_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_act_character_associations
    ADD CONSTRAINT storytelling_act_character_associations_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.storytelling_characters(id) ON DELETE CASCADE;


--
-- Name: storytelling_act_location_associations storytelling_act_location_associations_act_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_act_location_associations
    ADD CONSTRAINT storytelling_act_location_associations_act_id_fkey FOREIGN KEY (act_id) REFERENCES public.storytelling_acts(id) ON DELETE CASCADE;


--
-- Name: storytelling_act_location_associations storytelling_act_location_associations_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_act_location_associations
    ADD CONSTRAINT storytelling_act_location_associations_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.storytelling_locations(id) ON DELETE CASCADE;


--
-- Name: storytelling_act_lore_item_associations storytelling_act_lore_item_associations_act_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_act_lore_item_associations
    ADD CONSTRAINT storytelling_act_lore_item_associations_act_id_fkey FOREIGN KEY (act_id) REFERENCES public.storytelling_acts(id) ON DELETE CASCADE;


--
-- Name: storytelling_act_lore_item_associations storytelling_act_lore_item_associations_lore_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_act_lore_item_associations
    ADD CONSTRAINT storytelling_act_lore_item_associations_lore_item_id_fkey FOREIGN KEY (lore_item_id) REFERENCES public.storytelling_lore_items(id) ON DELETE CASCADE;


--
-- Name: storytelling_acts storytelling_acts_current_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_acts
    ADD CONSTRAINT storytelling_acts_current_image_id_fkey FOREIGN KEY (current_image_id) REFERENCES public.generated_images(id) ON DELETE SET NULL;


--
-- Name: storytelling_acts storytelling_acts_story_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_acts
    ADD CONSTRAINT storytelling_acts_story_class_id_fkey FOREIGN KEY (story_class_id) REFERENCES public.storytelling_story_classes(id) ON DELETE SET NULL;


--
-- Name: storytelling_acts storytelling_acts_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_acts
    ADD CONSTRAINT storytelling_acts_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.storytelling_stories(id) ON DELETE CASCADE;


--
-- Name: storytelling_acts storytelling_acts_system_prompt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_acts
    ADD CONSTRAINT storytelling_acts_system_prompt_id_fkey FOREIGN KEY (system_prompt_id) REFERENCES public.prompts(id) ON DELETE SET NULL;


--
-- Name: storytelling_brainstorm_favorites storytelling_brainstorm_favorites_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_brainstorm_favorites
    ADD CONSTRAINT storytelling_brainstorm_favorites_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.storytelling_brainstorm_sessions(id);


--
-- Name: storytelling_brainstorm_favorites storytelling_brainstorm_favorites_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_brainstorm_favorites
    ADD CONSTRAINT storytelling_brainstorm_favorites_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: storytelling_brainstorm_sessions storytelling_brainstorm_sessions_interview_response_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_brainstorm_sessions
    ADD CONSTRAINT storytelling_brainstorm_sessions_interview_response_id_fkey FOREIGN KEY (interview_response_id) REFERENCES public.storytelling_user_interview_responses(id);


--
-- Name: storytelling_brainstorm_sessions storytelling_brainstorm_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_brainstorm_sessions
    ADD CONSTRAINT storytelling_brainstorm_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: storytelling_brainstorm_stories storytelling_brainstorm_stories_favorite_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_brainstorm_stories
    ADD CONSTRAINT storytelling_brainstorm_stories_favorite_id_fkey FOREIGN KEY (favorite_id) REFERENCES public.storytelling_brainstorm_favorites(id);


--
-- Name: storytelling_brainstorm_stories storytelling_brainstorm_stories_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_brainstorm_stories
    ADD CONSTRAINT storytelling_brainstorm_stories_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.storytelling_stories(id);


--
-- Name: storytelling_brainstorm_stories storytelling_brainstorm_stories_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_brainstorm_stories
    ADD CONSTRAINT storytelling_brainstorm_stories_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: storytelling_characters storytelling_characters_current_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_characters
    ADD CONSTRAINT storytelling_characters_current_image_id_fkey FOREIGN KEY (current_image_id) REFERENCES public.generated_images(id) ON DELETE SET NULL;


--
-- Name: storytelling_characters storytelling_characters_current_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_characters
    ADD CONSTRAINT storytelling_characters_current_location_id_fkey FOREIGN KEY (current_location_id) REFERENCES public.storytelling_locations(id) ON DELETE SET NULL;


--
-- Name: storytelling_characters storytelling_characters_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_characters
    ADD CONSTRAINT storytelling_characters_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.storytelling_worlds(id) ON DELETE CASCADE;


--
-- Name: storytelling_location_connections storytelling_location_connections_from_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_location_connections
    ADD CONSTRAINT storytelling_location_connections_from_location_id_fkey FOREIGN KEY (from_location_id) REFERENCES public.storytelling_locations(id) ON DELETE CASCADE;


--
-- Name: storytelling_location_connections storytelling_location_connections_to_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_location_connections
    ADD CONSTRAINT storytelling_location_connections_to_location_id_fkey FOREIGN KEY (to_location_id) REFERENCES public.storytelling_locations(id) ON DELETE CASCADE;


--
-- Name: storytelling_locations storytelling_locations_current_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_locations
    ADD CONSTRAINT storytelling_locations_current_image_id_fkey FOREIGN KEY (current_image_id) REFERENCES public.generated_images(id) ON DELETE SET NULL;


--
-- Name: storytelling_locations storytelling_locations_parent_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_locations
    ADD CONSTRAINT storytelling_locations_parent_location_id_fkey FOREIGN KEY (parent_location_id) REFERENCES public.storytelling_locations(id) ON DELETE SET NULL;


--
-- Name: storytelling_locations storytelling_locations_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_locations
    ADD CONSTRAINT storytelling_locations_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.storytelling_worlds(id) ON DELETE CASCADE;


--
-- Name: storytelling_lore_items storytelling_lore_items_current_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_lore_items
    ADD CONSTRAINT storytelling_lore_items_current_image_id_fkey FOREIGN KEY (current_image_id) REFERENCES public.generated_images(id) ON DELETE SET NULL;


--
-- Name: storytelling_lore_items storytelling_lore_items_current_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_lore_items
    ADD CONSTRAINT storytelling_lore_items_current_location_id_fkey FOREIGN KEY (current_location_id) REFERENCES public.storytelling_locations(id) ON DELETE SET NULL;


--
-- Name: storytelling_lore_items storytelling_lore_items_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_lore_items
    ADD CONSTRAINT storytelling_lore_items_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.storytelling_worlds(id) ON DELETE CASCADE;


--
-- Name: storytelling_published_stories storytelling_published_stories_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_published_stories
    ADD CONSTRAINT storytelling_published_stories_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.storytelling_stories(id) ON DELETE CASCADE;


--
-- Name: storytelling_published_stories storytelling_published_stories_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_published_stories
    ADD CONSTRAINT storytelling_published_stories_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: storytelling_scene_character_associations storytelling_scene_character_associations_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scene_character_associations
    ADD CONSTRAINT storytelling_scene_character_associations_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.storytelling_characters(id) ON DELETE CASCADE;


--
-- Name: storytelling_scene_character_associations storytelling_scene_character_associations_scene_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scene_character_associations
    ADD CONSTRAINT storytelling_scene_character_associations_scene_id_fkey FOREIGN KEY (scene_id) REFERENCES public.storytelling_scenes(id) ON DELETE CASCADE;


--
-- Name: storytelling_scene_location_associations storytelling_scene_location_associations_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scene_location_associations
    ADD CONSTRAINT storytelling_scene_location_associations_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.storytelling_locations(id) ON DELETE CASCADE;


--
-- Name: storytelling_scene_location_associations storytelling_scene_location_associations_scene_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scene_location_associations
    ADD CONSTRAINT storytelling_scene_location_associations_scene_id_fkey FOREIGN KEY (scene_id) REFERENCES public.storytelling_scenes(id) ON DELETE CASCADE;


--
-- Name: storytelling_scene_lore_item_associations storytelling_scene_lore_item_associations_lore_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scene_lore_item_associations
    ADD CONSTRAINT storytelling_scene_lore_item_associations_lore_item_id_fkey FOREIGN KEY (lore_item_id) REFERENCES public.storytelling_lore_items(id) ON DELETE CASCADE;


--
-- Name: storytelling_scene_lore_item_associations storytelling_scene_lore_item_associations_scene_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scene_lore_item_associations
    ADD CONSTRAINT storytelling_scene_lore_item_associations_scene_id_fkey FOREIGN KEY (scene_id) REFERENCES public.storytelling_scenes(id) ON DELETE CASCADE;


--
-- Name: storytelling_scenes storytelling_scenes_act_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scenes
    ADD CONSTRAINT storytelling_scenes_act_id_fkey FOREIGN KEY (act_id) REFERENCES public.storytelling_acts(id) ON DELETE CASCADE;


--
-- Name: storytelling_scenes storytelling_scenes_current_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scenes
    ADD CONSTRAINT storytelling_scenes_current_image_id_fkey FOREIGN KEY (current_image_id) REFERENCES public.generated_images(id) ON DELETE SET NULL;


--
-- Name: storytelling_scenes storytelling_scenes_story_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_scenes
    ADD CONSTRAINT storytelling_scenes_story_class_id_fkey FOREIGN KEY (story_class_id) REFERENCES public.storytelling_story_classes(id) ON DELETE SET NULL;


--
-- Name: storytelling_stories storytelling_stories_current_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_stories
    ADD CONSTRAINT storytelling_stories_current_image_id_fkey FOREIGN KEY (current_image_id) REFERENCES public.generated_images(id) ON DELETE SET NULL;


--
-- Name: storytelling_stories storytelling_stories_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_stories
    ADD CONSTRAINT storytelling_stories_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: storytelling_stories storytelling_stories_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_stories
    ADD CONSTRAINT storytelling_stories_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.storytelling_worlds(id) ON DELETE RESTRICT;


--
-- Name: storytelling_story_character_associations storytelling_story_character_associations_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_character_associations
    ADD CONSTRAINT storytelling_story_character_associations_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.storytelling_characters(id) ON DELETE CASCADE;


--
-- Name: storytelling_story_character_associations storytelling_story_character_associations_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_character_associations
    ADD CONSTRAINT storytelling_story_character_associations_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.storytelling_stories(id) ON DELETE CASCADE;


--
-- Name: storytelling_story_chat_messages storytelling_story_chat_messages_cost_log_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_chat_messages
    ADD CONSTRAINT storytelling_story_chat_messages_cost_log_id_fkey FOREIGN KEY (cost_log_id) REFERENCES public.ai_call_logs(id) ON DELETE SET NULL;


--
-- Name: storytelling_story_chat_messages storytelling_story_chat_messages_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_chat_messages
    ADD CONSTRAINT storytelling_story_chat_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.storytelling_story_chat_sessions(id) ON DELETE CASCADE;


--
-- Name: storytelling_story_chat_sessions storytelling_story_chat_sessions_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_chat_sessions
    ADD CONSTRAINT storytelling_story_chat_sessions_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.storytelling_stories(id) ON DELETE CASCADE;


--
-- Name: storytelling_story_chat_sessions storytelling_story_chat_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_chat_sessions
    ADD CONSTRAINT storytelling_story_chat_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: storytelling_story_classes storytelling_story_classes_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_classes
    ADD CONSTRAINT storytelling_story_classes_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.storytelling_worlds(id) ON DELETE CASCADE;


--
-- Name: storytelling_story_comments storytelling_story_comments_parent_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_comments
    ADD CONSTRAINT storytelling_story_comments_parent_comment_id_fkey FOREIGN KEY (parent_comment_id) REFERENCES public.storytelling_story_comments(id) ON DELETE CASCADE;


--
-- Name: storytelling_story_comments storytelling_story_comments_published_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_comments
    ADD CONSTRAINT storytelling_story_comments_published_story_id_fkey FOREIGN KEY (published_story_id) REFERENCES public.storytelling_published_stories(id) ON DELETE CASCADE;


--
-- Name: storytelling_story_comments storytelling_story_comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_comments
    ADD CONSTRAINT storytelling_story_comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: storytelling_story_location_associations storytelling_story_location_associations_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_location_associations
    ADD CONSTRAINT storytelling_story_location_associations_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.storytelling_locations(id) ON DELETE CASCADE;


--
-- Name: storytelling_story_location_associations storytelling_story_location_associations_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_location_associations
    ADD CONSTRAINT storytelling_story_location_associations_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.storytelling_stories(id) ON DELETE CASCADE;


--
-- Name: storytelling_story_lore_item_associations storytelling_story_lore_item_associations_lore_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_lore_item_associations
    ADD CONSTRAINT storytelling_story_lore_item_associations_lore_item_id_fkey FOREIGN KEY (lore_item_id) REFERENCES public.storytelling_lore_items(id) ON DELETE CASCADE;


--
-- Name: storytelling_story_lore_item_associations storytelling_story_lore_item_associations_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_lore_item_associations
    ADD CONSTRAINT storytelling_story_lore_item_associations_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.storytelling_stories(id) ON DELETE CASCADE;


--
-- Name: storytelling_story_ratings storytelling_story_ratings_published_story_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_ratings
    ADD CONSTRAINT storytelling_story_ratings_published_story_id_fkey FOREIGN KEY (published_story_id) REFERENCES public.storytelling_published_stories(id) ON DELETE CASCADE;


--
-- Name: storytelling_story_ratings storytelling_story_ratings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_story_ratings
    ADD CONSTRAINT storytelling_story_ratings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: storytelling_user_interview_responses storytelling_user_interview_responses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_user_interview_responses
    ADD CONSTRAINT storytelling_user_interview_responses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: storytelling_world_collaborators storytelling_world_collaborators_invited_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_world_collaborators
    ADD CONSTRAINT storytelling_world_collaborators_invited_by_user_id_fkey FOREIGN KEY (invited_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: storytelling_world_collaborators storytelling_world_collaborators_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_world_collaborators
    ADD CONSTRAINT storytelling_world_collaborators_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: storytelling_world_collaborators storytelling_world_collaborators_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_world_collaborators
    ADD CONSTRAINT storytelling_world_collaborators_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.storytelling_worlds(id) ON DELETE CASCADE;


--
-- Name: storytelling_world_roles storytelling_world_roles_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_world_roles
    ADD CONSTRAINT storytelling_world_roles_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: storytelling_world_roles storytelling_world_roles_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_world_roles
    ADD CONSTRAINT storytelling_world_roles_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.storytelling_worlds(id) ON DELETE CASCADE;


--
-- Name: storytelling_worlds storytelling_worlds_current_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_worlds
    ADD CONSTRAINT storytelling_worlds_current_image_id_fkey FOREIGN KEY (current_image_id) REFERENCES public.generated_images(id) ON DELETE SET NULL;


--
-- Name: storytelling_worlds storytelling_worlds_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storytelling_worlds
    ADD CONSTRAINT storytelling_worlds_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: uploaded_documents uploaded_documents_source_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uploaded_documents
    ADD CONSTRAINT uploaded_documents_source_character_id_fkey FOREIGN KEY (source_character_id) REFERENCES public.storytelling_characters(id) ON DELETE SET NULL;


--
-- Name: uploaded_documents uploaded_documents_source_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uploaded_documents
    ADD CONSTRAINT uploaded_documents_source_location_id_fkey FOREIGN KEY (source_location_id) REFERENCES public.storytelling_locations(id) ON DELETE SET NULL;


--
-- Name: uploaded_documents uploaded_documents_source_lore_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uploaded_documents
    ADD CONSTRAINT uploaded_documents_source_lore_item_id_fkey FOREIGN KEY (source_lore_item_id) REFERENCES public.storytelling_lore_items(id) ON DELETE SET NULL;


--
-- Name: uploaded_documents uploaded_documents_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uploaded_documents
    ADD CONSTRAINT uploaded_documents_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: uploaded_documents uploaded_documents_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uploaded_documents
    ADD CONSTRAINT uploaded_documents_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.storytelling_worlds(id) ON DELETE SET NULL;


--
-- Name: user_accounts user_accounts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_accounts
    ADD CONSTRAINT user_accounts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_activities user_activities_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_activities
    ADD CONSTRAINT user_activities_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_interview_responses user_interview_responses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_interview_responses
    ADD CONSTRAINT user_interview_responses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_transactions user_transactions_ai_cost_log_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_transactions
    ADD CONSTRAINT user_transactions_ai_cost_log_id_fkey FOREIGN KEY (ai_cost_log_id) REFERENCES public.ai_call_logs(id) ON DELETE SET NULL;


--
-- Name: user_transactions user_transactions_credit_package_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_transactions
    ADD CONSTRAINT user_transactions_credit_package_id_fkey FOREIGN KEY (credit_package_id) REFERENCES public.credit_packages(id) ON DELETE SET NULL;


--
-- Name: user_transactions user_transactions_user_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_transactions
    ADD CONSTRAINT user_transactions_user_account_id_fkey FOREIGN KEY (user_account_id) REFERENCES public.user_accounts(id) ON DELETE CASCADE;


--
-- Name: users users_referred_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_referred_by_user_id_fkey FOREIGN KEY (referred_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: world_collaborators world_collaborators_invited_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.world_collaborators
    ADD CONSTRAINT world_collaborators_invited_by_user_id_fkey FOREIGN KEY (invited_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: world_collaborators world_collaborators_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.world_collaborators
    ADD CONSTRAINT world_collaborators_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: world_collaborators world_collaborators_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.world_collaborators
    ADD CONSTRAINT world_collaborators_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.worlds(id) ON DELETE CASCADE;


--
-- Name: world_roles world_roles_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.world_roles
    ADD CONSTRAINT world_roles_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: world_roles world_roles_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.world_roles
    ADD CONSTRAINT world_roles_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.worlds(id) ON DELETE CASCADE;


--
-- Name: worlds worlds_current_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.worlds
    ADD CONSTRAINT worlds_current_image_id_fkey FOREIGN KEY (current_image_id) REFERENCES public.generated_images(id) ON DELETE SET NULL;


--
-- Name: worlds worlds_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.worlds
    ADD CONSTRAINT worlds_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict SYs6sxL4ETBEpbv3rASBNeVYwgI311hvODct4p2E5UJVHXaw0IKwXeSSYHLS6jI

