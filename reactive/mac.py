from charms.reactive import when, when_not, set_state
from charmhelpers.core import hookenv
import subprocess
import netifaces
import time

@when_not('layer-mac.installed')
@when('layer-mac.ready')
def install_layer_mac():
    config = hookenv.config()
    if config['interface'] is not "" and config['address'] is not "":
        subprocess.check_call(["ip link set dev {} down".format(config['interface'])],shell=True)
        subprocess.check_call(["ip link set dev {} address {}".format(config['interface'],config['address'])],shell=True)
        subprocess.check_call(["ip link set dev {} up".format(config['interface'])],shell=True)
        subprocess.check_call(["dhclient {}".format(config['interface'])],shell=True)
        with open("/etc/systemd/system/macspoof.service",'w') as file:
            file.write('''
            [Unit]
            Description=MAC Address spoof {0}
            Wants=network-pre.target
            Before=network-pre.target
            BindsTo=sys.subsystem-net-devices-{0}.device
            After=sys-subsystem-net-devices-{0}.devices

            [Service]
            Type=oneshot
            ExecStart=/usr/bin/ip link set dev {0} address {1}
            ExecStart=/usr/bin/ip link set dev {0} up

            [Install]
            WantedBy=multi-user.taget'''.format(config['interface'],config['address']))
    else:
        print("No mac configuration, not configuring")
    set_state('layer-mac.installed')


#Systemd
#https://wiki.archlinux.org/index.php/MAC_address_spoofing
#/etc/systemd/system/macspoof@.service
#[Unit]
#Description=MAC Address Change %I
#Wants=network-pre.target
#Before=network-pre.target
#BindsTo=sys-subsystem-net-devices-%i.device
#After=sys-subsystem-net-devices-%i.device
#
#[Service]
#Type=oneshot
#ExecStart=/usr/bin/ip link set dev %i address 36:aa:88:c8:75:3a
#ExecStart=/usr/bin/ip link set dev %i up
#
#[Install]
#WantedBy=multi-user.target
