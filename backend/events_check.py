from app import create_app
from models.event import Event

app = create_app()
ctx = app.app_context()
ctx.push()

print('Eventos disponibles:')
events = Event.query.all()
for event in events:
    print(f'ID: {event.id}, Título: {event.title}, Activo: {event.is_active}, Fecha: {event.start_date} - {event.end_date}') 