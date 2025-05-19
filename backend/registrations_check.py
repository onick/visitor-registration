from app import create_app
from models.visitor import VisitorCheckIn
from models.event import Event
from models.visitor import Visitor

app = create_app()
ctx = app.app_context()
ctx.push()

print('Registros de visitantes en eventos:')
check_ins = VisitorCheckIn.query.all()

if not check_ins:
    print("No hay registros de visitantes en eventos.")
else:
    for check_in in check_ins:
        event = Event.query.get(check_in.event_id)
        visitor = Visitor.query.get(check_in.visitor_id)
        print(f'ID: {check_in.id}, Visitante: {visitor.name}, Evento: {event.title}, Fecha: {check_in.check_in_time}') 