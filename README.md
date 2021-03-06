# TG788vn-munin
This project provides munin plugins for the following stats:

- theoretical bandwidth (queried from `xdsl info`)

![tg788vn_bandwidth](doc/tg788vn_bandwidth-day.png)

- traffic (queried from `ip iflist`)

![tg788vn_traffic](doc/tg788vn_traffic-day.png)

## Installation
Clone this project on your server:

    git clone git@github.com:chteuchteu/TG788vn-munin.git
    cd TG788vn-munin

Provide TG788vn credentials:

    # vim main.py
    HOST = '172.17.1.1'
    USER = 'Administrator'
    PSWD = 'P@ssw0rd'

Install the plugin

    cp main.py /usr/share/munin/plugins/tg788vn
    ln -s /usr/share/munin/plugins/tg788vn /etc/munin/plugins/tg788vn-bandwidth
    ln -s /usr/share/munin/plugins/tg788vn /etc/munin/plugins/tg788vn-traffic
    service munin-node restard

The plugin should appear shortly on your munin report page.

> Note: the script will clear traffic stats every 5 minutes (using `ip clearifstats`).
