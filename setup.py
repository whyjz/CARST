import setuptools

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

with open("requirements.txt") as f:
    INSTALL_REQUIRES = f.read().strip().split("\n")

setuptools.setup(
    name="carst",
    author="The CARST Developers",
    author_email="wz278@cornell.edu",
    maintainer="Whyjay Zheng",
    maintainer_email="wz278@cornell.edu",
    description="Cryoshpere And Remote Sensing Toolkit",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/whyjz/CARST.git",
    license="MIT",
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3",
    scripts=["bin/dhdt.py", "bin/featuretrack.py"]
)
