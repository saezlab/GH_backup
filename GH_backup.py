import os
import sys
import json
import time
import subprocess

import pycurl

def token(filename='token'):

    with open(filename, 'r') as f:
        aux = f.read().strip()

    return aux

def request(url, multipage=True):
    # Request information to GitHub API

    dump = []
    page = 1

    while True:
        c = pycurl.Curl()

        c.setopt(c.USERPWD, ':'.join([__user__, __token__]))
        c.setopt(c.URL, url + '&page=%d' %page if multipage else url)

        # Load the output as a JSON object
        aux = json.loads(c.perform_rb())

        c.close()
        page += 1

        dump.extend(aux)

        if not aux or not multipage:
            break

    return dump

if __name__ == '__main__':
    start = time.time()
    print 'Session started @ %s\n' % time.strftime('%a %d %b %Y - %H:%M')

    __user__ = sys.argv[1]
    __token__ = token(filename=sys.argv[2])

    repos = request('https://api.github.com/%s/repos?type=all' % sys.argv[3])

    for repo in repos:
        name = repo['name']

        msg = 'Working on %s repository' % name
        print msg
        print '=' * len(msg) + '\n'

        if os.path.exists(name): # Repository already cloned
            print '"%s/" directory found' % name

            cloned = False


        else: # Clone the repository
            print '"%s/" directory not found' % name
            print 'Cloning repository "%s"' % name

            subprocess.call(('git clone --mirror %s %s/.git'
                             % (repo['ssh_url'], name)).split(' '),
                            stdout=sys.stdout)
            cloned = True

        print '>>> Entering subdirectory "%s/"' % name
        os.chdir(name)

        if cloned:
            subprocess.call('git config --bool core.bare false'.split(' '),
                            stdout=sys.stdout)

        print 'Checking branches...'
        branch_url = repo['branches_url'].split('{')[0]
        aux = request(branch_url, multipage=False)
        # Keep 'master' always last
        branches = [n['name'] for n in aux if n['name'] != 'master']
        branches.append('master')

        for branch in branches:
            print 'Checking out branch %s' % branch
            subprocess.call(('git checkout %s' % branch).split(' '),
                            stdout=sys.stdout)
            print 'Pulling branch %s' % branch
            subprocess.call(('git pull origin %s' % branch).split(' '),
                            stdout=sys.stdout)

        print '<<< Leaving subdirectory "%s/"' % name
        os.chdir('..')
        print '\n'

    print 'Backed up %d repositories' % len(repos)
    print 'Time elapsed %d sec.' %(time.time() - start)
    msg = 'Backup finished!'
    print '\n' + msg
    print '=' * len(msg)
