from app import create_app
from models.visitor import Visitor

app = create_app()
ctx = app.app_context()
ctx.push()

print('Visitantes registrados:')
visitors = Visitor.query.all()
if not visitors:
    print("No hay visitantes registrados en la base de datos.")
else:
    for visitor in visitors:
        print(f'ID: {visitor.id}, Nombre: {visitor.name}, Email: {visitor.email}, Teléfono: {visitor.phone}') 