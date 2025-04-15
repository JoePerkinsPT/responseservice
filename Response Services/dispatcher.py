from heapq import heappush, heappop

class Dispatcher:
    """Class to manage incidents and resources."""
    def __init__(self):
        self.incidents = []
        self.resources = []

    def add_incident(self, incident):
        """Add a new incident."""
        self.incidents.append(incident)

    def add_resource(self, resource):
        """Add a new resource."""
        self.resources.append(resource)

    def allocate_resources(self):
        """Allocate resources to incidents based on priority and availability."""
        # Create a max-heap for incidents (reverse priority order)
        incident_heap = []
        for incident in self.incidents:
            if incident.status == "Pending":
                heappush(incident_heap, incident)

        while incident_heap:
            incident = heappop(incident_heap)
            # Find matching resources
            for resource in self.resources:
                if (resource.is_available and 
                    resource.type in incident.required_resources and 
                    resource.location == incident.location):
                    resource.assign(incident)
                    break
            else:
                # No available resources; try reallocation
                self._reallocate_for(incident)

    def _reallocate_for(self, incident):
        """Reallocate resources from lower-priority incidents if needed."""
        # Sort incidents by priority (ascending) to find lower-priority ones
        sorted_incidents = sorted([i for i in self.incidents if i.status == "Assigned"], 
                                key=lambda x: {"High": 3, "Medium": 2, "Low": 1}[x.priority])
        for other_incident in sorted_incidents:
            if ({"High": 3, "Medium": 2, "Low": 1}[other_incident.priority] < 
                {"High": 3, "Medium": 2, "Low": 1}[incident.priority]):
                for resource in other_incident.assigned_resources[:]:
                    if resource.type in incident.required_resources:
                        resource.release()
                        resource.assign(incident)
                        return

    def update_incident_priority(self, incident_id, new_priority):
        """Update an incident's priority and reallocate if needed."""
        for incident in self.incidents:
            if incident.id == incident_id:
                incident.update_priority(new_priority)
                if new_priority == "High" and incident.status == "Pending":
                    self.allocate_resources()
                break

    def display_incidents(self):
        """Display all incidents in a table."""
        print("\nIncidents:")
        print(f"{'ID':<5} {'Location':<10} {'Type':<10} {'Priority':<10} {'Status':<10} {'Resources':<20}")
        for i in self.incidents:
            resources = ", ".join([r.id for r in i.assigned_resources]) or "None"
            print(f"{i.id:<5} {i.location:<10} {i.type:<10} {i.priority:<10} {i.status:<10} {resources:<20}")

    def display_resources(self):
        """Display all resources in a table."""
        print("\nResources:")
        print(f"{'ID':<5} {'Type':<10} {'Location':<10} {'Available':<10} {'Assigned To':<15}")
        for r in self.resources:
            assigned = r.assigned_incident.id if r.assigned_incident else "None"
            print(f"{r.id:<5} {r.type:<10} {r.location:<10} {str(r.is_available):<10} {assigned:<15}")
