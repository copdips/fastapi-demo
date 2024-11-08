# fastapi-demo

[![codecov](https://codecov.io/gh/copdips/fastapi-demo/graph/badge.svg?token=VM2WT1XTYM)](https://codecov.io/gh/copdips/fastapi-demo)

Based on the tutorials for [FastAPI](https://fastapi.tiangolo.com/tutorial/) and [SQLModel](https://sqlmodel.tiangolo.com/),
this project serves a simple demonstration of creating a REST API using FastAPI and SQLModel, incorporating async DB operations, and adhering to what I understand as best practices.

## Database

The database uses PostgreSQL for regular operations and SQLite for testing with the following schema.
Of course, with ORM, we can easily change the database type.

### Schema

```mermaid
erDiagram
    TEAM ||--|{ USER : "belongs"
    TEAM ||--|| TAG : "many-to-many"
    TEAM {
        string uid PK "Primary Key"
        string id "Unique Team ID"
        datetime created_at "creation date"
        datetime updated_at "last update date"
        string name UK "team name"
        string headquarters "Headquarters Location"
    }
    USER {
        string uid PK "Primary Key"
        string id "Unique User ID"
        datetime created_at "creation date"
        datetime updated_at "last update date"
        string name UK "user name"
        string first_name "user first name"
        string last_name "user last name"
        string email "user email"
        string team_id FK "Foreign Key to team"
    }
    TAG {
        string uid PK "Primary Key"
        string id "Unique Tag ID"
        datetime created_at "creation date"
        datetime updated_at "last update date"
        string name UK "tag name"
    }
    TAG_TEAM_LINK {
        string team_id FK "Foreign Key to team"
        string tag_id FK "Foreign Key to tag"
    }
    TASK {
        string uid PK "Primary Key"
        string id "Unique Task ID"
        datetime created_at "creation date"
        datetime updated_at "last update date"
        string name "Task Name"
        string type "Task Type"
        enum status "Task Status"
        string description "Task Description"
        string created_by "Creator"
        string message "Task Message"
        json email_notification "Email Notification Settings"
        json context "Task Context"
        datetime ended_at "End Date"
        interval task_duration "Task Duration"
    }
    EMAIL {
        string uid PK "Primary Key"
        string id "Unique Email ID"
        datetime created_at "creation date"
        datetime updated_at "last update date"
        string type "Email Type"
        string subject "Email Subject"
        string body "Email Body"
        string sender "Sender Address"
        string to "Recipient Address"
        string cc "CC Recipient Address"
        string bcc "BCC Recipient Address"
        string tracking_id "Tracking ID"
    }

```

### Alembic

```bash
alembic init -t async migrations
# edit alembic.ini and env.py

alembic revision --autogenerate -m "init"

# offline migration to generate SQL file with run_migrations_offline()
py_file=$(ls -t migrations/versions/*.py | head -n1)
sql_file="${py_file%.*}.sql"
alembic upgrade head --sql > $sql_file

# online migration
alembic upgrade head

# online migration to a specific revision
alembic upgrade <revision>
```

### Recreate schema public

```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

## External Task

Celery might not be the best tool: <https://github.com/tiangolo/full-stack-fastapi-template/pull/694>

## Profiling

### Pyinstrument

<https://pyinstrument.readthedocs.io/>

Add `$profile=1` in query param

### Py-spy

<https://github.com/benfred/py-spy>

```bash
py-spy top -- python -m uvicorn app.main:app

# or
make run
lsof -i :8000
py-spy top --pid $python_pid

# or dump current call stack to console
py-spy dump --pid $python_pid
py-spy dump --pid $python_pid --locals # with locals vars
```

Run in Docker:

```yaml
# https://github.com/benfred/py-spy?tab=readme-ov-file#how-do-i-run-py-spy-in-docker
your_service:
   cap_add:
     - SYS_PTRACE
```

Run in Kubernetes:

```yaml
# https://github.com/benfred/py-spy?tab=readme-ov-file#how-do-i-run-py-spy-in-kubernetes
securityContext:
  capabilities:
    add:
    - SYS_PTRACE
```
