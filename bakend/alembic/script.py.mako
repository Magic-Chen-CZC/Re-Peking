"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """
    升级数据库结构（应用此迁移）
    这个函数会在执行 alembic upgrade 时被调用
    """
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """
    降级数据库结构（回滚此迁移）
    这个函数会在执行 alembic downgrade 时被调用
    """
    ${downgrades if downgrades else "pass"}
