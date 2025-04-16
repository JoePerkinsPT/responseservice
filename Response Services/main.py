from incident import Incident
from resource import Resource
from allocator import Allocator
from display import DisplayManager
from session_storage import SessionStorage

def parse_resources_input(input_str):
    """Parse required resources, e.g., 'Ambulance:2,FireTruck:1'."""
    result = []
    try:
        for item in input_str.split(","):
            type_count = item.split(":")
            type_name = type_count[0].strip()
            count = int(type_count[1]) if len(type_count) > 1 else 1
            if count < 1:
                raise ValueError
            result.append((type_name, count))
        return result
    except (ValueError, IndexError):
        raise ValueError("Invalid format. Use 'Type:Count,Type:Count'")

def main():
    allocator = Allocator()
    display = DisplayManager()
    storage = SessionStorage()
    used_ids = set()

    # Try to load most recent session
    try:
        timestamp = storage.load_state(allocator)
        print(f"Loaded previous session from {timestamp}")
        # Update used_ids from loaded state
        used_ids.update(inc.id for inc in allocator.get_incidents())
        used_ids.update(res.id for res in allocator.resources)
    except ValueError:
        print("No previous session found. Starting fresh.")

    while True:
        print("\nEmergency Resource Allocation System")
        print("1. Add Incident")
        print("2. Add Resource")
        print("3. View Incidents")
        print("4. View Resources")
        print("5. Allocate Resources")
        print("6. Update Incident Priority")
        print("7. Save Session")
        print("8. Load Session")
        print("9. Exit")
        try:
            choice = input("Enter choice (1-9): ")
            if choice == "1":
                id = input("Incident ID: ")
                if id in used_ids:
                    raise ValueError("ID already used")
                location = input("Location (e.g., Zone 1): ")
                type = input("Type (e.g., Fire): ")
                priority = input("Priority (High/Medium/Low): ")
                resources = parse_resources_input(
                    input("Required resources (e.g., Ambulance:2,FireTruck:1): "))
                incident = Incident(id, location, type, priority, resources)
                allocator.add_incident(incident)
                used_ids.add(id)
                print("Incident added.")
                # Auto-save after adding incident
                storage.save_state(allocator)

            elif choice == "2":
                id = input("Resource ID: ")
                if id in used_ids:
                    raise ValueError("ID already used")
                type = input("Type (e.g., Ambulance): ")
                location = input("Location (e.g., Zone 1): ")
                resource = Resource(id, type, location)
                allocator.add_resource(resource)
                used_ids.add(id)
                print("Resource added.")
                # Auto-save after adding resource
                storage.save_state(allocator)

            elif choice == "3":
                display.display_incidents(allocator)

            elif choice == "4":
                display.display_resources(allocator)

            elif choice == "5":
                allocator.allocate_resources()
                print("Resources allocated.")
                display.display_incidents(allocator)
                # Auto-save after allocation
                storage.save_state(allocator)

            elif choice == "6":
                id = input("Incident ID: ")
                priority = input("New Priority (High/Medium/Low): ")
                allocator.update_incident_priority(id, priority)
                print("Priority updated.")
                display.display_incidents(allocator)
                # Auto-save after priority update
                storage.save_state(allocator)

            elif choice == "7":
                filepath = storage.save_state(allocator)
                print(f"Session saved to {filepath}")

            elif choice == "8":
                sessions = storage.list_sessions()
                if not sessions:
                    print("No saved sessions found.")
                    continue
                print("\nAvailable sessions:")
                for i, (filename, timestamp) in enumerate(sessions, 1):
                    print(f"{i}. {timestamp}")
                choice = input("Enter session number to load (or press Enter for most recent): ")
                if choice.strip():
                    try:
                        session_file = sessions[int(choice)-1][0]
                        timestamp = storage.load_state(allocator, session_file)
                        print(f"Loaded session from {timestamp}")
                        # Update used_ids from loaded state
                        used_ids.clear()
                        used_ids.update(inc.id for inc in allocator.get_incidents())
                        used_ids.update(res.id for res in allocator.resources)
                    except (ValueError, IndexError):
                        print("Invalid selection.")
                else:
                    timestamp = storage.load_state(allocator)
                    print(f"Loaded most recent session from {timestamp}")

            elif choice == "9":
                # Auto-save before exit
                storage.save_state(allocator)
                print("Session saved. Exiting...")
                break

            else:
                print("Invalid choice. Try again.")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
