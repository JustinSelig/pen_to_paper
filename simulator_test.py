import argparse
import msgpackrpc
import sys

def parse_args():
  parser = argparse.ArgumentParser(description='Interact with plotter.')
  parser.add_argument('-H', '--host', default='localhost', help="Host")
  return parser.parse_args()

def main():
  args = parse_args()
  client = msgpackrpc.Client(msgpackrpc.Address(args.host, 18800))
  print "Connected!"

  INCREASE = 1
  DECREASE = -1

  while True:
    cmd = sys.stdin.read(1)

    if cmd == "i":
        client.call('tick_left', INCREASE)
    elif cmd == "o":
        client.call('tick_right', INCREASE)
    elif cmd == "k":
        client.call('tick_left', DECREASE)
    elif cmd == "l":
        client.call('tick_right', DECREASE)
    elif cmd == "z":
        client.call('pen_up')
    elif cmd == "x":
        client.call('pen_down')
    elif cmd == "r":
        client.call('reset')
    elif cmd == "q":
        client.call('tick', INCREASE, INCREASE)
    elif cmd == "a":
        client.call('tick', DECREASE, DECREASE)

if __name__ == '__main__':
  main()