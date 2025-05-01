from app.dao.base import BaseDAO
from app.dao.models import Note, User


class UsersDAO(BaseDAO):
    model = User


class NotesDAO(BaseDAO):
    model = Note
