from setuptools import setup, find_packages

setup(
    name="audiotools",
    version="0.1.0",
    author="Lázaro Aguilar",
    author_email="aguilaofficial@gmail.com",
    description="CLI tools for audio processing: DC check, mono conversion, polarity check",
    url="https://github.com/aguila-sound/audiotools",
    packages=find_packages(),
    python_requires=">=3.13",
    install_requires=[
        "numpy",
        "soundfile"
    ],
    entry_points={
        "console_scripts": [
            "dccheck=audiotools.dccheck:main",
            "monomake=audiotools.monomake:main",
            "pcheck=audiotools.pcheck:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "License :: OSI Approved :: MIT License"
    ],
)
