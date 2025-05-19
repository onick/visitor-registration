from app import create_app
from models.kiosk import Kiosk

app = create_app()
ctx = app.app_context()
ctx.push()

print('Kioscos disponibles:')
kiosks = Kiosk.query.all()
for kiosk in kiosks:
    print(f'ID: {kiosk.id}, Nombre: {kiosk.name}, Ubicación: {kiosk.location}, Activo: {kiosk.is_active}') 