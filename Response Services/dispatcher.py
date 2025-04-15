from heapq import heappush, heappop
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(filename="allocation_log.txt", level=logging.INFO, 
                    format="%(asctime)s - %(message)s")

class Allocator:
    """Class to handle resource allocation logic."""
    def __init__(self):
        self.incidents = []
        self.resources = []

    def add_incident(self, incident):
        self.incidents.append(incident)
        logging.info(f"Added incident {incident.id} ({incident.type}, {incident.priority})")

    def add_resource(self, resource):
        self.resources.append(resource)
        logging.info(f"Added resource {resource.id} ({resource.type})")

    def calculate_distance(self, loc1, loc2):
        """Calculate distance between zones (simple numeric parsing)."""
        try:
            zone1 = int(loc1.split()[-1])
            zone2 = int(loc2.split()[-1])
            return abs(zone1 - zone2)
        except (ValueError, IndexError):
            return float("inf") if loc1 != loc2 else 0

    def allocate_resources(self):
        """Allocate resources with proximity consideration."""
        incident_heap = []
        for incident in self.incidents:
            if incident.status == "Pending":
                heappush(incident_heap, incident)

        while incident_heap:
            incident = heappop(incident_heap)
            # Find resources for each required type and count
            for req_type, req_count in incident.required_resources:
                current_count = sum(1 for r in incident.assigned_resources if r.type == req_type)
                needed = req_count - current_count
                if needed <= 0:
                    continue
                # Sort resources by proximity and availability
                candidates = [
                    (self.calculate_distance(r.location, incident.location), r)
                    for r in self.resources
                    if r.is_available and r.type == req_type
                ]
                candidates.sort()  # Sort by distance
                for _, resource in candidates[:needed]:
                    resource.assign(incident)
                    logging.info(f"Assigned {resource.id} to {incident.id} "
                                f"(distance: {self.calculate_distance(resource.location, incident.location)})")
                if current_count + len(candidates) < req_count:
                    self._reallocate_for(incident, req_type, needed - len(candidates))

    def _reallocate_for(self, incident, req_type, needed):
        """Reallocate resources optimally."""
        candidates = [
            ({"High": 3, "Medium": 2, "Low": 1}[i.priority], i, r)
            for i in self.incidents
            if i.status == "Assigned" and i != incident
            for r in i.assigned_resources
            if r.type == req_type
        ]
        candidates.sort()  # Lowest priority first
        for _, other_incident, resource in candidates[:needed]:
            if {"High": 3, "Medium": 2, "Low": 1}[other_incident.priority] < \
               {"High": 3, "Medium": 2, "Low": 1}[incident.priority]:
                resource.release()
                resource.assign(incident)
                logging.info(f"Reallocated {resource.id} from {other_incident.id} to {incident.id}")

    def update_incident_priority(self, incident_id, new_priority):
        for incident in self.incidents:
            if incident.id == incident_id:
                old_priority = incident.priority
                incident.update_priority(new_priority)
                logging.info(f"Updated {incident.id} priority from {old_priority} to {new_priority}")
                if new_priority == "High" and incident.status == "Pending":
                    self.allocate_resources()
                break