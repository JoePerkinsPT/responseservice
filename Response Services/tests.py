import unittest
from incident import Incident
from resource import Resource
from dispatcher import Dispatcher

class TestEmergencySystem(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.dispatcher = Dispatcher()
        self.incident1 = Incident("1", "Zone 1", "Fire", "High", ["Ambulance"])
        self.incident2 = Incident("2", "Zone 2", "Crash", "Medium", ["Ambulance"])
        self.resource1 = Resource("A1", "Ambulance", "Zone 1")
        self.resource2 = Resource("A2", "Ambulance", "Zone 2")

    def test_incident_creation(self):
        """Test incident initialization."""
        self.assertEqual(self.incident1.id, "1")
        self.assertEqual(self.incident1.priority, "High")
        self.assertEqual(self.incident1.status, "Pending")

    def test_resource_assign(self):
        """Test resource assignment to an incident."""
        self.dispatcher.add_incident(self.incident1)
        self.dispatcher.add_resource(self.resource1)
        self.resource1.assign(self.incident1)
        self.assertFalse(self.resource1.is_available)
        self.assertEqual(self.incident1.status, "Assigned")
        self.assertIn(self.resource1, self.incident1.assigned_resources)

    def test_allocation(self):
        """Test resource allocation to incidents."""
        self.dispatcher.add_incident(self.incident1)
        self.dispatcher.add_incident(self.incident2)
        self.dispatcher.add_resource(self.resource1)
        self.dispatcher.allocate_resources()
        self.assertFalse(self.resource1.is_available)
        self.assertEqual(self.incident1.status, "Assigned")

    def test_reallocation(self):
        """Test resource reallocation for high-priority incident."""
        self.dispatcher.add_incident(self.incident2)
        self.dispatcher.add_resource(self.resource2)
        self.dispatcher.allocate_resources()  # Assign to medium-priority
        self.assertFalse(self.resource2.is_available)
        self.dispatcher.add_incident(self.incident1)
        self.dispatcher.allocate_resources()  # Reallocate to high-priority
        self.assertEqual(self.incident1.status, "Assigned")
        self.assertEqual(self.incident2.status, "Pending")

if __name__ == "__main__":
    unittest.main()
