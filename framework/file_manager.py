import os
import pathlib

import log
from page import Page

DEFAULT_ROOT = "site"
DEFAULT_OUT = "out"

class File_manager:
	def __init__(self, root = DEFAULT_ROOT, out = DEFAULT_OUT):
		self.root = root
		self.out = out
	
	def __read(self, type_name, type_dir, name):
		path = pathlib.Path(self.root, type_dir, name)

		try:
			with open(path) as f:
				return f.read()
		
		except FileNotFoundError:
			log.fatal(f"Failed to load {type_name} {name} ({path})")
			return ""
		
		except Exception:
			log.internal_fatal()

	def read_style(self, name):
		return self.__read("style", "styles", name)

	def read_component(self, name):
		return self.__read("component", "components", name)

	def __walk(self, path):
		for dirpath, dirnames, filenames in os.walk(path):
			for filename in filenames:
				src_path = pathlib.Path(dirpath, filename)
				
				if filename.split('.')[-1] != "html":
					log.warn(f"Found non-HTML file ({src_path})")
				
				yield src_path

	def walk(self):
		log.info("Reading pages ...")
		path = pathlib.Path(self.root, "pages")

		if not os.path.isdir(path):
			log.fatal(f"Pages folder doesn't exist ({path})")

		# read all the pages first before processing any of them
		# this is so that any errors with reading are caught before anything is generated

		pages = []

		for src_path in self.__walk(path):
			page = Page(self, src_path)
			pages.append(page)

		log.info("Generating output ...")

		for page in pages: # TODO progress bar
			page.process()

		log.info("Creating output directory structure")

		try:
			os.mkdir(self.out)
		
		except FileExistsError:
			log.fatal(f"Output directory '{self.out}' already exists")

		for dirpath, dirnames, filenames in os.walk(path):
			for dirname in dirnames:
				os.mkdir(pathlib.Path(self.out, dirname))

		log.info("Writing output ...")

		for page in pages:
			parts = pathlib.Path(page.path).parts
			path = pathlib.Path(self.out, *parts[2:])

			with open(path, "w+") as f:
				f.write(page.out_html)