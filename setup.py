from setuptools import find_packages, setup

setup(
    name="netbox-data-flows",
    version="0.4.2",
    description="NetBox plugin to document applications and data flows",
    author="Thomas Fargeix",
    license="Apache 2.0",
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
