from .services import AuthService


def register_auth_routes(*args, **kwargs):
    from .routes import register_auth_routes as _register_auth_routes
    return _register_auth_routes(*args, **kwargs)


__all__ = ["AuthService", "register_auth_routes"]
