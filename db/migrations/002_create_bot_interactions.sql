-- migrate:up

CREATE TABLE bot_interactions (
    id                      BIGSERIAL PRIMARY KEY,

    source_message_id       TEXT NOT NULL
                            REFERENCES forum_messages(id),

    reply_target_message_id TEXT
                            REFERENCES forum_messages(id),

    status                  TEXT NOT NULL,

    response_type           TEXT,
    decision_reason         TEXT,

    response_text           TEXT,

    model                   TEXT,
    input_tokens            INTEGER,
    output_tokens           INTEGER,

    attempt_count           INTEGER NOT NULL DEFAULT 0,
    next_attempt_at         TIMESTAMPTZ,

    posting_started_at      TIMESTAMPTZ,
    replied_at              TIMESTAMPTZ,

    bot_message_id          TEXT,

    last_error              TEXT,

    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (source_message_id)
);

-- migrate:down

DROP TABLE bot_interactions;
