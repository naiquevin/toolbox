"""fabfile template for git based deployment workflows

It assumes that a remote with post_receive hook is configured on the
server(s) and public key ssh access for the user is set. Similarly a
local tracking branch is set from which code will be pushed to the
remotes on the servers to be deployed to

To deploy to staging , run::

    $ fab staging:develop prepare_deploy

This will start deployment and will merge develop branch in the
tracking branch for staging env (configured in the fab file itself)
and push code.
"""

from functools import wraps
from fabric.api import local, env, task
from fabric.colors import yellow, red, green


@task
def staging(branch):
    """Setup the deployment env to be staging.

    This command needs to be run before any other command that depends
    on the env.

    :usage: $ fab staging:develop
    """
    env.hosts = [] # add hosts here
    env.from_branch = branch # branch from which to upload code
    env.tracking_branch = 'to-staging' # this tracking branch is assumed to be set
    env.remote = 'staging' # git remote for this env
    local('git checkout %s' % env.from_branch)


@task
def production():
    """Setup the deployment env to be production.

    This command needs to be run before any other command that depends
    on the env
    """
    print(red('Production deployment isn\'t configured yet'))
    # configure prod env similar to staging above with one change that
    # instead of allowing the user to specify the `from_branch` hard
    # code your "always-stable" branch here


def env_required(func):
    """Decorator to stop a function from running if the deployment
    environment is not set. Decorate all such functions with this
    """
    @wraps(func)
    def dec(*args, **kwargs):
        if len(env.hosts) == 0:
            print(red("Error: Command '%s' needs env to be specified."))
            print(yellow("Run the command as $ fab <env_name> %s" % (func.__name__,)))
            exit(1)
        return func(*args, **kwargs)
    return dec


@task
@env_required
def prepare_deploy():
    """Set of tasks to be done before deployment.

    eg. running tests, minifying assets etc.
    """
    test()
    prompt_next(deploy)


@task
@env_required
def deploy():
    """Deploy the code"""
    backup_code()
    local("git checkout %s" % env.tracking_branch)
    local("git pull")
    local("git merge %s" % env.from_branch)
    local("git push %s" % env.remote)
    local("git checkout %s" % env.from_branch)
    prompt_next(post_deploy)


@task
@env_required
def post_deploy():
    """Set of tasks to be done post deployment

    eg. Running db migrations etc.
    """
    print(green('Executing post deployment tasks'))
    # add code here


@task
def test():
    """Run tests"""
    print(yellow('Running tests'))
    # call the test command here appropriately


@task
@env_required
def backup_code():
    """Backup code on the server"""
    print(yellow('Taking a backup on the server before uploading new code (todo)'))
    # code to take backup


def prompt_next(func, args=None, kwargs=None):
    """Function to chain together various tasks. The user is prompted
    whether to execute the next task in line
    """
    func_name = func.__name__
    print
    ques = "Proceed to the next step (%s)? [y/n] " % (func_name,)
    ans = raw_input(ques)
    if ans in ('y', 'Y'):
        func()
    else:
        print(red('You chose to stop! Please run the next steps manually to complete deployment'))
