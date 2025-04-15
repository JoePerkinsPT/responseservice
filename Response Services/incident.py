class Incident:
    """Class to represent an emergency incident."""
    def __init__(self, id, location, type, priority, required_resources):
        self.id = id
        self.location = location  # e.g., "Zone 1"
        self.type = type  # e.g., "Fire"
        self.priority = priority  # "High", "Medium", "Low"
        self.required_resources = required_resources  # List, e.g., ["Ambulance"]
        self.status = "Pending"
        self.assigned_resources = []

    def update_priority(self, new_priority):
        """Update the incident's priority."""
        self.priority = new_priority

    def update_status(self, status):
        """Update the incident's status."""
        self.status = status

    def __lt__(self, other):
        """Compare incidents by priority for sorting."""
        priority_order = {"High": 3, "Medium": 2, "Low": 1}
        return priority_order[self.priority] < priority_order[other.priority]
    