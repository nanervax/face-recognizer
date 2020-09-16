import os
import importlib.util
from importlib.machinery import SourceFileLoader

from setuptools import setup, find_packages
from pkg_resources import parse_requirements

module_name = "face_recognizer"

loader = SourceFileLoader(module_name, os.path.join(module_name, "__init__.py"))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


def load_requirements(fname):
    requirements = []
    with open(fname, 'r') as fp:
        for req in parse_requirements(fp.read()):
            extras = '[{}]'.format(','.join(req.extras)) if req.extras else ''
            requirements.append(
                '{}{}{}'.format(req.name, extras, req.specifier)
            )
    return requirements


setup(
    name=module_name.replace("_", "-"),
    version=module.__version__,
    author=module.__author__,
    packages=find_packages(),
    long_description=open("README.md").read(),
    python_requires=">=3.7",
    install_requires=load_requirements("requirements.txt"),
    extras_require={'dev': load_requirements("requirements.dev.txt")},
    include_package_data=True
)
