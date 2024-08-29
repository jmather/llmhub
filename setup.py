from setuptools import setup, find_packages

setup(
    name="llmhub-cli",
    version="0.1.7",
    author="Jacob Mather",
    author_email="jmather@jmather.com",
    description="LLMHub is a lightweight management platform designed to streamline working with LLMs.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jmather/llmhub",  # Replace with your project's URL
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",  # Add any other dependencies your project has
        "psutil",
        "requests",
        "click",
        "PyYAML"
    ],
    entry_points={
        'console_scripts': [
            'llmhub=cli:cli',
        ],
    },
    package_data={
        'llmhub_lib': ['web_server.py'],  # Include the web_server.py file in the package
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
