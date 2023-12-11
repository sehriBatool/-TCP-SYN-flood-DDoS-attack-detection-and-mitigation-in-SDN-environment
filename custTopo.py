#!/usr/bin/python
from mininet.net import Mininet
from mininet.node import RemoteController,OVSSwitch, Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.topo import Topo
from mininet.link import Link, Intf
from functools import partial
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch


def custTopo():
    net = Mininet( controller=RemoteController )
    info( '*** Adding controller\n' )
    net.addController(name ='c0',
                      controller = RemoteController,
                      ip = '127.0.0.1',
                      port=6633 )

    info( '*** Adding hosts\n' )
    h1 = net.addHost( 'h1', ip='10.0.0.54' )
    h2 = net.addHost( 'h2', ip='10.0.0.2' )
    h3 = net.addHost( 'h3', ip='10.0.0.3' )
    h4 = net.addHost( 'h4', ip='10.0.0.4' )
    h5 = net.addHost( 'h5', ip='10.0.0.5' )
    h6 = net.addHost( 'h6', ip='10.0.0.6' )
    h7 = net.addHost( 'h7', ip='10.0.0.7' )
    h8 = net.addHost( 'h8', ip='10.0.0.8' )
    h9 = net.addHost( 'h9', ip='10.0.0.9' )
    h10 = net.addHost( 'h10', ip='10.0.0.10' )
    h11 = net.addHost( 'h11', ip='10.0.0.11' )
    h12 = net.addHost( 'h12', ip='10.0.0.12' )
    h13 = net.addHost( 'h13', ip='10.0.0.13' )
    h14 = net.addHost( 'h14', ip='10.0.0.14' )
    h15 = net.addHost( 'h15', ip='10.0.0.15' )
    h16 = net.addHost( 'h16', ip='10.0.0.16' )
    h17 = net.addHost( 'h17', ip='10.0.0.17' )
    h18 = net.addHost( 'h18', ip='10.0.0.18' )
    h19 = net.addHost( 'h19', ip='10.0.0.19' )
    h20 = net.addHost( 'h20', ip='10.0.0.20' )

    h21 = net.addHost( 'h21', ip='10.0.0.21' )
    h22 = net.addHost( 'h22', ip='10.0.0.22' )
    h23 = net.addHost( 'h23', ip='10.0.0.23' )
    h24 = net.addHost( 'h24', ip='10.0.0.24' )
    h25 = net.addHost( 'h25', ip='10.0.0.25' )
    h26 = net.addHost( 'h26', ip='10.0.0.26' )
    h27 = net.addHost( 'h27', ip='10.0.0.27' )
    h28 = net.addHost( 'h28', ip='10.0.0.28' )
    h29 = net.addHost( 'h29', ip='10.0.0.29' )
    h30 = net.addHost( 'h30', ip='10.0.0.30' )

    h31 = net.addHost( 'h31', ip='10.0.0.31' )
    h32 = net.addHost( 'h32', ip='10.0.0.32' )
    h33 = net.addHost( 'h33', ip='10.0.0.33' )
    h34 = net.addHost( 'h34', ip='10.0.0.34' )
    h35 = net.addHost( 'h35', ip='10.0.0.35' )
    h36 = net.addHost( 'h36', ip='10.0.0.36' )
    h37 = net.addHost( 'h37', ip='10.0.0.37' )
    h38 = net.addHost( 'h38', ip='10.0.0.38' )
    h39 = net.addHost( 'h39', ip='10.0.0.39' )
    h40 = net.addHost( 'h40', ip='10.0.0.40' )

    h41 = net.addHost( 'h41', ip='10.0.0.41' )
    h42 = net.addHost( 'h42', ip='10.0.0.42' )
    h43 = net.addHost( 'h43', ip='10.0.0.43' )
    h44 = net.addHost( 'h44', ip='10.0.0.44' )

    h45 = net.addHost( 'h45', ip='10.0.0.45' )
    h46 = net.addHost( 'h46', ip='10.0.0.46' )

    h47 = net.addHost( 'h47', ip='10.0.0.47' )
    h48 = net.addHost( 'h48', ip='10.0.0.48' )
    h49 = net.addHost( 'h49', ip='10.0.0.49' )
    h50 = net.addHost( 'h50', ip='10.0.0.50' )
    h51 = net.addHost( 'h51', ip='10.0.0.51' )
    h52 = net.addHost( 'h52', ip='10.0.0.52' )
    h53 = net.addHost( 'h53', ip='10.0.0.53' )


    info( '*** Adding switches\n' )
    s1 = net.addSwitch( 's1', cls = OVSKernelSwitch )
    s2 = net.addSwitch( 's2', cls = OVSKernelSwitch )

    info( '*** Creating links\n' )
    net.addLink( s1, s2)
    net.addLink( h1, s2)
    net.addLink( h2, s2)
    net.addLink( h3, s2)
    net.addLink( h4, s2)
    net.addLink( h5, s2)
    net.addLink( h6, s2)
    net.addLink( h7, s2)
    net.addLink( h8, s2)
    net.addLink( h9, s2)
    net.addLink( h10, s2)
    net.addLink( h11, s2)
    net.addLink( h12, s2)
    net.addLink( h13, s2)
    net.addLink( h14, s2)
    net.addLink( h15, s2)
    net.addLink( h16, s2)
    net.addLink( h17, s2)
    net.addLink( h18, s2)
    net.addLink( h19, s2)
    net.addLink( h20, s2)
    net.addLink( h21, s2)
    net.addLink( h22, s2)
    net.addLink( h23, s2)
    net.addLink( h24, s2)
    net.addLink( h25, s2)
    net.addLink( h26, s2)
    net.addLink( h27, s2)
    net.addLink( h28, s2)
    net.addLink( h29, s2)
    net.addLink( h30, s2)
    net.addLink( h31, s2)
    net.addLink( h32, s2)
    net.addLink( h33, s2)
    net.addLink( h34, s2)
    net.addLink( h35, s2)
    net.addLink( h36, s2)
    net.addLink( h37, s2)
    net.addLink( h38, s2)
    net.addLink( h39, s2)
    net.addLink( h40, s2)
    net.addLink( h41, s2)
    net.addLink( h42, s2)
    net.addLink( h43, s2)
    net.addLink( h44, s2)
    net.addLink( h45, s2)
    net.addLink( h46, s2)
    net.addLink( h47, s2)
    net.addLink( h48, s2)
    net.addLink( h49, s2)
    net.addLink( h50, s2)
    net.addLink( h51, s2)
    net.addLink( h52, s2)
    net.addLink( h53, s1)

    root=s2
    layer1 = [s1,h53]
    for idx,l1 in enumerate(layer1):
        net.addLink( root,l1 )
    info( '*** Starting network\n')
    net.start()
    info( '*** Running CLI\n' )
    CLI( net )
    info( '*** Stopping network' )
    net.stop()
    if __name__ == '__main__':
        setLogLevel( 'info' )
        custTopo()
topos = { 'custTopo': ( lambda: custTopo() ) }
