import json
from typing import List, Optional
from textual.widgets import Label, ListItem, Tree


TASK_JSON_PATH = "tasks.json"


class Task(dict):
    def __init__(self, name: str, description: str = "", completed: bool = False):
        self.type = "task"
        self.name = name
        self.description = description
        self.completed = completed
        dict.__init__(
            self,
            name=name,
            type=self.type,
            description=description,
            completed=completed,
        )

    def __repr__(self):
        return f"Task(name={self.name}, description={self.description}, completed={self.completed})"

    # def get_list_item(self) -> ListItem:
    #     return ListItem(Label(f"[T] {self.name}"))


class TaskList(dict):
    def __init__(self, name: str, tasks: Optional[List[Task]] = None) -> None:
        self.type = "list"
        self.name = name
        if tasks is None:
            tasks = []
        self.tasks = tasks
        dict.__init__(self, name=name, type=self.type, tasks=tasks)

    def __repr__(self):
        return f"TaskList(name={self.name}, tasks={self.tasks})"

    # def get_list_item(self) -> ListItem:
    #     return ListItem(Label(f"[L] {self.name}"))

    def get_depth(self) -> int:
        return 1 + max(
            (
                tasklist.get_depth() if tasklist["type"] == "list" else 0
                for tasklist in self.tasks
            ),
            default=0,
        )


def read_json(path: str) -> List:
    with open(path) as f:
        data = json.load(f)
    return parse_tree(data)


def parse_tree(data):
    l = []
    for item in data:
        if item["type"] == "task":
            l.append(Task(item["name"], item["description"], item["completed"]))
        elif item["type"] == "list":
            l.append(TaskList(item["name"], parse_tree(item["items"])))
    return l


def get_root():
    return TaskList("Tasks", read_json(TASK_JSON_PATH))


def get_entire_tree():
    tree = Tree("Tasks", id="task_tree")

    def handle_node(item, node):
        if item["type"] == "list":
            new_node = node.add(item["name"], expand=True, data=item)
            for subtask in item["tasks"]:
                handle_node(subtask, new_node)
        else:
            node.add_leaf(item["name"], data=item)

    for task in get_root()["tasks"]:
        handle_node(task, tree.root)
    return tree


def walk_tree(tree: Tree):
    yield tree.root if isinstance(tree, Tree) else tree
    root = tree.root if isinstance(tree, Tree) else tree
    for node in root.children:
        if node.children:
            yield from walk_tree(node)
        else:
            yield node


def serialize_tree(tree: Tree) -> List[dict]:
    def serialize_node(node):
        if node.children:
            return {
                "name": str(node.label),
                "type": "list",
                "items": [serialize_node(child) for child in node.children],
            }
        else:
            return {
                "name": str(node.label),
                "type": "task",
                "description": node.data.get("description", ""),
                "completed": node.data.get("completed", False),
            }

    return [serialize_node(tree.root)]


def write_json(data: List[dict], path: str = TASK_JSON_PATH) -> None:
    with open(path, "w+") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    tree = get_entire_tree()
    for it in walk_tree(tree):
        print(it.label, it.data)
