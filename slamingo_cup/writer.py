from fetcher import fetch_record_data
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = "templates/"
DOCS_DIR = "docs/"


def load_template(filename):
    environment = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    return environment.get_template(filename)


def run(filename, context):
    template = load_template(filename)
    with open(f"{DOCS_DIR}/{filename}", mode="w", encoding="utf-8") as f:
        f.write(template.render(context))


if __name__ == "__main__":
    run("index.html", {"records": fetch_record_data()})
