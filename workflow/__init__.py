from .services import WorkflowService


def register_workflow_routes(*args, **kwargs):
    from .routes import register_workflow_routes as _register_workflow_routes
    return _register_workflow_routes(*args, **kwargs)


__all__ = ["WorkflowService", "register_workflow_routes"]
