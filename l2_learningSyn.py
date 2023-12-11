"""
  The learning switch "brain" associated with a single OpenFlow switch.

  When we see a packet, we'd like to output it on a port which will
  eventually lead to the destination.  To accomplish this, we build a
  table that maps addresses to ports.

  We populate the table by observing traffic.  When we see a packet
  from some source coming from some port, we know that source is out
  that port.

  When we want to forward traffic, we look up the desintation in our
  table.  If we don't know the port, we simply send the message out
  all ports except the one it came in on.  (In the presence of loops,
  this is bad!).

  In short, our algorithm looks like this:

  For each packet from the switch:
  1) Use source address and switch port to update address/port table
  2) Is transparent = False and either Ethertype is LLDP or the packet's
     destination address is a Bridge Filtered address?
     Yes:
        2a) Drop packet -- don't forward link-local traffic (LLDP, 802.1x)
            DONE
  3) Is destination multicast?
     Yes:
        3a) Flood the packet
            DONE
  4) Port for destination address in our address/port table?
     No:
        4a) Flood the packet
            DONE
  5) Is output port the same as input port?
     Yes:
        5a) Drop packet and similar ones for a while
  6) Install flow table entry in the switch so that this
     flow goes out the appopriate port
     6a) Send the packet out appropriate port
  """
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str, str_to_dpid
from pox.lib.util import str_to_bool
import time

from pox.forwarding.g import MyGlobals
#from pox.forwarding.stat import *
from pox.lib.revent import *
from pox.openflow.of_json import *
import math
import mysql.connector
import pandas as pd
import numpy as np
import datetime
from pox.lib.recoco import Timer
log = core.getLogger()
db = mysql.connector.connect(
                    host='localhost',
                    user='user',
                    password='password',
                    database='test')

mycursor =db.cursor()

_flood_delay = 0

class LearningSwitch (object):
  tcpflow = {}
  flowlist = []
  pflow = []
  nlist=[]
  ratio_l =[]
  threshold_1=[]
  threshold_2=[]
  def _timer_func(self, dt):
   # Copyright 2011-2012 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
An L2 learning switch.

It is derived from one written live for an SDN crash course.
It is somwhat similar to NOX's pyswitch in that it installs
exact-match rules for each flow.
"""
   
    Timer(dt, self.print_list, recurring=True)

  def __init__ (self, connection, transparent):
    # Switch we'll be adding L2 learning switch capabilities to
    self.connection = connection
    self.transparent = transparent

    # Our table
    self.macToPort = {}

    # We want to hear PacketIn messages, so we listen
    # to the connection
    connection.addListeners(self)

    # We just use this to know when to log a helpful message
    self.hold_down_expired = _flood_delay == 0

    #log.debug("Initializing LearningSwitch, transparent=%s",
    #          str(self.transparent))

  def _handle_PacketIn (self, event):
    """
    Handle packet in messages from the switch to implement above algorithm.
    """

    packet = event.parsed

    def flood (message = None):
      """ Floods the packet """
      msg = of.ofp_packet_out()
      if time.time() - self.connection.connect_time >= _flood_delay:
        # Only flood if we've been connected for a little while...

        if self.hold_down_expired is False:
          # Oh yes it is!
          self.hold_down_expired = True
          log.info("%s: Flood hold-down expired -- flooding",
              dpid_to_str(event.dpid))

        if message is not None: log.debug(message)
        #log.debug("%i: flood %s -> %s", event.dpid,packet.src,packet.dst)
        # OFPP_FLOOD is optional; on some switches you may need to change
        # this to OFPP_ALL.
        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
      else:
        pass
        #log.info("Holding down flood for %s", dpid_to_str(event.dpid))
      msg.data = event.ofp
      msg.in_port = event.port
      self.connection.send(msg)

    def drop (duration = None):
      """
      Drops this packet and optionally installs a flow to continue
      dropping similar ones for a while
      """
      if duration is not None:
        if not isinstance(duration, tuple):
          duration = (duration,duration)
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = duration[0]
        msg.hard_timeout = duration[1]
        msg.buffer_id = event.ofp.buffer_id
        self.connection.send(msg)
      elif event.ofp.buffer_id is not None:
        msg = of.ofp_packet_out()
        msg.buffer_id = event.ofp.buffer_id
        msg.in_port = event.port
        self.connection.send(msg)

    self.macToPort[packet.src] = event.port # 1

    if not self.transparent: # 2
      if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered():
        drop() # 2a
        return

    if packet.dst.is_multicast:
      flood() # 3a
    else:
      if packet.dst not in self.macToPort: # 4
        flood("Port for %s unknown -- flooding" % (packet.dst,)) # 4a
      else:
        port = self.macToPort[packet.dst]
        if port == event.port: # 5
          # 5a
          log.warning("Same port for packet from %s -> %s on %s.%s.  Drop."
              % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
          drop(10)
          return
        # 6
        log.debug("installing flow for %s.%i -> %s.%i" %
                  (packet.src, event.port, packet.dst, port))
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet, event.port)
        msg.idle_timeout = 10
        msg.hard_timeout = 30
        msg.actions.append(of.ofp_action_output(port = port))
        msg.data = event.ofp # 6a
        self.connection.send(msg)
        tcp_ack_flows=0
        threshold=0

        add=0
        flow=0
        #nlist=[]
        if packet.find('tcp') :
            tcp_found = packet.find('tcp')
            if tcp_found:
                add=0
                total_flows=0
                total_packets=0
                backoff=0
                flag=0
                #a=[self.tcpflow]
                #print "***************inside l2 learninig TCP**********************"

                for m in self.tcpflow:


                    if (str(msg.match.nw_src)+" "+str(msg.match.nw_dst) in self.tcpflow[m]) or (str(msg.match.nw_dst)+" "+str(msg.match.nw_src) in self.tcpflow[m]):
                        self.tcpflow[m]=list(self.tcpflow[m])
                        self.tcpflow[m]=tuple(self.tcpflow[m])
                        total_flows=total_flows+self.tcpflow[m][2]
                        total_packets=total_packets+self.tcpflow[m][3]
                        backoff=self.tcpflow[m][4]
                        backoff=MyGlobals.back_off
                        tcp_bytes += f.byte_count
                        tcp_flows += 1
                        add=add+1


                        msg.match.nw_src,msg.match.nw_dst,total_flows,total_packets,backoff=self.tcpflow.split('|')
                #     log.info("Host %s Host %s Flows %s Packets %s Backoff %s",msg.match.nw_src,msg.match.nw_dst,total_flows,total_packets,backoff)

                ts = time.time()
                timer = datetime.datetime.fromtimestamp(ts).strftime('%S')
                print "________________Timer fun",timer
                if (int(timer)>MyGlobals.end_timer):
                    tcp_found = packet.find('tcp')
                    if tcp_found.SYN:
                        MyGlobals.tcp_syn_flows+=1
                    print "<<<<<<<<SYN Packet Found",MyGlobals.tcp_syn_flows
                    x=MyGlobals.tcp_syn_flows
                    emwa=((MyGlobals.emwa_pre) + (0.5)*(x - MyGlobals.emwa_pre))
                    print":::::::EWMA::::::",emwa
                    MyGlobals.emwa_pre=emwa
                    alpha=0.5
                    sd=math.sqrt((alpha*pow((x-emwa),2))+((1-alpha)*pow(MyGlobals.sd_pre,2)))
                    MyGlobals.sd_pre=sd
                    print"^^^^^^^Standard Deviation^^^^",sd
                    MyGlobals.thresh_1=(emwa + sd)
                    print"^^^^^^^Threshhold Value 1 : - ",MyGlobals.thresh_1
                    for f in list(self.tcpflow.values()):
                        self.pflow.append(f[3])
                    for p in self.pflow:
                        c_total =sum(self.pflow)
                        #print "^^^^^^^^C Total^^^^^^",c_total
                        MyGlobals.p_ratio = ((self.pflow[p]*100)/c_total)
                        #print "****Ratio of Packet Count*****",p_ratio
                    xr=MyGlobals.p_ratio
                    emwa_r=((MyGlobals.emwa_r_pre) + (0.5)*(xr - MyGlobals.emwa_r_pre))
                    print":::::::EWMA of Ratio::::::",emwa_r
                    MyGlobals.emwa_r_pre=emwa_r
                    sd_r=math.sqrt((alpha*pow((xr-emwa_r),2))+((1-alpha)*pow(MyGlobals.sd_r_pre,2)))
                    MyGlobals.sd_r_pre=sd_r
                    print"^^^^^^^Standard Deviation of Ratio^^^^",sd_r
                    thresh_2=(emwa_r+(1)*sd_r)
                    print"?????Threshold 2????",thresh_2
                    ip_src=msg.match.nw_src
                    ip_dst=msg.match.nw_dst
                    data=[str(ip_src),str(ip_dst),timer]
                    for row in data:
                        #print row
                        #cur.execute("INSERT into table (tmp) VALUES (%s)" %row)
                        sql = "INSERT INTO pad (srcip,destip,daytime) VALUES (%s,%s,%s)"
                        val = (data)
                        mycursor.execute(sql, val)
                    db.commit()
                    MyGlobals.end_timer=int(timer)+3

                else:
                    if (MyGlobals.tcp_syn_flows>MyGlobals.thresh_1):
                        print"^^^^^^ TCP SYN is Greater Than Threshold 1"
                        ip_src=msg.match.nw_src
                        ip_dst=msg.match.nw_dst
                        key=[str(ip_src),str(ip_dst)]
                        mycursor.execute("SELECT srcip,destip FROM pad")
                        myresult = mycursor.fetchall()
                        if (list(myresult),key):
                            timer=MyGlobals.end_timer
                            print">>>>>>Detection phase 2"
                            Delete_all_rows = """truncate table pad """
                            mycursor.execute(Delete_all_rows)
                            db.commit()
                            print("All Record Deleted successfully ")
                        if (MyGlobals.p_ratio>MyGlobals.thresh_2):
                            msg=of.ofp_flow_mod()
                            msg.pripority=42
                            msg.actions.append(of.ofp_action_output(port=3))
                            self.connection.send(msg)
                            print"$$$$$$$pripority",msg.pripority
                        else:
                            timer=MyGlobals.end_timer
                            print">>>>>>Detection phase 2"
                            Delete_all_rows = """truncate table pad """
                            mycursor.execute(Delete_all_rows)
                            db.commit()
                            print("All Record Deleted successfully ")
                    else:
                        MyGlobals.tcp_syn_flows+=1
                        print"TCP SYN Flows",MyGlobals.tcp_syn_flows



class l2_learning (object):
  """
  Waits for OpenFlow switches to connect and makes them learning switches.
  """
  def __init__ (self, transparent):
    core.openflow.addListeners(self)
    self.transparent = transparent

  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s" % (event.connection,))
    LearningSwitch(event.connection, self.transparent)


def launch (transparent=False, hold_down=_flood_delay):
  """
  Starts an L2 learning switch.
  """
  try:
    global _flood_delay
    _flood_delay = int(str(hold_down), 10)
    assert _flood_delay >= 0
  except:
    raise RuntimeError("Expected hold-down to be a number")

  core.registerNew(l2_learning, str_to_bool(transparent))
