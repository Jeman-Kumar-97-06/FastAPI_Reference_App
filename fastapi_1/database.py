from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DB_URL = 'sqlite:///./blog.db'

engine = create_engine(
    SQLALCHEMY_DB_URL, 
    connect_args = {'check_same_thread':False} #Allows multiple threads to interact with DB safely.
)

#Session to communication with DB:
SessionLocal = sessionmaker(autocommit=False,
                            autoflush=False,
                            bind=engine)


#Parent class for all future database models:
class Base(DeclarativeBase):
    pass

#The following ensures : 
    #for every API request, a DB session is opened.
    #once the request is finished, it automatically closes the session. This prevents 'leaking' connections, which can crash your app
def get_db():
    with SessionLocal() as db:
        yield db