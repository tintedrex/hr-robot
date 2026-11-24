from setuptools import setup

package_name = "hr_balance_jetson"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="HR Software",
    maintainer_email="hr@example.com",
    description="Jetson-side balance outer-loop stub (SW-BAL-002).",
    license="Proprietary",
    entry_points={
        "console_scripts": [
            "balance_outer = hr_balance_jetson.balance_outer:main",
        ],
    },
)
