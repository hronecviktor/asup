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
from tasks import get_entire_tree, walk_tree


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
    current_node = None

    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        with HorizontalScroll(can_focus=False):
            self.tree = get_entire_tree()
            yield self.tree
            self.editor = TextArea(id="editor", show_line_numbers=True)
            yield self.editor
        yield Footer(id="Footer")

    def on_tree_node_highlighted(self, event) -> None:
        self.current_node = event.node
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
        node = self.current_node
        if node:
            node.set_label(self.editor.text.splitlines()[0])
            if node.data.type == "task":
                desc = self.editor.text.splitlines()[1:]
                for line in desc:
                    if line.strip() == "":
                        desc.remove(line)
                node.data["description"] = "\n".join(desc)
                print(f"Updated node {node.label} with new description.")
        else:
            print("No node found for the editor.")


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
