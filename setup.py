import setuptools, os

readme_path = os.path.join(os.getcwd(), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r") as f:
        long_description = f.read()
else:
    long_description = 'selenium_account'

setuptools.setup(
    name="selenium_account",
    version="0.2.3",
    author="Kristof",
    description="selenium_account",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kkristof200/selenium_account",
    packages=setuptools.find_packages(),
    install_requires=[
        'kproxy>=0.0.1',
        'kstopit>=0.0.16',
        'selenium-browser>=0.0.12',
        'setuptools>=67.8.0',
        'tldextract>=3.1.2'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)