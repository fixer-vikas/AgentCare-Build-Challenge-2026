from .services import DashboardService


def register_dashboard_routes(*args, **kwargs):
    from .routes import register_dashboard_routes as _register_dashboard_routes
    return _register_dashboard_routes(*args, **kwargs)


__all__ = ["DashboardService", "register_dashboard_routes"]
