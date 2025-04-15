class Resource:
    """Class to represent a resource (e.g., ambulance)."""
    def __init__(self, id, type, location):
        self.id = id
        self.type = type  # e.g., "Ambulance"
        self.location = location  # e.g., "Zone 1"
        self.is_available = True
        self.assigned_incident = None

    def assign(self, incident):
        """Assign the resource to an incident."""
        self.is_available = False
        self.assigned_incident = incident
        incident.assigned_resources.append(self)
        incident.update_status("Assigned")

    def release(self):
        """Release the resource from its current incident."""
        if self.assigned_incident:
            self.assigned_incident.assigned_resources.remove(self)
            if not self.assigned_incident.assigned_resources:
                self.assigned_incident.update_status("Pending")
            self.assigned_incident = None
        self.is_available = True
