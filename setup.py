from setuptools import setup, find_packages

setup(
    name="jira-analytics-tool",
    version="1.0.0",
    author="Pavel Belkov",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.3.0", 
        "matplotlib>=3.5.0",
        "numpy>=1.21.0",
    ],
    entry_points={
        "console_scripts": [
            "jira-analyzer=jira_analyzer:main",
        ],
    },
)
EOF