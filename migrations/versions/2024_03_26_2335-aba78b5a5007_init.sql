DB_HOST: aws-0-eu-central-1.pooler.supabase.com/postgres
BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> aba78b5a5007

CREATE TABLE tag (
    name VARCHAR NOT NULL,
    id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT pk_tag PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_tag_name ON tag (name);

CREATE TABLE team (
    name VARCHAR NOT NULL,
    headquarters VARCHAR NOT NULL,
    id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT pk_team PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_team_name ON team (name);

CREATE TABLE tag_team_link (
    tag_id VARCHAR NOT NULL,
    team_id VARCHAR NOT NULL,
    CONSTRAINT pk_tag_team_link PRIMARY KEY (tag_id, team_id),
    CONSTRAINT fk_tag_team_link_tag_id_tag FOREIGN KEY(tag_id) REFERENCES tag (id),
    CONSTRAINT fk_tag_team_link_team_id_team FOREIGN KEY(team_id) REFERENCES team (id)
);

CREATE TABLE "user" (
    name VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    team_id VARCHAR,
    CONSTRAINT pk_user PRIMARY KEY (id),
    CONSTRAINT fk_user_team_id_team FOREIGN KEY(team_id) REFERENCES team (id)
);

CREATE UNIQUE INDEX ix_user_name ON "user" (name);

INSERT INTO alembic_version (version_num) VALUES ('aba78b5a5007') RETURNING alembic_version.version_num;

COMMIT;
