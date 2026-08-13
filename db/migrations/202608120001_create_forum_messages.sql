-- migrate:up

CREATE TABLE forum_messages (
    id              TEXT PRIMARY KEY,

    forum_type_id   TEXT NOT NULL,
    target_id       TEXT NOT NULL,
    forum_slug      TEXT NOT NULL,
    permalink       TEXT NOT NULL,

    user_id         TEXT NOT NULL,
    username        TEXT NOT NULL,

    parent_id       TEXT,
    text            TEXT NOT NULL,

    created_at      TIMESTAMPTZ NOT NULL,
    discovered_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    likes           INTEGER NOT NULL DEFAULT 0,
    dislikes        INTEGER NOT NULL DEFAULT 0,

    is_bot          BOOLEAN NOT NULL DEFAULT FALSE,
    mentions_bot    BOOLEAN NOT NULL DEFAULT FALSE,

    raw_data        JSONB
);

-- migrate:down

DROP TABLE forum_messages;
