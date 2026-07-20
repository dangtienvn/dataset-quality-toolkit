from datetime import datetime

class AuditLogger:
    def __init__(self):
        self.logs = []

    def log_event(self, user_id: str, action: str, resource: str):
        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource
        })
