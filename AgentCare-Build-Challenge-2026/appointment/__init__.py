from .services import AppointmentService


def register_appointment_routes(*args, **kwargs):
    from .routes import register_appointment_routes as _register_appointment_routes
    return _register_appointment_routes(*args, **kwargs)


__all__ = ["AppointmentService", "register_appointment_routes"]
