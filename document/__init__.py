from .services import DocumentService


def register_document_routes(*args, **kwargs):
    from .routes import register_document_routes as _register_document_routes
    return _register_document_routes(*args, **kwargs)


__all__ = ["DocumentService", "register_document_routes"]
