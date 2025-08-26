from setuptools import setup, find_packages, Extension


def readme():
  with open('README.md', 'r', encoding='utf-8') as f:
    return f.read()

setup(
    name="value-widgets",
    version="0.8.0",
    packages=find_packages(),
    long_description=readme(),
    package_data={
        "value_widgets": [
            "images/*.png",
            "hooks/*.py",
        ]
    },
    include_package_data=True,
    entry_points={
        'pyinstaller40': [
            'hook-dirs = value_widgets:_get_hook_dirs',
        ],
    },
    install_requires=[
        "PyQt6",
        "numpy"
    ],
    
    author="Ovsyannikov Andrey",
    author_email="andsup108@gmail.com",
    keywords="widgets",
    python_requires='>=3.11'
)
