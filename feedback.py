import os
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, select
from sqlalchemy.exc import OperationalError


DATABASE_URL = os.environ.get('DATABASE_URL')


def _get_engine():
    """Create a SQLAlchemy engine. If DATABASE_URL is not set, fall back to a local SQLite file."""
    if DATABASE_URL:
        return create_engine(DATABASE_URL, connect_args={})
    # fallback to SQLite file in data/
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'feedback.db')
    d = os.path.dirname(db_path)
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    return create_engine(f'sqlite:///{db_path}', connect_args={})


_engine = _get_engine()
_metadata = MetaData()

feedback_table = Table(
    'feedback', _metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('timestamp', String),
    Column('candidate', String),
    Column('jd', String),
    Column('rating', Integer),
    Column('comments', String),
)


def _ensure_db():
    try:
        _metadata.create_all(_engine)
    except OperationalError:
        # if creation fails, log and continue; higher layers will see errors on use
        pass


def save_feedback(candidate, jd, rating, comments):
    _ensure_db()
    ins = feedback_table.insert().values(
        timestamp=datetime.utcnow().isoformat(),
        candidate=candidate,
        jd=jd,
        rating=rating,
        comments=comments,
    )
    conn = _engine.connect()
    try:
        conn.execute(ins)
        conn.commit()
    finally:
        conn.close()


def list_feedback(limit=50):
    _ensure_db()
    sel = select([
        feedback_table.c.timestamp,
        feedback_table.c.candidate,
        feedback_table.c.jd,
        feedback_table.c.rating,
        feedback_table.c.comments,
    ]).order_by(feedback_table.c.id.desc()).limit(limit)
    conn = _engine.connect()
    try:
        rows = conn.execute(sel).fetchall()
        return rows
    finally:
        conn.close()

