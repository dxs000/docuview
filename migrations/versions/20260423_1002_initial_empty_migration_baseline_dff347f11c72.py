"""initial empty migration - baseline

Revision ID: dff347f11c72
Revises: a1eda7b28416
Create Date: 2026-04-23 10:02:23.536153

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "dff347f11c72"
down_revision: str | Sequence[str] | None = "a1eda7b28416"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
