__author__ = 'kemi'

import tempfile
from cloudify import exceptions, ctx
from cloudify.decorators import operation
from package_installer_plugin.utils import run, download_package
from package_installer_plugin.service_tasks import start_service, stop_service


@operation
def start_tomcat(**_):
    # Configure before starting
    configure()
    ctx.logger.info('Starting service')
    start_service()


@operation
def deploy_tomcat_app(war_file_url, app_name, **_):
    """ Deploys a WAR file to the Tomcat server WebApps directory """

    war_file = tempfile.mkstemp()
    ctx.logger.info('Downloading file: ' + war_file_url)
    download_package(war_file, war_file_url)
    war_file_path = war_file[1]
    tomcat_webapp_dir = ctx.node.properties['tomcat_webapp_dir']

    ctx.logger.info('Moving file: ' + war_file_path)
    move_command = 'sudo mv ' + war_file_path + ' ' + tomcat_webapp_dir + '/' + app_name
    run(move_command)


@operation
def configure(**_):
    """ Installs a user-defined server.xml and restarts the service """

    server_config = ctx.node.properties['server_config']

    if 'server_xml' in server_config:

        server_xml_url = server_config['server_xml']
        ctx.logger.info('Downloading file: ' + server_xml_url)
        server_xml = tempfile.mkstemp()
        download_package(server_xml, server_xml_url)
        war_file_path = server_xml[1]
        tomcat_home_dir = ctx.node.properties['tomcat_home_dir']

        service_name = ctx.node.properties['service_name']
        ctx.logger.info('Stopping service: ' + service_name)
        stop_service(service_name)

        ctx.logger.info('Moving file: ' + server_xml_url)
        move_command = 'sudo mv ' + war_file_path + ' ' + tomcat_home_dir + '/server_xml'
        run(move_command)

        # ctx.logger.info('Starting service: ' + service_name)
        # start_service(service_name)


@operation
def package(module_source_url, app_name, **_):
    """ Deploys a WAR file to the Tomcat server WebApps directory """

    source_zip = tempfile.mkstemp()
    ctx.logger.info('Downloading file: ' + source_zip)
    download_package(source_zip, module_source_url)
    source_zip_path = source_zip[1]

    ctx.logger.info('Packaging module using maven: ' + source_zip_path)
    unzip_command = 'unzip {0} -d {1}'.format(source_zip_path, '/tmp')
    run(unzip_command)

    ctx.logger.info('Packaging module using maven: ' + source_zip_path)
    package_command = 'mvn -f {0} package'.format('/tmp/{0}/pom.xml'.format(app_name))
    run(package_command)

    ctx.instance.runtime_properties['war_file'] = '/tmp/{0}'.format(app_name)