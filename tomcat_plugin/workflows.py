from cloudify.decorators import workflow
from cloudify import ctx

__author__ = 'kemi'


@workflow
def check_tomcat_health(**kwargs):

    for node in ctx.nodes:
        if "tomcat_server" == node.id:
            for instance in node.instances:
                ctx.logger.info("Executing health check on instance {}".format(instance))
                instance.execute_operation("tomcat.commands.check_health")
                break
            break

