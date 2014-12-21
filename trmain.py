#!/usr/bin/env python

from subprocess import Popen, PIPE

# @see http://softwaredevelopment.gr/1074/traceroute-system-call-in-python/
def get_route(ip_address):
  p = Popen(['traceroute', ip_address], stdout=PIPE)

  while True:
    try:
      line = p.stdout.readline()
      if not line:
        break
      print line.rstrip() # removes blank newlines.
    except:
      break

def main():
  get_route("8.8.8.8")

if __name__ == '__main__':
  main()