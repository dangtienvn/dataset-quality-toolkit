class DatasetRBAC:
    def check_access(self, user_role: str, dataset_id: str, action: str) -> bool:
        if user_role == "admin":
            return True
        if action == "read":
            return True
        return False
