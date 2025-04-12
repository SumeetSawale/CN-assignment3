from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

class LoopyTopo(Topo):
    def build(self):
        # Create switches
        s1, s2, s3, s4 = [self.addSwitch(f's{i}') for i in range(1, 5)]

        # Create hosts with IPs
        hosts = {
            'h1': '10.0.0.2/24', 'h2': '10.0.0.3/24',
            'h3': '10.0.0.4/24', 'h4': '10.0.0.5/24',
            'h5': '10.0.0.6/24', 'h6': '10.0.0.7/24',
            'h7': '10.0.0.8/24', 'h8': '10.0.0.9/24'
        }

        for h, ip in hosts.items():
            host = self.addHost(h, ip=ip)
            sw = f's{((int(h[1]) - 1) // 2) + 1}'  # Map h1-h2 to s1, h3-h4 to s2, etc.
            self.addLink(host, sw, cls=TCLink, delay='5ms')

        # Add switch-switch links with 7ms latency
        switch_links = [('s1', 's2'), ('s2', 's3'), ('s3', 's4'), ('s4', 's1'), ('s1', 's3')]
        for sA, sB in switch_links:
            self.addLink(sA, sB, cls=TCLink, delay='7ms')

def run():
    topo = LoopyTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()
    print("*** Running CLI...")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
