--
-- PostgreSQL database dump
--

\restrict FGaHVuyov1bkWKrVwmMVuMX3DGA7RBRxYMYuWNqWunxGiRc9Js40DsooEOyFYAE

-- Dumped from database version 16.13 (Debian 16.13-1.pgdg12+1)
-- Dumped by pg_dump version 16.13 (Debian 16.13-1.pgdg12+1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: chat_messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_messages (
    id character varying NOT NULL,
    user_profile_id character varying,
    sender_name character varying,
    message_text text,
    created_at timestamp without time zone
);


--
-- Name: email_verifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.email_verifications (
    id character varying NOT NULL,
    user_id character varying,
    code character varying,
    expires_at timestamp without time zone,
    created_at timestamp without time zone
);


--
-- Name: families; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.families (
    id character varying NOT NULL,
    name character varying,
    join_code character varying,
    created_at timestamp without time zone
);


--
-- Name: hopper; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hopper (
    id character varying NOT NULL,
    user_profile_id character varying,
    submitter_name character varying,
    content_text text,
    image_url text,
    status character varying,
    created_at timestamp without time zone
);


--
-- Name: password_resets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.password_resets (
    id character varying NOT NULL,
    user_id character varying,
    code character varying,
    expires_at timestamp without time zone,
    created_at timestamp without time zone
);


--
-- Name: profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.profiles (
    id character varying NOT NULL,
    family_id character varying,
    user_id character varying,
    recipient_name character varying,
    printer_email character varying,
    auth_image_keys jsonb,
    preferences jsonb,
    created_at timestamp without time zone,
    difficulty character varying DEFAULT 'easy'::character varying
);


--
-- Name: provider_feedback; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.provider_feedback (
    id character varying NOT NULL,
    user_profile_id character varying,
    provider_name character varying,
    feedback_type character varying,
    created_at timestamp without time zone
);


--
-- Name: templates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.templates (
    id character varying NOT NULL,
    user_profile_id character varying,
    date timestamp without time zone,
    content_html text,
    status character varying
);


--
-- Name: user_families; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_families (
    id character varying NOT NULL,
    user_id character varying,
    family_id character varying,
    role character varying,
    is_primary boolean DEFAULT false,
    created_at timestamp without time zone
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id character varying NOT NULL,
    email character varying,
    name character varying,
    password_hash character varying,
    family_id character varying,
    role character varying,
    is_verified boolean,
    created_at timestamp without time zone
);


--
-- Data for Name: chat_messages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.chat_messages (id, user_profile_id, sender_name, message_text, created_at) FROM stdin;
7cc69bc589c4460ba2d9f3e0817f3c20	29fca03f603a4c92b006fad6555439d8	kkk	kkk	2026-03-14 20:49:41.800208
\.


--
-- Data for Name: email_verifications; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.email_verifications (id, user_id, code, expires_at, created_at) FROM stdin;
\.


--
-- Data for Name: families; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.families (id, name, join_code, created_at) FROM stdin;
fa99bad247e24dfbbbff90e004ce4d1d	Maple Grove	MAP111	2026-03-14 17:02:56.030394
f7213f3c5f7346c0b27b9fc4ffca6292	Harbor Point	HBR222	2026-03-14 17:02:56.030394
5ae49d56a4ad45338f6a92aede6ac672	Sunset Ridge	SUN333	2026-03-14 17:02:56.030394
\.


--
-- Data for Name: hopper; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hopper (id, user_profile_id, submitter_name, content_text, image_url, status, created_at) FROM stdin;
\.


--
-- Data for Name: password_resets; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.password_resets (id, user_id, code, expires_at, created_at) FROM stdin;
\.


--
-- Data for Name: profiles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.profiles (id, family_id, user_id, recipient_name, printer_email, auth_image_keys, preferences, created_at, difficulty) FROM stdin;
c3e9a73c060f4c3ea71514d9d37c6075	fa99bad247e24dfbbbff90e004ce4d1d	afc64a32ad0848e886f9f37127a249f4	Nina Maple	ericsilvertx+ninaprinter@gmail.com	["cake", "bird", "flower"]	{"hobbies": [], "era_of_youth": "1960s", "family_members": ["Clara", "Mason", "Taylor"], "favorite_singer": "Dolly Parton", "city_for_weather": "Waco, TX", "selected_providers": ["weather", "joke", "nostalgia", "daily_affirmation", "brain_booster", "sensory", "ai_trivia", "puzzle", "daily_quote", "gentle_exercise", "gratitude", "cat_fact", "dog_photo", "this_day_history", "finish_phrase", "odd_one_out", "riddle", "nature_scene", "simple_recipe", "missing_vowels", "word_scramble"], "favorite_activities": []}	2026-03-14 17:22:07.570632	easy
3cc443882f01423ba49f9614ed9101ec	f7213f3c5f7346c0b27b9fc4ffca6292	a4acabcac30049e9925f06c69f4af6ee	Olivia Harbor	ericsilvertx+oliviaprinter@gmail.com	["bird", "house", "tree"]	{"hobbies": [], "era_of_youth": "1950s", "family_members": ["Olivia", "Jack"], "favorite_singer": "Johnny Cash", "city_for_weather": "Portland, OR", "selected_providers": ["weather", "puzzle", "nostalgia", "riddle", "joke", "brain_booster", "dog_photo", "daily_affirmation", "this_day_history", "finish_phrase", "odd_one_out", "nature_scene", "cat_fact", "sensory", "ai_trivia", "gratitude", "simple_recipe", "missing_vowels", "word_scramble", "gentle_exercise", "daily_quote"], "favorite_activities": []}	2026-03-14 17:02:56.030394	easy
9aa669b657b949329cdf09af3eaa683e	fa99bad247e24dfbbbff90e004ce4d1d	2e28cb4cfd714d3b97b644153f9a8c7e	Mason Maple	ericsilvertx+masonprinter@gmail.com	["dog", "car", "tree"]	{"hobbies": [], "era_of_youth": "1950s", "include_jokes": true, "family_members": ["Clara", "Mason"], "favorite_singer": "Patsy Cline", "include_puzzles": true, "city_for_weather": "Austin, TX", "include_nostalgia": true, "selected_providers": ["weather", "joke", "nostalgia", "brain_booster", "cat_fact", "nature_scene", "simple_recipe", "this_day_history", "daily_affirmation"], "favorite_activities": [], "include_brain_boosters": true}	2026-03-14 17:02:56.030394	easy
88a52e36aaca4cc7a0fc5e1b8db7793e	f7213f3c5f7346c0b27b9fc4ffca6292	27c6950604dc45179de6ce3dc9c3e42d	Ethan Harbor	ericsilvertx+ethanprinter@gmail.com	["car", "sun", "bird"]	{"hobbies": [], "era_of_youth": "1960s", "family_members": ["Olivia", "Ethan"], "favorite_singer": "The Supremes", "city_for_weather": "Seattle, WA", "selected_providers": ["weather", "joke", "brain_booster", "daily_affirmation", "odd_one_out", "riddle", "nature_scene", "cat_fact", "gratitude", "gentle_exercise", "nostalgia", "sensory", "ai_trivia", "dog_photo", "this_day_history", "finish_phrase", "word_scramble", "missing_vowels", "simple_recipe", "puzzle", "daily_quote"], "favorite_activities": []}	2026-03-14 17:02:56.030394	easy
7addf21c29ac4191b0233436a1823d14	5ae49d56a4ad45338f6a92aede6ac672	173e41c13b0f43898237efe2edc5e248	Noah Sunset	ericsilvertx+noahprinter@gmail.com	["car", "dog", "bird"]	{"hobbies": ["quilting"], "era_of_youth": "1950s", "include_jokes": true, "family_members": ["Sophie", "Noah"], "favorite_singer": "Frank Sinatra", "include_puzzles": true, "city_for_weather": "Phoenix, AZ", "include_nostalgia": true, "selected_providers": ["weather", "joke", "nostalgia", "missing_vowels"], "favorite_activities": ["family calls"], "include_brain_boosters": false}	2026-03-14 17:02:56.030394	easy
69620653209a4d7793e5e9e59b9aae3d	5ae49d56a4ad45338f6a92aede6ac672	5c0efb55ff9a40629f3586b981f9dd8c	Sophie Sunset	ericsilvertx+sophieprinter@gmail.com	["flower", "tree", "sun"]	{"hobbies": ["photography"], "era_of_youth": "1970s", "include_jokes": true, "family_members": ["Sophie", "Maya"], "favorite_singer": "Carpenters", "include_puzzles": false, "city_for_weather": "Denver, CO", "include_nostalgia": true, "selected_providers": ["weather", "daily_quote", "nostalgia"], "favorite_activities": ["chai tea"], "include_brain_boosters": true}	2026-03-14 17:02:56.030394	easy
417a3741291f4510b2f39e711dfdefa9	fa99bad247e24dfbbbff90e004ce4d1d	9f21076a04df4c19800d5f5f7ba0d7a3	Clara Maple	ericsilvertx+claraprinter@gmail.com	["sun", "flower", "house"]	{"hobbies": [], "era_of_youth": "1940s", "family_members": ["Jenna", "Liam"], "favorite_singer": "Nat King Cole", "city_for_weather": "Dallas, TX", "selected_providers": ["weather", "nostalgia", "daily_quote", "joke", "puzzle", "ai_trivia", "sensory", "brain_booster"], "favorite_activities": []}	2026-03-14 17:02:56.030394	easy
9e3964503e59404ca617013ba6c3fc65	5ae49d56a4ad45338f6a92aede6ac672	4ac74113c215401da6dbb34843c050e8	Taylor Shared	ericsilvertx+taylor-sunset-printer@gmail.com	["flower", "tree", "cake"]	{"hobbies": ["podcasts"], "era_of_youth": "1970s", "include_jokes": true, "family_members": ["Sophie", "Noah", "Maya"], "favorite_singer": "Carole King", "include_puzzles": false, "city_for_weather": "Phoenix, AZ", "include_nostalgia": true, "selected_providers": ["weather", "daily_quote", "nostalgia"], "favorite_activities": ["family brunches"], "include_brain_boosters": true}	2026-03-14 17:22:07.570632	easy
4d1d0ad6d5514ac0a341c6ab58a26a30	f7213f3c5f7346c0b27b9fc4ffca6292	4ac74113c215401da6dbb34843c050e8	Taylor Shared	ericsilvertx+taylor-harbor-printer@gmail.com	["bird", "car", "house"]	{"hobbies": ["reading"], "era_of_youth": "1970s", "include_jokes": false, "family_members": ["Olivia", "Ethan", "Jack"], "favorite_singer": "Fleetwood Mac", "include_puzzles": true, "city_for_weather": "Seattle, WA", "include_nostalgia": true, "selected_providers": ["weather", "nostalgia", "puzzle"], "favorite_activities": ["walks by the water"], "include_brain_boosters": true}	2026-03-14 17:22:07.570632	easy
864d0ab0d9c0497b8c1e87310943f049	5ae49d56a4ad45338f6a92aede6ac672	5a24c5959fe144acb71ad1138c8d1a10	Maya Sunset	ericsilvertx+mayaprinter@gmail.com	["cake", "flower", "house"]	{"hobbies": ["watercolor"], "era_of_youth": "1990s", "include_jokes": true, "family_members": ["Sophie", "Noah", "Taylor"], "favorite_singer": "Celine Dion", "include_puzzles": true, "city_for_weather": "Scottsdale, AZ", "include_nostalgia": true, "selected_providers": ["weather", "joke", "nostalgia", "missing_vowels"], "favorite_activities": ["gardening", "sunrise walks"], "include_brain_boosters": false}	2026-03-14 17:22:07.570632	easy
c22ca0b89bfe4df59d3d98ad8652e9f6	f7213f3c5f7346c0b27b9fc4ffca6292	5e100203c18147ab9aadc595d3a2f6b6	Jack Harbor	ericsilvertx+jackprinter@gmail.com	["dog", "cake", "house"]	{"hobbies": [], "era_of_youth": "1980s", "family_members": ["Olivia", "Ethan", "Taylor"], "favorite_singer": "Hall & Oates", "city_for_weather": "Tacoma, WA", "selected_providers": ["weather", "joke", "brain_booster", "riddle", "sensory", "song_of_the_day", "finish_phrase", "odd_one_out", "word_scramble", "missing_vowels", "this_day_history", "daily_affirmation", "dog_photo", "nature_scene", "gratitude", "cat_fact", "ai_trivia", "nostalgia", "puzzle", "daily_quote", "gentle_exercise", "simple_recipe"], "favorite_activities": []}	2026-03-14 17:22:07.570632	easy
29fca03f603a4c92b006fad6555439d8	fa99bad247e24dfbbbff90e004ce4d1d	4ac74113c215401da6dbb34843c050e8	Taylor Shared	ericsilvertx+taylor-maple-printer@gmail.com	["sun", "dog", "cake"]	{"hobbies": [], "era_of_youth": "1970s", "family_members": ["Clara", "Mason", "Nina"], "favorite_singer": "James Taylor", "city_for_weather": "Austin, TX", "selected_providers": ["weather", "daily_quote", "nostalgia", "joke", "puzzle", "ai_trivia", "sensory", "brain_booster", "dog_photo", "cat_fact", "gratitude", "gentle_exercise", "simple_recipe", "nature_scene", "daily_affirmation", "this_day_history", "riddle", "missing_vowels", "word_scramble", "odd_one_out", "finish_phrase", "song_of_the_day"], "favorite_activities": []}	2026-03-14 17:22:07.570632	easy
\.


--
-- Data for Name: provider_feedback; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.provider_feedback (id, user_profile_id, provider_name, feedback_type, created_at) FROM stdin;
eed9f0dcb8214addadebd29f03b361fc	9aa669b657b949329cdf09af3eaa683e	weather	like	2026-03-14 20:51:28.274783
c92d9314c93746edb08cbac557fab58b	9aa669b657b949329cdf09af3eaa683e	joke	like	2026-03-14 20:51:30.331656
7016db4a48b84291a2adcae3c2ec7374	9aa669b657b949329cdf09af3eaa683e	nostalgia	like	2026-03-14 20:51:32.490101
c4ab044e0f7a433cabbd469c6acc57d8	c3e9a73c060f4c3ea71514d9d37c6075	daily_affirmation	like	2026-03-14 22:12:46.994227
ec6ab456c1744512b49291f71a1a4e56	c3e9a73c060f4c3ea71514d9d37c6075	nostalgia	like	2026-03-14 22:12:51.497144
bce7f72daed04e7197b5f1101775dfeb	c3e9a73c060f4c3ea71514d9d37c6075	joke	dislike	2026-03-14 22:12:58.64219
cd4004c8e9224dffa861842275015007	c22ca0b89bfe4df59d3d98ad8652e9f6	joke	like	2026-03-15 02:33:52.262727
2446f548cee44173a41bd283b00bfc53	69620653209a4d7793e5e9e59b9aae3d	nostalgia	like	2026-03-21 21:15:54.609805
f9a2c0c6829a466ebff6431f2638cbca	69620653209a4d7793e5e9e59b9aae3d	weather	like	2026-03-21 21:16:00.699764
\.


--
-- Data for Name: templates; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.templates (id, user_profile_id, date, content_html, status) FROM stdin;
\.


--
-- Data for Name: user_families; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_families (id, user_id, family_id, role, is_primary, created_at) FROM stdin;
704e0c38a70c43e1bede48ed5846ee3c	9f21076a04df4c19800d5f5f7ba0d7a3	fa99bad247e24dfbbbff90e004ce4d1d	OWNER	t	2026-03-14 17:02:56.030394
1ecf6cfd7d8e47248c81c60f46228651	a4acabcac30049e9925f06c69f4af6ee	f7213f3c5f7346c0b27b9fc4ffca6292	OWNER	t	2026-03-14 17:02:56.030394
986c5b21cf93463494653e7fba780696	5c0efb55ff9a40629f3586b981f9dd8c	5ae49d56a4ad45338f6a92aede6ac672	OWNER	t	2026-03-14 17:02:56.030394
61f3bbdf54ba4d0485d7fab088a1f4db	4ac74113c215401da6dbb34843c050e8	fa99bad247e24dfbbbff90e004ce4d1d	MEMBER	t	2026-03-14 17:02:56.030394
223ceb2c0b8e448d8c428432d76943db	4ac74113c215401da6dbb34843c050e8	f7213f3c5f7346c0b27b9fc4ffca6292	MEMBER	f	2026-03-14 17:02:56.030394
98a7aff7a1714126b3b0fde8b3dbce1b	4ac74113c215401da6dbb34843c050e8	5ae49d56a4ad45338f6a92aede6ac672	MEMBER	f	2026-03-14 17:02:56.030394
94c13fa687d245babbb306c8abcdd900	2e28cb4cfd714d3b97b644153f9a8c7e	fa99bad247e24dfbbbff90e004ce4d1d	MEMBER	t	2026-03-14 17:02:56.030394
2f754139dee84299b2b2902a423b93a5	afc64a32ad0848e886f9f37127a249f4	fa99bad247e24dfbbbff90e004ce4d1d	MEMBER	t	2026-03-14 17:02:56.030394
10d436100b5f4a6283fdba94d023deba	27c6950604dc45179de6ce3dc9c3e42d	f7213f3c5f7346c0b27b9fc4ffca6292	MEMBER	t	2026-03-14 17:02:56.030394
81863998dc534fccaa1a73aa4abb2ccd	5e100203c18147ab9aadc595d3a2f6b6	f7213f3c5f7346c0b27b9fc4ffca6292	MEMBER	t	2026-03-14 17:02:56.030394
e1d8538aada748978a1a14cdb16b00bb	173e41c13b0f43898237efe2edc5e248	5ae49d56a4ad45338f6a92aede6ac672	MEMBER	t	2026-03-14 17:02:56.030394
8161d7d84cc3417bb28819a0a6de0e2e	5a24c5959fe144acb71ad1138c8d1a10	5ae49d56a4ad45338f6a92aede6ac672	MEMBER	t	2026-03-14 17:02:56.030394
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, email, name, password_hash, family_id, role, is_verified, created_at) FROM stdin;
9f21076a04df4c19800d5f5f7ba0d7a3	ericsilvertx+clara@gmail.com	Clara Maple	74729299dc835449ef914190770c0d31fd46999c813d99eace0a58a03ee17c4c	fa99bad247e24dfbbbff90e004ce4d1d	OWNER	t	2026-03-14 17:02:56.030394
2e28cb4cfd714d3b97b644153f9a8c7e	ericsilvertx+mason@gmail.com	Mason Maple	74729299dc835449ef914190770c0d31fd46999c813d99eace0a58a03ee17c4c	fa99bad247e24dfbbbff90e004ce4d1d	MEMBER	t	2026-03-14 17:02:56.030394
afc64a32ad0848e886f9f37127a249f4	ericsilvertx+nina@gmail.com	Nina Maple	74729299dc835449ef914190770c0d31fd46999c813d99eace0a58a03ee17c4c	fa99bad247e24dfbbbff90e004ce4d1d	MEMBER	t	2026-03-14 17:02:56.030394
a4acabcac30049e9925f06c69f4af6ee	ericsilvertx+olivia@gmail.com	Olivia Harbor	74729299dc835449ef914190770c0d31fd46999c813d99eace0a58a03ee17c4c	f7213f3c5f7346c0b27b9fc4ffca6292	OWNER	t	2026-03-14 17:02:56.030394
27c6950604dc45179de6ce3dc9c3e42d	ericsilvertx+ethan@gmail.com	Ethan Harbor	74729299dc835449ef914190770c0d31fd46999c813d99eace0a58a03ee17c4c	f7213f3c5f7346c0b27b9fc4ffca6292	MEMBER	t	2026-03-14 17:02:56.030394
5e100203c18147ab9aadc595d3a2f6b6	ericsilvertx+jack@gmail.com	Jack Harbor	74729299dc835449ef914190770c0d31fd46999c813d99eace0a58a03ee17c4c	f7213f3c5f7346c0b27b9fc4ffca6292	MEMBER	t	2026-03-14 17:02:56.030394
5c0efb55ff9a40629f3586b981f9dd8c	ericsilvertx+sophie@gmail.com	Sophie Sunset	74729299dc835449ef914190770c0d31fd46999c813d99eace0a58a03ee17c4c	5ae49d56a4ad45338f6a92aede6ac672	OWNER	t	2026-03-14 17:02:56.030394
173e41c13b0f43898237efe2edc5e248	ericsilvertx+noah@gmail.com	Noah Sunset	74729299dc835449ef914190770c0d31fd46999c813d99eace0a58a03ee17c4c	5ae49d56a4ad45338f6a92aede6ac672	MEMBER	t	2026-03-14 17:02:56.030394
5a24c5959fe144acb71ad1138c8d1a10	ericsilvertx+maya@gmail.com	Maya Sunset	74729299dc835449ef914190770c0d31fd46999c813d99eace0a58a03ee17c4c	5ae49d56a4ad45338f6a92aede6ac672	MEMBER	t	2026-03-14 17:02:56.030394
4ac74113c215401da6dbb34843c050e8	ericsilvertx+taylor@gmail.com	Taylor Shared	74729299dc835449ef914190770c0d31fd46999c813d99eace0a58a03ee17c4c	fa99bad247e24dfbbbff90e004ce4d1d	MEMBER	t	2026-03-14 17:02:56.030394
\.


--
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (id);


--
-- Name: email_verifications email_verifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.email_verifications
    ADD CONSTRAINT email_verifications_pkey PRIMARY KEY (id);


--
-- Name: families families_join_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.families
    ADD CONSTRAINT families_join_code_key UNIQUE (join_code);


--
-- Name: families families_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.families
    ADD CONSTRAINT families_pkey PRIMARY KEY (id);


--
-- Name: hopper hopper_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hopper
    ADD CONSTRAINT hopper_pkey PRIMARY KEY (id);


--
-- Name: password_resets password_resets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT password_resets_pkey PRIMARY KEY (id);


--
-- Name: profiles profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (id);


--
-- Name: provider_feedback provider_feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.provider_feedback
    ADD CONSTRAINT provider_feedback_pkey PRIMARY KEY (id);


--
-- Name: templates templates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.templates
    ADD CONSTRAINT templates_pkey PRIMARY KEY (id);


--
-- Name: user_families user_families_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_families
    ADD CONSTRAINT user_families_pkey PRIMARY KEY (id);


--
-- Name: user_families user_families_user_id_family_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_families
    ADD CONSTRAINT user_families_user_id_family_id_key UNIQUE (user_id, family_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: profiles_family_user_uidx; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX profiles_family_user_uidx ON public.profiles USING btree (family_id, user_id) WHERE (user_id IS NOT NULL);


--
-- PostgreSQL database dump complete
--

\unrestrict FGaHVuyov1bkWKrVwmMVuMX3DGA7RBRxYMYuWNqWunxGiRc9Js40DsooEOyFYAE

