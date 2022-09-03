from os import system
import json


def load_conf(file='conf.json'):
    with open('conf.json', 'r') as conf:
        return json.load(conf)


def system_iptables(ipv):
    if ipv == 'ipv4':
        return 'iptables'
    if ipv == 'ipv6':
        return 'ip6tables'


def inbound_traffic(ipv, port, protocol):
    iptables = system_iptables(ipv)
    system(
        f"{iptables} -t nat -A PREROUTING -i {interface} \
            -p {protocol} --dport {port} -j DNAT \
            --to-destination {client_local_ip[ipv]};"
    )
    system(
        f"{iptables} -A FORWARD -d \
            {client_local_ip[ipv]} -p {protocol} --dport {port} -j ACCEPT;"
    )


def outbound_traffic(ipv, port, protocol):
    iptables = system_iptables(ipv)
    system(
        f"{iptables} -t nat -A POSTROUTING -s \
            {client_local_ip[ipv]} -p {protocol} --dport {port} -j SNAT --to \
            {server_public_ip[ipv]};"
    )
    system(
        f"{iptables} -A FORWARD -s \
            {client_local_ip[ipv]} -p {protocol} --dport {port} -j ACCEPT;"
    )


if __name__ == '__main__':

    conf = load_conf()
    interface = conf['interface']
    server_public_ip = conf['server_public_ip']
    client_local_ip = conf['client_local_ip']
    inbound = conf['inbound']
    outbound = conf['outbound']

    for protocol in inbound:
        for port in inbound[protocol]:
            if server_public_ip['ipv4']:
                inbound_traffic('ipv4', port, protocol)
            if server_public_ip['ipv6']:
                inbound_traffic('ipv6', port, protocol)

    for protocol in outbound:
        for port in outbound[protocol]:
            if server_public_ip['ipv4']:
                outbound_traffic('ipv4', port, protocol)
            if server_public_ip['ipv6']:
                outbound_traffic('ipv6', port, protocol)

    system('iptables --list')
    system('ip6tables --list')
