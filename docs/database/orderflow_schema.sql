-- Documentation snapshot: generated from the SQLAlchemy models.
-- Alembic migrations will own future schema changes.
CREATE TABLE "users" (
  "id" uuid PRIMARY KEY,
  "email" varchar UNIQUE NOT NULL,
  "hashed_password" varchar NOT NULL,
  "role" varchar NOT NULL,
  "is_active" boolean NOT NULL DEFAULT true,
  "created_at" timestamptz NOT NULL
);

CREATE TABLE "orders" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "status" varchar NOT NULL,
  "total_amount" numeric(10,2) NOT NULL,
  "idempotency_key" varchar UNIQUE NOT NULL,
  "created_at" timestamptz NOT NULL,
  "updated_at" timestamptz NOT NULL
);

CREATE TABLE "payments" (
  "id" uuid PRIMARY KEY,
  "order_id" uuid NOT NULL,
  "status" varchar NOT NULL,
  "transaction_id" varchar UNIQUE NOT NULL,
  "amount" numeric(10,2) NOT NULL,
  "created_at" timestamptz NOT NULL
);

CREATE TABLE "audit_logs" (
  "id" uuid PRIMARY KEY,
  "entity_type" varchar NOT NULL,
  "entity_id" uuid NOT NULL,
  "event_type" varchar NOT NULL,
  "actor_id" uuid,
  "metadata" jsonb,
  "timestamp" timestamptz NOT NULL
);

CREATE INDEX ON "orders" ("user_id");

CREATE INDEX ON "payments" ("order_id");

CREATE INDEX ON "audit_logs" ("entity_type", "entity_id");

COMMENT ON COLUMN "users"."role" IS 'admin | user';

COMMENT ON COLUMN "orders"."status" IS 'pending | confirmed | fulfilled | cancelled';

ALTER TABLE "orders" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "payments" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "audit_logs" ADD FOREIGN KEY ("actor_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;
