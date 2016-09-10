from setuptools import setup, find_packages

setup(
    name='pybot-systemd',
    setup_requires=['setuptools_scm'],
    use_scm_version={
        'write_to': 'src/pbsystemd/__version__.py'
    },
    install_requires=['pkg_resources'],
    packages=find_packages("src"),
    package_dir={'': 'src'},
    url='',
    license='',
    author='Eric Pascual',
    author_email='eric@pobot.org',
    download_url='https://github.com/Pobot/PyBot',
    description='systemd related utility functions for services setup/cleanup',
)
