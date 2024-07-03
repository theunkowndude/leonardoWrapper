from setuptools import setup, find_packages

setup(
    name="leonardoWrapper",
    version="1.1.0",
    author="the_unkown_dude, anditv21",
    author_email="zaima_max@proton.me",
    description="A wrapper for the leonardo.ai image generation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/theunkowndude/leonardoWrapper",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    python_requires=">=3.6",
)