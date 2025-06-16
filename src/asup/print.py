from html2image import Html2Image
import jinja2

hti = Html2Image(size=(1109, 696))
templateLoader = jinja2.FileSystemLoader(searchpath=".")
templateEnv = jinja2.Environment(loader=templateLoader)

TEMPLATE_FILE = "template.html"
template = templateEnv.get_template(TEMPLATE_FILE)

templateVars = {
    "header": "[DEV-276] Add CSP HTTP headers",
    "content": "Add CSP (content security policy) headers to nginx. Limit the origins from which javascript can be loaded to prevent XSS attacks. A list of origins has to be determined and properly tested",
    "footer": "•••",
}

outputText = template.render(templateVars)
with open("out.html", "w+") as f:
    f.write(outputText)

print(outputText)

hti.screenshot(
    url="file:///home/vhronec/PycharmProjects/asup/src/asup/out.html",
    save_as="test.png",
)
