"""initial empty migration - baseline

Revision ID: a1eda7b28416
Revises:
Create Date: 2026-04-22 10:18:04.124618

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "a1eda7b28416"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
