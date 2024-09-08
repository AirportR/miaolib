import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="miaospeedlib",
    version="0.0.1",
    author="airportr",
    url='xxx',
    author_email="xxx",
    description="xxx",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        'aiohttp>=3.9.2',
        'async_timeout>=4.0.2',
        'loguru>=0.6.0'
    ],
    python_requires=">=3.9",
)