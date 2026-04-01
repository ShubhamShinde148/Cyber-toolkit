class BreachTimeline:
    def __init__(self):
        self.data = []
    def clear(self):
        self.data = []
    def add_breach_from_dict(self, breach):
        self.data.append(breach)
    def get_full_report(self):
        return {"timeline": self.data}
    def get_chart_js_data(self, chart_type):
        return {"type": chart_type, "data": []}