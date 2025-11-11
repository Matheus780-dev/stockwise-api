from typing import Generator
from sqlmodel import Session, create_engine, SQLModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app import models, crud, auth

DATABASE_URL = "sqlite:///./stockwise.db"
engine = create_engine(DATABASE_URL, echo=False)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def get_current_user(token: str = Depends(oauth2_scheme), db: Session =
                     Depends(get_session)) -> models.User:
    payload = auth.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token\
                  payload")
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
