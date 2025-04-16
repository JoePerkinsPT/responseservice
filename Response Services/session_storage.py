import json
from datetime import datetime
import os

class SessionStorage:
    """Handles saving and loading of system states."""
    
    def __init__(self, storage_dir="sessions"):
        """Initialize storage with directory for session files."""
        self.storage_dir = storage_dir
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

    def save_state(self, allocator):
        """
        Save current system state to a JSON file.
        
        Args:
            allocator: Allocator instance containing current state
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_{timestamp}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        state = {
            "incidents": [
                {
                    "id": incident.id,
                    "location": incident.location,
                    "type": incident.type,
                    "priority": incident.priority,
                    "status": incident.status,
                    "required_resources": incident.required_resources
                }
                for incident in allocator.get_incidents()
            ],
            "resources": [
                {
                    "id": resource.id,
                    "type": resource.type,
                    "location": resource.location,
                    "assigned_to": resource.assigned_to.id if resource.assigned_to else None
                }
                for resource in allocator.resources
            ],
            "timestamp": timestamp
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=4)
        
        # Keep only last 5 sessions
        self._cleanup_old_sessions()
        
        return filepath

    def load_state(self, allocator, session_file=None):
        """
        Load system state from a JSON file.
        
        Args:
            allocator: Allocator instance to restore state to
            session_file: Optional specific session file to load
        """
        if session_file is None:
            # Get most recent session file
            files = self._get_session_files()
            if not files:
                raise ValueError("No saved sessions found")
            session_file = files[-1]
        
        filepath = os.path.join(self.storage_dir, session_file)
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        # Clear current state
        allocator.incidents.clear()
        allocator.resources.clear()
        
        # Load incidents first
        from incident import Incident
        for inc_data in state["incidents"]:
            incident = Incident(
                inc_data["id"],
                inc_data["location"],
                inc_data["type"],
                inc_data["priority"],
                inc_data["required_resources"]
            )
            incident.status = inc_data["status"]
            allocator.add_incident(incident)
        
        # Then load resources and their assignments
        from resource import Resource
        for res_data in state["resources"]:
            resource = Resource(
                res_data["id"],
                res_data["type"],
                res_data["location"]
            )
            if res_data["assigned_to"]:
                # Find the incident this resource was assigned to
                for incident in allocator.get_incidents():
                    if incident.id == res_data["assigned_to"]:
                        resource.assign(incident)
                        break
            allocator.add_resource(resource)
        
        return state["timestamp"]

    def list_sessions(self):
        """Return list of available session files with timestamps."""
        files = self._get_session_files()
        return [(f, f.replace("session_", "").replace(".json", ""))
                for f in files]

    def _get_session_files(self):
        """Get sorted list of session files."""
        files = [f for f in os.listdir(self.storage_dir)
                if f.startswith("session_") and f.endswith(".json")]
        return sorted(files)

    def _cleanup_old_sessions(self, keep=5):
        """Remove all but the most recent session files."""
        files = self._get_session_files()
        if len(files) > keep:
            for old_file in files[:-keep]:
                os.remove(os.path.join(self.storage_dir, old_file)) 