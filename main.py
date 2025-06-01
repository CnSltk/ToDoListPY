import json
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)  # auto-reset colors after each print


class InvalidDateError(Exception):
    pass

class InvalidPriorityError(Exception):
    pass

class TaskNotFoundError(Exception):
    pass

class Task:
    def __init__(self, description, due_date, priority, tags=None, completed=False):
        try:
            self.description = description
            self.due_date = datetime.strptime(due_date, "%Y-%m-%d")
            self.priority = priority.capitalize()
            if self.priority not in ["High", "Medium", "Low"]:
                raise InvalidPriorityError("Priority must be High, Medium, or Low.")
            self.completed = completed
            self.tags = tags or []
        except ValueError:
            raise InvalidDateError("Date must be in YYYY-MM-DD format.")

    def to_dict(self):
        return {
            "description": self.description,
            "due_date": self.due_date.strftime("%Y-%m-%d"),
            "priority": self.priority,
            "completed": self.completed,
            "tags": self.tags
        }

    @staticmethod
    def from_dict(data):
        return Task(
            description=data["description"],
            due_date=data["due_date"],
            priority=data["priority"],
            completed=data.get("completed", False),
            tags=data.get("tags", [])
        )

    def __str__(self):
        color = {
            "High": Fore.RED,
            "Medium": Fore.YELLOW,
            "Low": Fore.GREEN
        }.get(self.priority, Style.RESET_ALL)
        status = "✅" if self.completed else "❌"
        tags_str = ", ".join(self.tags) if self.tags else "No tags"
        return f"{status} {color}{self.description}{Style.RESET_ALL} | Due: {self.due_date.date()} | Priority: {self.priority} | Tags: {tags_str}"


# --- ToDoList Class ---
class ToDoList:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, description):
        for task in self.tasks:
            if task.description == description:
                self.tasks.remove(task)
                return
        raise TaskNotFoundError(f"Task '{description}' not found.")

    def mark_completed(self, description):
        for task in self.tasks:
            if task.description == description:
                task.completed = True
                return
        raise TaskNotFoundError(f"Task '{description}' not found.")

    def list_tasks(self, filter_by=None, value=None):
        filtered = self.tasks
        if filter_by == "priority":
            filtered = [t for t in self.tasks if t.priority.lower() == value.lower()]
        elif filter_by == "due_date":
            date_obj = datetime.strptime(value, "%Y-%m-%d").date()
            filtered = [t for t in self.tasks if t.due_date.date() == date_obj]
        elif filter_by == "tag":
            filtered = [t for t in self.tasks if value.lower() in [tag.lower() for tag in t.tags]]
        elif filter_by == "keyword":
            filtered = [t for t in self.tasks if value.lower() in t.description.lower()]
        return filtered

    def save_to_file(self, filename="tasks.json"):
        with open(filename, "w") as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=4)

    def load_from_file(self, filename="tasks.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(task) for task in data]
        except FileNotFoundError:
            self.tasks = []


# --- CLI Interface ---
def main():
    todo = ToDoList()
    todo.load_from_file()

    menu = """
=== TO-DO LIST MENU ===
1. Add Task
2. List All Tasks
3. Filter Tasks by Priority
4. Filter Tasks by Due Date
5. Filter Tasks by Tag
6. Search Tasks by Keyword
7. Mark Task as Completed
8. Delete Task
9. Exit
"""

    while True:
        print(menu)
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                desc = input("Description: ").strip()
                date = input("Due date (YYYY-MM-DD): ").strip()
                priority = input("Priority (Low/Medium/High): ").strip()
                tags = input("Tags (comma-separated): ").strip().split(",")
                tags = [t.strip() for t in tags if t.strip()]
                task = Task(desc, date, priority, tags)
                todo.add_task(task)
                print(Fore.GREEN + "Task added.\n")

            elif choice == "2":
                tasks = todo.list_tasks()
                if not tasks:
                    print("No tasks found.")
                for task in tasks:
                    print(task)

            elif choice == "3":
                priority = input("Enter priority to filter (Low/Medium/High): ").strip()
                tasks = todo.list_tasks(filter_by="priority", value=priority)
                for task in tasks:
                    print(task)

            elif choice == "4":
                date = input("Enter due date (YYYY-MM-DD): ").strip()
                tasks = todo.list_tasks(filter_by="due_date", value=date)
                for task in tasks:
                    print(task)

            elif choice == "5":
                tag = input("Enter tag to filter: ").strip()
                tasks = todo.list_tasks(filter_by="tag", value=tag)
                for task in tasks:
                    print(task)

            elif choice == "6":
                keyword = input("Enter keyword to search: ").strip()
                tasks = todo.list_tasks(filter_by="keyword", value=keyword)
                for task in tasks:
                    print(task)

            elif choice == "7":
                desc = input("Enter task description to mark as completed: ").strip()
                todo.mark_completed(desc)
                print(Fore.GREEN + "Marked as completed.\n")

            elif choice == "8":
                desc = input("Enter task description to delete: ").strip()
                todo.remove_task(desc)
                print(Fore.RED + "Task deleted.\n")

            elif choice == "9":
                todo.save_to_file()
                print("Tasks saved. Goodbye!")
                break

            else:
                print(Fore.YELLOW + "Invalid option. Try again.")

        except (InvalidDateError, InvalidPriorityError, TaskNotFoundError) as e:
            print(Fore.RED + f"Error: {e}")

if __name__ == "__main__":
    main()
