MVN_PACKAGE = 'package'
__author__ = 'kemi'

import tempfile
from cloudify import exceptions, ctx
from cloudify.decorators import operation
from package_installer_plugin.utils import run, download_package
from package_installer_plugin.service_tasks import start_service


@operation
def start_tomcat(service_name, server_config, **_):

    # Configure before starting
    if server_config is not None:
        configure(server_config)

    ctx.logger.info('Starting service')
    start_service(service_name)


@operation
def deploy_tomcat_app(war_file_url, server_config, app_name, **_):
    """ Deploys a WAR file to the Tomcat server WebApps directory """

    try:
        if 'http' in war_file_url:
            ctx.logger.info('Downloading file: ' + war_file_url)
            war_file = download_package(tempfile.mkstemp(), war_file_url)
        else:
            war_file = war_file_url

        ctx.logger.info('Moving file: ' + war_file)
        tomcat_webapp_dir = server_config['tomcat_webapp_dir']
        move_command = 'sudo mv ' + war_file + ' ' + tomcat_webapp_dir + '/' + app_name
        run(move_command)
    except Exception as e:
        raise exceptions.NonRecoverableError(
            'Failed to deploy Tomcat App: ' + e.message)


def configure(server_config, **_):
    """ Installs a user-defined server.xml and restarts the service """

    if 'server_xml' in server_config:

        server_xml_url = server_config['server_xml']
        ctx.logger.info('Downloading file: ' + server_xml_url)
        server_xml = tempfile.mkstemp()
        download_package(server_xml, server_xml_url)
        war_file_path = server_xml[1]
        tomcat_home_dir = ctx.node.properties['tomcat_home_dir']

        ctx.logger.info('Moving file: ' + server_xml_url)
        move_command = 'sudo mv ' + war_file_path + ' ' + tomcat_home_dir + '/server_xml'
        run(move_command)


def _run_maven_command(pom_xml, mvn_operation):
    package_command = 'mvn -f {0} {1}'.format(pom_xml, mvn_operation)
    ctx.logger.info('Executing maven operation: ' + package_command)
    run(package_command)


def _maven_package(app_name):
    _run_maven_command('/tmp/{0}/pom.xml'.format(app_name), MVN_PACKAGE)