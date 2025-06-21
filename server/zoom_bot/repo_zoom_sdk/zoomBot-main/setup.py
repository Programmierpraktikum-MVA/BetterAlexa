from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "meeting_sdk",
        ["meeting_sdk_pybind.cpp", "meeting_sdk.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++"
    ),
]

setup(
    name="meeting_sdk",
    ext_modules=ext_modules,
)
