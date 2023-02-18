import os
import sys

DESCR_TAG = "<div class=\"Nd\">"

argc = len(sys.argv)

if argc < 2:
	print("Expecting path to binary output as an argument")
	exit(1)

path = sys.argv[1]
pages = {}

print("Getting list of manual pages ...")

for dir_path, _, filenames in os.walk(path):
	for filename in filenames:
		if \
			not filename.endswith(".1.gz") and \
			not filename.endswith(".2.gz") and \
			not filename.endswith(".3.gz") and \
			not filename.endswith(".4.gz") and \
			not filename.endswith(".5.gz") and \
			not filename.endswith(".6.gz") and \
			not filename.endswith(".7.gz") and \
			not filename.endswith(".8.gz") and \
			not filename.endswith(".9.gz"):
			continue

		if filename in pages:
			print(f"Found '{filename}' in multiple places: '{dir_path}' & '{pages[filename]}'")

		pages[filename] = dir_path

print("Processing manual pages ...")

script_path = "/".join(os.path.realpath(__file__).split('/')[:-1])

def try_cmd(cmd):
	if os.system(cmd):
		print(f"'{cmd}' failed")
		exit(1)

for filename, dir_path in pages.items():
	try:
		name, section, _ = filename.split('.')

	except Exception:
		continue

	print(f"Processing {name}({section}) ...")

	path = f"{dir_path}/{filename}"
	out = f"{script_path}/{name}.{section}.html"

	try_cmd(f"gunzip -c {path} | mandoc -T html -O fragment,includes='../src/%I.html',man='%N.%S.html' > {out}")

	# add the surrounding stuff

	with open(out) as f:
		fragment = f.read()

	fragment = fragment.replace("<h1", "<h2")
	fragment = fragment.replace("</h1", "</h2")

	descr_start = fragment.find(DESCR_TAG) + len(DESCR_TAG)
	descr_end = fragment.find("</div>", descr_start)
	descr = fragment[descr_start: descr_end] if descr_start > len(DESCR_TAG) else "no description"

	with open(out, "w") as f:
		f.write(f"""
<title>{name}({section})</title>
<description>{descr}</description>
<keywords>
	<keyword>man</keyword>
	<keyword>{name}</keyword>
</keywords>
<styles>
	<css src = "main.css" />
	<css src = "docs.css" />
	<css src = "navbar.css" />
	<css src = "footer.css" />
	<css src = "man.css" />
</styles>
<html>
	<head></head>
	<body>
		<component src = "navbar.html" />
		<div class = "docs-container">
			<component src = "docs/sidebar.html" />
			<div class = "docs">
				<h1>{name}({section})</h1>
				{fragment}
			</div>
		</div>
		<component src = "footer.html" />
	</body>
</html>
		""")
