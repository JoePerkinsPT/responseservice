from abc import ABC, abstractmethod
from typing import Optional
from incident import Incident

class ResourceInterface(ABC):
    """
    Abstract interface defining the contract for resource management.
    
    This interface ensures that all resource implementations provide
    the necessary methods for assignment and management.
    """
    @abstractmethod
    def assign(self, incident):
        """Assign this resource to an incident."""
        pass

class Resource(ResourceInterface):
    """
    Represents an emergency response resource that can be allocated to incidents.
    
    This class manages:
    - Resource details (ID, type, location)
    - Assignment status and tracking
    - Availability checking
    - Resource release and reassignment
    
    The class implements validation for all inputs and provides
    methods for incident assignment and status tracking.
    """
    def __init__(self, id: str, type: str, location: str):
        """
        Initialize a new resource.
        
        Args:
            id (str): Unique identifier for the resource
            type (str): Type of resource (e.g., "Ambulance", "FireTruck")
            location (str): Current location of the resource (e.g., "Zone 1")
            
        Raises:
            ValueError: If any input validation fails
        """
        self.id = id
        self.type = type
        self.location = location
        self.assigned_to: Optional['Incident'] = None
        self._validate_inputs()

    @property
    def is_available(self) -> bool:
        """
        Check if the resource is currently available for assignment.
        
        Returns:
            bool: True if the resource is not assigned to any incident
        """
        return self.assigned_to is None

    def _validate_inputs(self):
        """
        Validate all input parameters for the resource.
        
        Raises:
            ValueError: If any required field is empty
        """
        if not self.id:
            raise ValueError("Resource ID cannot be empty")
        if not self.type:
            raise ValueError("Resource type cannot be empty")
        if not self.location:
            raise ValueError("Location cannot be empty")

    def assign(self, incident: 'Incident'):
        """
        Assign this resource to an incident and update statuses.
        
        Args:
            incident (Incident): The incident to assign to
            
        Raises:
            ValueError: If the resource is already assigned
        """
        if not self.is_available:
            raise ValueError("Resource already assigned")
        if self in incident.assigned_resources:
            raise ValueError("Resource already assigned to this incident")
        self.assigned_to = incident
        incident.assigned_resources.append(self)
        # Check if all required resources are now allocated
        required_counts = {r[0]: r[1] for r in incident.required_resources}
        allocated_counts = {}
        for resource in incident.assigned_resources:
            allocated_counts[resource.type] = allocated_counts.get(resource.type, 0) + 1
        if all(allocated_counts.get(r_type, 0) >= count for r_type, count in required_counts.items()):
            incident.update_status("Assigned")

    def release(self):
        """
        Release the resource from its current assignment.
        
        This method:
        1. Removes the resource from its assigned incident
        2. Updates the incident's status if necessary
        3. Marks the resource as available
        """
        if self.assigned_to:
            old_incident = self.assigned_to
            old_incident.assigned_resources.remove(self)
            # Check if the incident still has enough resources
            required_counts = {r[0]: r[1] for r in old_incident.required_resources}
            allocated_counts = {}
            for resource in old_incident.assigned_resources:
                allocated_counts[resource.type] = allocated_counts.get(resource.type, 0) + 1
            if not all(allocated_counts.get(r_type, 0) >= count for r_type, count in required_counts.items()):
                old_incident.update_status("Pending")
            self.assigned_to = None

    def __str__(self) -> str:
        """
        Get a string representation of the resource.
        
        Returns:
            str: A formatted string showing the resource's details and status
        """
        status = "Available" if self.is_available else f"Assigned to {self.assigned_to.id}"
        return f"{self.type} {self.id} at {self.location} - {status}"