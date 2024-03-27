DB_HOST: aws-0-eu-central-1.pooler.supabase.com/postgres
BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 08d73fea4454

CREATE TABLE tag (
    name VARCHAR NOT NULL,
    uid VARCHAR NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT pk_tag PRIMARY KEY (uid)
);

CREATE UNIQUE INDEX ix_tag_id ON tag (id);

CREATE UNIQUE INDEX ix_tag_name ON tag (name);

CREATE TABLE team (
    name VARCHAR NOT NULL,
    headquarters VARCHAR NOT NULL,
    uid VARCHAR NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT pk_team PRIMARY KEY (uid)
);

CREATE UNIQUE INDEX ix_team_id ON team (id);

CREATE UNIQUE INDEX ix_team_name ON team (name);

CREATE TABLE tag_team_link (
    tag_id UUID NOT NULL,
    team_id UUID NOT NULL,
    CONSTRAINT pk_tag_team_link PRIMARY KEY (tag_id, team_id),
    CONSTRAINT fk_tag_team_link_tag_id_tag FOREIGN KEY(tag_id) REFERENCES tag (id),
    CONSTRAINT fk_tag_team_link_team_id_team FOREIGN KEY(team_id) REFERENCES team (id)
);

CREATE TABLE "user" (
    name VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    uid VARCHAR NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    team_id UUID,
    CONSTRAINT pk_user PRIMARY KEY (uid),
    CONSTRAINT fk_user_team_id_team FOREIGN KEY(team_id) REFERENCES team (id)
);

CREATE UNIQUE INDEX ix_user_id ON "user" (id);

CREATE UNIQUE INDEX ix_user_name ON "user" (name);

INSERT INTO alembic_version (version_num) VALUES ('08d73fea4454') RETURNING alembic_version.version_num;

COMMIT;
