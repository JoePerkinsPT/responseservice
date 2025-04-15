from incident import Incident
from resource import Resource
from allocator import Allocator
from display import DisplayManager

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
    used_ids = set()

    while True:
        print("\nEmergency Resource Allocation System")
        print("1. Add Incident")
        print("2. Add Resource")
        print("3. View Incidents")
        print("4. View Resources")
        print("5. Allocate Resources")
        print("6. Update Incident Priority")
        print("7. Exit")
        try:
            choice = input("Enter choice (1-7): ")
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

            elif choice == "3":
                display.display_incidents(allocator)

            elif choice == "4":
                display.display_resources(allocator)

            elif choice == "5":
                allocator.allocate_resources()
                print("Resources allocated.")
                display.display_incidents(allocator)

            elif choice == "6":
                id = input("Incident ID: ")
                priority = input("New Priority (High/Medium/Low): ")
                allocator.update_incident_priority(id, priority)
                print("Priority updated.")
                display.display_incidents(allocator)

            elif choice == "7":
                print("Exiting...")
                break

            else:
                print("Invalid choice. Try again.")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
