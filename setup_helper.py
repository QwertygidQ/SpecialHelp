from app import db
from app.models import User

u = User(username="admin", email="admin@example.com", role=1)
u.set_password("admin12345")

db.session.add(u)
db.session.commit()
