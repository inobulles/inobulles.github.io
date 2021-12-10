import sys

import log
from file_manager import File_manager

if __name__ == "__main__":
	args = sys.argv[1:]

	file_manager = File_manager(*args)
	file_manager.walk()

	log.info("Done!")