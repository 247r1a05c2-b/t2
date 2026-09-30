import os
from sqlalchemy import create_engine, String, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
url=os.getenv("DATABASE_URL","sqlite:///./tracegaurd.db")
if url.startswith("postgres://"): url=url.replace("postgres://","postgresql+psycopg://",1)
engine=create_engine(url,connect_args={"check_same_thread":False} if url.startswith("sqlite") else {})
SessionLocal=sessionmaker(bind=engine)
class Base(DeclarativeBase): pass
class UserRecord(Base):
    __tablename__="users"; email:Mapped[str]=mapped_column(String(255),primary_key=True); role:Mapped[str]=mapped_column(String(50),default="SOFTWARE_ENGINEER")
class ApprovalRecord(Base):
    __tablename__="approvals"; id:Mapped[str]=mapped_column(String(100),primary_key=True); incident_id:Mapped[str]=mapped_column(String(100)); action:Mapped[str]=mapped_column(String(100)); engineer:Mapped[str]=mapped_column(String(255)); state:Mapped[str]=mapped_column(String(30))
class ClientRecord(Base):
    __tablename__="clients"; id:Mapped[str]=mapped_column(String(100),primary_key=True); name:Mapped[str]=mapped_column(String(255)); environment:Mapped[str]=mapped_column(String(50)); service:Mapped[str]=mapped_column(String(100)); incidents:Mapped[int]=mapped_column(Integer,default=0); status:Mapped[str]=mapped_column(String(30),default="ONLINE")
class RemediationExecutionRecord(Base):
    __tablename__="executions"; id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True); incident_id:Mapped[str]=mapped_column(String(100)); action:Mapped[str]=mapped_column(String(100)); engineer:Mapped[str]=mapped_column(String(255)); status:Mapped[str]=mapped_column(String(50)); verification:Mapped[str]=mapped_column(Text)
Base.metadata.create_all(engine)
def database_status():
    try:
        with engine.connect() as c: c.exec_driver_sql("SELECT 1")
        return "connected"
    except Exception: return "unavailable"
