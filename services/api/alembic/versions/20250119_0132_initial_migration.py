"""Initial migration with pgvector support

Revision ID: 20250119_0132
Revises: 
Create Date: 2025-01-19 01:32:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import pgvector.sqlalchemy

# revision identifiers, used by Alembic.
revision: str = '20250119_0132'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create subreddits table
    op.create_table('subreddits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('about', sa.Text(), nullable=True),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=384), nullable=True),
        sa.Column('quality_score', sa.Real(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_unique_constraint('uq_subreddits_name', 'subreddits', ['name'])
    op.create_index('ix_subreddits_quality_score', 'subreddits', ['quality_score'])
    
    # Create vector index for subreddits
    op.execute("""
        CREATE INDEX ix_subreddits_embedding_cosine 
        ON subreddits USING ivfflat (embedding vector_cosine_ops) 
        WITH (lists = 100)
    """)
    
    # Create posts table
    op.create_table('posts',
        sa.Column('id', sa.String(length=20), nullable=False),
        sa.Column('subreddit', sa.String(length=50), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('selftext', sa.Text(), nullable=True),
        sa.Column('author', sa.String(length=50), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('num_comments', sa.Integer(), nullable=True),
        sa.Column('url', sa.Text(), nullable=True),
        sa.Column('created_utc', sa.DateTime(timezone=True), nullable=True),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=384), nullable=True),
        sa.Column('indexed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_posts_subreddit', 'posts', ['subreddit'])
    op.create_index('ix_posts_created_utc', 'posts', ['created_utc'])
    op.create_index('ix_posts_score', 'posts', ['score'])
    
    # Create vector index for posts
    op.execute("""
        CREATE INDEX ix_posts_embedding_cosine 
        ON posts USING ivfflat (embedding vector_cosine_ops) 
        WITH (lists = 100)
    """)
    
    # Create alerts table
    op.create_table('alerts',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=True),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('positive_filters', ARRAY(sa.String()), nullable=True),
        sa.Column('negative_filters', ARRAY(sa.String()), nullable=True),
        sa.Column('subreddits', ARRAY(sa.String()), nullable=True),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=384), nullable=True),
        sa.Column('frequency_minutes', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_alerts_user_id', 'alerts', ['user_id'])
    op.create_index('ix_alerts_is_active', 'alerts', ['is_active'])
    
    # Create vector index for alerts
    op.execute("""
        CREATE INDEX ix_alerts_embedding_cosine 
        ON alerts USING ivfflat (embedding vector_cosine_ops) 
        WITH (lists = 100)
    """)
    
    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('alert_id', UUID(as_uuid=True), nullable=False),
        sa.Column('post_id', sa.String(length=20), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['alert_id'], ['alerts.id'], ),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notifications_alert_id', 'notifications', ['alert_id'])
    op.create_index('ix_notifications_sent_at', 'notifications', ['sent_at'])


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('alerts')
    op.drop_table('posts')
    op.drop_table('subreddits')
    op.execute('DROP EXTENSION IF EXISTS vector')
