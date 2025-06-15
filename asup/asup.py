from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, VerticalScroll
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Placeholder,
    Header,
    Footer,
    ListItem,
    ListView,
    Label,
    TextArea,
)
from textual.app import App, ComposeResult
from tasks import get_entire_tree, walk_tree, serialize_tree, write_json, Task, TaskList


# class Header(Placeholder):
#     DEFAULT_CSS = """
#     Header {
#         height: 3;
#         dock: top;
#     }
#     """
#
#
# class Footer(Placeholder):
#     DEFAULT_CSS = """
#     Footer {
#         height: 3;
#         dock: bottom;
#     }
#     """


# class ListItem(Placeholder):
#     DEFAULT_CSS = """
#     ListItem {
#         height: 5;
#         width: 1fr;
#         border: tall $background;
#     }
#     """


# class Column(VerticalScroll):
#     DEFAULT_CSS = """
#     Column {
#         height: 1fr;
#         width: 1fr;
#         margin: 0 2;
#     }
#     """
#     selected = reactive(0)
#     all_items = []
#
#     def compose(self) -> ComposeResult:
#         for tweet_no in range(1, 20):
#             it = ListItem(id=f"Tweet{tweet_no}")
#             self.all_items.append(it)
#             yield it
#         self.selected = 0
#
#     def watch_selected(self, selected: int) -> None:
#         if 0 <= selected < len(self.all_items):
#             self.all_items[selected].focus()
#         else:
#             self.selected = 0
#             self.all_items[0].focus()
#
#
# class Column(VerticalScroll):
#     DEFAULT_CSS = """
#     Column {
#         height: 1fr;
#         width: 1fr;
#         margin: 0 2;
#     }
#     """
#
#     def compose(self) -> ComposeResult:
#         for tweet_no in range(1, 20):
#             it = ListItem(id=f"Tweet{tweet_no}")
#             self.all_items.append(it)
#             yield it
#         self.selected = 0


class BaseScreen(Screen):
    tree = None
    editor = None
    selected_node = None

    BINDINGS = [
        ("c", "create", "Create task"),
        ("x", "create_list", "Create List"),
        ("d", "delete", "Delete task"),
    ]

    def action_create(self) -> None:
        if self.selected_node:
            if self.selected_node.allow_expand:
                new_node = self.selected_node.add_leaf(
                    "New Task",
                    data=Task(
                        name="New Task", description="Fill me in", completed=False
                    ),
                )
            else:
                new_node = self.selected_node.parent.add_leaf(
                    "New Task",
                    data=Task(
                        name="New Task", description="Fill me in", completed=False
                    ),
                )
            self.tree.refresh()
            self.tree.focus(new_node)
            self.editor.text = f"{new_node.label}\n\n{new_node.data.description}"
            self.selected_node = new_node
            print(f"Created new node: {new_node.label}")
        else:
            print("No node selected to create a new task under.")

    def action_create_list(self) -> None:
        if self.selected_node:
            if self.selected_node.allow_expand:
                new_node = self.selected_node.add(
                    "New List",
                    expand=True,
                    data=TaskList(name="New List"),
                )
            else:
                new_node = self.selected_node.parent.add(
                    "New List",
                    expand=True,
                    data=TaskList(name="New List"),
                )
            self.tree.refresh()
            self.tree.focus(new_node)
            self.editor.text = f"{new_node.label}\n\n"
            self.selected_node = new_node
            print(f"Created new list: {new_node.label}")
        else:
            print("No node selected to create a new list under.")

    def action_delete(self) -> None:
        if self.selected_node and self.selected_node != self.tree.root:
            parent = self.selected_node.parent
            if parent:
                node_to_select = (
                    self.selected_node.previous_sibling
                    or self.selected_node.next_sibling
                    or parent
                )
                self.selected_node.remove()
                self.tree.refresh()
                self.editor.text = ""
                print(f"Deleted node: {self.selected_node.label}")
                self.tree.select_node(node_to_select)
            else:
                print("Cannot delete the root node.")
        else:
            print("No node selected or trying to delete the root node.")

    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        with HorizontalScroll(can_focus=False):
            self.tree = get_entire_tree()
            yield self.tree
            self.editor = TextArea(id="editor", show_line_numbers=True)
            yield self.editor
        yield Footer(id="Footer")

    def on_tree_node_highlighted(self, event) -> None:
        self.selected_node = event.node
        node = event.node
        print(f"HIGHLIGHTED: {node}")
        if node == self.tree.root:
            self.editor.disabled = True
            self.editor.text = "Root node selected, nothing to edit."
        else:
            self.editor.disabled = False
            if node.data.type == "task":
                self.editor.text = f"{node.label}\n\n{node.data['description']}"
            else:
                self.editor.text = f"{node.label}"
        # for n in walk_tree(self.tree):
        #     if n == node:
        #         n.set_label(f"Selected: {n.label}")
        #     else:
        #         if str(n.label).startswith("Selected: "):
        #             n.set_label(str(n.label).replace("Selected: ", ""))

    def on_text_area_changed(self):
        if self.editor.disabled:
            return
        node = self.selected_node
        if node:
            label = self.editor.text.splitlines()[0]
            node.set_label(label)
            self.selected_node.data.name = label
            if node.data.type == "task":
                desc = self.editor.text.splitlines()[1:]
                for line in desc:
                    if line.strip() == "":
                        desc.remove(line)
                node.data["description"] = "\n".join(desc)
                print(f"Updated node {node.label} with new description.")
        else:
            print("No node found for the editor.")
        # TODO turn on again
        print(serialize_tree(self.tree))
        # write_json(serialize_tree(self.tree)[0]["items"])


class Asup(App):
    AUTO_FOCUS = "#task_tree"
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def on_ready(self) -> None:
        self.push_screen(BaseScreen())

    def action_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = Asup()
    app.run()
