#!/usr/bin/env python

from subprocess import Popen, PIPE
import os # for writing to folder.

import netaddr # If this doesn't exist, run 'sudo pip install netaddr'.

import re # For cleaning things.

import trparse.trparse as trp


# @see http://softwaredevelopment.gr/1074/traceroute-system-call-in-python/
def get_route(ip_address):
  p = Popen(['traceroute', str(ip_address)], stdout=PIPE)
  output = ""

  while True:
    try:
      line = p.stdout.readline()
      if not line:
        break
      output += line
    except:
      break
  # Weird preprocessing thing for when outside the US.
  output = re.sub(r".in-addr.arpa", r"", output)
  return output



def IPAddress(x):
  try:
    return netaddr.IPAddress(x)
  except Exception, e:
    raise e



class RouteParser(object):
  """
  This class adapts the trparse package into a common interface.
  """

  def __init__(self):
    super(RouteParser, self).__init__()

  @property
  def route(self):
    """Returns the route AST the parser is currently processing."""
    return self._route
  @route.setter
  def route(self, value):
    self._route = trp.loads(value)
  
  def error_condition(self):
    for hop in self.route.hops:
      for probe in hop.probes:
        if probe.anno:
          return probe.anno
    return "success"

  def total_time(self):
    """
    Each route comprises multiple hops (each IP between the source and destination).
    Each of those comprises three probes, each with their own duration.
    With this, we add up the maximum route times to get a total path length.
    IMPORTANT QUESTION: Should this be minimum?
    """
    # Uncomment for debugging.
    # print [[probe.rtt for probe in hop.probes] for hop in self._route.hops]
    return sum([max([probe.rtt for probe in hop.probes]) for hop in self.route.hops])

  def ip_list(self):
    """
    Get all IPs along the way.
    """
    # Hops themselves don't contain an IP address.
    # Still, each probe should have the same IP address.
    # That means, we could get the IP of any probe to represent its hop.
    return [hop.probes[0].ip for hop in self.route.hops]



class TraceroutePrinter(object):
  """docstring for TraceroutePrinter"""
  def __init__(self):
    super(TraceroutePrinter, self).__init__()

  @staticmethod
  def ensureDataFolderExists():
    if not os.access('./data', os.F_OK):
      os.makedirs('./data')

  @staticmethod
  def printDataToFile(parser, dest_ip):
    TraceroutePrinter.ensureDataFolderExists()
    with open('data/' + str(dest_ip) + ".txt", 'w') as file:
      print >> file, parser.error_condition()
      print >> file, "\n".join(parser.ip_list())
      print >> file, str(parser.total_time()) + " ms"   


class TracerouteProcessor(object):
  """docstring for TracerouteProcessor"""
  def __init__(self):
    super(TracerouteProcessor, self).__init__()

  @property
  def parser(self):
    try:
      return self._parser
    except:
      self._parser = RouteParser() # Lazy instantiation.
      return self._parser
  @parser.setter
  def parser(self, value):
      self._parser = value
  
  @property
  def printer(self):
    try:
      return self._printer
    except:
      self._printer = TraceroutePrinter()
      return self._printer
  @printer.setter
  def printer(self, value):
      self._printer = value
  
  def process_ip(self, ip_address):
    route = get_route(ip_address)
    # We do this next step instead of making a new parser
    # for performance reasons: if we process millions of IPs,
    # we'd be making millions of parser objects. 
    try:
      self.parser.route = route
    except Exception, e:
      print ' '.join(['trparse:', str(e)])
      return # Typically, this signifies a failed routing. Fail silently, move on.
    self.printer.printDataToFile(self.parser, ip_address)

  def process_ip_list(self, ip_list):
    for ip in ip_list:
      self.process_ip(ip)



def main():
  processor = TracerouteProcessor()
  processor.process_ip_list(IPAddress(x) for x in ["8.8.8.8", "127.000.000.1"])

if __name__ == '__main__':
  main()