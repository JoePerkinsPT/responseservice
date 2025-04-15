from typing import List
from incident import Incident
from resource import Resource
import logging
import heapq
from datetime import datetime

class Allocator:
    """
    Manages the allocation and reallocation of emergency resources to incidents.
    
    This class implements a priority-based resource allocation system that considers:
    - Incident priority (High > Medium > Low)
    - Geographic proximity of resources
    - Resource availability and type requirements
    - Timestamp of incident creation
    
    The system automatically reallocates resources when high-priority incidents arise,
    potentially taking resources from lower-priority incidents.
    """
    
    def __init__(self):
        """
        Initialize the Allocator with empty lists for incidents and resources.
        Sets up logging to track allocation decisions.
        """
        self.incidents = []  # Priority queue for unprocessed incidents
        self.all_incidents = []  # List of all incidents
        self.resources = []
        self.setup_logging()

    def get_incidents(self):
        """Convert heap to list of incidents for external access."""
        return self.all_incidents

    def setup_logging(self):
        """
        Configure logging to file with timestamp and level information.
        Logs are written to 'allocation_log.txt' in the current directory.
        """
        logging.basicConfig(
            filename='allocation_log.txt',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def add_incident(self, incident):
        """
        Add a new incident to the system.
        
        Args:
            incident (Incident): The incident to be added
            
        Logs the addition of the incident with its key details.
        """
        # Convert priority to a numeric value for heap ordering
        priority_value = {"High": 0, "Medium": 1, "Low": 2}[incident.priority]
        # Use timestamp for tie-breaking within same priority
        heapq.heappush(self.incidents, (priority_value, incident.timestamp, incident))
        self.all_incidents.append(incident)
        logging.info(f"Added new incident: {incident.id} - {incident.type} - Priority: {incident.priority}")

    def add_resource(self, resource):
        """
        Add a new resource to the system.
        
        Args:
            resource (Resource): The resource to be added
            
        Logs the addition of the resource with its key details.
        """
        self.resources.append(resource)
        logging.info(f"Added new resource: {resource.id} - {resource.type} - Location: {resource.location}")

    def calculate_proximity(self, incident_location, resource_location):
        """
        Calculate the proximity between an incident and a resource based on their zones.
        
        Args:
            incident_location (str): Location of the incident (e.g., "Zone 1")
            resource_location (str): Location of the resource (e.g., "Zone 2")
            
        Returns:
            int: The absolute difference between zone numbers
            
        Note:
            This is a simplified proximity calculation based on zone numbers.
            In a real system, this would use actual geographic coordinates.
        """
        try:
            incident_zone = int(incident_location.split()[-1])
            resource_zone = int(resource_location.split()[-1])
            return abs(incident_zone - resource_zone)
        except (ValueError, IndexError):
            return float("inf") if incident_location != resource_location else 0

    def allocate_resources(self):
        """
        Allocate available resources to incidents based on priority and proximity.
        
        The allocation process:
        1. Sorts incidents by priority (High > Medium > Low) and timestamp
        2. For each incident:
           - Identifies required resource types and counts
           - Sorts available resources by proximity
           - Allocates resources until requirements are met
           - For high priority incidents, reallocates from lower priority if needed
        3. Logs all allocation decisions
        """
        # Create a temporary list to store incidents that still need resources
        pending_incidents = []
        
        # Process each incident in priority order
        while self.incidents:
            # Get the highest priority incident
            _, _, incident = heapq.heappop(self.incidents)
            
            # Skip if already fully allocated
            if incident.is_allocated():
                continue
            
            # Calculate total resources needed
            needed_resources = {}
            for req_type, req_count in incident.required_resources:
                current_count = sum(1 for r in incident.assigned_resources if r.type == req_type)
                if current_count < req_count:
                    needed_resources[req_type] = req_count - current_count
            
            if not needed_resources:
                continue
            
            # Try to allocate available resources first
            for req_type, needed in needed_resources.items():
                available_resources = [
                    r for r in self.resources 
                    if r.is_available and r.type == req_type
                ]
                available_resources.sort(
                    key=lambda r: self.calculate_proximity(incident.location, r.location)
                )
                
                # Assign available resources
                for resource in available_resources[:needed]:
                    try:
                        resource.assign(incident)
                        needed_resources[req_type] -= 1
                        logging.info(
                            f"Allocated {resource.type} {resource.id} to incident {incident.id}"
                        )
                    except ValueError:
                        continue
            
            # If still need resources and this is high priority, try to reallocate
            if any(needed > 0 for needed in needed_resources.values()) and incident.priority == "High":
                # Find all resources assigned to lower priority incidents
                lower_priority_resources = []
                for other_incident in self.get_incidents():
                    if other_incident != incident and other_incident.priority in ["Medium", "Low"]:
                        for resource in other_incident.assigned_resources:
                            if resource.type in needed_resources and needed_resources[resource.type] > 0:
                                lower_priority_resources.append((
                                    self.calculate_proximity(incident.location, resource.location),
                                    resource,
                                    other_incident
                                ))
                
                # Sort by proximity
                lower_priority_resources.sort()
                
                # Reallocate resources
                for _, resource, old_incident in lower_priority_resources:
                    if needed_resources[resource.type] > 0:
                        try:
                            resource.release()
                            resource.assign(incident)
                            needed_resources[resource.type] -= 1
                            logging.info(
                                f"Reallocated {resource.type} {resource.id} from incident {old_incident.id} to incident {incident.id}"
                            )
                        except ValueError:
                            continue
            
            # If still not fully allocated, add to pending
            if not incident.is_allocated():
                heapq.heappush(pending_incidents, (
                    {"High": 0, "Medium": 1, "Low": 2}[incident.priority],
                    incident.timestamp,
                    incident
                ))
        
        # Restore pending incidents back to the main heap
        self.incidents = pending_incidents

    def reallocate_resources(self, new_incident):
        """
        Reallocate resources for a new high-priority incident.
        
        This method:
        1. Checks if the new incident is high priority
        2. Identifies resources assigned to lower-priority incidents
        3. Reallocates suitable resources to the new incident
        4. Logs all reallocation decisions
        
        Args:
            new_incident (Incident): The new incident requiring resources
            
        Note:
            Only triggers for high-priority incidents and only takes resources
            from medium or low priority incidents.
        """
        if new_incident.priority != "High":
            return

        # Calculate how many resources of each type are still needed
        needed_resources = {}
        for req_type, req_count in new_incident.required_resources:
            current_count = sum(1 for r in new_incident.assigned_resources if r.type == req_type)
            if current_count < req_count:
                needed_resources[req_type] = req_count - current_count

        if not needed_resources:
            return  # No more resources needed

        # Get all resources currently allocated to lower priority incidents
        lower_priority_resources = []
        incidents_to_update = []
        for incident in self.get_incidents():
            if incident != new_incident and incident.priority in ["Medium", "Low"]:
                for resource in incident.assigned_resources[:]:  # Create a copy to avoid modification during iteration
                    if resource.type in needed_resources:
                        lower_priority_resources.append((
                            self.calculate_proximity(new_incident.location, resource.location),
                            resource,
                            incident
                        ))
                        if incident not in incidents_to_update:
                            incidents_to_update.append(incident)

        # Sort by proximity to new incident
        lower_priority_resources.sort()

        # Try to allocate these resources to the new high-priority incident
        for _, resource, old_incident in lower_priority_resources:
            if resource.type in needed_resources and needed_resources[resource.type] > 0:
                resource.release()  # This will update old_incident's status
                resource.assign(new_incident)
                needed_resources[resource.type] -= 1
                logging.info(
                    f"Reallocated {resource.type} {resource.id} from incident {old_incident.id} to incident {new_incident.id}"
                )
                
                # Check if we have all needed resources
                if all(count <= 0 for count in needed_resources.values()):
                    break

        # Re-add affected incidents to the heap with updated priorities
        new_heap = []
        while self.incidents:
            priority, timestamp, incident = heapq.heappop(self.incidents)
            if incident in incidents_to_update:
                # Re-add with updated status
                heapq.heappush(new_heap, (
                    {"High": 0, "Medium": 1, "Low": 2}[incident.priority],
                    incident.timestamp,
                    incident
                ))
            else:
                heapq.heappush(new_heap, (priority, timestamp, incident))
        self.incidents = new_heap

    def update_incident_priority(self, incident_id, new_priority):
        """
        Update the priority of an existing incident.
        
        Args:
            incident_id (str): ID of the incident to update
            new_priority (str): New priority level (High/Medium/Low)
            
        Note:
            If the new priority is "High", triggers resource reallocation
            to ensure the incident gets necessary resources.
        """
        # Find and update the incident
        updated_incident = None
        new_incidents = []
        
        # Remove all incidents from the heap
        while self.incidents:
            priority, timestamp, incident = heapq.heappop(self.incidents)
            if incident.id == incident_id:
                old_priority = incident.priority
                incident.update_priority(new_priority)
                # Update priority value for heap
                priority = {"High": 0, "Medium": 1, "Low": 2}[new_priority]
                updated_incident = incident
                logging.info(
                    f"Updated priority for incident {incident_id} from {old_priority} to {new_priority}"
                )
            new_incidents.append((priority, timestamp, incident))
        
        # Rebuild the heap with updated priorities
        for item in new_incidents:
            heapq.heappush(self.incidents, item)
        
        # If we updated to high priority, trigger reallocation
        if updated_incident and new_priority == "High":
            self.reallocate_resources(updated_incident) 