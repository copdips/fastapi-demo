-- alembic upgrade head --sql > migrations/versions/4d9c56c5ec2e_init.sql
BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 4d9c56c5ec2e

CREATE TABLE tag (
    name VARCHAR NOT NULL,
    id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_tag_name ON tag (name);

CREATE TABLE team (
    name VARCHAR NOT NULL,
    headquarters VARCHAR NOT NULL,
    id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_team_name ON team (name);

CREATE TABLE tag_team_link (
    tag_id VARCHAR NOT NULL,
    team_id VARCHAR NOT NULL,
    PRIMARY KEY (tag_id, team_id),
    FOREIGN KEY(tag_id) REFERENCES tag (id),
    FOREIGN KEY(team_id) REFERENCES team (id)
);

CREATE TABLE "user" (
    name VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    team_id VARCHAR,
    PRIMARY KEY (id),
    FOREIGN KEY(team_id) REFERENCES team (id)
);

CREATE UNIQUE INDEX ix_user_name ON "user" (name);

INSERT INTO alembic_version (version_num) VALUES ('4d9c56c5ec2e') RETURNING alembic_version.version_num;

COMMIT;
