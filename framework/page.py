import re
import bs4
import htmlmin

import log

class Page:
	def __init__(self, file_manager, path):
		self.file_manager = file_manager
		self.path = path

		with open(self.path) as f:
			self.raw = f.read()
		
		self.soup = self.parse(self.raw)
		self.out_html = ""

		# attributes

		self.title = "Unknown"
		self.description = "Unknown"
		
		self.keywords = []
		self.styles = []

	def __str__(self):
		return f"Page '{self.title}'"

	def parse(self, raw):
		return bs4.BeautifulSoup(raw, "lxml")

	def minify_css(self, raw):
		# from this excellent answer on stackoverflow: https://stackoverflow.com/questions/222581/python-script-for-minifying-css

		raw = re.sub(r'/\*[\s\S]*?\*/', '', raw) # remove comments
		raw = re.sub(r'url\((["\'])([^)]*)\1\)', r'url(\2)', raw) # remove 'url()' quotes
		raw = re.sub(r'\s+', ' ', raw) # collapse spaces
		raw = re.sub(r'#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3(\s|;)', r'#\1\2\3\4', raw) # collapse colours
		raw = re.sub(r':\s*0(\.\d+([cm]m|e[mx]|in|p[ctx]))\s*;', r':\1;', raw) # remove extraneous zeros

		css = raw # because there's an issue for special props like @media with nested braces

		"""
		css = ""

		for rule in re.findall(r'([^{]+){([^}]*)}', raw):
			# selectors = [re.sub(r'(?<=[\[\(>+=])\s+|\s+(?=[=~^$*|>+\]\)])', r'', selector.strip()) for selector in rule[0].split(',')] # remove spaces around operators
			selectors = map(str.strip, rule[0].split(',')) # previous line was breaking something

			props = {}
			order = []

			for prop in re.findall('(.*?):(.*?)(;|$)', rule[1]):
				key = prop[0].strip().lower()

				if key not in order:
					order.append(key)
				
				props[key] = prop[1].strip()
			
			if props:
				selector = ','.join(selectors)
				props = ''.join([f"{key}:{props[key]};" for key in order])[:-1]

				css += f"{selector}{{{props}}}"
		"""

		return css

	def process(self):
		# read all attributes

		title = self.soup.title
		description = self.soup.description
		keywords = self.soup.keywords
		styles = self.soup.styles

		if title:
			self.title = title.string
			title.decompose()

		else:
			log.fatal(f"{self} doesn't have a title")

		if description:
			self.description = description.string

			if not self.description:
				self.description = "unreadable description"

			if len(self.description) > 275:
				log.warn(f"{self} description should be no longer than 275 characters (as per Google's 2017 max length on the SERP)")

			description.decompose()
		
		else:
			log.warn(f"{self} doesn't have a description")

		if keywords:
			for child in keywords:
				if child.name is None:
					continue

				if child.name != "keyword":
					log.warn(f"{self} 'keywords' tag may only contain 'keyword' tags! (found '{child.name}' instead)")
					continue
				
				self.keywords.append(child.string)

			keywords.decompose()
		
		if styles:
			for child in styles:
				if child.name is None:
					continue

				if child.name != "css":
					log.warn(f"{self} 'styles' tag may only contain 'css' tags! (found '{child.name}' instead)")
					continue
				
				path = child.get("src")

				if path is None:
					log.warn(f"{self} 'css' tag must have a 'src' attribute")

				self.styles.append(path)
			
			styles.decompose()
		
		# make sure of a few things

		if self.soup.html is None:
			log.fatal(f"{self} must have a 'html' tag")
		
		head = self.soup.html.head
		body = self.soup.html.body

		if head is None:
			log.fatal(f"{self} must have a 'head' tag")
		
		if body is None:
			log.fatal(f"{self} must have a 'body' tag")

		# add stuff in head

		head.append(self.soup.new_tag("meta", charset = "UTF-8")) # must be in the first 1024 bytes of the document
		# head.append(self.soup.new_tag("meta", name = "viewport", content = "width=device-width,initial-scale=1"))
		# head.append(self.soup.new_tag("meta", name = "robots", content = "index,follow"))
		# head.append(self.soup.new_tag("meta", name = "description", content = self.description))
		
		title = self.soup.new_tag("title")
		title.string = self.title
		head.append(title)

		keywords = ','.join(self.keywords)
		head.append(self.soup.new_tag("keywords", content = keywords))

		# add styles

		styles = self.soup.new_tag("style")
		styles.string = ""

		for style in self.styles:
			raw = self.file_manager.read_style(style)
			styles.string += self.minify_css(self.file_manager.read_style(style))

		head.append(styles)

		# substitute all components

		components = self.soup.find_all("component")

		for component in components:
			path = component.get("src")
			
			if path is None:
				log.warn(f"{self} 'component' tag must have a 'src' attribute")
				continue

			raw = self.file_manager.read_component(path)
			soup = self.parse(raw)

			component.replaceWith(soup)

		# minify and output

		self.out_html = "<!DOCTYPE html>\n"
		self.out_html += htmlmin.minify(str(self.soup), remove_all_empty_space = True, remove_comments = True)
