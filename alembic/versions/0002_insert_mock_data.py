"""insert mock data

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-01 00:10:00
"""

import datetime
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.services.security import hash_password

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    users_table = sa.table(
        "users",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.String()),
        sa.column("email", sa.String()),
        sa.column("password_hash", sa.String()),
        sa.column("registered_at", sa.DateTime()),
        sa.column("is_author", sa.Boolean()),
        sa.column("is_admin", sa.Boolean()),
        sa.column("avatar_url", sa.String()),
    )

    admin_id = uuid.uuid4()
    author_id = uuid.uuid4()
    user_id = uuid.uuid4()

    now = datetime.datetime.utcnow()

    op.bulk_insert(
        users_table,
        [
            {
                "id": admin_id,
                "name": "Admin",
                "email": "admin@example.com",
                "password_hash": hash_password("adminpass"),
                "registered_at": now,
                "is_author": True,
                "is_admin": True,
                "avatar_url": None,
            },
            {
                "id": author_id,
                "name": "Author",
                "email": "author@example.com",
                "password_hash": hash_password("authorpass"),
                "registered_at": now,
                "is_author": True,
                "is_admin": False,
                "avatar_url": None,
            },
            {
                "id": user_id,
                "name": "Reader",
                "email": "reader@example.com",
                "password_hash": hash_password("readerpass"),
                "registered_at": now,
                "is_author": False,
                "is_admin": False,
                "avatar_url": None,
            },
        ],
    )

    news_table = sa.table(
        "news",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("title", sa.String()),
        sa.column("content", postgresql.JSONB()),
        sa.column("published_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
        sa.column("cover_url", sa.String()),
        sa.column("author_id", postgresql.UUID(as_uuid=True)),
    )

    news_id = uuid.uuid4()

    op.bulk_insert(
        news_table,
        [
            {
                "id": news_id,
                "title": "First news",
                "content": {"body": "Welcome to the platform"},
                "published_at": now,
                "updated_at": now,
                "cover_url": None,
                "author_id": author_id,
            }
        ],
    )

    comments_table = sa.table(
        "comments",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("text", sa.Text()),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
        sa.column("news_id", postgresql.UUID(as_uuid=True)),
        sa.column("author_id", postgresql.UUID(as_uuid=True)),
    )

    op.bulk_insert(
        comments_table,
        [
            {
                "id": uuid.uuid4(),
                "text": "Great news!",
                "created_at": now,
                "updated_at": now,
                "news_id": news_id,
                "author_id": user_id,
            }
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM comments")
    op.execute("DELETE FROM news")
    op.execute("DELETE FROM users")
