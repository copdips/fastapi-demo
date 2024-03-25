# fastapi-demo

Based on the tutorials for [FastAPI](https://fastapi.tiangolo.com/tutorial/) and [SQLModel](https://sqlmodel.tiangolo.com/),
this project serves a simple demonstration of creating a REST API using FastAPI and SQLModel, incorporating async DB operations, and adhering to what I understand as best practices.

## Database

The database uses PostgreSQL for regular operations and SQLite for testing with the following schema.
Of course, with ORM, we can easily change the database type.

### Schema

```mermaid
erDiagram
    user ||--|{ team : belongs
    team ||--|| tag : "many-to-many"
    team {
        string id PK "Primary Key"
        datetime created_at "creation date"
        datetime updated_at "last update date"
        string name UK "team name"
    }
    user {
        string id PK "Primary Key"
        datetime created_at "creation date"
        datetime updated_at "last update date"
        string name UK "user name"
        string first_name "user first name"
        string last_name "user last name"
        str team_id FK "Foreign Key to team"
    }
    tag {
        string id PK "Primary Key"
        datetime created_at "creation date"
        datetime updated_at "last update date"
        string name UK "tag name"
    }
    tag_team_link {
        string team_id FK "Foreign Key to team"
        string tag_id FK "Foreign Key to tag"
    }
```

### Alembic

```bash
alembic init -t async migrations
# edit alembic.ini and env.py
alembic revision --autogenerate -m "init"
alembic upgrade head
# to generate SQL file with run_migrations_offline()
alembic upgrade head --sql > migrations.sql
```

### Recreate schema public

```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

## External Task

Celery might not be the best tool: <https://github.com/tiangolo/full-stack-fastapi-template/pull/694>
