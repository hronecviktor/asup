from html2image import Html2Image
import jinja2

from asup.tasks import Task


def print_task(task: Task):
    hti = Html2Image(size=(1109, 696))
    templateLoader = jinja2.FileSystemLoader(searchpath=".")
    templateEnv = jinja2.Environment(loader=templateLoader)

    TEMPLATE_FILE = "template.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    templateVars = {
        "header": task.name,
        "content": task.description,
        "footer": "•" * task.priority,
    }

    outputText = template.render(templateVars)
    with open("out.html", "w+") as f:
        f.write(outputText)

    print(outputText)

    hti.screenshot(
        url="file:///home/vhronec/PycharmProjects/asup/src/asup/out.html",
        save_as="test.png",
    )
