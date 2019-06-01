import plex

class ParseError(Exception):
	pass

class MyParser:

	def __init__(self):

		letter = plex.Range('azAZ')
		digit = plex.Range('01')
		name = letter + plex.Rep(letter|digit)
		digit2 = plex.Rep1(digit)

		space = plex.Any(' \n\t')

		keyword = plex.Str('print','PRINT')

		equals = plex.Str( '=')
		parethensys1 = plex.Str('(')
		parethensys2 = plex.Str(')')

		mask_and = plex.Str('and')
		mask_or = plex.Str('or')
		mask_xor = plex.Str('xor')

		self.lexicon = plex.Lexicon([
			(keyword, 'PRINT_TOKEN'),
			(name, 'ID_TOKEN'),             #name = letter + plex.Rep(letter|digit)
			(equals, '='),
			(parethensys1, '('),
			(parethensys2, ')'),
			(space, plex.IGNORE),
            (mask_and, plex.TEXT),
            (mask_or, plex.TEXT),
            (mask_xor, plex.TEXT),
			(digit2, 'digit')
		])

	def createScanner(self,fp):
		self.scanner = plex.Scanner(self.lexicon,fp)
		self.la , self.text = self.next_token()


	def next_token(self):
		return self.scanner.read()


	def match(self,token):
		if self.la == token:
			self.la, self.text=self.next_token()
		else:
			raise ParseError(" waiting for something to be received ")


	def parse(self,fp):
		self.createScanner(fp)
		self.stmt_list()


	def stmt_list(self):
		if self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN':
			self.stmt()
			self.stmt_list()
		elif self.la == None:
			return
		else:
			raise ParseError("Expected id or print")


	def stmt(self):
		if self.la == 'ID_TOKEN':
			varname = self.text
			self.match('ID_TOKEN')
			self.match('=')
			e = self.expr()
			self.st[varname] = e
		elif self.la == 'PRINT_TOKEN':
			self.match('PRINT_TOKEN')
			print(self.expr())
		else:
			raise ParseError("Expected id or print")


	def expr(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'digit':
			t = self.term()
			while self.la == 'and':
				self.match('and')
				t &= self.term()
			if self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None or self.la == ')':
				return t
			raise ParseError("Expecting and")
		else:
			raise ParseError("Expecting (,id or digit")


	def term(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'digit':
			f = self.factor()
			while self.la == 'or':
				self.match('or')
				f |= self.factor()
			if self.la == 'and' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None or self.la == ')':
				return f
			raise ParseError("Expected or ")
		else:
			raise ParseError("Expected (,id or digit")


	def factor(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'digit':
			a = self.atom()
			while self.la == 'xor':
				self.match('xor')
				a &= self.atom()
			if self.la == 'and' or self.la == 'or' or self.la == 'ID_TOKEN' or self.la == 'print' or self.la == None or self.la == ')':
				return a
			raise ParseError('Expected a')
		else:
			raise ParseError("Expecting (,digit or id ")


	def atom(self):
		if self.la == '(':
			self.match('(')
			e = self.expr()
			self.match(')')
		elif self.la == 'ID_TOKEN':
			varname = self.text
			self.match('ID_TOKEN')
			if varname in self.st:
				return self.st[varname]
			raise RunError("no value")
		elif self.la == 'digit':
			value = float(self.text)
			self.match('digit')
			return value
		else:
			raise ParseError("Expecting (,digit or id ")


parser = MyParser()

with open('new.txt', 'r') as fp:
	parser.parse(fp)
