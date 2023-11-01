--
-- PostgreSQL database dump
--

-- Dumped from database version 16.0 (Debian 16.0-1.pgdg120+1)
-- Dumped by pg_dump version 16.0 (Debian 16.0-1.pgdg120+1)

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
-- Name: create_admin(character varying, character varying, boolean); Type: PROCEDURE; Schema: public; Owner: postgres
--

CREATE PROCEDURE public.create_admin(IN email character varying, IN password character varying, IN can_edit_admins boolean DEFAULT false)
    LANGUAGE plpgsql
    AS $$
DECLARE password_hash varchar(256);
BEGIN
    IF length(password) < 8
    THEN
        RAISE 'Password to short. At least 8 symbols required.';
    END IF;
    password_hash = hash_password(password);
    INSERT INTO admins(email, password_hash, can_edit_admins) 
    VALUES 
    (email, password_hash, can_edit_admins);
END
$$;


ALTER PROCEDURE public.create_admin(IN email character varying, IN password character varying, IN can_edit_admins boolean) OWNER TO postgres;

--
-- Name: hash_password(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.hash_password(password character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN encode(sha256(password::bytea), 'hex');
END 
$$;


ALTER FUNCTION public.hash_password(password character varying) OWNER TO postgres;

--
-- Name: is_admission_committe_available(bigint); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.is_admission_committe_available(chat_id bigint) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF (SELECT TRUE 
        WHERE EXISTS(
            SELECT 
            FROM admission_committee_timetable t
            WHERE t.applicant_chat_id = chat_id
              AND t.start_time <= now()::time without time zone
              AND t.end_time > now()::time without time zone)
        )
    THEN
        RETURN TRUE;
    END IF;
    RETURN FALSE;
END 
$$;


ALTER FUNCTION public.is_admission_committe_available(chat_id bigint) OWNER TO postgres;

--
-- Name: is_relatively_old(timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.is_relatively_old(t timestamp without time zone, relative_to timestamp without time zone DEFAULT NULL::timestamp without time zone) RETURNS boolean
    LANGUAGE sql
    RETURN (t < (COALESCE((relative_to)::timestamp with time zone, now()) - '1 day'::interval));


ALTER FUNCTION public.is_relatively_old(t timestamp without time zone, relative_to timestamp without time zone) OWNER TO postgres;

--
-- Name: is_user_limited(bigint, bigint); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.is_user_limited(user_id bigint, chat_id bigint) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF (SELECT TRUE 
        WHERE EXISTS(
            SELECT 
            FROM chat_member_limitations cml
            WHERE cml.user_id = is_user_limited.user_id
              AND cml.chat_id = is_user_limited.chat_id
              AND (cml."end" ISNULL OR cml."end" > now()))
        )
    THEN
        RETURN TRUE;
    END IF;
    RETURN FALSE;
END 
$$;


ALTER FUNCTION public.is_user_limited(user_id bigint, chat_id bigint) OWNER TO postgres;

--
-- Name: limit_chat_member(bigint, bigint, timestamp without time zone, character varying); Type: PROCEDURE; Schema: public; Owner: postgres
--

CREATE PROCEDURE public.limit_chat_member(IN chat_id bigint, IN user_id bigint, IN since timestamp without time zone DEFAULT CURRENT_TIMESTAMP, IN limitation_type character varying DEFAULT 'ban'::character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE limitation_id int;
BEGIN 
    SELECT id FROM chat_member_limitation_types WHERE name=limitation_type INTO limitation_id;
    IF limitation_id ISNULL 
    THEN
        INSERT INTO chat_member_limitation_types(name) 
        VALUES (limitation_type) 
        RETURNING id INTO limitation_id;
    END IF;
    INSERT INTO chat_member_limitations(chat_id, user_id, start, type_id) 
    VALUES (chat_id, user_id, since, limitation_id);
END 
$$;


ALTER PROCEDURE public.limit_chat_member(IN chat_id bigint, IN user_id bigint, IN since timestamp without time zone, IN limitation_type character varying) OWNER TO postgres;

--
-- Name: remove_old_messages(); Type: PROCEDURE; Schema: public; Owner: postgres
--

CREATE PROCEDURE public.remove_old_messages()
    LANGUAGE sql
    AS $$
DELETE
FROM messages
WHERE is_relatively_old(messages.sent_at);
$$;


ALTER PROCEDURE public.remove_old_messages() OWNER TO postgres;

--
-- Name: remove_relatively_old_messages(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.remove_relatively_old_messages() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE
    FROM messages
    WHERE is_relatively_old(messages.sent_at, NEW.sent_at);
    RETURN NEW;
END
$$;


ALTER FUNCTION public.remove_relatively_old_messages() OWNER TO postgres;

--
-- Name: validate_admission_committee_timetable(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.validate_admission_committee_timetable() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    RAISE WARNING '%', new;
    IF NEW.start_time > NEW.end_time
        OR (SELECT TRUE
            FROM admission_committee_timetable
            WHERE date = NEW.date
              AND id <> NEW.id
              AND applicant_chat_id = NEW.applicant_chat_id
              AND (start_time <= NEW.start_time
                       AND NEW.start_time < end_time
                OR end_time <= NEW.end_time)
              AND NEW.end_time > start_time)
    THEN
        RAISE 'Impossible or overlapping timetable record';
    END IF;
    RETURN NEW;
END
$$;


ALTER FUNCTION public.validate_admission_committee_timetable() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admins; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.admins (
    id integer NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(256) NOT NULL,
    can_edit_admins boolean NOT NULL
);


ALTER TABLE public.admins OWNER TO postgres;

--
-- Name: admins_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.admins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.admins_id_seq OWNER TO postgres;

--
-- Name: admins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.admins_id_seq OWNED BY public.admins.id;


--
-- Name: admission_committee_timetable; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.admission_committee_timetable (
    applicant_chat_id bigint NOT NULL,
    date date NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.admission_committee_timetable OWNER TO postgres;

--
-- Name: admission_committee_timetable_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.admission_committee_timetable_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.admission_committee_timetable_id_seq OWNER TO postgres;

--
-- Name: admission_committee_timetable_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.admission_committee_timetable_id_seq OWNED BY public.admission_committee_timetable.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: applicant_chat_programs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.applicant_chat_programs (
    program_id integer NOT NULL,
    applicant_chat_id bigint NOT NULL
);


ALTER TABLE public.applicant_chat_programs OWNER TO postgres;

--
-- Name: applicant_chat_useful_links; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.applicant_chat_useful_links (
    link_id integer NOT NULL,
    applicant_chat_id bigint NOT NULL
);


ALTER TABLE public.applicant_chat_useful_links OWNER TO postgres;

--
-- Name: applicant_chats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.applicant_chats (
    chat_id bigint NOT NULL,
    flood_chat_id bigint NOT NULL,
    greet_new_members boolean NOT NULL,
    active boolean NOT NULL
);


ALTER TABLE public.applicant_chats OWNER TO postgres;

--
-- Name: applicant_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.applicant_documents (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    description character varying
);


ALTER TABLE public.applicant_documents OWNER TO postgres;

--
-- Name: applicant_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.applicant_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.applicant_documents_id_seq OWNER TO postgres;

--
-- Name: applicant_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.applicant_documents_id_seq OWNED BY public.applicant_documents.id;


--
-- Name: chat_member_limitation_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_member_limitation_types (
    id integer NOT NULL,
    name character varying(10) NOT NULL
);


ALTER TABLE public.chat_member_limitation_types OWNER TO postgres;

--
-- Name: chat_member_limitations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_member_limitations (
    chat_id bigint NOT NULL,
    user_id bigint NOT NULL,
    start timestamp without time zone NOT NULL,
    "end" timestamp without time zone,
    type_id integer NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.chat_member_limitations OWNER TO postgres;

--
-- Name: chat_members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_members (
    chat_id bigint NOT NULL,
    user_id bigint NOT NULL,
    joined timestamp without time zone NOT NULL,
    role_id integer NOT NULL
);


ALTER TABLE public.chat_members OWNER TO postgres;

--
-- Name: banned_chat_members; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.banned_chat_members AS
 SELECT chat_id,
    user_id,
    joined,
    role_id
   FROM public.chat_members
  WHERE (EXISTS ( SELECT chat_member_limitations.chat_id,
            chat_member_limitations.user_id,
            chat_member_limitations.start,
            chat_member_limitations."end",
            chat_member_limitations.type_id,
            cmlt.id,
            cmlt.name
           FROM (public.chat_member_limitations
             JOIN public.chat_member_limitation_types cmlt ON ((cmlt.id = chat_member_limitations.type_id)))
          WHERE ((chat_members.chat_id = chat_member_limitations.chat_id) AND (chat_members.user_id = chat_member_limitations.user_id) AND ((chat_member_limitations."end" IS NULL) OR (chat_member_limitations."end" > now())) AND ((cmlt.name)::text = 'ban'::text))));


ALTER VIEW public.banned_chat_members OWNER TO postgres;

--
-- Name: chat_member_limitation_types_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_member_limitation_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chat_member_limitation_types_id_seq OWNER TO postgres;

--
-- Name: chat_member_limitation_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_member_limitation_types_id_seq OWNED BY public.chat_member_limitation_types.id;


--
-- Name: chat_member_limitations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_member_limitations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chat_member_limitations_id_seq OWNER TO postgres;

--
-- Name: chat_member_limitations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_member_limitations_id_seq OWNED BY public.chat_member_limitations.id;


--
-- Name: chat_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_roles (
    id integer NOT NULL,
    name character varying(30) NOT NULL
);


ALTER TABLE public.chat_roles OWNER TO postgres;

--
-- Name: chat_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chat_roles_id_seq OWNER TO postgres;

--
-- Name: chat_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_roles_id_seq OWNED BY public.chat_roles.id;


--
-- Name: chats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chats (
    id bigint NOT NULL,
    title character varying(256) NOT NULL,
    description character varying NOT NULL,
    invite_link character varying(500) NOT NULL
);


ALTER TABLE public.chats OWNER TO postgres;

--
-- Name: flood_chats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.flood_chats (
    chat_id bigint NOT NULL
);


ALTER TABLE public.flood_chats OWNER TO postgres;

--
-- Name: messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.messages (
    message_id bigint NOT NULL,
    chat_id bigint NOT NULL,
    user_id bigint NOT NULL,
    sent_at timestamp without time zone NOT NULL,
    last_edit_at timestamp without time zone NOT NULL,
    content json NOT NULL
);


ALTER TABLE public.messages OWNER TO postgres;

--
-- Name: programs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.programs (
    id integer NOT NULL,
    title character varying(50) NOT NULL,
    first_year integer NOT NULL,
    description character varying NOT NULL,
    subject_list_url character varying(500) NOT NULL
);


ALTER TABLE public.programs OWNER TO postgres;

--
-- Name: programs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.programs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.programs_id_seq OWNER TO postgres;

--
-- Name: programs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.programs_id_seq OWNED BY public.programs.id;


--
-- Name: required_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.required_documents (
    document_id integer NOT NULL,
    applicant_chat_id bigint NOT NULL,
    added_at timestamp without time zone NOT NULL,
    optional boolean NOT NULL
);


ALTER TABLE public.required_documents OWNER TO postgres;

--
-- Name: useful_links; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.useful_links (
    id integer NOT NULL,
    title character varying(256) NOT NULL,
    url character varying(500) NOT NULL
);


ALTER TABLE public.useful_links OWNER TO postgres;

--
-- Name: useful_links_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.useful_links_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.useful_links_id_seq OWNER TO postgres;

--
-- Name: useful_links_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.useful_links_id_seq OWNED BY public.useful_links.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    first_name character varying(256) NOT NULL,
    last_name character varying(256),
    username character varying(256)
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: admins id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admins ALTER COLUMN id SET DEFAULT nextval('public.admins_id_seq'::regclass);


--
-- Name: admission_committee_timetable id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admission_committee_timetable ALTER COLUMN id SET DEFAULT nextval('public.admission_committee_timetable_id_seq'::regclass);


--
-- Name: applicant_documents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applicant_documents ALTER COLUMN id SET DEFAULT nextval('public.applicant_documents_id_seq'::regclass);


--
-- Name: chat_member_limitation_types id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_member_limitation_types ALTER COLUMN id SET DEFAULT nextval('public.chat_member_limitation_types_id_seq'::regclass);


--
-- Name: chat_member_limitations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_member_limitations ALTER COLUMN id SET DEFAULT nextval('public.chat_member_limitations_id_seq'::regclass);


--
-- Name: chat_roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_roles ALTER COLUMN id SET DEFAULT nextval('public.chat_roles_id_seq'::regclass);


--
-- Name: programs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programs ALTER COLUMN id SET DEFAULT nextval('public.programs_id_seq'::regclass);


--
-- Name: useful_links id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.useful_links ALTER COLUMN id SET DEFAULT nextval('public.useful_links_id_seq'::regclass);


--
-- Data for Name: admins; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.admins (id, email, password_hash, can_edit_admins) FROM stdin;
1	test@test.com	ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f	f
2	test@test.com	ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f	t
\.


--
-- Data for Name: admission_committee_timetable; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.admission_committee_timetable (applicant_chat_id, date, start_time, end_time, id) FROM stdin;
1	2023-11-01	11:39:49	12:00:03	2
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
ea228a99bae4
\.


--
-- Data for Name: applicant_chat_programs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.applicant_chat_programs (program_id, applicant_chat_id) FROM stdin;
\.


--
-- Data for Name: applicant_chat_useful_links; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.applicant_chat_useful_links (link_id, applicant_chat_id) FROM stdin;
\.


--
-- Data for Name: applicant_chats; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.applicant_chats (chat_id, flood_chat_id, greet_new_members, active) FROM stdin;
1	2	f	t
\.


--
-- Data for Name: applicant_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.applicant_documents (id, title, description) FROM stdin;
\.


--
-- Data for Name: chat_member_limitation_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_member_limitation_types (id, name) FROM stdin;
1	ban
\.


--
-- Data for Name: chat_member_limitations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_member_limitations (chat_id, user_id, start, "end", type_id, id) FROM stdin;
1	1	2023-11-01 12:26:06	\N	1	1
1	1	2023-11-01 13:58:22.804063	\N	1	2
\.


--
-- Data for Name: chat_members; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_members (chat_id, user_id, joined, role_id) FROM stdin;
1	1	2023-11-01 12:25:26	1
\.


--
-- Data for Name: chat_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_roles (id, name) FROM stdin;
1	admin
\.


--
-- Data for Name: chats; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chats (id, title, description, invite_link) FROM stdin;
1	a	b	url
2	v	b	url
\.


--
-- Data for Name: flood_chats; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.flood_chats (chat_id) FROM stdin;
2
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.messages (message_id, chat_id, user_id, sent_at, last_edit_at, content) FROM stdin;
1	1	1	2023-10-31 13:25:16	2023-10-31 13:25:17	{}
2	1	1	2023-10-31 13:25:16	2023-10-31 13:25:17	{}
\.


--
-- Data for Name: programs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.programs (id, title, first_year, description, subject_list_url) FROM stdin;
\.


--
-- Data for Name: required_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.required_documents (document_id, applicant_chat_id, added_at, optional) FROM stdin;
\.


--
-- Data for Name: useful_links; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.useful_links (id, title, url) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, first_name, last_name, username) FROM stdin;
1	a	\N	\N
\.


--
-- Name: admins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.admins_id_seq', 2, true);


--
-- Name: admission_committee_timetable_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.admission_committee_timetable_id_seq', 3, true);


--
-- Name: applicant_documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.applicant_documents_id_seq', 1, false);


--
-- Name: chat_member_limitation_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.chat_member_limitation_types_id_seq', 2, true);


--
-- Name: chat_member_limitations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.chat_member_limitations_id_seq', 2, true);


--
-- Name: chat_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.chat_roles_id_seq', 1, true);


--
-- Name: programs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.programs_id_seq', 1, false);


--
-- Name: useful_links_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.useful_links_id_seq', 1, false);


--
-- Name: admins admins_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_pkey PRIMARY KEY (id);


--
-- Name: admission_committee_timetable admission_committee_timetable_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admission_committee_timetable
    ADD CONSTRAINT admission_committee_timetable_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: applicant_chat_programs applicant_chat_programs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applicant_chat_programs
    ADD CONSTRAINT applicant_chat_programs_pkey PRIMARY KEY (program_id, applicant_chat_id);


--
-- Name: applicant_chat_useful_links applicant_chat_useful_links_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applicant_chat_useful_links
    ADD CONSTRAINT applicant_chat_useful_links_pkey PRIMARY KEY (link_id, applicant_chat_id);


--
-- Name: applicant_chats applicant_chats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applicant_chats
    ADD CONSTRAINT applicant_chats_pkey PRIMARY KEY (chat_id);


--
-- Name: applicant_documents applicant_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applicant_documents
    ADD CONSTRAINT applicant_documents_pkey PRIMARY KEY (id);


--
-- Name: chat_member_limitation_types chat_member_limitation_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_member_limitation_types
    ADD CONSTRAINT chat_member_limitation_types_pkey PRIMARY KEY (id);


--
-- Name: chat_member_limitations chat_member_limitations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_member_limitations
    ADD CONSTRAINT chat_member_limitations_pkey PRIMARY KEY (id);


--
-- Name: chat_members chat_members_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_members
    ADD CONSTRAINT chat_members_pkey PRIMARY KEY (chat_id, user_id);


--
-- Name: chat_roles chat_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_roles
    ADD CONSTRAINT chat_roles_pkey PRIMARY KEY (id);


--
-- Name: chats chats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_pkey PRIMARY KEY (id);


--
-- Name: flood_chats flood_chats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flood_chats
    ADD CONSTRAINT flood_chats_pkey PRIMARY KEY (chat_id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (message_id, chat_id);


--
-- Name: programs programs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programs
    ADD CONSTRAINT programs_pkey PRIMARY KEY (id);


--
-- Name: required_documents required_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.required_documents
    ADD CONSTRAINT required_documents_pkey PRIMARY KEY (document_id, applicant_chat_id);


--
-- Name: useful_links useful_links_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.useful_links
    ADD CONSTRAINT useful_links_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: messages remove_old_messages_on_insert; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_old_messages_on_insert BEFORE INSERT ON public.messages FOR EACH STATEMENT EXECUTE FUNCTION public.remove_relatively_old_messages();


--
-- Name: admission_committee_timetable validate_admission_committee_timetable; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER validate_admission_committee_timetable BEFORE INSERT OR UPDATE ON public.admission_committee_timetable FOR EACH ROW EXECUTE FUNCTION public.validate_admission_committee_timetable();


--
-- Name: admission_committee_timetable admission_committee_timetable_applicant_chat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admission_committee_timetable
    ADD CONSTRAINT admission_committee_timetable_applicant_chat_id_fkey FOREIGN KEY (applicant_chat_id) REFERENCES public.applicant_chats(chat_id) ON DELETE CASCADE;


--
-- Name: applicant_chat_programs applicant_chat_programs_applicant_chat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applicant_chat_programs
    ADD CONSTRAINT applicant_chat_programs_applicant_chat_id_fkey FOREIGN KEY (applicant_chat_id) REFERENCES public.applicant_chats(chat_id) ON DELETE CASCADE;


--
-- Name: applicant_chat_programs applicant_chat_programs_program_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applicant_chat_programs
    ADD CONSTRAINT applicant_chat_programs_program_id_fkey FOREIGN KEY (program_id) REFERENCES public.programs(id) ON DELETE CASCADE;


--
-- Name: applicant_chat_useful_links applicant_chat_useful_links_applicant_chat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applicant_chat_useful_links
    ADD CONSTRAINT applicant_chat_useful_links_applicant_chat_id_fkey FOREIGN KEY (applicant_chat_id) REFERENCES public.applicant_chats(chat_id) ON DELETE CASCADE;


--
-- Name: applicant_chat_useful_links applicant_chat_useful_links_link_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applicant_chat_useful_links
    ADD CONSTRAINT applicant_chat_useful_links_link_id_fkey FOREIGN KEY (link_id) REFERENCES public.useful_links(id) ON DELETE CASCADE;


--
-- Name: applicant_chats applicant_chats_chat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applicant_chats
    ADD CONSTRAINT applicant_chats_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES public.chats(id) ON DELETE CASCADE;


--
-- Name: applicant_chats applicant_chats_flood_chat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applicant_chats
    ADD CONSTRAINT applicant_chats_flood_chat_id_fkey FOREIGN KEY (flood_chat_id) REFERENCES public.flood_chats(chat_id);


--
-- Name: chat_member_limitations chat_member_limitations_chat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_member_limitations
    ADD CONSTRAINT chat_member_limitations_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES public.chats(id);


--
-- Name: chat_member_limitations chat_member_limitations_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_member_limitations
    ADD CONSTRAINT chat_member_limitations_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.chat_member_limitation_types(id);


--
-- Name: chat_member_limitations chat_member_limitations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_member_limitations
    ADD CONSTRAINT chat_member_limitations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: chat_members chat_members_chat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_members
    ADD CONSTRAINT chat_members_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES public.chats(id);


--
-- Name: chat_members chat_members_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_members
    ADD CONSTRAINT chat_members_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.chat_roles(id);


--
-- Name: chat_members chat_members_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_members
    ADD CONSTRAINT chat_members_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: flood_chats flood_chats_chat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flood_chats
    ADD CONSTRAINT flood_chats_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES public.chats(id) ON DELETE CASCADE;


--
-- Name: messages messages_chat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES public.chats(id);


--
-- Name: messages messages_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: required_documents required_documents_applicant_chat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.required_documents
    ADD CONSTRAINT required_documents_applicant_chat_id_fkey FOREIGN KEY (applicant_chat_id) REFERENCES public.applicant_chats(chat_id) ON DELETE CASCADE;


--
-- Name: required_documents required_documents_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.required_documents
    ADD CONSTRAINT required_documents_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.applicant_documents(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

