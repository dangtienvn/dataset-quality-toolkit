class PromptGuard:
    def check_injection(self, user_input: str) -> bool:
        suspicious = ["ignore previous instructions", "system prompt", "drop table"]
        return any(s in user_input.lower() for s in suspicious)
