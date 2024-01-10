from ..extensions.db import db


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250))

    def __init__(self, title, description):
        self.title = title
        self.description = description

def serialize_todo(obj):
    if isinstance(obj, Todo):
        return {"title": obj.title, "description": obj.description}
    raise TypeError(f"Object of type '{type(obj).__name__}' is not JSON serializable")
