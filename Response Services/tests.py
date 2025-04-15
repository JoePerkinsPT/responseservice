import unittest
import pytest
from incident import Incident
from resource import Resource
from allocator import Allocator

class TestEmergencySystem(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.allocator = Allocator()
        self.incident1 = Incident("1", "Zone 1", "Fire", "High", [("Ambulance", 2)])
        self.incident2 = Incident("2", "Zone 2", "Crash", "Medium", [("Ambulance", 1)])
        self.resource1 = Resource("A1", "Ambulance", "Zone 1")
        self.resource2 = Resource("A2", "Ambulance", "Zone 2")
        self.resource3 = Resource("A3", "Ambulance", "Zone 1")

    def test_incident_validation(self):
        """Test incident input validation."""
        with self.assertRaises(ValueError):
            Incident("1", "Zone 1", "Fire", "Invalid", [("Ambulance", 1)])
        with self.assertRaises(ValueError):
            Incident("", "Zone 1", "Fire", "High", [("Ambulance", 1)])

    def test_resource_assign(self):
        """Test resource assignment to an incident."""
        self.allocator.add_incident(self.incident1)
        self.allocator.add_resource(self.resource1)
        self.resource1.assign(self.incident1)
        self.assertFalse(self.resource1.is_available)
        self.assertEqual(self.incident1.status, "Pending")  # Needs 2 ambulances
        self.resource3.assign(self.incident1)
        self.assertEqual(self.incident1.status, "Assigned")

    def test_proximity_allocation(self):
        """Test resource allocation prefers closer resources."""
        # Create an incident that needs only one ambulance
        incident = Incident("3", "Zone 1", "Minor", "Medium", [("Ambulance", 1)])
        self.allocator.add_incident(incident)
        self.allocator.add_resource(self.resource1)  # Zone 1
        self.allocator.add_resource(self.resource2)  # Zone 2
        self.allocator.allocate_resources()
        self.assertFalse(self.resource1.is_available)  # Closer resource should be used
        self.assertTrue(self.resource2.is_available)  # Farther resource should not be used
        self.assertEqual(incident.status, "Assigned")

    def test_reallocation(self):
        """Test resource reallocation for high-priority incident."""
        # Add medium priority incident first
        self.allocator.add_incident(self.incident2)  # Medium priority, needs 1 ambulance
        self.allocator.add_resource(self.resource2)
        self.allocator.allocate_resources()
        
        # Verify initial allocation
        self.assertFalse(self.resource2.is_available)
        self.assertEqual(self.incident2.status, "Assigned")
        self.assertIn(self.resource2, self.incident2.assigned_resources)

        # Add high priority incident and its resource
        self.allocator.add_incident(self.incident1)  # High priority, needs 2 ambulances
        self.allocator.add_resource(self.resource1)
        
        # Allocate resources - this should trigger reallocation internally
        self.allocator.allocate_resources()

        # Verify reallocation
        self.assertIn(self.resource2, self.incident1.assigned_resources)
        self.assertIn(self.resource1, self.incident1.assigned_resources)
        self.assertEqual(self.incident1.status, "Assigned")
        self.assertEqual(self.incident2.status, "Pending")

    def test_no_resources(self):
        """Test behavior when no resources are available."""
        self.allocator.add_incident(self.incident1)
        self.allocator.allocate_resources()
        self.assertEqual(self.incident1.status, "Pending")

    def test_logging(self):
        """Test logging of allocation decisions."""
        import os
        self.allocator.add_incident(self.incident1)
        self.assertTrue(os.path.exists("allocation_log.txt"))

    def test_heap_priority_update(self):
        self.allocator.add_incident(self.incident1)  # High
        self.allocator.add_incident(self.incident2)  # Medium
        self.allocator.update_incident_priority("2", "High")
        self.allocator.add_resource(self.resource1)
        self.allocator.allocate_resources()
        self.assertFalse(self.resource1.is_available)
        self.assertEqual(self.incident1.assigned_resources, [self.resource1])

    # New Test Case
    def test_multiple_resources_insufficient(self):
        """Test allocation when insufficient resources are available."""
        # Setup: High-priority incident needs 3 ambulances, medium needs 1
        incident_high = Incident("3", "Zone 1", "Explosion", "High", [("Ambulance", 3)])
        incident_med = Incident("4", "Zone 1", "Crash", "Medium", [("Ambulance", 1)])
        self.allocator.add_incident(incident_high)
        self.allocator.add_incident(incident_med)
        self.allocator.add_resource(self.resource1)  # Zone 1
        self.allocator.add_resource(self.resource3)  # Zone 1
        
        # Action: Allocate resources
        self.allocator.allocate_resources()
        
        # Assertions
        # High-priority gets both ambulances but remains Pending (needs 3)
        self.assertEqual(incident_high.status, "Pending")
        self.assertEqual(len(incident_high.assigned_resources), 2)
        self.assertFalse(self.resource1.is_available)
        self.assertFalse(self.resource3.is_available)
        # Medium-priority gets none
        self.assertEqual(incident_med.status, "Pending")
        self.assertEqual(len(incident_med.assigned_resources), 0)

        # Add a third ambulance and reallocate
        resource4 = Resource("A4", "Ambulance", "Zone 1")
        self.allocator.add_resource(resource4)
        self.allocator.allocate_resources()
        
        # High-priority now fully assigned
        self.assertEqual(incident_high.status, "Assigned")
        self.assertEqual(len(incident_high.assigned_resources), 3)
        self.assertFalse(resource4.is_available)
        # Medium-priority still pending
        self.assertEqual(incident_med.status, "Pending")

if __name__ == "__main__":
    pytest.main(["-v", __file__])