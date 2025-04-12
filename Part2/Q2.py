from mininet.net import Mininet
from mininet.node import OVSController, OVSKernelSwitch
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.cli import CLI
import time
import os

class SimpleNATTopo(Topo):
    def build(self):
        # External switches
        s1 = self.addSwitch('s1', stp=True)
        s2 = self.addSwitch('s2', stp=True)
        s3 = self.addSwitch('s3', stp=True)
        s4 = self.addSwitch('s4', stp=True)

        # Hosts
        h1 = self.addHost('h1', ip='10.1.1.2/24')
        h2 = self.addHost('h2', ip='10.1.1.3/24')
        h3 = self.addHost('h3', ip='10.0.0.4/24')
        h4 = self.addHost('h4', ip='10.0.0.5/24')
        h5 = self.addHost('h5', ip='10.0.0.6/24')
        h6 = self.addHost('h6', ip='10.0.0.7/24')
        h7 = self.addHost('h7', ip='10.0.0.8/24')
        h8 = self.addHost('h8', ip='10.0.0.9/24')
        h9 = self.addHost('h9')  # NAT router

        # Internal links to NAT (h9)
        self.addLink(h1, h9, delay='5ms')
        self.addLink(h2, h9, delay='5ms')

        # External connectivity
        self.addLink(h9, s1, delay='5ms')  # h9 external side
        self.addLink(h4, s2, delay='5ms')  # h4 to s2
        self.addLink(h3, s2, delay='5ms')
        self.addLink(h6, s3, delay='5ms')
        self.addLink(h5, s3, delay='5ms')
        self.addLink(h7, s4, delay='5ms')
        self.addLink(h8, s4, delay='5ms')
        
        self.addLink(s1, s2, delay='7ms')
        self.addLink(s3, s2, delay='7ms')  
        self.addLink(s1, s3, delay='7ms')  
        self.addLink(s1, s4, delay='7ms')  
        self.addLink(s4, s3, delay='7ms')   
        

def run():
    net = Mininet(topo=SimpleNATTopo(), controller=OVSController, switch=OVSKernelSwitch, link=TCLink)
    net.start()

    h1, h2, h9, h4, h3, h5, h6, h7, h8 = net.get('h1', 'h2', 'h9', 'h4', 'h3', 'h5', 'h6', 'h7', 'h8')
    
    # Enable STP on all switches
    for sw in ['s1', 's2', 's3', 's4']:
        sw_obj = net.get(sw)
        sw_obj.cmd('ovs-vsctl set Bridge {} stp_enable=true'.format(sw))
    
    # Create a bridge on h9 to join internal interfaces
    h9.cmd('ip link add name br0 type bridge')
    h9.cmd('ip link set br0 up')
    h9.cmd('ip link set h9-eth0 master br0')  # link to h1
    h9.cmd('ip link set h9-eth1 master br0')  # link to h2
    h9.cmd('ip addr add 10.1.1.1/24 dev br0')  # internal gateway IP
    

    # Set default routes for internal hosts
    h1.cmd('ip route add default via 10.1.1.1')
    h2.cmd('ip route add default via 10.1.1.1')

    # Set default route on h4 toward h9 (NAT's external IP)
    h3.cmd('ip route add default via 10.0.0.1')
    h4.cmd('ip route add default via 10.0.0.1')
    h5.cmd('ip route add default via 10.0.0.1')
    h6.cmd('ip route add default via 10.0.0.1')
    h7.cmd('ip route add default via 10.0.0.1')
    h8.cmd('ip route add default via 10.0.0.1')

    # Enable IP forwarding on NAT
    h9.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Setup NAT: masquerade internal traffic via h9-eth2
    h9.cmd('iptables -t nat -F')
    h9.cmd('iptables -t nat -A POSTROUTING -s 10.1.1.0/24 -o h9-eth2 -j MASQUERADE')

    # Clear any existing IPs on h9
    h9.cmd("ip addr flush dev h9-eth0")
    h9.cmd("ip addr flush dev h9-eth1")
    h9.cmd("ip addr flush dev h9-eth2")

    # Create bridge and assign internal interfaces
    h9.cmd('ip link add name br0 type bridge')
    h9.cmd('ip link set br0 up')
    h9.cmd('ip link set h9-eth0 master br0')  # assume eth0 is h1
    h9.cmd('ip link set h9-eth1 master br0')  # assume eth1 is h2
    h9.cmd('ip addr add 10.1.1.1/24 dev br0')

    # Set external IP
    h9.setIP('10.0.0.1/24', intf='h9-eth2')
    h9.cmd('ip addr add 172.16.10.10/24 dev h9-eth2')
    
    print("Waiting 30 seconds for routes/NAT to settle...")
    time.sleep(30)
    
    net.pingAll()
    
    print("\nTesting connectivity (each test runs 3 times with 30s interval):")


    print("a) Test communication to an external host from an internal host")
    for i in range(3):
        result = h1.cmd('ping -c 4 10.0.0.6')
        print(f"\n--- Test {i+1}/3: Ping h5 from h1 ---\n{result}")
    for i in range(3):
        result = h2.cmd('ping -c 4 10.0.0.4')
        print(f"\n--- Test {i+1}/3: Ping h3 from h2 ---\n{result}")


    print("b) Test communication to an internal host from an external host")
    for i in range(3):
        result = h8.cmd('ping -c 4 10.1.1.2')
        print(f"\n--- Test {i+1}/3: Ping h1 from h8 ---\n{result}")
    for i in range(3):
        result = h6.cmd('ping -c 4 10.1.1.3')
        print(f"\n--- Test {i+1}/3: Ping h2 from h6 ---\n{result}")

    print("c) Iperf tests: 3 tests of 120s each")
    h1.cmd('iperf3 -s -D')  # Start iperf3 server
    time.sleep(2)
    for i in range(3):
        result = h6.cmd('iperf3 -c 10.1.1.2 -t 120')
        print(f"\n--- iPerf3 Test {i+1}/3: h6 -> h1 ---\n{result}")
        time.sleep(5)
    h1.cmd('pkill iperf3')

    print("\n--- iPerf3 Test: h2 client -> h8 server ---\n")
    h8.cmd('iperf3 -s -D')
    time.sleep(2)
    for i in range(3):
        result = h2.cmd('iperf3 -c 10.0.0.9 -t 120')
        print(f"\n--- iPerf3 Test {i+1}/3: h2 -> h8 ---\n{result}")
        time.sleep(5)
    h8.cmd('pkill iperf3')

    net.stop()
    os.system('sudo mn -c')

if __name__ == '__main__':
    run()