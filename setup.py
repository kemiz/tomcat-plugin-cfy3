from setuptools import setup

setup(
    name='cloudify-tomcat-plugin',
    version='1.2.1',
    author='kemiz',
    packages=['tomcat_plugin'],
    license='LICENSE',
    install_requires=[
        'cloudify-plugins-common==3.2.1',
        'requests',
        'cloudify==3.2.1'
    ],
    dependency_links=[
        'https://github.com/kemiz/cloudify-package-installer-plugin/archive/master.zip',
        'https://github.com/kemiz/maven_plugin/archive/master.zip'
    ]
)
