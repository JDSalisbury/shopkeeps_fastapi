from sqlmodel import Session, SQLModel, create_engine
import os
from dotenv import load_dotenv
load_dotenv()

render_external_url = os.getenv("DATABASE_URL")


engine = create_engine(
    render_external_url, pool_pre_ping=True
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
