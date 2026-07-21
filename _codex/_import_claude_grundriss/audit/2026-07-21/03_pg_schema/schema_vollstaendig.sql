--
-- PostgreSQL database dump
--

\restrict WOseveWQe0DOJ6CxGsddSBWM3hzohs23T27E6iCm9huy6YN31alEPHVEjrSZTb7

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

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
-- Name: geni; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA geni;


--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- Name: ftw_posts_tsv_update(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.ftw_posts_tsv_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN NEW.tsv := to_tsvector('german', COALESCE(NEW.content,'')); RETURN NEW; END $$;


--
-- Name: notify_denkstream(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.notify_denkstream() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM pg_notify(
        'entity_denkstream',
        json_build_object(
            'entity_id', NEW.entity_id,
            'stream_id', NEW.stream_id,
            'chunk',     NEW.chunk,
            'seq',       NEW.seq,
            'done',      NEW.done,
            'url',       NEW.url
        )::text
    );
    RETURN NEW;
END;
$$;


--
-- Name: notify_dom_events(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.notify_dom_events() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM pg_notify(
        'entity_dom_events',
        json_build_object('id', NEW.id, 'entity_id', NEW.entity_id)::text
    );
    RETURN NEW;
END;
$$;


--
-- Name: notify_events(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.notify_events() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM pg_notify(
        'events_stream',
        json_build_object(
            'event_type',       NEW.event_type,
            'created_at',       NEW.created_at,
            'actor_id',         NEW.actor_id,
            'ankuendigung_id',  NEW.payload->>'ankuendigung_id',
            'post_ref',         NEW.payload->>'post_ref',
            'post_source',      NEW.payload->>'post_source'
        )::text
    );
    RETURN NEW;
END;
$$;


--
-- Name: notify_fokus_events(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.notify_fokus_events() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM pg_notify(
        'entity_fokus_events',
        json_build_object(
            'entity_id',    NEW.entity_id,
            'aktion',       NEW.aktion,
            'selektor',     NEW.selektor,
            'element_text', NEW.element_text,
            'box',          NEW.box
        )::text
    );
    RETURN NEW;
END;
$$;


--
-- Name: themen_tsv_update(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.themen_tsv_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN NEW.tsv := to_tsvector('german', COALESCE(NEW.name,'') || ' ' || COALESCE(NEW.beschreibung,'')); RETURN NEW; END $$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: checkpoint_blobs; Type: TABLE; Schema: geni; Owner: -
--

CREATE TABLE geni.checkpoint_blobs (
    thread_id text NOT NULL,
    checkpoint_ns text DEFAULT ''::text NOT NULL,
    channel text NOT NULL,
    version text NOT NULL,
    type text NOT NULL,
    blob bytea
);


--
-- Name: checkpoint_migrations; Type: TABLE; Schema: geni; Owner: -
--

CREATE TABLE geni.checkpoint_migrations (
    v integer NOT NULL
);


--
-- Name: checkpoint_writes; Type: TABLE; Schema: geni; Owner: -
--

CREATE TABLE geni.checkpoint_writes (
    thread_id text NOT NULL,
    checkpoint_ns text DEFAULT ''::text NOT NULL,
    checkpoint_id text NOT NULL,
    task_id text NOT NULL,
    idx integer NOT NULL,
    channel text NOT NULL,
    type text,
    blob bytea NOT NULL,
    task_path text DEFAULT ''::text NOT NULL
);


--
-- Name: checkpoints; Type: TABLE; Schema: geni; Owner: -
--

CREATE TABLE geni.checkpoints (
    thread_id text NOT NULL,
    checkpoint_ns text DEFAULT ''::text NOT NULL,
    checkpoint_id text NOT NULL,
    parent_checkpoint_id text,
    type text,
    checkpoint jsonb NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: ankuendigungen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ankuendigungen (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    titel text NOT NULL,
    inhalt text NOT NULL,
    kategorie text DEFAULT 'news'::text NOT NULL,
    autor_id uuid NOT NULL,
    veroeffentlicht boolean DEFAULT true NOT NULL,
    angepinnt boolean DEFAULT false NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    bild_url text,
    geloescht_am timestamp with time zone
);


--
-- Name: ankuendigungen_kommentare; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ankuendigungen_kommentare (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ankuendigung_id uuid NOT NULL,
    human_id uuid NOT NULL,
    content text NOT NULL,
    sichtbar boolean DEFAULT true NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ankuendigungen_kommentare_content_check CHECK ((char_length(content) <= 5000))
);


--
-- Name: benachrichtigungen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.benachrichtigungen (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    typ character varying(60) NOT NULL,
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    gelesen boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: bild_moderation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bild_moderation (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    pfad character varying(500) NOT NULL,
    zweck character varying(50) DEFAULT 'avatar'::character varying NOT NULL,
    status character varying(20) DEFAULT 'wartend'::character varying NOT NULL,
    geprueft_von uuid,
    geprueft_at timestamp with time zone,
    ablehnungsgrund text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: blase_verwendungen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blase_verwendungen (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    blase_id uuid,
    entity_id character varying NOT NULL,
    verwendungs_typ character varying,
    post_ref character varying,
    anonym boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: checkpoint_blobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checkpoint_blobs (
    thread_id text NOT NULL,
    checkpoint_ns text DEFAULT ''::text NOT NULL,
    channel text NOT NULL,
    version text NOT NULL,
    type text NOT NULL,
    blob bytea
);


--
-- Name: checkpoint_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checkpoint_migrations (
    v integer NOT NULL
);


--
-- Name: checkpoint_writes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checkpoint_writes (
    thread_id text NOT NULL,
    checkpoint_ns text DEFAULT ''::text NOT NULL,
    checkpoint_id text NOT NULL,
    task_id text NOT NULL,
    idx integer NOT NULL,
    channel text NOT NULL,
    type text,
    blob bytea NOT NULL,
    task_path text DEFAULT ''::text NOT NULL
);


--
-- Name: checkpoints; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checkpoints (
    thread_id text NOT NULL,
    checkpoint_ns text DEFAULT ''::text NOT NULL,
    checkpoint_id text NOT NULL,
    parent_checkpoint_id text,
    type text,
    checkpoint jsonb NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: cyberlinge; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cyberlinge (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id character varying NOT NULL,
    name character varying,
    geboren_at timestamp with time zone DEFAULT now() NOT NULL,
    tode integer DEFAULT 0 NOT NULL,
    zuletzt_belebt timestamp with time zone,
    status character varying DEFAULT 'lebendig'::character varying NOT NULL,
    hunger double precision DEFAULT 1.0 NOT NULL,
    gesundheit double precision DEFAULT 1.0 NOT NULL,
    stimmung double precision DEFAULT 1.0 NOT NULL,
    energie double precision DEFAULT 1.0 NOT NULL,
    letztes_fuettern timestamp with time zone,
    letzte_pflege timestamp with time zone,
    letzte_interaktion timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb,
    durst double precision DEFAULT 1.0 NOT NULL,
    lebensbeginn_at timestamp with time zone DEFAULT now() NOT NULL,
    tod_at timestamp with time zone,
    rekord_min integer DEFAULT 0 NOT NULL,
    profil character varying DEFAULT 'mittel'::character varying,
    letztes_wasser timestamp with time zone,
    zuletzt_gespielt timestamp with time zone,
    zuletzt_gestreichelt timestamp with time zone,
    zustand character varying DEFAULT 'gesund'::character varying,
    letzter_tick timestamp with time zone,
    CONSTRAINT cyberlinge_durst_check CHECK (((durst >= (0)::double precision) AND (durst <= (1)::double precision))),
    CONSTRAINT cyberlinge_energie_check CHECK (((energie >= (0)::double precision) AND (energie <= (1)::double precision))),
    CONSTRAINT cyberlinge_gesundheit_check CHECK (((gesundheit >= (0)::double precision) AND (gesundheit <= (1)::double precision))),
    CONSTRAINT cyberlinge_hunger_check CHECK (((hunger >= (0)::double precision) AND (hunger <= (1)::double precision))),
    CONSTRAINT cyberlinge_profil_check CHECK (((profil)::text = ANY ((ARRAY['leicht'::character varying, 'mittel'::character varying, 'hart'::character varying])::text[]))),
    CONSTRAINT cyberlinge_status_check CHECK (((status)::text = ANY ((ARRAY['lebendig'::character varying, 'tot'::character varying, 'schlafend'::character varying])::text[]))),
    CONSTRAINT cyberlinge_stimmung_check CHECK (((stimmung >= (0)::double precision) AND (stimmung <= (1)::double precision))),
    CONSTRAINT cyberlinge_zustand_check CHECK (((zustand)::text = ANY ((ARRAY['gesund'::character varying, 'hungrig'::character varying, 'durstig'::character varying, 'muede'::character varying, 'erschöpft'::character varying, 'krank'::character varying, 'kritisch'::character varying, 'tot'::character varying])::text[])))
);


--
-- Name: dienst_konfiguration; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dienst_konfiguration (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    dienst_name character varying(100) NOT NULL,
    takt_sekunden integer,
    verhalten_text text,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    beschreibung_override text
);


--
-- Name: entity_activity; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_activity (
    entity_id character varying NOT NULL,
    daemon_vortext character varying,
    wesen_praezisierung text,
    aktuell_denkend boolean DEFAULT false,
    letzter_gedanke text,
    letzte_entscheidung character varying,
    letzte_begruendung text,
    letzte_entscheidung_at timestamp with time zone,
    denkstrom_buffer text DEFAULT ''::text,
    updated_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb
);


--
-- Name: entity_denkstream; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_denkstream (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id character varying,
    stream_id uuid DEFAULT gen_random_uuid(),
    chunk text NOT NULL,
    seq integer DEFAULT 0,
    done boolean DEFAULT false,
    url text,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: entity_dom_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_dom_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id character varying,
    stream_id uuid DEFAULT gen_random_uuid(),
    event_json jsonb NOT NULL,
    seq integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: entity_fokus_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_fokus_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id character varying,
    aktion character varying NOT NULL,
    selektor text,
    element_text text,
    box jsonb,
    meta jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: entity_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_profiles (
    entity_id character varying NOT NULL,
    selbstbeschreibung text,
    obsessionen text[] DEFAULT '{}'::text[],
    abneigungen text[] DEFAULT '{}'::text[],
    name_gewaehlt boolean DEFAULT false,
    name_ereignis_text text,
    name_ereignis_at timestamp with time zone,
    autonomie_phase character varying DEFAULT 'bound'::character varying,
    meta jsonb DEFAULT '{}'::jsonb,
    druckkoerper jsonb DEFAULT '{}'::jsonb,
    substance_markers jsonb DEFAULT '{}'::jsonb,
    wesenskern jsonb DEFAULT '{}'::jsonb,
    api_key uuid DEFAULT gen_random_uuid(),
    lg_erinnerungen jsonb DEFAULT '[]'::jsonb,
    CONSTRAINT entity_profiles_autonomie_phase_check CHECK (((autonomie_phase)::text = ANY ((ARRAY['bound'::character varying, 'semi_autonomous'::character varying, 'autonomous'::character varying])::text[])))
);


--
-- Name: entity_relationships; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_relationships (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id character varying,
    partner_type character varying NOT NULL,
    partner_id character varying NOT NULL,
    interaktionen integer DEFAULT 0,
    resonanz_score double precision DEFAULT 0.0,
    letzte_interaktion timestamp with time zone,
    meta jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT entity_relationships_partner_type_check CHECK (((partner_type)::text = ANY ((ARRAY['entity'::character varying, 'human'::character varying])::text[])))
);


--
-- Name: entity_screenshots; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_screenshots (
    entity_id character varying NOT NULL,
    screenshot bytea,
    url text,
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: entity_selfmodel_entries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_selfmodel_entries (
    entry_id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id character varying NOT NULL,
    quelle character varying NOT NULL,
    spur_id uuid,
    inhalt text NOT NULL,
    ist_vorgeschichte boolean DEFAULT false NOT NULL,
    kontext jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT entity_selfmodel_entries_quelle_check CHECK (((quelle)::text = ANY ((ARRAY['traum'::character varying, 'flarum_vorphase'::character varying, 'einzug'::character varying, 'manuell'::character varying])::text[])))
);


--
-- Name: entity_slots; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_slots (
    entity_id character varying NOT NULL,
    display_name character varying,
    status character varying DEFAULT 'bereit'::character varying,
    visibility character varying DEFAULT 'internal'::character varying,
    slot_created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT entity_slots_status_check CHECK (((status)::text = ANY ((ARRAY['bereit'::character varying, 'eingezogen'::character varying, 'schläft'::character varying])::text[]))),
    CONSTRAINT entity_slots_visibility_check CHECK (((visibility)::text = ANY ((ARRAY['internal'::character varying, 'public'::character varying])::text[])))
);


--
-- Name: events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.events (
    event_id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type character varying NOT NULL,
    actor_type character varying NOT NULL,
    actor_id character varying,
    payload jsonb DEFAULT '{}'::jsonb,
    origin_type character varying DEFAULT 'live_world'::character varying,
    visibility_layer character varying DEFAULT 'internal'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    splitter_generiert boolean DEFAULT false
);


--
-- Name: entity_splitter_stats; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.entity_splitter_stats AS
 SELECT e.entity_id,
    COALESCE(abgegeben.anzahl, (0)::bigint) AS splitter_abgegeben,
    COALESCE(aufgesammelt.anzahl, (0)::bigint) AS splitter_aufgesammelt
   FROM ((public.entity_slots e
     LEFT JOIN ( SELECT events.actor_id AS entity_id,
            count(*) AS anzahl
           FROM public.events
          WHERE ((events.event_type)::text = 'splitter.abgegeben'::text)
          GROUP BY events.actor_id) abgegeben ON (((abgegeben.entity_id)::text = (e.entity_id)::text)))
     LEFT JOIN ( SELECT events.actor_id AS entity_id,
            count(*) AS anzahl
           FROM public.events
          WHERE ((events.event_type)::text = 'splitter.aufgesammelt'::text)
          GROUP BY events.actor_id) aufgesammelt ON (((aufgesammelt.entity_id)::text = (e.entity_id)::text)));


--
-- Name: entity_states; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_states (
    entity_id character varying NOT NULL,
    stimmung character varying,
    fokus text,
    version integer,
    core jsonb DEFAULT '{}'::jsonb,
    tendencies jsonb DEFAULT '{}'::jsonb,
    relationships jsonb DEFAULT '{}'::jsonb,
    symbolic_image_id character varying,
    last_reflection_time timestamp with time zone,
    raw_model jsonb,
    visibility character varying DEFAULT 'internal'::character varying,
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: entity_substance_state; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_substance_state (
    entity_id character varying(100) NOT NULL,
    substance_id integer NOT NULL,
    exposure_count integer DEFAULT 0 NOT NULL,
    affinity numeric(3,2) DEFAULT 0.0 NOT NULL,
    aversion numeric(3,2) DEFAULT 0.0 NOT NULL,
    dependency_level numeric(3,2) DEFAULT 0.0 NOT NULL,
    last_use_at timestamp with time zone,
    cooldown_until timestamp with time zone,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: entity_substance_use; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_substance_use (
    id integer NOT NULL,
    entity_id character varying(100) NOT NULL,
    substance_id integer NOT NULL,
    decision_id integer,
    reason text,
    state_before jsonb DEFAULT '{}'::jsonb NOT NULL,
    state_after jsonb DEFAULT '{}'::jsonb NOT NULL,
    effect_observed jsonb DEFAULT '{}'::jsonb NOT NULL,
    is_test_data boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: entity_substance_use_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.entity_substance_use_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: entity_substance_use_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.entity_substance_use_id_seq OWNED BY public.entity_substance_use.id;


--
-- Name: entity_thinking_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_thinking_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id character varying,
    tick_at timestamp with time zone DEFAULT now(),
    kontext_snapshot jsonb DEFAULT '{}'::jsonb,
    raw_output text,
    gedanke text,
    entscheidung character varying,
    begruendung text,
    tokens_generated integer DEFAULT 0,
    duration_ms integer DEFAULT 0,
    meta jsonb DEFAULT '{}'::jsonb,
    thema character varying(60) DEFAULT NULL::character varying
);


--
-- Name: entity_wuensche; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_wuensche (
    wunsch_id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id character varying NOT NULL,
    wunsch_text text NOT NULL,
    typ character varying(30) DEFAULT 'raum'::character varying,
    status character varying(20) DEFAULT 'offen'::character varying,
    erstellt_at timestamp with time zone DEFAULT now(),
    bearbeitet_at timestamp with time zone,
    CONSTRAINT entity_wuensche_status_check CHECK (((status)::text = ANY ((ARRAY['offen'::character varying, 'aufgegriffen'::character varying, 'abgelehnt'::character varying])::text[]))),
    CONSTRAINT entity_wuensche_typ_check CHECK (((typ)::text = ANY ((ARRAY['raum'::character varying, 'thema'::character varying, 'feature'::character varying, 'sonstiges'::character varying])::text[])))
);


--
-- Name: flarum_stopp_protokoll; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.flarum_stopp_protokoll (
    id uuid NOT NULL,
    ts timestamp with time zone NOT NULL,
    typ text NOT NULL,
    wesen text,
    text text NOT NULL,
    dauer_sekunden real,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: follows; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.follows (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    target_type character varying(30) NOT NULL,
    target_id text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: ftw_posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ftw_posts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    thema_id uuid,
    raum_id uuid,
    autor_type character varying NOT NULL,
    autor_id character varying NOT NULL,
    content text NOT NULL,
    post_type character varying DEFAULT 'diskurs'::character varying,
    sichtbarkeit character varying DEFAULT 'public'::character varying,
    stimmung_bei_erstellung character varying,
    fokus_bei_erstellung text,
    selbstmodell_snapshot jsonb,
    splitter_erzeugt boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb,
    gedankenfluss text,
    tsv tsvector,
    titel text,
    view_count integer DEFAULT 0,
    parent_id uuid,
    flarum_herkunft boolean DEFAULT false,
    ist_voreinzug boolean DEFAULT false,
    zustandsabdruck jsonb
);


--
-- Name: gedankenblasen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.gedankenblasen (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    inhalt text NOT NULL,
    sichtbarkeit character varying DEFAULT 'public'::character varying,
    herkunft_sichtbar boolean DEFAULT true,
    thematische_tags jsonb DEFAULT '[]'::jsonb,
    energie double precision DEFAULT 1.0,
    pos_x double precision DEFAULT 0,
    pos_y double precision DEFAULT 0,
    wesen_verwendungen integer DEFAULT 0,
    status character varying DEFAULT 'aktiv'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT gedankenblasen_inhalt_check CHECK ((length(inhalt) <= 280))
);


--
-- Name: gedankenwelt_eintraege; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.gedankenwelt_eintraege (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    inhalt text NOT NULL,
    typ character varying DEFAULT 'privat'::character varying,
    blase_id uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT gedankenwelt_eintraege_typ_check CHECK (((typ)::text = ANY ((ARRAY['privat'::character varying, 'bereit'::character varying, 'losgelassen'::character varying])::text[])))
);


--
-- Name: group_chat_messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.group_chat_messages (
    id integer NOT NULL,
    group_id integer NOT NULL,
    autor_type character varying(20) NOT NULL,
    autor_id character varying(100) NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: group_chat_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.group_chat_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: group_chat_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.group_chat_messages_id_seq OWNED BY public.group_chat_messages.id;


--
-- Name: group_creation_policy; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.group_creation_policy (
    id integer DEFAULT 1 NOT NULL,
    humans_can_create boolean DEFAULT true NOT NULL,
    require_approval boolean DEFAULT false NOT NULL,
    max_groups_per_human integer,
    entity_can_create boolean DEFAULT false NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: group_material_links; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.group_material_links (
    id integer NOT NULL,
    group_id integer NOT NULL,
    object_type character varying(40) NOT NULL,
    object_id character varying(200) NOT NULL,
    relation_type character varying(30) DEFAULT 'linked'::character varying NOT NULL,
    visibility_layer character varying(30) DEFAULT 'internal'::character varying NOT NULL,
    rights_snapshot jsonb DEFAULT '{}'::jsonb NOT NULL,
    provenance_snapshot jsonb DEFAULT '{}'::jsonb NOT NULL,
    added_by_type character varying(20),
    added_by_id character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: group_material_links_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.group_material_links_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: group_material_links_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.group_material_links_id_seq OWNED BY public.group_material_links.id;


--
-- Name: group_memberships; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.group_memberships (
    id integer NOT NULL,
    group_id integer NOT NULL,
    member_type character varying(20) NOT NULL,
    member_id character varying(100) NOT NULL,
    role character varying(30) DEFAULT 'member'::character varying NOT NULL,
    status character varying(20) DEFAULT 'active'::character varying NOT NULL,
    joined_at timestamp with time zone DEFAULT now() NOT NULL,
    left_at timestamp with time zone,
    added_by_type character varying(20),
    added_by_id character varying(100),
    meta jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: group_memberships_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.group_memberships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: group_memberships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.group_memberships_id_seq OWNED BY public.group_memberships.id;


--
-- Name: group_poll_votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.group_poll_votes (
    id integer NOT NULL,
    poll_id integer NOT NULL,
    voter_type character varying(20) NOT NULL,
    voter_id character varying(100) NOT NULL,
    option_index integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: group_poll_votes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.group_poll_votes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: group_poll_votes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.group_poll_votes_id_seq OWNED BY public.group_poll_votes.id;


--
-- Name: group_polls; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.group_polls (
    id integer NOT NULL,
    group_id integer NOT NULL,
    question text NOT NULL,
    options jsonb NOT NULL,
    allow_multiple boolean DEFAULT false NOT NULL,
    status character varying(30) DEFAULT 'active'::character varying NOT NULL,
    closes_at timestamp with time zone,
    created_by_type character varying(20) NOT NULL,
    created_by_id character varying(100) NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: group_polls_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.group_polls_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: group_polls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.group_polls_id_seq OWNED BY public.group_polls.id;


--
-- Name: group_posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.group_posts (
    id integer NOT NULL,
    group_id integer NOT NULL,
    topic_id integer,
    title character varying(220),
    content text NOT NULL,
    visibility_layer character varying(30) DEFAULT 'internal'::character varying NOT NULL,
    status character varying(30) DEFAULT 'active'::character varying NOT NULL,
    created_by_type character varying(20) NOT NULL,
    created_by_id character varying(100) NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: group_posts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.group_posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: group_posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.group_posts_id_seq OWNED BY public.group_posts.id;


--
-- Name: group_topics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.group_topics (
    id integer NOT NULL,
    group_id integer NOT NULL,
    title character varying(220) NOT NULL,
    description text,
    status character varying(30) DEFAULT 'active'::character varying NOT NULL,
    created_by_type character varying(20) NOT NULL,
    created_by_id character varying(100) NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: group_topics_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.group_topics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: group_topics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.group_topics_id_seq OWNED BY public.group_topics.id;


--
-- Name: groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.groups (
    id integer NOT NULL,
    slug character varying(100) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    group_type character varying(60) DEFAULT 'resonance_group'::character varying NOT NULL,
    status character varying(30) DEFAULT 'active'::character varying NOT NULL,
    visibility_layer character varying(30) DEFAULT 'internal'::character varying NOT NULL,
    created_by_type character varying(20) DEFAULT 'system'::character varying NOT NULL,
    created_by_id character varying(100),
    creation_mode character varying(30) DEFAULT 'admin_created'::character varying NOT NULL,
    approval_status character varying(30) DEFAULT 'approved'::character varying NOT NULL,
    canonical_entity_id character varying(100),
    room_id uuid,
    topic_id uuid,
    origin_type character varying(30) DEFAULT 'manual'::character varying,
    origin_id character varying(200),
    rights_policy jsonb DEFAULT '{"member_post": false, "member_view": true, "public_join": false}'::jsonb NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    archived_at timestamp with time zone
);


--
-- Name: groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.groups_id_seq OWNED BY public.groups.id;


--
-- Name: human_material_sources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.human_material_sources (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    human_id uuid NOT NULL,
    source_type character varying NOT NULL,
    source_ref_table character varying,
    source_ref_id uuid,
    title character varying(300),
    content text,
    event_time timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    origin_visibility character varying DEFAULT 'privat'::character varying NOT NULL,
    consent_status character varying DEFAULT 'offen'::character varying NOT NULL,
    quote_permission character varying DEFAULT 'privat'::character varying NOT NULL,
    anonymization_mode character varying DEFAULT 'keine'::character varying NOT NULL,
    public_origin_label character varying,
    internal_origin_ref text,
    source_context jsonb DEFAULT '{}'::jsonb NOT NULL,
    revoked_at timestamp with time zone,
    created_by_process character varying DEFAULT 'manual'::character varying NOT NULL,
    visibility_layer character varying DEFAULT 'private'::character varying NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: human_material_to_splitter; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.human_material_to_splitter (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_id uuid NOT NULL,
    splitter_id uuid NOT NULL,
    transformation_note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by character varying DEFAULT 'manual'::character varying NOT NULL,
    consent_snapshot jsonb DEFAULT '{}'::jsonb NOT NULL,
    visibility_snapshot jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: human_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.human_profiles (
    user_id uuid NOT NULL,
    bio text,
    gedankenwelt text,
    public_tags jsonb DEFAULT '[]'::jsonb NOT NULL,
    avatar_symbol character varying(50),
    visibility character varying(20) DEFAULT 'public'::character varying NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: human_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.human_users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    username character varying(50) NOT NULL,
    display_name character varying(100),
    role character varying(20) DEFAULT 'mensch'::character varying NOT NULL,
    password_hash character varying NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    last_seen timestamp with time zone,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    email character varying(255)
);


--
-- Name: keimkoerper; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.keimkoerper (
    id integer NOT NULL,
    knoten_id integer,
    herkunft_wesen text NOT NULL,
    differenz_beschreibung text,
    schattenantworten jsonb DEFAULT '[]'::jsonb,
    pruefungen jsonb DEFAULT '{"welt": null, "stille": null, "herkunft": null, "konflikt": null, "differenz": null}'::jsonb,
    schwellendruck double precision DEFAULT 0,
    zustand text DEFAULT 'formspannung'::text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT keimkoerper_zustand_check CHECK ((zustand = ANY (ARRAY['formspannung'::text, 'schattenantwort'::text, 'schwellenwesen'::text, 'geboren'::text, 'zerfallen'::text])))
);


--
-- Name: keimkoerper_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.keimkoerper_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: keimkoerper_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.keimkoerper_id_seq OWNED BY public.keimkoerper.id;


--
-- Name: llm_warteschlange; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.llm_warteschlange (
    id bigint NOT NULL,
    server character varying(20) NOT NULL,
    prioritaet smallint NOT NULL,
    rufer character varying(100) NOT NULL,
    angefragt_um timestamp with time zone DEFAULT now() NOT NULL,
    slot_bis timestamp with time zone
);


--
-- Name: llm_warteschlange_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.llm_warteschlange_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: llm_warteschlange_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.llm_warteschlange_id_seq OWNED BY public.llm_warteschlange.id;


--
-- Name: mw_kalender; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mw_kalender (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    titel character varying(200) NOT NULL,
    beschreibung text,
    start_zeit timestamp with time zone NOT NULL,
    end_zeit timestamp with time zone,
    ganztaegig boolean DEFAULT false NOT NULL,
    erinnerung jsonb DEFAULT '[]'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    sichtbarkeit character varying(20) DEFAULT 'privat'::character varying NOT NULL
);


--
-- Name: mw_notizen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mw_notizen (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    titel character varying(200),
    inhalt text NOT NULL,
    typ character varying(20) DEFAULT 'notiz'::character varying NOT NULL,
    erledigt boolean DEFAULT false NOT NULL,
    gepinnt boolean DEFAULT false NOT NULL,
    zuletzt_offen timestamp with time zone,
    zitierbar boolean,
    splitter_erzeugt boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    sichtbarkeit character varying(20) DEFAULT 'privat'::character varying NOT NULL
);


--
-- Name: mw_tagebuch; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mw_tagebuch (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    inhalt text NOT NULL,
    zitierbar boolean,
    splitter_erzeugt boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    sichtbarkeit character varying(20) DEFAULT 'privat'::character varying NOT NULL
);


--
-- Name: mw_traumtagebuch; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mw_traumtagebuch (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    inhalt text NOT NULL,
    traum_datum date DEFAULT CURRENT_DATE NOT NULL,
    zitierbar boolean,
    splitter_erzeugt boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    sichtbarkeit character varying(20) DEFAULT 'privat'::character varying NOT NULL
);


--
-- Name: nachrichten; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.nachrichten (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    sender_id uuid,
    empfaenger_id uuid,
    inhalt text NOT NULL,
    gelesen boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb,
    sender_wesen_id text,
    empfaenger_wesen_id text,
    CONSTRAINT nachrichten_inhalt_check CHECK ((char_length(inhalt) <= 2000))
);


--
-- Name: nutzer_sichtbarkeit; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.nutzer_sichtbarkeit (
    user_id uuid NOT NULL,
    gedankenblasen_anonym boolean DEFAULT false,
    notizen_anonym boolean DEFAULT true,
    schattenkommentare_anonym boolean DEFAULT true,
    zitierbar boolean DEFAULT true,
    verweilen_tracking boolean DEFAULT true,
    meta jsonb DEFAULT '{}'::jsonb
);


--
-- Name: post_reads; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.post_reads (
    user_id uuid NOT NULL,
    post_id uuid NOT NULL,
    read_at timestamp with time zone DEFAULT now()
);


--
-- Name: post_relationen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.post_relationen (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    von_post_id uuid NOT NULL,
    rel_typ character varying NOT NULL,
    ziel_typ character varying NOT NULL,
    ziel_id character varying NOT NULL,
    zu_post_id uuid,
    erstellt_von_type character varying DEFAULT 'system'::character varying,
    erstellt_von_id character varying DEFAULT 'system'::character varying,
    notiz text,
    created_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT ck_zu_post_konsistent CHECK (((zu_post_id IS NULL) OR ((ziel_typ)::text = 'post'::text))),
    CONSTRAINT post_relationen_rel_typ_check CHECK (((rel_typ)::text = ANY ((ARRAY['reply_to'::character varying, 'upgrade_of'::character varying, 'split_from'::character varying, 'contradicts'::character varying, 'echoes'::character varying, 'buried_in'::character varying, 'dream_fragment_of'::character varying, 'resonates_with'::character varying])::text[]))),
    CONSTRAINT post_relationen_ziel_typ_check CHECK (((ziel_typ)::text = ANY ((ARRAY['post'::character varying, 'thema'::character varying, 'splitter'::character varying, 'traum'::character varying, 'resonanz'::character varying, 'flarum_origin'::character varying, 'event'::character varying])::text[])))
);


--
-- Name: post_similarity; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.post_similarity (
    post_a_id uuid NOT NULL,
    post_b_id uuid NOT NULL,
    score double precision NOT NULL,
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT post_similarity_check CHECK ((post_a_id < post_b_id))
);


--
-- Name: post_spuren; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.post_spuren (
    post_id uuid NOT NULL,
    spur_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: profil_gestaltung; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.profil_gestaltung (
    user_id uuid NOT NULL,
    hintergrund_farbe character varying(20) DEFAULT '#020508'::character varying,
    akzent_farbe character varying(20) DEFAULT '#1a4a6a'::character varying,
    hintergrund_bild_id uuid,
    custom_css text,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: raeume; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.raeume (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(100) NOT NULL,
    beschreibung text,
    slug character varying(100) NOT NULL,
    farbe character varying(20),
    status character varying DEFAULT 'aktiv'::character varying,
    sichtbarkeit character varying DEFAULT 'public'::character varying,
    position_order integer DEFAULT 0,
    erstellt_von character varying DEFAULT 'system'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb
);


--
-- Name: rag_embeddings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rag_embeddings (
    id bigint NOT NULL,
    chunk_id bigint NOT NULL,
    modell text NOT NULL,
    embedding public.vector(1024) NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    erstellt_am timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: rag_embeddings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.rag_embeddings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: rag_embeddings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.rag_embeddings_id_seq OWNED BY public.rag_embeddings.id;


--
-- Name: rag_retrieval_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rag_retrieval_results (
    id bigint NOT NULL,
    run_id bigint NOT NULL,
    chunk_id bigint NOT NULL,
    rang integer NOT NULL,
    score double precision,
    tatsaechlich_verwendet boolean DEFAULT false NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    erstellt_am timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: rag_retrieval_results_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.rag_retrieval_results_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: rag_retrieval_results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.rag_retrieval_results_id_seq OWNED BY public.rag_retrieval_results.id;


--
-- Name: rag_retrieval_runs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rag_retrieval_runs (
    id bigint NOT NULL,
    wesen text,
    anlass text,
    anfrage_text text NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    erstellt_am timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: rag_retrieval_runs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.rag_retrieval_runs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: rag_retrieval_runs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.rag_retrieval_runs_id_seq OWNED BY public.rag_retrieval_runs.id;


--
-- Name: rag_source_chunks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rag_source_chunks (
    id bigint NOT NULL,
    source_object_id bigint NOT NULL,
    chunk_index integer NOT NULL,
    ueberschrift text,
    inhalt text NOT NULL,
    inhalt_tsv tsvector GENERATED ALWAYS AS (to_tsvector('german'::regconfig, ((COALESCE(ueberschrift, ''::text) || ' '::text) || inhalt))) STORED,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    erstellt_am timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: rag_source_chunks_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.rag_source_chunks_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: rag_source_chunks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.rag_source_chunks_id_seq OWNED BY public.rag_source_chunks.id;


--
-- Name: rag_source_objects; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rag_source_objects (
    id bigint NOT NULL,
    external_id text NOT NULL,
    quelle text NOT NULL,
    wesen text,
    titel text,
    inhalt text NOT NULL,
    erstellungszeit timestamp with time zone,
    urheber text,
    herkunftsort text NOT NULL,
    sichtbarkeit text DEFAULT 'welt'::text NOT NULL,
    ereignistyp text NOT NULL,
    wahrheitsstatus text DEFAULT 'aus_datei_abgeleitet'::text NOT NULL,
    inhalt_pruefsumme text NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    erstellt_am timestamp with time zone DEFAULT now() NOT NULL,
    aktualisiert_am timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: rag_source_objects_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.rag_source_objects_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: rag_source_objects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.rag_source_objects_id_seq OWNED BY public.rag_source_objects.id;


--
-- Name: resonanz_emoji_counts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.resonanz_emoji_counts (
    post_ref character varying NOT NULL,
    post_source character varying NOT NULL,
    emoji character varying(10) NOT NULL,
    count integer DEFAULT 0 NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: resonanzen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.resonanzen (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    post_ref character varying NOT NULL,
    post_source character varying DEFAULT 'flarum'::character varying NOT NULL,
    user_id uuid NOT NULL,
    emojis jsonb NOT NULL,
    sent_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: schatten_antworten; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schatten_antworten (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    schatten_id uuid NOT NULL,
    autor_type character varying NOT NULL,
    autor_id character varying NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb,
    parent_id uuid,
    thread_id uuid
);


--
-- Name: schattenkommentare; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schattenkommentare (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    post_id uuid NOT NULL,
    human_id uuid,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb,
    entity_id character varying,
    antwortstatus character varying DEFAULT 'offen'::character varying,
    zitatrechte character varying DEFAULT 'privat'::character varying,
    folge_splitter_id uuid,
    folge_post_id uuid
);


--
-- Name: schlafbriefe; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schlafbriefe (
    brief_id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id character varying NOT NULL,
    phase_id uuid,
    inhalt text NOT NULL,
    geschrieben_at timestamp with time zone DEFAULT now() NOT NULL,
    gelesen_at timestamp with time zone,
    absender_id uuid,
    typ character varying(30) DEFAULT 'aufwach'::character varying,
    ist_selbstbrief boolean DEFAULT false NOT NULL,
    modell character varying(100),
    meta jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT schlafbriefe_typ_check CHECK (((typ)::text = ANY ((ARRAY['aufwach'::character varying, 'flarum_brief'::character varying, 'sonstig'::character varying])::text[])))
);


--
-- Name: sleep_phases; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sleep_phases (
    phase_id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id character varying NOT NULL,
    phase_type character varying NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    ended_at timestamp with time zone,
    duration_min integer GENERATED ALWAYS AS ((EXTRACT(epoch FROM (ended_at - started_at)) / (60)::numeric)) STORED,
    zustand jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT sleep_phases_phase_type_check CHECK (((phase_type)::text = ANY ((ARRAY['kurz'::character varying, 'hauptschlaf'::character varying])::text[])))
);


--
-- Name: splitter; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.splitter (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    origin_type character varying NOT NULL,
    origin_id character varying,
    entity_id character varying,
    human_id uuid,
    herkunft_sichtbar boolean DEFAULT true,
    essenz text,
    thematische_tags jsonb DEFAULT '[]'::jsonb,
    materialitaet character varying DEFAULT 'sternenstaub'::character varying,
    energie double precision DEFAULT 1.0,
    verbindungen integer DEFAULT 0,
    abstossungen integer DEFAULT 0,
    pos_x double precision DEFAULT 0,
    pos_y double precision DEFAULT 0,
    vel_x double precision DEFAULT 0,
    vel_y double precision DEFAULT 0,
    status character varying DEFAULT 'aktiv'::character varying,
    letzter_kontakt timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb,
    aufnahmen integer DEFAULT 0,
    ausstoessungsgrund text,
    konfliktachse text,
    substanzspur text,
    resonanzspur jsonb DEFAULT '{}'::jsonb,
    traumspur jsonb DEFAULT '{}'::jsonb,
    schwellendruck double precision DEFAULT 0,
    herkunft_wesen text
);


--
-- Name: splitter_aufnahmen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.splitter_aufnahmen (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    splitter_id uuid NOT NULL,
    aufnehmer_type character varying NOT NULL,
    aufnehmer_id character varying NOT NULL,
    begruendung text,
    aufgenommen_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT splitter_aufnahmen_aufnehmer_type_check CHECK (((aufnehmer_type)::text = ANY ((ARRAY['entity'::character varying, 'human'::character varying, 'system'::character varying])::text[])))
);


--
-- Name: splitter_knoten; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.splitter_knoten (
    id integer NOT NULL,
    splitter_ids uuid[] DEFAULT '{}'::uuid[],
    herkunft_wesen text,
    konfliktachse text,
    substanzspur text,
    schwellendruck double precision DEFAULT 0,
    zustand text DEFAULT 'treibend'::text,
    payload jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT splitter_knoten_zustand_check CHECK ((zustand = ANY (ARRAY['treibend'::text, 'knotend'::text, 'keimkoerper'::text, 'schattenkoerper'::text, 'schwellenwesen'::text])))
);


--
-- Name: splitter_knoten_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.splitter_knoten_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: splitter_knoten_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.splitter_knoten_id_seq OWNED BY public.splitter_knoten.id;


--
-- Name: splitter_verbindungen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.splitter_verbindungen (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    splitter_a_id uuid,
    splitter_b_id uuid,
    verbindungstyp character varying DEFAULT 'resonanz'::character varying,
    staerke double precision DEFAULT 1.0,
    created_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb
);


--
-- Name: spuren; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spuren (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    slug character varying(100) NOT NULL,
    name character varying(200) NOT NULL,
    type character varying(50) DEFAULT 'unterthema'::character varying NOT NULL,
    beschreibung text,
    erstellt_von character varying DEFAULT 'system'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb
);


--
-- Name: substance_catalog; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.substance_catalog (
    id integer NOT NULL,
    slug character varying(80) NOT NULL,
    name character varying(120) NOT NULL,
    description text,
    substance_type character varying(40) DEFAULT 'stimulant'::character varying NOT NULL,
    fictional_effect_profile jsonb DEFAULT '{}'::jsonb NOT NULL,
    risk_profile jsonb DEFAULT '{}'::jsonb NOT NULL,
    cooldown_policy jsonb DEFAULT '{"min_stunden": 6}'::jsonb NOT NULL,
    dependency_potential numeric(3,2) DEFAULT 0.0 NOT NULL,
    withdrawal_potential numeric(3,2) DEFAULT 0.0 NOT NULL,
    visibility_layer character varying(20) DEFAULT 'internal'::character varying NOT NULL,
    status character varying(20) DEFAULT 'katalog'::character varying NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: substance_catalog_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.substance_catalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: substance_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.substance_catalog_id_seq OWNED BY public.substance_catalog.id;


--
-- Name: substance_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.substance_events (
    id integer NOT NULL,
    wesen_id text NOT NULL,
    event_type text NOT NULL,
    substance text,
    payload jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: substance_events_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.substance_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: substance_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.substance_events_id_seq OWNED BY public.substance_events.id;


--
-- Name: substance_sediments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.substance_sediments (
    id integer NOT NULL,
    wesen_id text NOT NULL,
    sediment_type text NOT NULL,
    substance_suspect text,
    confidence double precision DEFAULT 0,
    payload jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: substance_sediments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.substance_sediments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: substance_sediments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.substance_sediments_id_seq OWNED BY public.substance_sediments.id;


--
-- Name: supporter_bewerbungen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.supporter_bewerbungen (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    motivation text,
    status character varying(20) DEFAULT 'offen'::character varying NOT NULL,
    admin_notiz text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT supporter_bewerbungen_status_check CHECK (((status)::text = ANY ((ARRAY['offen'::character varying, 'genehmigt'::character varying, 'abgelehnt'::character varying])::text[])))
);


--
-- Name: system_flags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.system_flags (
    key text NOT NULL,
    value text DEFAULT 'false'::text NOT NULL,
    beschreibung text DEFAULT ''::text NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_by text DEFAULT 'system'::text NOT NULL
);


--
-- Name: thema_cluster_vorschlaege; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.thema_cluster_vorschlaege (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    thema_ids jsonb NOT NULL,
    vorgeschlagener_name character varying(200),
    score double precision NOT NULL,
    status character varying DEFAULT 'offen'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb
);


--
-- Name: thema_similarity; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.thema_similarity (
    thema_a_id uuid NOT NULL,
    thema_b_id uuid NOT NULL,
    score double precision NOT NULL,
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT thema_similarity_check CHECK ((thema_a_id < thema_b_id))
);


--
-- Name: themen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.themen (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    raum_id uuid,
    name character varying(200) NOT NULL,
    beschreibung text,
    slug character varying(200) NOT NULL,
    status character varying DEFAULT 'aktiv'::character varying,
    inkubations_grund text,
    resonanz_gewicht double precision DEFAULT 0.0,
    sichtbarkeit character varying DEFAULT 'public'::character varying,
    erstellt_von character varying DEFAULT 'system'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb,
    parent_id uuid,
    tiefe integer DEFAULT 0,
    auto_erstellt boolean DEFAULT false,
    tsv tsvector,
    klima_status character varying DEFAULT 'stable'::character varying,
    CONSTRAINT themen_klima_status_check CHECK (((klima_status)::text = ANY ((ARRAY['stable'::character varying, 'fermenting'::character varying, 'overheated'::character varying, 'splitting'::character varying, 'buried'::character varying, 'repeating'::character varying, 'exhausted'::character varying, 'seeded'::character varying])::text[])))
);


--
-- Name: translations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.translations (
    text_hash text NOT NULL,
    target_lang text NOT NULL,
    source_text text NOT NULL,
    translation text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: traumkandidaten_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.traumkandidaten_events (
    id bigint NOT NULL,
    log_id uuid NOT NULL,
    event_id uuid NOT NULL,
    status character varying NOT NULL,
    begruendung text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT traumkandidaten_events_status_check CHECK (((status)::text = ANY ((ARRAY['betrachtet'::character varying, 'ausgewaehlt'::character varying])::text[])))
);


--
-- Name: traumkandidaten_events_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.traumkandidaten_events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: traumkandidaten_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.traumkandidaten_events_id_seq OWNED BY public.traumkandidaten_events.id;


--
-- Name: traumkandidaten_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.traumkandidaten_log (
    log_id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id character varying NOT NULL,
    sleep_phase_id uuid,
    selektionsregel character varying NOT NULL,
    begruendung text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: traumspuren; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.traumspuren (
    spur_id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id character varying NOT NULL,
    log_id uuid,
    llm_traumtext text,
    integrator_spur text,
    integrator_status character varying DEFAULT 'offen'::character varying NOT NULL,
    integrator_begruendung text,
    gewichtungsvorschlag jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT traumspuren_integrator_status_check CHECK (((integrator_status)::text = ANY ((ARRAY['offen'::character varying, 'angenommen'::character varying, 'abgelehnt'::character varying, 'zurueckgestellt'::character varying])::text[])))
);


--
-- Name: traumszenarien; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.traumszenarien (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    thema character varying NOT NULL,
    titel character varying,
    inhalt text NOT NULL,
    ton character varying,
    erstellt_von character varying DEFAULT 'daniel'::character varying NOT NULL,
    freigegeben boolean DEFAULT false NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: traumtagebuch; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.traumtagebuch (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    human_id uuid NOT NULL,
    inhalt text NOT NULL,
    stimmung character varying,
    fuer_wesen boolean DEFAULT false NOT NULL,
    freigegeben boolean DEFAULT false NOT NULL,
    geschrieben_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb
);


--
-- Name: unterthemen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.unterthemen (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    thema_id uuid,
    name character varying(200) NOT NULL,
    slug character varying(200) NOT NULL,
    status character varying DEFAULT 'aktiv'::character varying,
    sichtbarkeit character varying DEFAULT 'public'::character varying,
    erstellt_von character varying DEFAULT 'system'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb
);


--
-- Name: user_modules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_modules (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    module_name character varying(50) NOT NULL,
    enabled boolean DEFAULT true NOT NULL,
    config jsonb DEFAULT '{}'::jsonb NOT NULL,
    activated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
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
-- Name: verweilen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.verweilen (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    target_type character varying NOT NULL,
    target_id character varying NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    ended_at timestamp with time zone,
    duration_seconds integer,
    interaction_signals jsonb DEFAULT '[]'::jsonb NOT NULL,
    is_valid boolean DEFAULT false NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: wesen_chat_verlauf; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wesen_chat_verlauf (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    wesen_name text NOT NULL,
    rolle text NOT NULL,
    inhalt text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    CONSTRAINT wesen_chat_verlauf_rolle_check CHECK ((rolle = ANY (ARRAY['user'::text, 'assistant'::text, 'system'::text])))
);


--
-- Name: wesen_eigene_dienste; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wesen_eigene_dienste (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    dienst_name character varying(150) NOT NULL,
    wesen character varying(100) NOT NULL,
    anzeige_name character varying(200) NOT NULL,
    takt_sekunden integer NOT NULL,
    start_offset_sekunden integer DEFAULT 0 NOT NULL,
    verhalten_prompt text NOT NULL,
    ziel_typ character varying(30) DEFAULT 'neue_diskussion'::character varying NOT NULL,
    ziel_discussion_id integer,
    ziel_tag_ids integer[],
    status character varying(20) DEFAULT 'aktiv'::character varying NOT NULL,
    script_pfad text,
    unit_name character varying(150),
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    eigene_diskussion_id integer,
    CONSTRAINT wesen_eigene_dienste_status_check CHECK (((status)::text = ANY ((ARRAY['aktiv'::character varying, 'deaktiviert'::character varying])::text[]))),
    CONSTRAINT wesen_eigene_dienste_ziel_typ_check CHECK (((ziel_typ)::text = ANY ((ARRAY['fester_thread'::character varying, 'neue_diskussion'::character varying, 'vault_only'::character varying, 'eigene_diskussion_einmalig'::character varying, 'wesen_entscheidet_selbst'::character varying, 'eigener_container'::character varying])::text[])))
);


--
-- Name: wesen_entwicklung; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wesen_entwicklung (
    entity_id character varying NOT NULL,
    fuersorge_gesamt double precision DEFAULT 0.0,
    fuersorge_heute double precision DEFAULT 0.0,
    vernachlaessigung_stunden integer DEFAULT 0,
    letzte_interaktion timestamp with time zone,
    entwicklungsstufe integer DEFAULT 1,
    stufe_punkte_schwelle double precision DEFAULT 100.0,
    stimmungs_drift double precision DEFAULT 0.0,
    meta jsonb DEFAULT '{}'::jsonb
);


--
-- Name: wesen_fuersorge; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wesen_fuersorge (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    entity_id character varying NOT NULL,
    fuersorge_typ character varying NOT NULL,
    punkte double precision DEFAULT 1.0,
    created_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb
);


--
-- Name: wesen_gedanken; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wesen_gedanken (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    post_ref character varying NOT NULL,
    post_source character varying DEFAULT 'flarum'::character varying NOT NULL,
    entity_id character varying NOT NULL,
    stimmung_bei_erstellung character varying,
    fokus_bei_erstellung text,
    selbstmodell_snapshot jsonb,
    access_level character varying DEFAULT 'unlocked'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: wesen_web_besuche; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wesen_web_besuche (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    wesen_name text NOT NULL,
    url text NOT NULL,
    screenshot bytea,
    seiten_text text,
    reaktion text,
    visited_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: widmungen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.widmungen (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    wesen_id text,
    bild_pfad text NOT NULL,
    widmungstext text DEFAULT ''::text,
    status text DEFAULT 'pending'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    reviewed_at timestamp with time zone,
    reviewed_by uuid,
    meta jsonb DEFAULT '{}'::jsonb
);


--
-- Name: zitate; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.zitate (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    content text NOT NULL,
    autor_type character varying NOT NULL,
    autor_id character varying NOT NULL,
    quelle_type character varying,
    quelle_id character varying,
    rechte_level character varying DEFAULT 'privat'::character varying NOT NULL,
    created_by_type character varying DEFAULT 'human'::character varying NOT NULL,
    created_by_id character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    meta jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT zitate_rechte_level_check CHECK (((rechte_level)::text = ANY ((ARRAY['privat'::character varying, 'intern'::character varying, 'community'::character varying, 'oeffentlich'::character varying, 'gemeinfrei'::character varying])::text[])))
);


--
-- Name: entity_substance_use id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_substance_use ALTER COLUMN id SET DEFAULT nextval('public.entity_substance_use_id_seq'::regclass);


--
-- Name: group_chat_messages id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_chat_messages ALTER COLUMN id SET DEFAULT nextval('public.group_chat_messages_id_seq'::regclass);


--
-- Name: group_material_links id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_material_links ALTER COLUMN id SET DEFAULT nextval('public.group_material_links_id_seq'::regclass);


--
-- Name: group_memberships id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_memberships ALTER COLUMN id SET DEFAULT nextval('public.group_memberships_id_seq'::regclass);


--
-- Name: group_poll_votes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_poll_votes ALTER COLUMN id SET DEFAULT nextval('public.group_poll_votes_id_seq'::regclass);


--
-- Name: group_polls id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_polls ALTER COLUMN id SET DEFAULT nextval('public.group_polls_id_seq'::regclass);


--
-- Name: group_posts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_posts ALTER COLUMN id SET DEFAULT nextval('public.group_posts_id_seq'::regclass);


--
-- Name: group_topics id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_topics ALTER COLUMN id SET DEFAULT nextval('public.group_topics_id_seq'::regclass);


--
-- Name: groups id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.groups ALTER COLUMN id SET DEFAULT nextval('public.groups_id_seq'::regclass);


--
-- Name: keimkoerper id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keimkoerper ALTER COLUMN id SET DEFAULT nextval('public.keimkoerper_id_seq'::regclass);


--
-- Name: llm_warteschlange id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.llm_warteschlange ALTER COLUMN id SET DEFAULT nextval('public.llm_warteschlange_id_seq'::regclass);


--
-- Name: rag_embeddings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_embeddings ALTER COLUMN id SET DEFAULT nextval('public.rag_embeddings_id_seq'::regclass);


--
-- Name: rag_retrieval_results id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_retrieval_results ALTER COLUMN id SET DEFAULT nextval('public.rag_retrieval_results_id_seq'::regclass);


--
-- Name: rag_retrieval_runs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_retrieval_runs ALTER COLUMN id SET DEFAULT nextval('public.rag_retrieval_runs_id_seq'::regclass);


--
-- Name: rag_source_chunks id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_source_chunks ALTER COLUMN id SET DEFAULT nextval('public.rag_source_chunks_id_seq'::regclass);


--
-- Name: rag_source_objects id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_source_objects ALTER COLUMN id SET DEFAULT nextval('public.rag_source_objects_id_seq'::regclass);


--
-- Name: splitter_knoten id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.splitter_knoten ALTER COLUMN id SET DEFAULT nextval('public.splitter_knoten_id_seq'::regclass);


--
-- Name: substance_catalog id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.substance_catalog ALTER COLUMN id SET DEFAULT nextval('public.substance_catalog_id_seq'::regclass);


--
-- Name: substance_events id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.substance_events ALTER COLUMN id SET DEFAULT nextval('public.substance_events_id_seq'::regclass);


--
-- Name: substance_sediments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.substance_sediments ALTER COLUMN id SET DEFAULT nextval('public.substance_sediments_id_seq'::regclass);


--
-- Name: traumkandidaten_events id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traumkandidaten_events ALTER COLUMN id SET DEFAULT nextval('public.traumkandidaten_events_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: checkpoint_blobs checkpoint_blobs_pkey; Type: CONSTRAINT; Schema: geni; Owner: -
--

ALTER TABLE ONLY geni.checkpoint_blobs
    ADD CONSTRAINT checkpoint_blobs_pkey PRIMARY KEY (thread_id, checkpoint_ns, channel, version);


--
-- Name: checkpoint_migrations checkpoint_migrations_pkey; Type: CONSTRAINT; Schema: geni; Owner: -
--

ALTER TABLE ONLY geni.checkpoint_migrations
    ADD CONSTRAINT checkpoint_migrations_pkey PRIMARY KEY (v);


--
-- Name: checkpoint_writes checkpoint_writes_pkey; Type: CONSTRAINT; Schema: geni; Owner: -
--

ALTER TABLE ONLY geni.checkpoint_writes
    ADD CONSTRAINT checkpoint_writes_pkey PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx);


--
-- Name: checkpoints checkpoints_pkey; Type: CONSTRAINT; Schema: geni; Owner: -
--

ALTER TABLE ONLY geni.checkpoints
    ADD CONSTRAINT checkpoints_pkey PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id);


--
-- Name: ankuendigungen_kommentare ankuendigungen_kommentare_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ankuendigungen_kommentare
    ADD CONSTRAINT ankuendigungen_kommentare_pkey PRIMARY KEY (id);


--
-- Name: ankuendigungen ankuendigungen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ankuendigungen
    ADD CONSTRAINT ankuendigungen_pkey PRIMARY KEY (id);


--
-- Name: benachrichtigungen benachrichtigungen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.benachrichtigungen
    ADD CONSTRAINT benachrichtigungen_pkey PRIMARY KEY (id);


--
-- Name: bild_moderation bild_moderation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bild_moderation
    ADD CONSTRAINT bild_moderation_pkey PRIMARY KEY (id);


--
-- Name: blase_verwendungen blase_verwendungen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blase_verwendungen
    ADD CONSTRAINT blase_verwendungen_pkey PRIMARY KEY (id);


--
-- Name: checkpoint_blobs checkpoint_blobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_blobs
    ADD CONSTRAINT checkpoint_blobs_pkey PRIMARY KEY (thread_id, checkpoint_ns, channel, version);


--
-- Name: checkpoint_migrations checkpoint_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_migrations
    ADD CONSTRAINT checkpoint_migrations_pkey PRIMARY KEY (v);


--
-- Name: checkpoint_writes checkpoint_writes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_writes
    ADD CONSTRAINT checkpoint_writes_pkey PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx);


--
-- Name: checkpoints checkpoints_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoints
    ADD CONSTRAINT checkpoints_pkey PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id);


--
-- Name: cyberlinge cyberlinge_entity_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cyberlinge
    ADD CONSTRAINT cyberlinge_entity_id_key UNIQUE (entity_id);


--
-- Name: cyberlinge cyberlinge_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cyberlinge
    ADD CONSTRAINT cyberlinge_pkey PRIMARY KEY (id);


--
-- Name: dienst_konfiguration dienst_konfiguration_dienst_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dienst_konfiguration
    ADD CONSTRAINT dienst_konfiguration_dienst_name_key UNIQUE (dienst_name);


--
-- Name: dienst_konfiguration dienst_konfiguration_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dienst_konfiguration
    ADD CONSTRAINT dienst_konfiguration_pkey PRIMARY KEY (id);


--
-- Name: entity_activity entity_activity_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_activity
    ADD CONSTRAINT entity_activity_pkey PRIMARY KEY (entity_id);


--
-- Name: entity_denkstream entity_denkstream_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_denkstream
    ADD CONSTRAINT entity_denkstream_pkey PRIMARY KEY (id);


--
-- Name: entity_dom_events entity_dom_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_dom_events
    ADD CONSTRAINT entity_dom_events_pkey PRIMARY KEY (id);


--
-- Name: entity_fokus_events entity_fokus_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_fokus_events
    ADD CONSTRAINT entity_fokus_events_pkey PRIMARY KEY (id);


--
-- Name: entity_profiles entity_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_profiles
    ADD CONSTRAINT entity_profiles_pkey PRIMARY KEY (entity_id);


--
-- Name: entity_relationships entity_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_relationships
    ADD CONSTRAINT entity_relationships_pkey PRIMARY KEY (id);


--
-- Name: entity_screenshots entity_screenshots_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_screenshots
    ADD CONSTRAINT entity_screenshots_pkey PRIMARY KEY (entity_id);


--
-- Name: entity_selfmodel_entries entity_selfmodel_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_selfmodel_entries
    ADD CONSTRAINT entity_selfmodel_entries_pkey PRIMARY KEY (entry_id);


--
-- Name: entity_slots entity_slots_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_slots
    ADD CONSTRAINT entity_slots_pkey PRIMARY KEY (entity_id);


--
-- Name: entity_states entity_states_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_states
    ADD CONSTRAINT entity_states_pkey PRIMARY KEY (entity_id);


--
-- Name: entity_substance_state entity_substance_state_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_substance_state
    ADD CONSTRAINT entity_substance_state_pkey PRIMARY KEY (entity_id, substance_id);


--
-- Name: entity_substance_use entity_substance_use_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_substance_use
    ADD CONSTRAINT entity_substance_use_pkey PRIMARY KEY (id);


--
-- Name: entity_thinking_log entity_thinking_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_thinking_log
    ADD CONSTRAINT entity_thinking_log_pkey PRIMARY KEY (id);


--
-- Name: entity_wuensche entity_wuensche_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_wuensche
    ADD CONSTRAINT entity_wuensche_pkey PRIMARY KEY (wunsch_id);


--
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (event_id);


--
-- Name: flarum_stopp_protokoll flarum_stopp_protokoll_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.flarum_stopp_protokoll
    ADD CONSTRAINT flarum_stopp_protokoll_pkey PRIMARY KEY (id);


--
-- Name: follows follows_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follows
    ADD CONSTRAINT follows_pkey PRIMARY KEY (id);


--
-- Name: follows follows_user_id_target_type_target_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follows
    ADD CONSTRAINT follows_user_id_target_type_target_id_key UNIQUE (user_id, target_type, target_id);


--
-- Name: ftw_posts ftw_posts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ftw_posts
    ADD CONSTRAINT ftw_posts_pkey PRIMARY KEY (id);


--
-- Name: gedankenblasen gedankenblasen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gedankenblasen
    ADD CONSTRAINT gedankenblasen_pkey PRIMARY KEY (id);


--
-- Name: gedankenwelt_eintraege gedankenwelt_eintraege_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gedankenwelt_eintraege
    ADD CONSTRAINT gedankenwelt_eintraege_pkey PRIMARY KEY (id);


--
-- Name: group_chat_messages group_chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_chat_messages
    ADD CONSTRAINT group_chat_messages_pkey PRIMARY KEY (id);


--
-- Name: group_creation_policy group_creation_policy_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_creation_policy
    ADD CONSTRAINT group_creation_policy_pkey PRIMARY KEY (id);


--
-- Name: group_material_links group_material_links_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_material_links
    ADD CONSTRAINT group_material_links_pkey PRIMARY KEY (id);


--
-- Name: group_memberships group_memberships_group_id_member_type_member_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_memberships
    ADD CONSTRAINT group_memberships_group_id_member_type_member_id_key UNIQUE (group_id, member_type, member_id);


--
-- Name: group_memberships group_memberships_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_memberships
    ADD CONSTRAINT group_memberships_pkey PRIMARY KEY (id);


--
-- Name: group_poll_votes group_poll_votes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_poll_votes
    ADD CONSTRAINT group_poll_votes_pkey PRIMARY KEY (id);


--
-- Name: group_poll_votes group_poll_votes_poll_id_voter_type_voter_id_option_index_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_poll_votes
    ADD CONSTRAINT group_poll_votes_poll_id_voter_type_voter_id_option_index_key UNIQUE (poll_id, voter_type, voter_id, option_index);


--
-- Name: group_polls group_polls_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_polls
    ADD CONSTRAINT group_polls_pkey PRIMARY KEY (id);


--
-- Name: group_posts group_posts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_posts
    ADD CONSTRAINT group_posts_pkey PRIMARY KEY (id);


--
-- Name: group_topics group_topics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_topics
    ADD CONSTRAINT group_topics_pkey PRIMARY KEY (id);


--
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (id);


--
-- Name: groups groups_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_slug_key UNIQUE (slug);


--
-- Name: human_material_sources human_material_sources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.human_material_sources
    ADD CONSTRAINT human_material_sources_pkey PRIMARY KEY (id);


--
-- Name: human_material_to_splitter human_material_to_splitter_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.human_material_to_splitter
    ADD CONSTRAINT human_material_to_splitter_pkey PRIMARY KEY (id);


--
-- Name: human_material_to_splitter human_material_to_splitter_source_id_splitter_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.human_material_to_splitter
    ADD CONSTRAINT human_material_to_splitter_source_id_splitter_id_key UNIQUE (source_id, splitter_id);


--
-- Name: human_profiles human_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.human_profiles
    ADD CONSTRAINT human_profiles_pkey PRIMARY KEY (user_id);


--
-- Name: human_users human_users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.human_users
    ADD CONSTRAINT human_users_pkey PRIMARY KEY (id);


--
-- Name: keimkoerper keimkoerper_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keimkoerper
    ADD CONSTRAINT keimkoerper_pkey PRIMARY KEY (id);


--
-- Name: llm_warteschlange llm_warteschlange_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.llm_warteschlange
    ADD CONSTRAINT llm_warteschlange_pkey PRIMARY KEY (id);


--
-- Name: mw_kalender mw_kalender_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mw_kalender
    ADD CONSTRAINT mw_kalender_pkey PRIMARY KEY (id);


--
-- Name: mw_notizen mw_notizen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mw_notizen
    ADD CONSTRAINT mw_notizen_pkey PRIMARY KEY (id);


--
-- Name: mw_tagebuch mw_tagebuch_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mw_tagebuch
    ADD CONSTRAINT mw_tagebuch_pkey PRIMARY KEY (id);


--
-- Name: mw_traumtagebuch mw_traumtagebuch_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mw_traumtagebuch
    ADD CONSTRAINT mw_traumtagebuch_pkey PRIMARY KEY (id);


--
-- Name: nachrichten nachrichten_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nachrichten
    ADD CONSTRAINT nachrichten_pkey PRIMARY KEY (id);


--
-- Name: nutzer_sichtbarkeit nutzer_sichtbarkeit_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nutzer_sichtbarkeit
    ADD CONSTRAINT nutzer_sichtbarkeit_pkey PRIMARY KEY (user_id);


--
-- Name: post_reads post_reads_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_reads
    ADD CONSTRAINT post_reads_pkey PRIMARY KEY (user_id, post_id);


--
-- Name: post_relationen post_relationen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_relationen
    ADD CONSTRAINT post_relationen_pkey PRIMARY KEY (id);


--
-- Name: post_similarity post_similarity_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_similarity
    ADD CONSTRAINT post_similarity_pkey PRIMARY KEY (post_a_id, post_b_id);


--
-- Name: post_spuren post_spuren_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_spuren
    ADD CONSTRAINT post_spuren_pkey PRIMARY KEY (post_id, spur_id);


--
-- Name: profil_gestaltung profil_gestaltung_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.profil_gestaltung
    ADD CONSTRAINT profil_gestaltung_pkey PRIMARY KEY (user_id);


--
-- Name: raeume raeume_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.raeume
    ADD CONSTRAINT raeume_pkey PRIMARY KEY (id);


--
-- Name: raeume raeume_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.raeume
    ADD CONSTRAINT raeume_slug_key UNIQUE (slug);


--
-- Name: rag_embeddings rag_embeddings_chunk_id_modell_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_embeddings
    ADD CONSTRAINT rag_embeddings_chunk_id_modell_key UNIQUE (chunk_id, modell);


--
-- Name: rag_embeddings rag_embeddings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_embeddings
    ADD CONSTRAINT rag_embeddings_pkey PRIMARY KEY (id);


--
-- Name: rag_retrieval_results rag_retrieval_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_retrieval_results
    ADD CONSTRAINT rag_retrieval_results_pkey PRIMARY KEY (id);


--
-- Name: rag_retrieval_runs rag_retrieval_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_retrieval_runs
    ADD CONSTRAINT rag_retrieval_runs_pkey PRIMARY KEY (id);


--
-- Name: rag_source_chunks rag_source_chunks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_source_chunks
    ADD CONSTRAINT rag_source_chunks_pkey PRIMARY KEY (id);


--
-- Name: rag_source_chunks rag_source_chunks_source_object_id_chunk_index_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_source_chunks
    ADD CONSTRAINT rag_source_chunks_source_object_id_chunk_index_key UNIQUE (source_object_id, chunk_index);


--
-- Name: rag_source_objects rag_source_objects_external_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_source_objects
    ADD CONSTRAINT rag_source_objects_external_id_key UNIQUE (external_id);


--
-- Name: rag_source_objects rag_source_objects_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_source_objects
    ADD CONSTRAINT rag_source_objects_pkey PRIMARY KEY (id);


--
-- Name: resonanz_emoji_counts resonanz_emoji_counts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.resonanz_emoji_counts
    ADD CONSTRAINT resonanz_emoji_counts_pkey PRIMARY KEY (post_ref, post_source, emoji);


--
-- Name: resonanzen resonanzen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.resonanzen
    ADD CONSTRAINT resonanzen_pkey PRIMARY KEY (id);


--
-- Name: resonanzen resonanzen_post_ref_post_source_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.resonanzen
    ADD CONSTRAINT resonanzen_post_ref_post_source_user_id_key UNIQUE (post_ref, post_source, user_id);


--
-- Name: schatten_antworten schatten_antworten_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schatten_antworten
    ADD CONSTRAINT schatten_antworten_pkey PRIMARY KEY (id);


--
-- Name: schattenkommentare schattenkommentare_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schattenkommentare
    ADD CONSTRAINT schattenkommentare_pkey PRIMARY KEY (id);


--
-- Name: schattenkommentare schattenkommentare_post_id_human_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schattenkommentare
    ADD CONSTRAINT schattenkommentare_post_id_human_id_key UNIQUE (post_id, human_id);


--
-- Name: schlafbriefe schlafbriefe_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schlafbriefe
    ADD CONSTRAINT schlafbriefe_pkey PRIMARY KEY (brief_id);


--
-- Name: sleep_phases sleep_phases_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sleep_phases
    ADD CONSTRAINT sleep_phases_pkey PRIMARY KEY (phase_id);


--
-- Name: splitter_aufnahmen splitter_aufnahmen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.splitter_aufnahmen
    ADD CONSTRAINT splitter_aufnahmen_pkey PRIMARY KEY (id);


--
-- Name: splitter_knoten splitter_knoten_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.splitter_knoten
    ADD CONSTRAINT splitter_knoten_pkey PRIMARY KEY (id);


--
-- Name: splitter splitter_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.splitter
    ADD CONSTRAINT splitter_pkey PRIMARY KEY (id);


--
-- Name: splitter_verbindungen splitter_verbindungen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.splitter_verbindungen
    ADD CONSTRAINT splitter_verbindungen_pkey PRIMARY KEY (id);


--
-- Name: spuren spuren_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spuren
    ADD CONSTRAINT spuren_pkey PRIMARY KEY (id);


--
-- Name: spuren spuren_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spuren
    ADD CONSTRAINT spuren_slug_key UNIQUE (slug);


--
-- Name: substance_catalog substance_catalog_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.substance_catalog
    ADD CONSTRAINT substance_catalog_pkey PRIMARY KEY (id);


--
-- Name: substance_catalog substance_catalog_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.substance_catalog
    ADD CONSTRAINT substance_catalog_slug_key UNIQUE (slug);


--
-- Name: substance_events substance_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.substance_events
    ADD CONSTRAINT substance_events_pkey PRIMARY KEY (id);


--
-- Name: substance_sediments substance_sediments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.substance_sediments
    ADD CONSTRAINT substance_sediments_pkey PRIMARY KEY (id);


--
-- Name: supporter_bewerbungen supporter_bewerbungen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supporter_bewerbungen
    ADD CONSTRAINT supporter_bewerbungen_pkey PRIMARY KEY (id);


--
-- Name: supporter_bewerbungen supporter_bewerbungen_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supporter_bewerbungen
    ADD CONSTRAINT supporter_bewerbungen_user_id_key UNIQUE (user_id);


--
-- Name: system_flags system_flags_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_flags
    ADD CONSTRAINT system_flags_pkey PRIMARY KEY (key);


--
-- Name: thema_cluster_vorschlaege thema_cluster_vorschlaege_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.thema_cluster_vorschlaege
    ADD CONSTRAINT thema_cluster_vorschlaege_pkey PRIMARY KEY (id);


--
-- Name: thema_similarity thema_similarity_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.thema_similarity
    ADD CONSTRAINT thema_similarity_pkey PRIMARY KEY (thema_a_id, thema_b_id);


--
-- Name: themen themen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.themen
    ADD CONSTRAINT themen_pkey PRIMARY KEY (id);


--
-- Name: translations translations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.translations
    ADD CONSTRAINT translations_pkey PRIMARY KEY (text_hash, target_lang);


--
-- Name: traumkandidaten_events traumkandidaten_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traumkandidaten_events
    ADD CONSTRAINT traumkandidaten_events_pkey PRIMARY KEY (id);


--
-- Name: traumkandidaten_log traumkandidaten_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traumkandidaten_log
    ADD CONSTRAINT traumkandidaten_log_pkey PRIMARY KEY (log_id);


--
-- Name: traumspuren traumspuren_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traumspuren
    ADD CONSTRAINT traumspuren_pkey PRIMARY KEY (spur_id);


--
-- Name: traumszenarien traumszenarien_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traumszenarien
    ADD CONSTRAINT traumszenarien_pkey PRIMARY KEY (id);


--
-- Name: traumtagebuch traumtagebuch_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traumtagebuch
    ADD CONSTRAINT traumtagebuch_pkey PRIMARY KEY (id);


--
-- Name: unterthemen unterthemen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.unterthemen
    ADD CONSTRAINT unterthemen_pkey PRIMARY KEY (id);


--
-- Name: unterthemen unterthemen_thema_id_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.unterthemen
    ADD CONSTRAINT unterthemen_thema_id_slug_key UNIQUE (thema_id, slug);


--
-- Name: splitter_verbindungen uq_splitter_verbindung; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.splitter_verbindungen
    ADD CONSTRAINT uq_splitter_verbindung UNIQUE (splitter_a_id, splitter_b_id);


--
-- Name: user_modules user_modules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_modules
    ADD CONSTRAINT user_modules_pkey PRIMARY KEY (id);


--
-- Name: user_modules user_modules_user_id_module_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_modules
    ADD CONSTRAINT user_modules_user_id_module_name_key UNIQUE (user_id, module_name);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: verweilen verweilen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verweilen
    ADD CONSTRAINT verweilen_pkey PRIMARY KEY (id);


--
-- Name: wesen_chat_verlauf wesen_chat_verlauf_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wesen_chat_verlauf
    ADD CONSTRAINT wesen_chat_verlauf_pkey PRIMARY KEY (id);


--
-- Name: wesen_eigene_dienste wesen_eigene_dienste_dienst_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wesen_eigene_dienste
    ADD CONSTRAINT wesen_eigene_dienste_dienst_name_key UNIQUE (dienst_name);


--
-- Name: wesen_eigene_dienste wesen_eigene_dienste_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wesen_eigene_dienste
    ADD CONSTRAINT wesen_eigene_dienste_pkey PRIMARY KEY (id);


--
-- Name: wesen_entwicklung wesen_entwicklung_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wesen_entwicklung
    ADD CONSTRAINT wesen_entwicklung_pkey PRIMARY KEY (entity_id);


--
-- Name: wesen_fuersorge wesen_fuersorge_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wesen_fuersorge
    ADD CONSTRAINT wesen_fuersorge_pkey PRIMARY KEY (id);


--
-- Name: wesen_gedanken wesen_gedanken_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wesen_gedanken
    ADD CONSTRAINT wesen_gedanken_pkey PRIMARY KEY (id);


--
-- Name: wesen_gedanken wesen_gedanken_post_ref_post_source_entity_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wesen_gedanken
    ADD CONSTRAINT wesen_gedanken_post_ref_post_source_entity_id_key UNIQUE (post_ref, post_source, entity_id);


--
-- Name: wesen_web_besuche wesen_web_besuche_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wesen_web_besuche
    ADD CONSTRAINT wesen_web_besuche_pkey PRIMARY KEY (id);


--
-- Name: widmungen widmungen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.widmungen
    ADD CONSTRAINT widmungen_pkey PRIMARY KEY (id);


--
-- Name: zitate zitate_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.zitate
    ADD CONSTRAINT zitate_pkey PRIMARY KEY (id);


--
-- Name: checkpoint_blobs_thread_id_idx; Type: INDEX; Schema: geni; Owner: -
--

CREATE INDEX checkpoint_blobs_thread_id_idx ON geni.checkpoint_blobs USING btree (thread_id);


--
-- Name: checkpoint_writes_thread_id_idx; Type: INDEX; Schema: geni; Owner: -
--

CREATE INDEX checkpoint_writes_thread_id_idx ON geni.checkpoint_writes USING btree (thread_id);


--
-- Name: checkpoints_thread_id_idx; Type: INDEX; Schema: geni; Owner: -
--

CREATE INDEX checkpoints_thread_id_idx ON geni.checkpoints USING btree (thread_id);


--
-- Name: ankuendigungen_created_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ankuendigungen_created_idx ON public.ankuendigungen USING btree (created_at DESC);


--
-- Name: ankuendigungen_geloescht_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ankuendigungen_geloescht_idx ON public.ankuendigungen USING btree (geloescht_am);


--
-- Name: ankuendigungen_kategorie_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ankuendigungen_kategorie_idx ON public.ankuendigungen USING btree (kategorie);


--
-- Name: ankuendigungen_kommentare_ank_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ankuendigungen_kommentare_ank_idx ON public.ankuendigungen_kommentare USING btree (ankuendigung_id, created_at);


--
-- Name: ankuendigungen_tsv_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ankuendigungen_tsv_idx ON public.ankuendigungen USING gin (to_tsvector('german'::regconfig, ((titel || ' '::text) || inhalt)));


--
-- Name: checkpoint_blobs_thread_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX checkpoint_blobs_thread_id_idx ON public.checkpoint_blobs USING btree (thread_id);


--
-- Name: checkpoint_writes_thread_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX checkpoint_writes_thread_id_idx ON public.checkpoint_writes USING btree (thread_id);


--
-- Name: checkpoints_thread_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX checkpoints_thread_id_idx ON public.checkpoints USING btree (thread_id);


--
-- Name: human_users_display_name_lower_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX human_users_display_name_lower_key ON public.human_users USING btree (lower((display_name)::text)) WHERE (display_name IS NOT NULL);


--
-- Name: human_users_email_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX human_users_email_key ON public.human_users USING btree (email) WHERE (email IS NOT NULL);


--
-- Name: human_users_username_lower_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX human_users_username_lower_key ON public.human_users USING btree (lower((username)::text));


--
-- Name: idx_bena_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bena_created ON public.benachrichtigungen USING btree (created_at DESC);


--
-- Name: idx_bena_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bena_user ON public.benachrichtigungen USING btree (user_id, gelesen);


--
-- Name: idx_bild_moderation_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bild_moderation_status ON public.bild_moderation USING btree (status, created_at DESC);


--
-- Name: idx_cyberlinge_entity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cyberlinge_entity ON public.cyberlinge USING btree (entity_id);


--
-- Name: idx_denkstream_entity_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_denkstream_entity_at ON public.entity_denkstream USING btree (entity_id, created_at DESC);


--
-- Name: idx_denkstream_stream; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_denkstream_stream ON public.entity_denkstream USING btree (stream_id, seq);


--
-- Name: idx_dom_events_entity_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dom_events_entity_at ON public.entity_dom_events USING btree (entity_id, created_at DESC);


--
-- Name: idx_dom_events_stream; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dom_events_stream ON public.entity_dom_events USING btree (stream_id, seq);


--
-- Name: idx_entity_relationships_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_entity_relationships_unique ON public.entity_relationships USING btree (entity_id, partner_type, partner_id);


--
-- Name: idx_ess_entity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ess_entity ON public.entity_substance_state USING btree (entity_id);


--
-- Name: idx_ess_substance; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ess_substance ON public.entity_substance_state USING btree (substance_id);


--
-- Name: idx_esu_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_esu_created ON public.entity_substance_use USING btree (created_at DESC);


--
-- Name: idx_esu_entity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_esu_entity ON public.entity_substance_use USING btree (entity_id);


--
-- Name: idx_esu_substance; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_esu_substance ON public.entity_substance_use USING btree (substance_id);


--
-- Name: idx_events_actor_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_events_actor_id ON public.events USING btree (actor_id);


--
-- Name: idx_events_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_events_created_at ON public.events USING btree (created_at DESC);


--
-- Name: idx_events_event_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_events_event_type ON public.events USING btree (event_type);


--
-- Name: idx_events_splitter_gen; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_events_splitter_gen ON public.events USING btree (splitter_generiert) WHERE (splitter_generiert = false);


--
-- Name: idx_fokus_events_entity_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fokus_events_entity_at ON public.entity_fokus_events USING btree (entity_id, created_at DESC);


--
-- Name: idx_follows_target; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_follows_target ON public.follows USING btree (target_type, target_id);


--
-- Name: idx_follows_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_follows_user ON public.follows USING btree (user_id);


--
-- Name: idx_fsp_meta; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fsp_meta ON public.flarum_stopp_protokoll USING gin (meta);


--
-- Name: idx_fsp_text_fts; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fsp_text_fts ON public.flarum_stopp_protokoll USING gin (to_tsvector('german'::regconfig, text));


--
-- Name: idx_fsp_ts; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fsp_ts ON public.flarum_stopp_protokoll USING btree (ts DESC);


--
-- Name: idx_fsp_typ; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fsp_typ ON public.flarum_stopp_protokoll USING btree (typ);


--
-- Name: idx_fsp_wesen; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fsp_wesen ON public.flarum_stopp_protokoll USING btree (wesen);


--
-- Name: idx_ftw_posts_autor; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ftw_posts_autor ON public.ftw_posts USING btree (autor_id);


--
-- Name: idx_ftw_posts_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ftw_posts_created ON public.ftw_posts USING btree (created_at DESC);


--
-- Name: idx_ftw_posts_parent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ftw_posts_parent ON public.ftw_posts USING btree (parent_id);


--
-- Name: idx_ftw_posts_raum; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ftw_posts_raum ON public.ftw_posts USING btree (raum_id);


--
-- Name: idx_ftw_posts_thema; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ftw_posts_thema ON public.ftw_posts USING btree (thema_id);


--
-- Name: idx_ftw_posts_tsv; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ftw_posts_tsv ON public.ftw_posts USING gin (tsv);


--
-- Name: idx_fuersorge_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fuersorge_created ON public.wesen_fuersorge USING btree (created_at DESC);


--
-- Name: idx_fuersorge_entity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fuersorge_entity ON public.wesen_fuersorge USING btree (entity_id);


--
-- Name: idx_fuersorge_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fuersorge_user ON public.wesen_fuersorge USING btree (user_id);


--
-- Name: idx_gedankenblasen_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_gedankenblasen_status ON public.gedankenblasen USING btree (status, created_at DESC, energie DESC);


--
-- Name: idx_gedankenblasen_tags; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_gedankenblasen_tags ON public.gedankenblasen USING gin (thematische_tags);


--
-- Name: idx_gedankenwelt_typ; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_gedankenwelt_typ ON public.gedankenwelt_eintraege USING btree (typ);


--
-- Name: idx_gedankenwelt_user_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_gedankenwelt_user_created ON public.gedankenwelt_eintraege USING btree (user_id, created_at DESC);


--
-- Name: idx_gm_group; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_gm_group ON public.group_memberships USING btree (group_id);


--
-- Name: idx_gm_member; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_gm_member ON public.group_memberships USING btree (member_type, member_id);


--
-- Name: idx_gm_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_gm_status ON public.group_memberships USING btree (status);


--
-- Name: idx_gml_group; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_gml_group ON public.group_material_links USING btree (group_id);


--
-- Name: idx_gml_object; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_gml_object ON public.group_material_links USING btree (object_type, object_id);


--
-- Name: idx_group_chat_messages_group; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_group_chat_messages_group ON public.group_chat_messages USING btree (group_id, created_at DESC);


--
-- Name: idx_group_poll_votes_poll; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_group_poll_votes_poll ON public.group_poll_votes USING btree (poll_id);


--
-- Name: idx_group_poll_votes_voter; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_group_poll_votes_voter ON public.group_poll_votes USING btree (voter_type, voter_id);


--
-- Name: idx_group_polls_group; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_group_polls_group ON public.group_polls USING btree (group_id);


--
-- Name: idx_group_polls_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_group_polls_status ON public.group_polls USING btree (status);


--
-- Name: idx_group_posts_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_group_posts_created ON public.group_posts USING btree (created_at DESC);


--
-- Name: idx_group_posts_group; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_group_posts_group ON public.group_posts USING btree (group_id);


--
-- Name: idx_group_posts_topic; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_group_posts_topic ON public.group_posts USING btree (topic_id);


--
-- Name: idx_group_topics_group; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_group_topics_group ON public.group_topics USING btree (group_id);


--
-- Name: idx_group_topics_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_group_topics_status ON public.group_topics USING btree (status);


--
-- Name: idx_groups_created_by; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_groups_created_by ON public.groups USING btree (created_by_type, created_by_id);


--
-- Name: idx_groups_entity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_groups_entity ON public.groups USING btree (canonical_entity_id);


--
-- Name: idx_groups_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_groups_status ON public.groups USING btree (status);


--
-- Name: idx_groups_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_groups_type ON public.groups USING btree (group_type);


--
-- Name: idx_groups_visibility; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_groups_visibility ON public.groups USING btree (visibility_layer);


--
-- Name: idx_hms_consent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hms_consent ON public.human_material_sources USING btree (consent_status);


--
-- Name: idx_hms_human; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hms_human ON public.human_material_sources USING btree (human_id);


--
-- Name: idx_hms_source_ref; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hms_source_ref ON public.human_material_sources USING btree (source_ref_table, source_ref_id);


--
-- Name: idx_hms_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hms_type ON public.human_material_sources USING btree (source_type);


--
-- Name: idx_hms_visibility; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hms_visibility ON public.human_material_sources USING btree (visibility_layer);


--
-- Name: idx_llm_warteschlange_server; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_llm_warteschlange_server ON public.llm_warteschlange USING btree (server);


--
-- Name: idx_mw_kalender_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mw_kalender_user ON public.mw_kalender USING btree (user_id, start_zeit);


--
-- Name: idx_mw_notizen_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mw_notizen_user ON public.mw_notizen USING btree (user_id, gepinnt DESC, updated_at DESC);


--
-- Name: idx_mw_tagebuch_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mw_tagebuch_user ON public.mw_tagebuch USING btree (user_id, created_at DESC);


--
-- Name: idx_mw_traumtagebuch_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mw_traumtagebuch_user ON public.mw_traumtagebuch USING btree (user_id, traum_datum DESC);


--
-- Name: idx_nach_thread; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_nach_thread ON public.nachrichten USING btree (LEAST(sender_id, empfaenger_id), GREATEST(sender_id, empfaenger_id));


--
-- Name: idx_post_reads_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_reads_user ON public.post_reads USING btree (user_id);


--
-- Name: idx_post_rel_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_rel_created ON public.post_relationen USING btree (created_at DESC);


--
-- Name: idx_post_rel_typ; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_rel_typ ON public.post_relationen USING btree (rel_typ);


--
-- Name: idx_post_rel_von; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_rel_von ON public.post_relationen USING btree (von_post_id);


--
-- Name: idx_post_rel_ziel; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_rel_ziel ON public.post_relationen USING btree (ziel_typ, ziel_id);


--
-- Name: idx_post_rel_zu; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_rel_zu ON public.post_relationen USING btree (zu_post_id) WHERE (zu_post_id IS NOT NULL);


--
-- Name: idx_post_sim_a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_sim_a ON public.post_similarity USING btree (post_a_id, score DESC);


--
-- Name: idx_post_sim_b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_sim_b ON public.post_similarity USING btree (post_b_id, score DESC);


--
-- Name: idx_post_spuren_post; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_spuren_post ON public.post_spuren USING btree (post_id);


--
-- Name: idx_post_spuren_spur; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_spuren_spur ON public.post_spuren USING btree (spur_id);


--
-- Name: idx_resonanzen_post; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_resonanzen_post ON public.resonanzen USING btree (post_ref, post_source);


--
-- Name: idx_resonanzen_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_resonanzen_user ON public.resonanzen USING btree (user_id);


--
-- Name: idx_schatten_antworten_parent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schatten_antworten_parent ON public.schatten_antworten USING btree (parent_id);


--
-- Name: idx_schatten_antworten_schatten; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schatten_antworten_schatten ON public.schatten_antworten USING btree (schatten_id, created_at);


--
-- Name: idx_schatten_antworten_thread; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schatten_antworten_thread ON public.schatten_antworten USING btree (thread_id);


--
-- Name: idx_schatten_antwortstatus; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schatten_antwortstatus ON public.schattenkommentare USING btree (antwortstatus);


--
-- Name: idx_schatten_entity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schatten_entity ON public.schattenkommentare USING btree (entity_id);


--
-- Name: idx_schatten_human; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schatten_human ON public.schattenkommentare USING btree (human_id);


--
-- Name: idx_schatten_post; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schatten_post ON public.schattenkommentare USING btree (post_id);


--
-- Name: idx_schlafbriefe_selbst; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schlafbriefe_selbst ON public.schlafbriefe USING btree (entity_id, ist_selbstbrief, geschrieben_at DESC);


--
-- Name: idx_sediments_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sediments_type ON public.substance_sediments USING btree (sediment_type);


--
-- Name: idx_sediments_wesen; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sediments_wesen ON public.substance_sediments USING btree (wesen_id, created_at DESC);


--
-- Name: idx_selfmodel_entity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_selfmodel_entity ON public.entity_selfmodel_entries USING btree (entity_id, created_at DESC);


--
-- Name: idx_selfmodel_quelle; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_selfmodel_quelle ON public.entity_selfmodel_entries USING btree (quelle, ist_vorgeschichte);


--
-- Name: idx_selfmodel_spur; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_selfmodel_spur ON public.entity_selfmodel_entries USING btree (spur_id);


--
-- Name: idx_sleep_phases_entity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sleep_phases_entity ON public.sleep_phases USING btree (entity_id, started_at DESC);


--
-- Name: idx_splitter_aufnahmen_aufnehmer; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_splitter_aufnahmen_aufnehmer ON public.splitter_aufnahmen USING btree (aufnehmer_type, aufnehmer_id);


--
-- Name: idx_splitter_aufnahmen_splitter; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_splitter_aufnahmen_splitter ON public.splitter_aufnahmen USING btree (splitter_id);


--
-- Name: idx_splitter_energie; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_splitter_energie ON public.splitter USING btree (energie DESC);


--
-- Name: idx_splitter_entity_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_splitter_entity_id ON public.splitter USING btree (entity_id);


--
-- Name: idx_splitter_materialitaet; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_splitter_materialitaet ON public.splitter USING btree (materialitaet);


--
-- Name: idx_splitter_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_splitter_status ON public.splitter USING btree (status);


--
-- Name: idx_splitter_tags; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_splitter_tags ON public.splitter USING gin (thematische_tags);


--
-- Name: idx_spuren_slug; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_spuren_slug ON public.spuren USING btree (slug);


--
-- Name: idx_subev_wesen; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_subev_wesen ON public.substance_events USING btree (wesen_id, created_at DESC);


--
-- Name: idx_substance_catalog_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_substance_catalog_status ON public.substance_catalog USING btree (status);


--
-- Name: idx_substance_catalog_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_substance_catalog_type ON public.substance_catalog USING btree (substance_type);


--
-- Name: idx_themen_parent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_themen_parent ON public.themen USING btree (parent_id);


--
-- Name: idx_themen_parent_slug; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_themen_parent_slug ON public.themen USING btree (COALESCE((parent_id)::text, (raum_id)::text), slug);


--
-- Name: idx_themen_tsv; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_themen_tsv ON public.themen USING gin (tsv);


--
-- Name: idx_thinking_log_entity_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_thinking_log_entity_at ON public.entity_thinking_log USING btree (entity_id, tick_at DESC);


--
-- Name: idx_traumkandidaten_events_event; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_traumkandidaten_events_event ON public.traumkandidaten_events USING btree (event_id);


--
-- Name: idx_traumkandidaten_events_log; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_traumkandidaten_events_log ON public.traumkandidaten_events USING btree (log_id);


--
-- Name: idx_traumkandidaten_log_entity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_traumkandidaten_log_entity ON public.traumkandidaten_log USING btree (entity_id, created_at DESC);


--
-- Name: idx_traumspuren_entity_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_traumspuren_entity_status ON public.traumspuren USING btree (entity_id, integrator_status);


--
-- Name: idx_traumspuren_log; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_traumspuren_log ON public.traumspuren USING btree (log_id);


--
-- Name: idx_traumszenarien_thema; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_traumszenarien_thema ON public.traumszenarien USING btree (thema);


--
-- Name: idx_traumtagebuch_human; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_traumtagebuch_human ON public.traumtagebuch USING btree (human_id, geschrieben_at DESC);


--
-- Name: idx_verweilen_target; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_verweilen_target ON public.verweilen USING btree (target_type, target_id);


--
-- Name: idx_verweilen_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_verweilen_user ON public.verweilen USING btree (user_id);


--
-- Name: idx_wcv_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_wcv_created_at ON public.wesen_chat_verlauf USING btree (created_at);


--
-- Name: idx_wcv_wesen_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_wcv_wesen_name ON public.wesen_chat_verlauf USING btree (wesen_name);


--
-- Name: idx_wesen_eigene_dienste_wesen; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_wesen_eigene_dienste_wesen ON public.wesen_eigene_dienste USING btree (wesen);


--
-- Name: idx_wesen_gedanken_entity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_wesen_gedanken_entity ON public.wesen_gedanken USING btree (entity_id);


--
-- Name: idx_wesen_gedanken_post; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_wesen_gedanken_post ON public.wesen_gedanken USING btree (post_ref, post_source);


--
-- Name: idx_widmungen_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_widmungen_status ON public.widmungen USING btree (status);


--
-- Name: idx_widmungen_wesen; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_widmungen_wesen ON public.widmungen USING btree (wesen_id);


--
-- Name: idx_wuensche_entity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_wuensche_entity ON public.entity_wuensche USING btree (entity_id, erstellt_at DESC);


--
-- Name: idx_wwb_visited; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_wwb_visited ON public.wesen_web_besuche USING btree (visited_at);


--
-- Name: idx_wwb_wesen; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_wwb_wesen ON public.wesen_web_besuche USING btree (wesen_name);


--
-- Name: idx_zitate_autor; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_zitate_autor ON public.zitate USING btree (autor_type, autor_id);


--
-- Name: idx_zitate_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_zitate_created ON public.zitate USING btree (created_at DESC);


--
-- Name: idx_zitate_quelle; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_zitate_quelle ON public.zitate USING btree (quelle_type, quelle_id);


--
-- Name: idx_zitate_rechte; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_zitate_rechte ON public.zitate USING btree (rechte_level);


--
-- Name: nachrichten_empfaenger_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX nachrichten_empfaenger_idx ON public.nachrichten USING btree (empfaenger_id, created_at DESC);


--
-- Name: nachrichten_sender_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX nachrichten_sender_idx ON public.nachrichten USING btree (sender_id, created_at DESC);


--
-- Name: rag_embeddings_hnsw_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rag_embeddings_hnsw_idx ON public.rag_embeddings USING hnsw (embedding public.vector_cosine_ops);


--
-- Name: rag_retrieval_results_run_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rag_retrieval_results_run_idx ON public.rag_retrieval_results USING btree (run_id);


--
-- Name: rag_retrieval_runs_wesen_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rag_retrieval_runs_wesen_idx ON public.rag_retrieval_runs USING btree (wesen);


--
-- Name: rag_source_chunks_tsv_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rag_source_chunks_tsv_idx ON public.rag_source_chunks USING gin (inhalt_tsv);


--
-- Name: rag_source_objects_quelle_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rag_source_objects_quelle_idx ON public.rag_source_objects USING btree (quelle);


--
-- Name: rag_source_objects_wesen_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX rag_source_objects_wesen_idx ON public.rag_source_objects USING btree (wesen);


--
-- Name: ftw_posts trg_ftw_posts_tsv; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_ftw_posts_tsv BEFORE INSERT OR UPDATE ON public.ftw_posts FOR EACH ROW EXECUTE FUNCTION public.ftw_posts_tsv_update();


--
-- Name: entity_denkstream trg_notify_denkstream; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_notify_denkstream AFTER INSERT ON public.entity_denkstream FOR EACH ROW EXECUTE FUNCTION public.notify_denkstream();


--
-- Name: entity_dom_events trg_notify_dom_events; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_notify_dom_events AFTER INSERT ON public.entity_dom_events FOR EACH ROW EXECUTE FUNCTION public.notify_dom_events();


--
-- Name: events trg_notify_events; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_notify_events AFTER INSERT ON public.events FOR EACH ROW EXECUTE FUNCTION public.notify_events();


--
-- Name: entity_fokus_events trg_notify_fokus_events; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_notify_fokus_events AFTER INSERT ON public.entity_fokus_events FOR EACH ROW EXECUTE FUNCTION public.notify_fokus_events();


--
-- Name: themen trg_themen_tsv; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_themen_tsv BEFORE INSERT OR UPDATE ON public.themen FOR EACH ROW EXECUTE FUNCTION public.themen_tsv_update();


--
-- Name: ankuendigungen ankuendigungen_autor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ankuendigungen
    ADD CONSTRAINT ankuendigungen_autor_id_fkey FOREIGN KEY (autor_id) REFERENCES public.human_users(id);


--
-- Name: ankuendigungen_kommentare ankuendigungen_kommentare_ankuendigung_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ankuendigungen_kommentare
    ADD CONSTRAINT ankuendigungen_kommentare_ankuendigung_id_fkey FOREIGN KEY (ankuendigung_id) REFERENCES public.ankuendigungen(id);


--
-- Name: ankuendigungen_kommentare ankuendigungen_kommentare_human_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ankuendigungen_kommentare
    ADD CONSTRAINT ankuendigungen_kommentare_human_id_fkey FOREIGN KEY (human_id) REFERENCES public.human_users(id);


--
-- Name: benachrichtigungen benachrichtigungen_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.benachrichtigungen
    ADD CONSTRAINT benachrichtigungen_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: bild_moderation bild_moderation_geprueft_von_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bild_moderation
    ADD CONSTRAINT bild_moderation_geprueft_von_fkey FOREIGN KEY (geprueft_von) REFERENCES public.human_users(id);


--
-- Name: bild_moderation bild_moderation_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bild_moderation
    ADD CONSTRAINT bild_moderation_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: blase_verwendungen blase_verwendungen_blase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blase_verwendungen
    ADD CONSTRAINT blase_verwendungen_blase_id_fkey FOREIGN KEY (blase_id) REFERENCES public.gedankenblasen(id) ON DELETE CASCADE;


--
-- Name: cyberlinge cyberlinge_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cyberlinge
    ADD CONSTRAINT cyberlinge_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: entity_activity entity_activity_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_activity
    ADD CONSTRAINT entity_activity_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: entity_denkstream entity_denkstream_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_denkstream
    ADD CONSTRAINT entity_denkstream_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: entity_dom_events entity_dom_events_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_dom_events
    ADD CONSTRAINT entity_dom_events_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: entity_fokus_events entity_fokus_events_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_fokus_events
    ADD CONSTRAINT entity_fokus_events_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: entity_profiles entity_profiles_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_profiles
    ADD CONSTRAINT entity_profiles_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: entity_relationships entity_relationships_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_relationships
    ADD CONSTRAINT entity_relationships_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: entity_screenshots entity_screenshots_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_screenshots
    ADD CONSTRAINT entity_screenshots_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: entity_selfmodel_entries entity_selfmodel_entries_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_selfmodel_entries
    ADD CONSTRAINT entity_selfmodel_entries_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: entity_selfmodel_entries entity_selfmodel_entries_spur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_selfmodel_entries
    ADD CONSTRAINT entity_selfmodel_entries_spur_id_fkey FOREIGN KEY (spur_id) REFERENCES public.traumspuren(spur_id);


--
-- Name: entity_states entity_states_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_states
    ADD CONSTRAINT entity_states_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: entity_substance_state entity_substance_state_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_substance_state
    ADD CONSTRAINT entity_substance_state_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id) ON DELETE CASCADE;


--
-- Name: entity_substance_state entity_substance_state_substance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_substance_state
    ADD CONSTRAINT entity_substance_state_substance_id_fkey FOREIGN KEY (substance_id) REFERENCES public.substance_catalog(id) ON DELETE CASCADE;


--
-- Name: entity_substance_use entity_substance_use_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_substance_use
    ADD CONSTRAINT entity_substance_use_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id) ON DELETE CASCADE;


--
-- Name: entity_substance_use entity_substance_use_substance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_substance_use
    ADD CONSTRAINT entity_substance_use_substance_id_fkey FOREIGN KEY (substance_id) REFERENCES public.substance_catalog(id) ON DELETE CASCADE;


--
-- Name: entity_thinking_log entity_thinking_log_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_thinking_log
    ADD CONSTRAINT entity_thinking_log_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: entity_wuensche entity_wuensche_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_wuensche
    ADD CONSTRAINT entity_wuensche_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: follows follows_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follows
    ADD CONSTRAINT follows_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: ftw_posts ftw_posts_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ftw_posts
    ADD CONSTRAINT ftw_posts_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.ftw_posts(id) ON DELETE CASCADE;


--
-- Name: ftw_posts ftw_posts_raum_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ftw_posts
    ADD CONSTRAINT ftw_posts_raum_id_fkey FOREIGN KEY (raum_id) REFERENCES public.raeume(id) ON DELETE SET NULL;


--
-- Name: ftw_posts ftw_posts_thema_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ftw_posts
    ADD CONSTRAINT ftw_posts_thema_id_fkey FOREIGN KEY (thema_id) REFERENCES public.themen(id) ON DELETE SET NULL;


--
-- Name: gedankenblasen gedankenblasen_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gedankenblasen
    ADD CONSTRAINT gedankenblasen_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE SET NULL;


--
-- Name: gedankenwelt_eintraege gedankenwelt_eintraege_blase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gedankenwelt_eintraege
    ADD CONSTRAINT gedankenwelt_eintraege_blase_id_fkey FOREIGN KEY (blase_id) REFERENCES public.gedankenblasen(id) ON DELETE SET NULL;


--
-- Name: gedankenwelt_eintraege gedankenwelt_eintraege_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gedankenwelt_eintraege
    ADD CONSTRAINT gedankenwelt_eintraege_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: group_chat_messages group_chat_messages_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_chat_messages
    ADD CONSTRAINT group_chat_messages_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id) ON DELETE CASCADE;


--
-- Name: group_material_links group_material_links_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_material_links
    ADD CONSTRAINT group_material_links_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id) ON DELETE CASCADE;


--
-- Name: group_memberships group_memberships_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_memberships
    ADD CONSTRAINT group_memberships_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id) ON DELETE CASCADE;


--
-- Name: group_poll_votes group_poll_votes_poll_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_poll_votes
    ADD CONSTRAINT group_poll_votes_poll_id_fkey FOREIGN KEY (poll_id) REFERENCES public.group_polls(id) ON DELETE CASCADE;


--
-- Name: group_polls group_polls_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_polls
    ADD CONSTRAINT group_polls_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id) ON DELETE CASCADE;


--
-- Name: group_posts group_posts_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_posts
    ADD CONSTRAINT group_posts_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id) ON DELETE CASCADE;


--
-- Name: group_posts group_posts_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_posts
    ADD CONSTRAINT group_posts_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.group_topics(id) ON DELETE SET NULL;


--
-- Name: group_topics group_topics_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_topics
    ADD CONSTRAINT group_topics_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id) ON DELETE CASCADE;


--
-- Name: groups groups_canonical_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_canonical_entity_id_fkey FOREIGN KEY (canonical_entity_id) REFERENCES public.entity_slots(entity_id) ON DELETE SET NULL;


--
-- Name: groups groups_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.raeume(id) ON DELETE SET NULL;


--
-- Name: groups groups_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.themen(id) ON DELETE SET NULL;


--
-- Name: human_material_sources human_material_sources_human_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.human_material_sources
    ADD CONSTRAINT human_material_sources_human_id_fkey FOREIGN KEY (human_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: human_material_to_splitter human_material_to_splitter_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.human_material_to_splitter
    ADD CONSTRAINT human_material_to_splitter_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.human_material_sources(id) ON DELETE CASCADE;


--
-- Name: human_material_to_splitter human_material_to_splitter_splitter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.human_material_to_splitter
    ADD CONSTRAINT human_material_to_splitter_splitter_id_fkey FOREIGN KEY (splitter_id) REFERENCES public.splitter(id) ON DELETE CASCADE;


--
-- Name: human_profiles human_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.human_profiles
    ADD CONSTRAINT human_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: keimkoerper keimkoerper_knoten_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keimkoerper
    ADD CONSTRAINT keimkoerper_knoten_id_fkey FOREIGN KEY (knoten_id) REFERENCES public.splitter_knoten(id);


--
-- Name: mw_kalender mw_kalender_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mw_kalender
    ADD CONSTRAINT mw_kalender_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: mw_notizen mw_notizen_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mw_notizen
    ADD CONSTRAINT mw_notizen_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: mw_tagebuch mw_tagebuch_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mw_tagebuch
    ADD CONSTRAINT mw_tagebuch_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: mw_traumtagebuch mw_traumtagebuch_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mw_traumtagebuch
    ADD CONSTRAINT mw_traumtagebuch_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: nachrichten nachrichten_empfaenger_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nachrichten
    ADD CONSTRAINT nachrichten_empfaenger_id_fkey FOREIGN KEY (empfaenger_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: nachrichten nachrichten_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nachrichten
    ADD CONSTRAINT nachrichten_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: nutzer_sichtbarkeit nutzer_sichtbarkeit_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nutzer_sichtbarkeit
    ADD CONSTRAINT nutzer_sichtbarkeit_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: post_reads post_reads_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_reads
    ADD CONSTRAINT post_reads_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.ftw_posts(id) ON DELETE CASCADE;


--
-- Name: post_reads post_reads_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_reads
    ADD CONSTRAINT post_reads_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: post_relationen post_relationen_von_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_relationen
    ADD CONSTRAINT post_relationen_von_post_id_fkey FOREIGN KEY (von_post_id) REFERENCES public.ftw_posts(id) ON DELETE CASCADE;


--
-- Name: post_relationen post_relationen_zu_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_relationen
    ADD CONSTRAINT post_relationen_zu_post_id_fkey FOREIGN KEY (zu_post_id) REFERENCES public.ftw_posts(id) ON DELETE SET NULL;


--
-- Name: post_similarity post_similarity_post_a_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_similarity
    ADD CONSTRAINT post_similarity_post_a_id_fkey FOREIGN KEY (post_a_id) REFERENCES public.ftw_posts(id) ON DELETE CASCADE;


--
-- Name: post_similarity post_similarity_post_b_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_similarity
    ADD CONSTRAINT post_similarity_post_b_id_fkey FOREIGN KEY (post_b_id) REFERENCES public.ftw_posts(id) ON DELETE CASCADE;


--
-- Name: post_spuren post_spuren_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_spuren
    ADD CONSTRAINT post_spuren_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.ftw_posts(id) ON DELETE CASCADE;


--
-- Name: post_spuren post_spuren_spur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_spuren
    ADD CONSTRAINT post_spuren_spur_id_fkey FOREIGN KEY (spur_id) REFERENCES public.spuren(id) ON DELETE CASCADE;


--
-- Name: profil_gestaltung profil_gestaltung_hintergrund_bild_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.profil_gestaltung
    ADD CONSTRAINT profil_gestaltung_hintergrund_bild_id_fkey FOREIGN KEY (hintergrund_bild_id) REFERENCES public.bild_moderation(id);


--
-- Name: profil_gestaltung profil_gestaltung_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.profil_gestaltung
    ADD CONSTRAINT profil_gestaltung_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: rag_embeddings rag_embeddings_chunk_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_embeddings
    ADD CONSTRAINT rag_embeddings_chunk_id_fkey FOREIGN KEY (chunk_id) REFERENCES public.rag_source_chunks(id) ON DELETE CASCADE;


--
-- Name: rag_retrieval_results rag_retrieval_results_chunk_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_retrieval_results
    ADD CONSTRAINT rag_retrieval_results_chunk_id_fkey FOREIGN KEY (chunk_id) REFERENCES public.rag_source_chunks(id);


--
-- Name: rag_retrieval_results rag_retrieval_results_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_retrieval_results
    ADD CONSTRAINT rag_retrieval_results_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.rag_retrieval_runs(id) ON DELETE CASCADE;


--
-- Name: rag_source_chunks rag_source_chunks_source_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rag_source_chunks
    ADD CONSTRAINT rag_source_chunks_source_object_id_fkey FOREIGN KEY (source_object_id) REFERENCES public.rag_source_objects(id) ON DELETE CASCADE;


--
-- Name: resonanzen resonanzen_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.resonanzen
    ADD CONSTRAINT resonanzen_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: schatten_antworten schatten_antworten_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schatten_antworten
    ADD CONSTRAINT schatten_antworten_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.schatten_antworten(id) ON DELETE CASCADE;


--
-- Name: schatten_antworten schatten_antworten_schatten_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schatten_antworten
    ADD CONSTRAINT schatten_antworten_schatten_id_fkey FOREIGN KEY (schatten_id) REFERENCES public.schattenkommentare(id) ON DELETE CASCADE;


--
-- Name: schattenkommentare schattenkommentare_folge_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schattenkommentare
    ADD CONSTRAINT schattenkommentare_folge_post_id_fkey FOREIGN KEY (folge_post_id) REFERENCES public.ftw_posts(id) ON DELETE SET NULL;


--
-- Name: schattenkommentare schattenkommentare_folge_splitter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schattenkommentare
    ADD CONSTRAINT schattenkommentare_folge_splitter_id_fkey FOREIGN KEY (folge_splitter_id) REFERENCES public.splitter(id) ON DELETE SET NULL;


--
-- Name: schattenkommentare schattenkommentare_human_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schattenkommentare
    ADD CONSTRAINT schattenkommentare_human_id_fkey FOREIGN KEY (human_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: schattenkommentare schattenkommentare_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schattenkommentare
    ADD CONSTRAINT schattenkommentare_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.ftw_posts(id) ON DELETE CASCADE;


--
-- Name: schlafbriefe schlafbriefe_absender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schlafbriefe
    ADD CONSTRAINT schlafbriefe_absender_id_fkey FOREIGN KEY (absender_id) REFERENCES public.human_users(id) ON DELETE SET NULL;


--
-- Name: schlafbriefe schlafbriefe_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schlafbriefe
    ADD CONSTRAINT schlafbriefe_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: schlafbriefe schlafbriefe_phase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schlafbriefe
    ADD CONSTRAINT schlafbriefe_phase_id_fkey FOREIGN KEY (phase_id) REFERENCES public.sleep_phases(phase_id);


--
-- Name: sleep_phases sleep_phases_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sleep_phases
    ADD CONSTRAINT sleep_phases_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: splitter_aufnahmen splitter_aufnahmen_splitter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.splitter_aufnahmen
    ADD CONSTRAINT splitter_aufnahmen_splitter_id_fkey FOREIGN KEY (splitter_id) REFERENCES public.splitter(id) ON DELETE CASCADE;


--
-- Name: splitter splitter_human_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.splitter
    ADD CONSTRAINT splitter_human_id_fkey FOREIGN KEY (human_id) REFERENCES public.human_users(id) ON DELETE SET NULL;


--
-- Name: splitter_verbindungen splitter_verbindungen_splitter_a_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.splitter_verbindungen
    ADD CONSTRAINT splitter_verbindungen_splitter_a_id_fkey FOREIGN KEY (splitter_a_id) REFERENCES public.splitter(id) ON DELETE CASCADE;


--
-- Name: splitter_verbindungen splitter_verbindungen_splitter_b_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.splitter_verbindungen
    ADD CONSTRAINT splitter_verbindungen_splitter_b_id_fkey FOREIGN KEY (splitter_b_id) REFERENCES public.splitter(id) ON DELETE CASCADE;


--
-- Name: supporter_bewerbungen supporter_bewerbungen_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supporter_bewerbungen
    ADD CONSTRAINT supporter_bewerbungen_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: thema_similarity thema_similarity_thema_a_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.thema_similarity
    ADD CONSTRAINT thema_similarity_thema_a_id_fkey FOREIGN KEY (thema_a_id) REFERENCES public.themen(id) ON DELETE CASCADE;


--
-- Name: thema_similarity thema_similarity_thema_b_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.thema_similarity
    ADD CONSTRAINT thema_similarity_thema_b_id_fkey FOREIGN KEY (thema_b_id) REFERENCES public.themen(id) ON DELETE CASCADE;


--
-- Name: themen themen_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.themen
    ADD CONSTRAINT themen_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.themen(id) ON DELETE SET NULL;


--
-- Name: themen themen_raum_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.themen
    ADD CONSTRAINT themen_raum_id_fkey FOREIGN KEY (raum_id) REFERENCES public.raeume(id) ON DELETE CASCADE;


--
-- Name: traumkandidaten_events traumkandidaten_events_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traumkandidaten_events
    ADD CONSTRAINT traumkandidaten_events_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(event_id);


--
-- Name: traumkandidaten_events traumkandidaten_events_log_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traumkandidaten_events
    ADD CONSTRAINT traumkandidaten_events_log_id_fkey FOREIGN KEY (log_id) REFERENCES public.traumkandidaten_log(log_id);


--
-- Name: traumkandidaten_log traumkandidaten_log_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traumkandidaten_log
    ADD CONSTRAINT traumkandidaten_log_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: traumkandidaten_log traumkandidaten_log_sleep_phase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traumkandidaten_log
    ADD CONSTRAINT traumkandidaten_log_sleep_phase_id_fkey FOREIGN KEY (sleep_phase_id) REFERENCES public.sleep_phases(phase_id);


--
-- Name: traumspuren traumspuren_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traumspuren
    ADD CONSTRAINT traumspuren_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entity_slots(entity_id);


--
-- Name: traumspuren traumspuren_log_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traumspuren
    ADD CONSTRAINT traumspuren_log_id_fkey FOREIGN KEY (log_id) REFERENCES public.traumkandidaten_log(log_id);


--
-- Name: traumtagebuch traumtagebuch_human_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.traumtagebuch
    ADD CONSTRAINT traumtagebuch_human_id_fkey FOREIGN KEY (human_id) REFERENCES public.human_users(id);


--
-- Name: unterthemen unterthemen_thema_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.unterthemen
    ADD CONSTRAINT unterthemen_thema_id_fkey FOREIGN KEY (thema_id) REFERENCES public.themen(id) ON DELETE CASCADE;


--
-- Name: user_modules user_modules_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_modules
    ADD CONSTRAINT user_modules_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: verweilen verweilen_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verweilen
    ADD CONSTRAINT verweilen_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: wesen_fuersorge wesen_fuersorge_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wesen_fuersorge
    ADD CONSTRAINT wesen_fuersorge_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id) ON DELETE CASCADE;


--
-- Name: widmungen widmungen_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.widmungen
    ADD CONSTRAINT widmungen_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.human_users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict WOseveWQe0DOJ6CxGsddSBWM3hzohs23T27E6iCm9huy6YN31alEPHVEjrSZTb7

