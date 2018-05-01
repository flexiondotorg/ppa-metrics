#!/usr/bin/env python3

# Refernce
#  * https://api.launchpad.net/+apidoc/devel.html#binary_package_publishing_history
#  * https://help.launchpad.net/API/launchpadlib
#
# apt install python3-launchpadlib python3-matplotlib

import argparse
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import operator
import os
import sys
from dateutil import parser
from launchpadlib.launchpad import Launchpad

if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument('--architecture', dest='architecture', nargs='?', default='amd64', help="Build architecture. (i386, amd64, armhf)")
    cli.add_argument('--graphs', dest='graphs', action='store_true', help="Enable creation daily download graphs for each package in the PPA.")
    cli.add_argument('--owner', dest='owner', help="PPA Owner. The acount/group that owns the PPA.", required=True)
    cli.add_argument('--ppa', dest='ppa', help="PPA Name. The name of PPA to query.", required=True)
    cli.add_argument('--release', dest='release', help="Ubuntu Release. (xenial, bionic)", required=True)
    cli.set_defaults(graphs=False)
    args = cli.parse_args()

    CACHE = os.path.join(os.environ['HOME'], 'launchpadlib', 'cache')
    API_URL = 'https://api.launchpad.net/devel/ubuntu/' + args.release + '/' + args.architecture
    lp = Launchpad.login_anonymously('ppastat', 'production', CACHE)
    ppa = lp.people[args.owner].getPPAByName(name=args.ppa)
    published_packages = ppa.getPublishedBinaries(status='Published', distro_arch_series=API_URL)

    debs = []
    for package in published_packages:
        download_count = package.getDownloadCount()
        if download_count:
            print('Processing ' + package.binary_package_name)
            debs.append([download_count,'%s %s' % (package.binary_package_name,package.binary_package_version)])

            if args.graphs:
                print('Plotting ' + package.binary_package_name)
                daily_stats = sorted(package.getDailyDownloadTotals().items(), key=operator.itemgetter(0))
                for daily_stat in daily_stats:
                    #date = daily_stat[0]
                    datetime = parser.parse(daily_stat[0])
                    #datenum = dates.date2num(datetime)
                    #print(datetime)
                    #print(datenum)
                    downloads = daily_stat[1]
                    plt.xlabel('Date')
                    plt.ylabel('Downloads')
                    plt.plot(datetime,int(downloads))
                    # beautify the x-labels
                    plt.gcf().autofmt_xdate()
                    plt.savefig(package.binary_package_name + '-' + args.release + '.png')

    debs_sorted = sorted(debs,key=lambda download_count: download_count[0],reverse=True)
    for deb in debs_sorted:
       print('%s:%s' % (deb[0], deb[1]))
