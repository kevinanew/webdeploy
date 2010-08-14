# coding: utf-8


def print_server_info(env):
    print '%s server hosts:' % env.server_type, env.hosts
    print '--- port:', env.port
    print '--- username:', env.user

    if env.password:
        print '--- password: ******'
    else:
        print '--- password: (Not use)'
