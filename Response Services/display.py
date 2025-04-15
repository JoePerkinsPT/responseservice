class DisplayManager:
    """Class to handle console output."""
    @staticmethod
    def display_incidents(allocator):
        """Display all incidents in the system."""
        print("\nIncidents:")
        print(f"{'ID':<5} {'Location':<10} {'Type':<10} {'Priority':<10} {'Status':<10}")
        for incident in allocator.get_incidents():
            print(f"{incident.id:<5} {incident.location:<10} {incident.type:<10} {incident.priority:<10} {incident.status:<10}")

    @staticmethod
    def display_resources(allocator):
        """Display all resources in the system."""
        print("\nResources:")
        print(f"{'ID':<5} {'Type':<10} {'Location':<10} {'Status':<10}")
        for resource in allocator.resources:
            status = "Available" if resource.is_available else f"Assigned to {resource.assigned_to.id}"
            print(f"{resource.id:<5} {resource.type:<10} {resource.location:<10} {status:<10}")