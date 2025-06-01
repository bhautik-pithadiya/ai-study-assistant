from fastapi.routing import APIRoute, WebSocketRoute

for route in app.routes:
    if isinstance(route, WebSocketRoute):
        print(f"WebSocket path: {route.path}")
