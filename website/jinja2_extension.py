from jinja2 import nodes
from jinja2.ext import Extension
from flask import g

class RequireExtension(Extension):
	tags = set(['require'])
	rendered = set()

	def __init__(self, environment):
		super(RequireExtension, self).__init__(environment)
		self.rendered = set()

	def parse(self, parser):
		if not g.get("jinja2_require", False):
			self.rendered.clear()
			g.jinja2_require = True

		lineno = next(parser.stream).lineno
		requirement = nodes.Include(lineno=lineno)
		requirement.template = parser.parse_expression()
		requirement.ignore_missing = False
		node = parser.parse_import_context(requirement, True)
		
		name = requirement.template.as_const()
		if name in self.rendered:
			return nodes.Output([])
		else:
			self.rendered.add(name)
			return node
