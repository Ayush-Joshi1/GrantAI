"""
Versioned HTTP routers/controllers.

Rules:
- Keep these thin: validate input, call application services via DI, map outputs to DTOs.
- Do not call external systems directly from routes.
"""


