from setuptools import setup  # type: ignore

setup(
    name="dataclass-jsonable",
    version="0.0.4",
    author="hit9",
    author_email="hit9@icloud.com",
    description="Conversions between dataclasses and jsonable dictionaries.",
    license="BSD",
    keywords="dataclasses,json,jsonable",
    url="https://github.com/hit9/dataclass-jsonable",
    packages=["dataclass_jsonable"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
)
