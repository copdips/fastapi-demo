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

-- Running upgrade 08d73fea4454 -> e8d0473197d0

CREATE TYPE taskstatus AS ENUM ('in_progress', 'pending', 'done', 'failed');

CREATE TABLE task (
    name VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    status taskstatus NOT NULL,
    description VARCHAR,
    created_by VARCHAR,
    message VARCHAR,
    email_notification JSON,
    context JSON,
    uid VARCHAR NOT NULL,
    id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    task_duration INTERVAL,
    CONSTRAINT pk_task PRIMARY KEY (uid)
);

CREATE UNIQUE INDEX ix_task_id ON task (id);

ALTER TABLE tag_team_link DROP CONSTRAINT fk_tag_team_link_tag_id_tag;

ALTER TABLE tag_team_link DROP CONSTRAINT fk_tag_team_link_team_id_team;

ALTER TABLE "user" DROP CONSTRAINT fk_user_team_id_team;

ALTER TABLE tag ALTER COLUMN id TYPE VARCHAR USING id::text;

ALTER TABLE tag_team_link ALTER COLUMN tag_id TYPE VARCHAR USING tag_id::text;

ALTER TABLE tag_team_link ALTER COLUMN team_id TYPE VARCHAR USING team_id::text;

ALTER TABLE team ALTER COLUMN id TYPE VARCHAR USING id::text;

ALTER TABLE "user" ALTER COLUMN id TYPE VARCHAR USING id::text;

ALTER TABLE "user" ALTER COLUMN team_id TYPE VARCHAR USING team_id::text;

ALTER TABLE tag_team_link ADD CONSTRAINT fk_tag_team_link_tag_id_tag FOREIGN KEY(tag_id) REFERENCES tag (id);

ALTER TABLE tag_team_link ADD CONSTRAINT fk_tag_team_link_team_id_team FOREIGN KEY(team_id) REFERENCES team (id);

ALTER TABLE "user" ADD CONSTRAINT fk_user_team_id_team FOREIGN KEY(team_id) REFERENCES team (id);

UPDATE alembic_version SET version_num='e8d0473197d0' WHERE alembic_version.version_num = '08d73fea4454';

COMMIT;
