from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from datetime import datetime

class IncidentInterface(ABC):
    """
    This interface ensures that all incident implementations provide
    the necessary methods for priority management.
    """
    @abstractmethod
    def update_priority(self, new_priority):
        """Update the priority level of the incident."""
        pass

class Incident(IncidentInterface):
    """
    Represents an emergency incident requiring resource allocation.
    
    This class manages:
    - Incident details (ID, location, type, priority)
    - Required resources and their counts
    - Currently assigned resources
    - Incident status and timestamp
    
    The class implements validation for all inputs and provides
    methods for resource allocation and status tracking.
    """
    VALID_PRIORITIES = {"High", "Medium", "Low"}

    def __init__(self, id: str, location: str, type: str, priority: str, required_resources: List[Tuple[str, int]]):
        """
        Initialize a new incident.
        
        Args:
            id (str): Unique identifier for the incident
            location (str): Location of the incident (e.g., "Zone 1")
            type (str): Type of emergency (e.g., "Fire", "Medical")
            priority (str): Priority level (High/Medium/Low)
            required_resources (List[Tuple[str, int]]): List of (resource_type, count) pairs
            
        Raises:
            ValueError: If any input validation fails
        """
        self.id = id
        self.location = location
        self.type = type
        self.priority = priority
        self.required_resources = required_resources
        self.assigned_resources = []  # Will contain Resource objects
        self.timestamp = datetime.now()
        self.status = "Pending"
        self._validate_inputs()

    def _validate_inputs(self):
        """
        Validate all input parameters for the incident.
        
        Raises:
            ValueError: If any required field is empty or invalid
        """
        if not self.id:
            raise ValueError("Incident ID cannot be empty")
        if not self.location:
            raise ValueError("Location cannot be empty")
        if not self.type:
            raise ValueError("Type cannot be empty")
        if self.priority not in self.VALID_PRIORITIES:
            raise ValueError("Priority must be High, Medium, or Low")
        if not self.required_resources:
            raise ValueError("At least one resource type must be required")

    def allocate_resource(self, resource: 'Resource'):
        """
        Assign a resource to this incident.
        
        Args:
            resource (Resource): The resource to be assigned
        """
        self.assigned_resources.append(resource)

    def release_resource(self, resource: 'Resource'):
        """
        Release a resource from this incident.
        
        Args:
            resource (Resource): The resource to be released
        """
        if resource in self.assigned_resources:
            self.assigned_resources.remove(resource)

    def is_allocated(self) -> bool:
        """
        Check if all required resources have been allocated.
        
        Returns:
            bool: True if all required resources are allocated, False otherwise
        """
        required_counts = {r[0]: r[1] for r in self.required_resources}
        allocated_counts = {}
        for resource in self.assigned_resources:
            allocated_counts[resource.type] = allocated_counts.get(resource.type, 0) + 1
        
        return all(
            allocated_counts.get(r_type, 0) >= count
            for r_type, count in required_counts.items()
        )

    def update_status(self, new_status: str):
        self.status = new_status

    def update_priority(self, new_priority: str):
        """
        Update the priority level of this incident.
        
        Args:
            new_priority (str): New priority level (High/Medium/Low)
            
        Raises:
            ValueError: If the new priority is invalid
        """
        if new_priority not in self.VALID_PRIORITIES:
            raise ValueError("Priority must be High, Medium, or Low")
        self.priority = new_priority

    def get_status(self) -> str:
        """
        Get the current status of the incident.
        
        Returns:
            str: One of:
                - "Assigned" (all required resources allocated)
                - "Partially Assigned" (some resources allocated)
                - "Pending" (no resources allocated)
        """
        if self.is_allocated():
            return "Assigned"
        elif self.assigned_resources:
            return "Partially Assigned"
        return "Pending"

    def __lt__(self, other):
        """
        Compare incidents based on priority for sorting.
        
        Args:
            other (Incident): The incident to compare against
            
        Returns:
            bool: True if this incident has lower priority than the other
        """
        priority_order = {"High": 3, "Medium": 2, "Low": 1}
        return priority_order[self.priority] < priority_order[other.priority]