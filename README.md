# OrderFlow Backend

OrderFlow is an asynchronous REST API for an order-management platform,
built with modern Python, FastAPI, SQLAlchemy 2.0 and PostgreSQL.

The repository is a production-oriented portfolio project for practising
backend architecture, database design, transactional data access,
authentication, testing and cloud deployment.

## Current Capabilities

- Async FastAPI application
- SQLAlchemy 2.0 with the asyncpg PostgreSQL driver
- Async database engine and session dependency
- PostgreSQL 15 and Redis 7 development containers
- UUID-based primary and foreign keys
- User roles and soft-delete support
- Order lifecycle states and idempotency-key storage
- Payment records and unique transaction references
- Generic audit-log records with PostgreSQL JSONB metadata
- Indexed foreign keys and lookup fields
- Repository-layer functions for data access
- Transaction ownership outside the repository layer
- uv-based package and virtual-environment management
- Editable and exported database relationship diagrams

## Data Model

| Entity | Purpose |
| --- | --- |
| `users` | Account identity, role, password hash and active state |
| `orders` | Customer order, amount, status and idempotency key |
| `payments` | Payments associated with an order |
| `audit_logs` | Entity changes and user or system events |

An order belongs to a user and may have multiple payments. Audit entries use
`entity_type` and `entity_id` to associate events with any entity, while
`actor_id` identifies the user responsible when one is available.

## Architecture

The target application layering is:

```text
routers -> services -> repositories -> models
```

- Routers expose HTTP endpoints and contain no business logic.
- Services enforce domain rules and own transaction boundaries.
- Repositories perform data access and contain no business logic.
- Models describe SQLAlchemy database entities.

Repository write operations call `flush()` and `refresh()`, leaving commits
and rollbacks to the service layer. This allows multiple repository operations
to participate in one transaction.

## Technology Stack

| Area | Technology |
| --- | --- |
| API | FastAPI |
| Runtime | Python 3.13 |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 15 |
| Database driver | asyncpg |
| Cache | Redis 7 |
| Package manager | uv |
| Containers | Docker Compose / Podman Compose |
| Target deployment | Railway |

## Project Structure

```text
orderflow_backend/
├── models/                  SQLAlchemy ORM models
├── repositories/            Async database data-access functions
├── docs/
│   ├── architecture/        System and database architecture images
│   ├── database/            ERD, editable source and SQL schema snapshot
│   └── setup/               Docker, roadmap and implementation guides
├── database.py              Async engine, sessions and database setup
├── main.py                  FastAPI application and health endpoint
├── docker-compose.yaml      PostgreSQL and Redis containers
└── pyproject.toml           Python dependencies and project metadata
```

Planned but not yet implemented: Pydantic schemas, services, routers,
authentication, Alembic migrations and application tests.

## Local Setup

### Practical

```bash
uv sync
docker compose up -d
uv run uvicorn main:app --reload
```

For Podman:

```bash
podman-compose up -d
```


### Environment

Create a `.env` file for database configuration:

```dotenv
DATABASE_URL=postgresql+asyncpg://orderflow:orderflow@localhost:5432/orderflow
```

Docker Compose provisions Redis on port `6379`, but Redis is not currently
connected to the application.

## Health Endpoint

```http
GET /health
```

The current response is:

```json
{
  "status": "ok",
  "version": "1.0"
}
```

The planned health response includes database connectivity, Redis connectivity
and application uptime.

## Documentation

- [Database documentation](docs/database/README.md)
- [PostgreSQL schema snapshot](docs/database/orderflow_schema.sql)
- [Editable database ERD](docs/database/order_flow_database.excalidraw)
- [Database ERD image](docs/database/orderflow_erd.png)

## Implementation Status

### Completed

- Project initialisation
- Docker Compose infrastructure
- Async SQLAlchemy database setup
- User, order, payment and audit-log models
- Repository data-access layer
- Database relationship and indexing documentation

### Next

- Pydantic request and response schemas
- Live PostgreSQL table verification
- Expanded health response
- JWT authentication and refresh-token rotation
- Role-based access control
- CRUD services and API routers
- Alembic migrations
- Middleware, logging and structured error handling
- Unit and integration tests
- Redis caching and Celery tasks
- Prometheus metrics
- GitHub Actions CI/CD
- Railway deployment
- API and release documentation

## License

This project is licensed under the [GPL-3.0 license](LICENSE).
