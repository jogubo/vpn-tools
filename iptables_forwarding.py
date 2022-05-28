from os import system as cmd

INTERFACE = 'ens3'

PUBLIC_IP = {
    'ipv4': 'xxx.xxx.xxx.xxx',
    'ipv6': '2001:xxxx:xxxx:xxx::xxxx',
}

VPN_CLIENT_IP = {
    'ipv4': '10.8.0.100',
    'ipv6': 'fd42:42:42:42::100',
}

FROM_VPN_CLIENT_TO_INTERNET = {
    'tcp': [
        25,
        587,
    ],
    'udp': [
    ]
}

FROM_INTERNET_TO_VPN_CLIENT = {
    'tcp': [
        25,
        80,
        140,
        443,
        587,
        993,
        5222,
        5269,
    ],
    'udp': [
    ]
}


def cmd_iptables(ipv):
    if ipv == 'ipv4':
        return 'iptables'
    if ipv == 'ipv6':
        return 'ip6tables'


def routing_to_internet(ipv, port, protocol):
    iptables = cmd_iptables(ipv)
    cmd(
        f"{iptables} -t nat -A POSTROUTING -s \
            {VPN_CLIENT_IP[ipv]} -p {protocol} --dport {port} -j SNAT --to \
            {PUBLIC_IP[ipv]};"
    )
    cmd(
        f"{iptables} -A FORWARD -s \
            {VPN_CLIENT_IP[ipv]} -p {protocol} --dport {port} -j ACCEPT;"
    )


def routing_to_vpn_client(ipv, port, protocol):
    iptables = cmd_iptables(ipv)
    cmd(
        f"{iptables} -t nat -A PREROUTING -i {INTERFACE} \
            -p {protocol} --dport {port} -j DNAT \
            --to-destination {VPN_CLIENT_IP[ipv]};"
    )
    cmd(
        f"{iptables} -A FORWARD -d \
            {VPN_CLIENT_IP[ipv]} -p {protocol} --dport {port} -j ACCEPT;"
    )


if __name__ == '__main__':

    for protocol in FROM_VPN_CLIENT_TO_INTERNET:
        for port in FROM_VPN_CLIENT_TO_INTERNET[protocol]:
            if PUBLIC_IP['ipv4']:
                routing_to_internet('ipv4', port, protocol)
            if PUBLIC_IP['ipv6']:
                routing_to_internet('ipv6', port, protocol)

    for protocol in FROM_INTERNET_TO_VPN_CLIENT:
        for port in FROM_INTERNET_TO_VPN_CLIENT[protocol]:
            if PUBLIC_IP['ipv4']:
                routing_to_vpn_client('ipv4', port, protocol)
            if PUBLIC_IP['ipv6']:
                routing_to_vpn_client('ipv6', port, protocol)

    cmd('iptables --list')
    cmd('ip6tables --list')
