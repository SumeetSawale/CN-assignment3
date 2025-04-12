#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSController, OVSSwitch
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time
import os

class custom_topo(Topo):
    def build(self):
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        
        # Add hosts
        h1 = self.addHost('h1', ip='10.0.0.2/24')
        h2 = self.addHost('h2', ip='10.0.0.3/24')
        h3 = self.addHost('h3', ip='10.0.0.4/24')
        h4 = self.addHost('h4', ip='10.0.0.5/24')
        h5 = self.addHost('h5', ip='10.0.0.6/24')
        h6 = self.addHost('h6', ip='10.0.0.7/24')
        h7 = self.addHost('h7', ip='10.0.0.8/24')
        h8 = self.addHost('h8', ip='10.0.0.9/24')
        
        # Add links between switches (7ms delay)
        self.addLink(s1, s2, delay='7ms')
        self.addLink(s2, s3, delay='7ms')
        self.addLink(s3, s4, delay='7ms')
        self.addLink(s4, s1, delay='7ms')
        self.addLink(s1, s3, delay='7ms')  # Cross-link creating the loop
        
        # Add links between hosts and switches (5ms delay)
        self.addLink(h1, s1, delay='5ms')
        self.addLink(h2, s1, delay='5ms')
        self.addLink(h3, s2, delay='5ms')
        self.addLink(h4, s2, delay='5ms')
        self.addLink(h5, s3, delay='5ms')
        self.addLink(h6, s3, delay='5ms')
        self.addLink(h7, s4, delay='5ms')
        self.addLink(h8, s4, delay='5ms')


def enable_stp(net):
    print("\nEnabling STP")
    
    for switch in net.switches:
        print(f"Enabling STP on {switch.name}")
        
        switch.cmd('ovs-vsctl set bridge %s stp_enable=true' % switch.name)
        
        # Verify STP is enabled
        stp_status = switch.cmd('ovs-vsctl get bridge %s stp_enable' % switch.name).strip()
        print(f"STP status for {switch.name}: {stp_status}")


def test(net, source, dest):
    print(f"\n--- Testing ping from {source} to {dest} ---")
    
    # Run ping with 3 packets
    result = net.get(source).cmd(f"ping -c 3 {net.get(dest).IP()}")
    print(result)
    
    return result


def main():
    
    topo = custom_topo()
    net = Mininet(topo=topo, link=TCLink, switch=OVSSwitch, controller=OVSController)
    net.start()
    
    print("Network topology created.")
    
    # Enable STP on all switches
    enable_stp(net)
    
    print("Waiting for STP to converge (30 seconds)")    
    time.sleep(30)
    
    print("Running ping tests...")
    
    # Run the ping tests
    test(net, 'h3', 'h1')
    print("Waiting 45 seconds before the next test...")
    time.sleep(45)  # Wait 30 seconds between tests as instructed
    
    test(net, 'h5', 'h7')
    print("Waiting 45 seconds before the next test...")
    time.sleep(45)
    
    test(net, 'h8', 'h2')
        
    # Cleanup
    net.stop()
    os.system('sudo mn -c')  # Clean up Mininet environment

if __name__ == '__main__':
    # setLogLevel('info')
    main()