-- migrate:up

CREATE TABLE bot_interactions (
    id                      BIGSERIAL PRIMARY KEY,
    sourceMessageId         VARCHAR(255) NOT NULL,
    status                  VARCHAR(20) NOT NULL,
    responseType            VARCHAR(20) NOT NULL,
    responseText            TEXT,
    responseMessageId       VARCHAR(255),
    model                   TEXT,
    inputTokens             INTEGER,
    outputTokens            INTEGER,
    createdAt               BIGINT NOT NULL,
    updatedAt               BIGINT NOT NULL,

    UNIQUE (sourceMessageId)
);

-- migrate:down

DROP TABLE bot_interactions;
