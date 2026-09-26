"""Migrate legacy bookings table to current Booking model schema

Revision ID: a1b2c3d4e5f6
Revises: 7adf02fc54e3
Create Date: 2026-09-27 00:19:00.000000

This migration non-destructively upgrades the legacy bookings table:
  Legacy columns: id, trip_id, vendor_id, type, status, cost, confirmation_code
  Target columns: id, trip_id, itinerary_item_id, traveler_id, provider_id,
                  booking_type, status, confirmation_code, start_datetime,
                  end_datetime, location, estimated_cost, currency,
                  provider_reference, source_type, cancellation_policy,
                  created_at, updated_at

Existing booking row is preserved and legacy fields are mapped:
  type          -> booking_type
  cost          -> estimated_cost
  status        -> status        (preserved as-is)
  confirmation_code -> confirmation_code (preserved as-is)
  vendor_id, trip_id -> kept (vendor_id set to NULL after migration)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '7adf02fc54e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add missing columns to the bookings table (SQLite-safe batch mode).
    Preserve existing row. Map legacy fields to new column names.
    """
    bind = op.get_bind()

    # Step 1: Read existing booking rows BEFORE schema change
    existing_rows = bind.execute(
        sa.text("SELECT id, trip_id, type, status, cost, confirmation_code FROM bookings")
    ).fetchall()

    # Step 2: Add all missing columns using batch_alter_table (SQLite-compatible)
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('itinerary_item_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('traveler_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('provider_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('booking_type', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('start_datetime', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('end_datetime', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('location', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('estimated_cost', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('currency', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('provider_reference', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('source_type', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('cancellation_policy', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))

    # Step 3: Backfill the new columns from legacy field values
    # Map: type -> booking_type, cost -> estimated_cost
    # Set: currency = 'INR', source_type = 'DEMO'
    for row in existing_rows:
        row_id, trip_id, legacy_type, legacy_status, legacy_cost, legacy_code = row
        bind.execute(
            sa.text("""
                UPDATE bookings SET
                    booking_type = :booking_type,
                    estimated_cost = :estimated_cost,
                    currency = 'INR',
                    source_type = 'DEMO'
                WHERE id = :row_id
            """),
            {
                "booking_type": legacy_type,
                "estimated_cost": legacy_cost,
                "row_id": row_id,
            }
        )


def downgrade() -> None:
    """
    Remove the newly added columns, reverting to the legacy schema.
    Note: this will lose data stored in the new columns.
    """
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('cancellation_policy')
        batch_op.drop_column('source_type')
        batch_op.drop_column('provider_reference')
        batch_op.drop_column('currency')
        batch_op.drop_column('estimated_cost')
        batch_op.drop_column('location')
        batch_op.drop_column('end_datetime')
        batch_op.drop_column('start_datetime')
        batch_op.drop_column('booking_type')
        batch_op.drop_column('provider_id')
        batch_op.drop_column('traveler_id')
        batch_op.drop_column('itinerary_item_id')
