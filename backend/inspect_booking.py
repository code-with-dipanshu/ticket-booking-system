from app.db.database import SessionLocal
import pkgutil
import importlib

# Dynamically import all modules in app.models so SQLAlchemy mappers register
import app.models as _models_pkg
for _mod in pkgutil.iter_modules(_models_pkg.__path__):
    importlib.import_module(f"app.models.{_mod.name}")

from app.models.booking import Booking
from sqlalchemy import desc


s = SessionLocal()
try:
    b = s.query(Booking).order_by(desc(Booking.id)).first()
    if b:
        print('id:', b.id)
        print('ticket_reference:', b.ticket_reference)
        print('ticket_code:', getattr(b, 'ticket_code', None))
        print('qr_payload:', b.qr_payload)
        print('qr_code_len:', len(getattr(b, 'qr_code', '') or ''))
    else:
        print('no booking found')
finally:
    s.close()
