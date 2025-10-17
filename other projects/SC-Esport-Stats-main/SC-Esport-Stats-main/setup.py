from setuptools import setup, find_packages

setup(
    name="sc_esport_stats",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'pandas',
        'plotly',
    ]
)
