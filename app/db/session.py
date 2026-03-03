from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from config import settings
from .models import Base, Group


engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    required_groups = ("admins", "engineers")
    with Session() as session:
        existing_names = set(session.execute(select(Group.name)).scalars().all())
        missing_groups = [Group(name=name) for name in required_groups if name not in existing_names]
        if missing_groups:
            session.add_all(missing_groups)
            session.commit()