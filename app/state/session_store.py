import uuid

from .session import Session


class SessionStore:

    def __init__(self):
        self.sessions = {}

    def get(self, session_id=None):

        if session_id is None:

            session_id = str(uuid.uuid4())

        if session_id not in self.sessions:

            self.sessions[session_id] = Session()

        return session_id, self.sessions[session_id]