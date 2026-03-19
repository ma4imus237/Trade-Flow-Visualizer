"""Initial tables and aggregated_flows materialized view

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-03-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- countries ---
    op.create_table(
        "countries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("iso3", sa.String(3), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("region", sa.String(50), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
    )
    op.create_index("ix_countries_iso3", "countries", ["iso3"], unique=True)

    # --- commodities ---
    op.create_table(
        "commodities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("color", sa.String(7), nullable=True),
    )
    op.create_index("ix_commodities_code", "commodities", ["code"], unique=True)

    # --- hs_code_mappings ---
    op.create_table(
        "hs_code_mappings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "commodity_id",
            sa.Integer(),
            sa.ForeignKey("commodities.id"),
            nullable=False,
        ),
        sa.Column("hs6", sa.String(6), nullable=False),
        sa.Column("description", sa.String(200), nullable=True),
    )
    op.create_index("ix_hs_code_mappings_hs6", "hs_code_mappings", ["hs6"])

    # --- trade_flows ---
    op.create_table(
        "trade_flows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "reporter_id",
            sa.Integer(),
            sa.ForeignKey("countries.id"),
            nullable=False,
        ),
        sa.Column(
            "partner_id",
            sa.Integer(),
            sa.ForeignKey("countries.id"),
            nullable=False,
        ),
        sa.Column(
            "commodity_id",
            sa.Integer(),
            sa.ForeignKey("commodities.id"),
            nullable=False,
        ),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("flow_type", sa.String(10), nullable=False),
        sa.Column("value_usd", sa.BigInteger(), nullable=False),
        sa.Column("weight_kg", sa.BigInteger(), nullable=True),
        sa.Column("is_estimated", sa.Boolean(), server_default=sa.text("false")),
        sa.UniqueConstraint(
            "reporter_id",
            "partner_id",
            "commodity_id",
            "year",
            "flow_type",
            name="uq_trade_flow",
        ),
    )
    op.create_index("ix_trade_flows_reporter_id", "trade_flows", ["reporter_id"])
    op.create_index("ix_trade_flows_partner_id", "trade_flows", ["partner_id"])
    op.create_index("ix_trade_flows_commodity_id", "trade_flows", ["commodity_id"])
    op.create_index("ix_trade_flows_year", "trade_flows", ["year"])
    op.create_index("idx_flow_commodity_year", "trade_flows", ["commodity_id", "year"])

    # --- materialized view: aggregated_flows ---
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS aggregated_flows AS
        SELECT
            commodity_id,
            year,
            reporter_id,
            partner_id,
            flow_type,
            SUM(value_usd) AS total_value,
            SUM(weight_kg) AS total_weight,
            COUNT(*) AS record_count
        FROM trade_flows
        GROUP BY commodity_id, year, reporter_id, partner_id, flow_type;
    """)
    op.execute("""
        CREATE UNIQUE INDEX idx_agg_flows_lookup
        ON aggregated_flows (commodity_id, year, reporter_id, partner_id, flow_type);
    """)


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS aggregated_flows;")
    op.drop_table("trade_flows")
    op.drop_table("hs_code_mappings")
    op.drop_table("commodities")
    op.drop_table("countries")
