from .services import PatientService


def register_patient_routes(*args, **kwargs):
    from .routes import register_patient_routes as _register_patient_routes
    return _register_patient_routes(*args, **kwargs)


__all__ = ["PatientService", "register_patient_routes"]
