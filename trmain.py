#!/usr/bin/env python

from subprocess import Popen, PIPE
import trparse.trparse as trp

# @see http://softwaredevelopment.gr/1074/traceroute-system-call-in-python/
def get_route(ip_address):
  p = Popen(['traceroute', ip_address], stdout=PIPE)
  output = ""

  while True:
    try:
      line = p.stdout.readline()
      if not line:
        break
      output += line
    except:
      break

  return output

class RouteParser(object):
  """
  This class adapts the trparse package into a common interface.
  """

  def __init__(self, route):
    super(RouteParser, self).__init__()
    self._route = trp.loads(route)

  def total_time(self):
    """
    Each route comprises multiple hops (each IP between the source and destination).
    Each of those comprises three probes, each with their own duration.
    With this, we add up the maximum route times to get a total path length.
    IMPORTANT QUESTION: Should this be minimum?
    """
    # Uncomment for debugging.
    # print [[probe.rtt for probe in hop.probes] for hop in self._route.hops]
    return sum([max([probe.rtt for probe in hop.probes]) for hop in self._route.hops])

  def all_stops(self):
    pass
    

#def parse_route(route):
#  duration = max([[[probe.rtt for probe in hop.probes] for hop in route.]])

def main():
  route = get_route("8.8.8.8")
  parser = RouteParser(route)
  print parser.total_time()

if __name__ == '__main__':
  main()