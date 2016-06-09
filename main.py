#!/usr/bin/python2
# -*- coding: utf-8 -*-
import re
import telnetlib
import argparse
import sys

# Credentials
HOST = ''
USER = ''
PSWD = ''

LNRT = '\r\n'
PRPT = '=>'

# Mode: either 'tg788vn-bandwidth' or 'tg788vn-traffic', determined by symlink name
mode = __file__.split('/')[-1]
modes = ['tg788vn-bandwidth', 'tg788vn-traffic']

if mode not in modes:
    print('Unknown mode {}.'.format(mode))
    print('Accepted modes are {}'.format(','.join(modes)))
    sys.exit(1)

# Check credentials
if len(HOST) == 0 or len(USER) == 0 or len(PSWD) == 0:
    print('Empty credentials')
    sys.exit(1)

parser = argparse.ArgumentParser()
parser.add_argument('config', nargs='?')
args = parser.parse_args()

if args.config == 'config':
    if mode == 'tg788vn-bandwidth':
        print('graph_title TG788vn XDSL bandwidth')
        print('graph_vlabel bandwidth')
        print('graph_category network')
        print('up.label Up')
        print('down.label Down')
    elif mode == 'tg788vn-traffic':
        print('graph_title TG788vn Internet interface traffic')
        print('graph_vlabel bits in (-) / out (+) per second')
        print('graph_category network')
        print('up.label Up (B/s)')
        print('up.draw AREA')
        print('down.label Down (B/s)')
        print('down.draw AREA')

    sys.exit(0)

# Connect to host & authenticate
#print('Connecting...')
tn = telnetlib.Telnet(HOST)

tn.read_until(b'Username : ', 2)
tn.write(USER + LNRT)
#print(' -> {}'.format(USER))

tn.read_until(b'Password : ', 2)
tn.write(PSWD + LNRT)
#print(' -> {}'.format('*' * len(PSWD)))

tn.read_until(PRPT)

# Query data
if mode == 'tg788vn-bandwidth':
    tn.write('xdsl' + LNRT)
    tn.read_until(PRPT)
    tn.write('info' + LNRT)
    xdsl_stats = tn.read_until(PRPT)
    tn.write('exit')
    tn.close()

    # Parse xdsl stats

    # Modem state:                             up
    # Up time (Days hh:mm:ss):                 0 jours, 1:06:47
    # xDSL Type:                               ADSL2+
    # Bandwidth (Down/Up - kbit/s):            20108/1032
    regex = re.compile('Bandwidth \(Down\/Up - kbit\/s\):\s*(\d*)\/(\d*)')
    for row in xdsl_stats.split('\n'):
        matches = regex.findall(row)

        if len(matches) > 0:
            matches = matches[0]
            down = int(matches[0])
            up = int(matches[1])

            # Convert kbit/s to bit/s
            down *= 1000
            up *= 1000

            print('up.value {}'.format(up))
            print('down.value {}'.format(down))

            sys.exit(0)

    # Could not find row
    print('Could not find Bandwidth row in command output.')
    sys.exit(1)

elif mode == 'tg788vn-traffic':
    tn.write('ip' + LNRT)
    tn.read_until(PRPT)
    tn.write('iflist' + LNRT)
    if_stats = tn.read_until(PRPT)

    # Parse if stats
    # Interface                            Group  MTU   RX         TX         Admin  Oper
    # 1   loop. . . . . . . . . . . . . .  local  4096  8711 KB    5220 KB    UP     [UP]
    # 2   Internet. . . . . . . . . . . .  wan    1492  555 MB     606 MB     UP     UP
    # 3   LocalNetwork. . . . . . . . . .  lan    1456  647 MB     561 MB     UP     [UP]

    # We're looking for line #2 in the above example
    regex = re.compile('\d   Internet(?:\. )* wan \s*\d*\s* (\d*) (KB|MB|GB|TB) \s* (\d*) (KB|MB|GB|TB) ')
    for row in if_stats.split('\n'):
        matches = regex.findall(row)

        if len(matches) > 0:
            matches = matches[0]
            rx = int(matches[0])
            rx_unit = matches[1]
            tx = int(matches[2])
            tx_unit = matches[3]

            # Handle units
            units = {
                'KB': 1024,
                'MB': 1024**2,
                'GB': 1024**3,
                'TB': 1024**4,
            }

            rx *= units[rx_unit]
            tx *= units[tx_unit]

            one_sec_rx = rx / (5 * 60)
            one_sec_tx = tx / (5 * 60)

            # Download should be negative (in = -)
            one_sec_rx *= -1

            print('up.value {}'.format(str(one_sec_tx)))
            print('down.value {}'.format(str(one_sec_rx)))

            # Flush stats
            tn.write('clearifstats' + LNRT)
            tn.read_until(PRPT)

            tn.write('exit')
            tn.close()
            sys.exit(0)

    # Couldn't find regex match
    tn.write('exit')
    tn.close()

    print('Could not find Internet row in command output.')
    sys.exit(1)
