# TODO add colours!

import traceback

def info(msg):
	print(msg)

def warn(msg):
	print(f"WARNING {msg}")

def internal_fatal():
	print(traceback.format_exc())
	print("INTERNAL ERROR, ABORTING NOW")
	exit(1)

def fatal(msg):
	print(f"FATAL ERROR {msg}")
	exit(1)