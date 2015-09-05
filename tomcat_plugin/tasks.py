MVN_PACKAGE = 'package'
__author__ = 'kemi'

import tempfile
from cloudify import exceptions, ctx
from cloudify.decorators import operation
from package_installer_plugin.utils import run, download_package
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
    # if 'artefact_url' \
    #         or 'webapps_dir' \
    #         or 'app_name' not in kwargs:
    #             raise exceptions.NonRecoverableError('No server configuration specified!')

    artefact_url = kwargs['artefact_url']
    tomcat_webapp_dir = kwargs['webapps_dir']
    app_name = kwargs['app_name']

    try:
        if 'http' in artefact_url:
            try:
                ctx.logger.info('Downloading file: ' + artefact_url)
                war_file = tempfile.mkstemp()
                download_package(war_file, artefact_url)
            except Exception as e:
                raise exceptions.RecoverableError(e)
        else:
            war_file = artefact_url

        ctx.logger.info('Moving file: ' + war_file[1])
        move_command = 'sudo mv ' + war_file[1] + ' ' + tomcat_webapp_dir + '/' + app_name
        run(move_command)
    except Exception as e:
        raise exceptions.NonRecoverableError(
            'Failed to deploy Tomcat App: ' + e.message)


@operation
def configure(server_config, **_):
    """ Installs a user-defined server.xml and restarts the service """

    if 'java_opts' in server_config:
        if server_config['java_opts'] is not None:
            java_opts = 'export JAVA_OPTS="' + server_config['java_opts'] + '"'
            ctx.logger.info('Custom JAVA_OPTS requested: ' + java_opts)
            set_env_sh = '/tmp/setenv.sh'
            ctx.logger.info('Opening temp setenv.sh at {0}, writing: {1}'.format(set_env_sh, java_opts))
            with open(set_env_sh, 'wb') as f:
                f.write(java_opts)
                f.flush()
                f.close()
            if 'catalina_home' not in server_config:
                raise exceptions.NonRecoverableError('Requested custom JAVA_OPTS but no "catalina_home" home specified!')
            destination = server_config['catalina_home'] + 'bin/setenv.sh'
            ctx.logger.info('Moving file to Catalina home: {0}'.format(destination))
            move_command = 'sudo mv ' + set_env_sh + ' ' + destination
            run(move_command)

    if 'server_xml' in server_config:
        if server_config['server_xml'] is not None:
            server_xml_url = server_config['server_xml']
            ctx.logger.info('Custom server.xml requested: ' + server_xml_url)
            server_xml = tempfile.mkstemp()
            download_package(server_xml, server_xml_url)
            war_file_path = server_xml[1]
            if ctx.node.properties['tomcat_home_dir'] is None:
                raise exceptions.NonRecoverableError('Requested custom server.xml but no "tomcat_home_dir" specified!')
            tomcat_home_dir = ctx.node.properties['tomcat_home_dir']
            ctx.logger.info('Moving file: ' + server_xml_url)
            move_command = 'sudo mv ' + war_file_path + ' ' + tomcat_home_dir + '/server_xml'
            run(move_command)