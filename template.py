from jinja2 import Environment, FileSystemLoader
import os.path


def bond_render(info):
    path = '{}/templates/'.format(os.path.dirname(__file__))
    loader = FileSystemLoader(path)
    env = Environment(loader=loader)
    template = env.get_template('bond.html')
    content = template.render(info=info)
    return content


def index_render(info):
    path = '{}/templates/'.format(os.path.dirname(__file__))
    loader = FileSystemLoader(path)
    env = Environment(loader=loader)
    template = env.get_template('index.html')
    content = template.render(info=info)
    return content
