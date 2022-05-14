from setuptools import setup, find_packages

# with open("requirements.txt") as f:
#     requirements = f.readlines()
requirements = []


setup(
    name="grantme",
    version="0.1.0",
    author="Chuzhe Tang",
    author_email="t.chuzhe@qq.com",
    # url="https://github.com/Vibhu-Agarwal/vibhu4gfg",
    description="Machine access control utility.",
    long_description=(
        'This is a utility for "granting" exclusive/shared machine access to users.'
    ),
    long_description_content_type="text/markdown",
    # license="MIT",
    packages=find_packages(),
    entry_points={"console_scripts": ["grantme = grantme.main:main"]},
    classifiers=(
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    # keywords="",
    install_requires=requirements,
    zip_safe=False,
)
