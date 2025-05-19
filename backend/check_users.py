from app import create_app
from models.user import User

app = create_app()
ctx = app.app_context()
ctx.push()

print('Usuarios registrados:')
users = User.query.all()
if not users:
    print("No hay usuarios registrados en la base de datos.")
else:
    for user in users:
        print(f"- Email: {user.email}, Rol: {user.role}, Activo: {user.is_active}") 