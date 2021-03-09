import setuptools

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

with open("requirements.txt") as f:
    INSTALL_REQUIRES = f.read().strip().split("\n")

setuptools.setup(
    name="carst",
    version="2.0.0a1",
    author="The CARST Developers",
    author_email="wz278@cornell.edu",
    maintainer="Whyjay Zheng",
    maintainer_email="wz278@cornell.edu",
    description="Cryoshpere And Remote Sensing Toolkit",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/whyjz/CARST.git",
    license="MIT",
    packages=setuptools.find_packages(exclude=["*extra"]),
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3",
    scripts=["bin/dhdt.py", "bin/featuretrack.py"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: Physics"
    ],
)
