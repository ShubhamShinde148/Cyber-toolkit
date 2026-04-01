class SecurityAdvisor:
    def __init__(self):
        pass
    def set_context(self, data):
        pass
    def get_recommendations(self, max_count=10):
        return ["Use strong passwords", "Enable 2FA"]
    def get_quick_wins(self):
        return ["Update your passwords", "Enable 2FA"]
    def generate_action_plan(self, timeframe):
        return {"plan": ["Do X", "Do Y"], "timeframe": timeframe}