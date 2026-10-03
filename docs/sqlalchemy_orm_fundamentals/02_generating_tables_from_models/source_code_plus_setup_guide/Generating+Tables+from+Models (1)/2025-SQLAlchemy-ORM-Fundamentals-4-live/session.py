from contextlib import contextmanager

from db import SessionLocal


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        raise
    finally:
        session.close()
