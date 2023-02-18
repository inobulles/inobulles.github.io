import os
import pathlib
import shutil

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
		for dir_path, _, filenames in os.walk(path):
			for filename in filenames:
				src_path = pathlib.Path(dir_path, filename)

				if filename.split('.')[-1] != "html":
					log.warn(f"Found non-HTML file ({src_path})")
					continue

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

		log.info("Creating output directory structure by first copying resources tree")

		shutil.copytree(pathlib.Path(self.root, "res"), self.out)

		for dirpath, dirnames, filenames in os.walk(path):
			for dirname in dirnames:
				os.mkdir(pathlib.Path(self.out, dirname))

		log.info("Writing output ...")

		for page in pages:
			parts = pathlib.Path(page.path).parts
			path = pathlib.Path(self.out, *parts[2:])

			with open(path, "w+") as f:
				f.write(page.out_html)
