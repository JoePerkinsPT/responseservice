from incident import Incident
from resource import Resource
from dispatcher import Dispatcher

def main():
    """Main function to run the console-based application."""
    dispatcher = Dispatcher()
    
    while True:
        print("\nEmergency Resource Allocation System")
        print("1. Add Incident")
        print("2. Add Resource")
        print("3. View Incidents")
        print("4. View Resources")
        print("5. Allocate Resources")
        print("6. Update Incident Priority")
        print("7. Exit")
        choice = input("Enter choice (1-7): ")

        if choice == "1":
            id = input("Incident ID: ")
            location = input("Location (e.g., Zone 1): ")
            type = input("Type (e.g., Fire): ")
            priority = input("Priority (High/Medium/Low): ")
            resources = input("Required resources (comma-separated, e.g., Ambulance): ").split(",")
            dispatcher.add_incident(Incident(id, location, type, priority, resources))
            print("Incident added.")

        elif choice == "2":
            id = input("Resource ID: ")
            type = input("Type (e.g., Ambulance): ")
            location = input("Location (e.g., Zone 1): ")
            dispatcher.add_resource(Resource(id, type, location))
            print("Resource added.")

        elif choice == "3":
            dispatcher.display_incidents()

        elif choice == "4":
            dispatcher.display_resources()

        elif choice == "5":
            dispatcher.allocate_resources()
            print("Resources allocated.")
            dispatcher.display_incidents()

        elif choice == "6":
            id = input("Incident ID: ")
            priority = input("New Priority (High/Medium/Low): ")
            dispatcher.update_incident_priority(id, priority)
            print("Priority updated.")
            dispatcher.display_incidents()

        elif choice == "7":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
