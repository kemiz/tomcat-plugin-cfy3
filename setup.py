from setuptools import setup

setup(
    name='cloudify-tomcat-plugin',
    version='1.2',
    author='kemiz',
    packages=['tomcat_plugin'],
    license='LICENSE',
    install_requires=[
        "cloudify-plugins-common==3.2",
        "requests",
        'cloudify',
        'https://github.com/kemiz/cloudify-package-installer-plugin/archive/master.zip'
    ]
)
