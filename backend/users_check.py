from app import create_app
from models.user import User

app = create_app()
ctx = app.app_context()
ctx.push()

print('Usuarios existentes:')
users = User.query.all()
for user in users:
    print(f'ID: {user.id}, Email: {user.email}, Role: {user.role}, Active: {user.is_active}') 