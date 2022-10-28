from setuptools import setup  # type: ignore

setup(
    name="dataclass-jsonable",
    version="0.0.13",
    author="hit9",
    author_email="hit9@icloud.com",
    description="Simple and flexible conversions between dataclasses and jsonable dictionaries.",
    license="BSD",
    keywords="dataclasses,json,jsonable",
    url="https://github.com/hit9/dataclass-jsonable",
    packages=["dataclass_jsonable"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
