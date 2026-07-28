from .services import AdminService


def register_admin_routes(*args, **kwargs):
    from .routes import register_admin_routes as _register_admin_routes
    return _register_admin_routes(*args, **kwargs)


__all__ = ["AdminService", "register_admin_routes"]
