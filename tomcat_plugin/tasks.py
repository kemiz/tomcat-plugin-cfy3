MVN_PACKAGE = 'package'
__author__ = 'kemi'

import tempfile
from cloudify import exceptions, ctx
from cloudify.decorators import operation
from package_installer_plugin.utils import run, download_file, unzip
from package_installer_plugin.service_tasks import start_service

@operation
def start_tomcat(service_name, **kwargs):

    # Configure before starting
    if kwargs is not None:
        if 'service_config' in kwargs:
            configure(kwargs['service_config'])

    ctx.logger.info('Starting service')
    start_service(service_name)


@operation
def deploy_tomcat_app(**kwargs):
    """ Deploys a WAR file to the Tomcat server WebApps directory """

    ctx.logger.info(kwargs)

    artefact_url = kwargs['artefact_url']
    tomcat_webapp_dir = kwargs['webapps_dir']
    app_name = kwargs['app_name']

    try:
        if 'http' in artefact_url:
            ctx.logger.info('Downloading file: ' + artefact_url)
            war_file_path, file_path = '/tmp/{0}'.format(app_name)
            download_file(file_path, artefact_url)
            if kwargs['maven_app'] is True:
                war_file_path = package(file_path, app_name)

            ctx.logger.info('Moving file: ' + war_file_path)
            move_command = 'sudo mv ' + war_file_path + ' ' + tomcat_webapp_dir + '/' + app_name
            run(move_command)
    except Exception as e:
        raise exceptions.NonRecoverableError(
            'Failed to deploy Tomcat App: ' + e.message)


@operation
def configure(server_config, **_):
    """ Configures the Tomcat server with a given server_config """

    # Installs a custom setenv.sh with custom server jvm configuration
    if 'java_opts' in server_config:
        if server_config['java_opts'] is not None:
            java_opts = 'export JAVA_OPTS="' + server_config['java_opts'] + '"'
            ctx.logger.info('Custom JAVA_OPTS requested: ' + java_opts)
            set_env_sh = tempfile.mkstemp()
            set_env_sh_path = set_env_sh[1]
            ctx.logger.info('Opening temp setenv.sh at {0}, writing: {1}'.format(set_env_sh_path, java_opts))
            with open(set_env_sh_path, 'wb') as f:
                f.write(java_opts)
                f.flush()
                f.close()
            if 'catalina_home' not in server_config:
                raise exceptions.NonRecoverableError('Requested custom JAVA_OPTS but no "catalina_home" home specified!')
            destination = server_config['catalina_home'] + 'bin/setenv.sh'
            ctx.logger.info('Moving file to Catalina home: {0}'.format(destination))
            move_command = 'sudo mv ' + set_env_sh_path + ' ' + destination
            run(move_command)

    # Installs a user-defined server.xml and restarts the service
    if 'server_xml' in server_config:
        if server_config['server_xml'] is not None:
            server_xml_url = server_config['server_xml']
            ctx.logger.info('Custom server.xml requested: ' + server_xml_url)
            server_xml = tempfile.mkstemp()
            download_file(source=server_xml_url, destination=server_xml)
            server_xml_path = server_xml[1]
            if ctx.node.properties['tomcat_home_dir'] is None:
                raise exceptions.NonRecoverableError('Requested custom server.xml but no "tomcat_home_dir" specified!')
            tomcat_home_dir = ctx.node.properties['tomcat_home_dir']
            ctx.logger.info('Moving file: ' + server_xml_url)
            move_command = 'sudo mv ' + server_xml_path + ' ' + tomcat_home_dir + '/server_xml'
            run(move_command)


def package(module_source_zip_path, app_name, **_):
    """
    Downloads application source as zip and uses maven to
    build and package a deployable WAR file
    """

    ctx.logger.info('Unzipping: ' + module_source_zip_path)
    unzip(module_source_zip_path, '/tmp')
    _run_maven_command('/tmp/{0}/pom.xml'.format(app_name), MVN_PACKAGE)
    return '/tmp/{0}/target/{0}.war'.format(app_name)


def _run_maven_command(pom_xml, mvn_operation):
    package_command = 'mvn -f {0} {1}'.format(pom_xml, mvn_operation)
    ctx.logger.info('Executing maven operation: ' + package_command)
    run(package_command)