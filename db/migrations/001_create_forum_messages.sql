-- migrate:up

CREATE TABLE forum_messages (
    id              VARCHAR(255) PRIMARY KEY,
    companyId       VARCHAR(255) NOT NULL,
    userId          VARCHAR(255) NOT NULL,
    username        TEXT NOT NULL,
    parentId        VARCHAR(255),
    content         TEXT NOT NULL,
    createdAt       BIGINT NOT NULL
);

-- migrate:down

DROP TABLE forum_messages;
