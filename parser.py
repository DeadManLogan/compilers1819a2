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
            (mask_and, 'and'),
            (mask_or, 'or'),
            (mask_xor, 'xor'),
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
			self.match('ID_TOKEN')
			self.match('=')
			self.expr()
		elif self.la == 'PRINT_TOKEN':
			self.match('PRINT_TOKEN')
			print(self.expr())
		else:
			raise ParseError("Expected id or print")


	def expr(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'digit':
			self.term()
			self.term_tail()
		else:
			raise ParseError("Expecting ( or id or digit")


	def term_tail(self):
		if self.la == 'and':
			self.match('and')
			self.term()
			self.term_tail()
		elif self.la == 'ID_TOKEN' or self.la == 'PRINT' or self.la == None or self.la == ')':
			return
		else:
			raise ParseError('Expected and')


	def term(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'digit':
			self.factor()
			self.factor_tail()
		else:
			raise ParseError("Expected (,id or digit")


	def factor_tail(self):
		if self.la == 'or':
			self.match('or')
			self.factor()
			self.factor_tail()
		elif self.la == 'and' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None or self.la == ')':
			return
		else:
			raise ParseError('Expected or')


	def factor(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'digit':
			self.atom()
			self.atom_tail()

		else:
			raise ParseError("Expecting (,digit or id ")


		def atom_tail(self):
			if self.la == 'xor':
				self.match('xor')
				self.atom()
				self.atom_tail()
			elif self.la == 'or' or self.la == 'and' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None or self.la == ')':
				return
			else:
				raise ParseError('Expected xor')


		def atom(self):
			if self.la == '(':
				self.match('(')
				self.expr()
				self.match(')')
			elif self.la == 'ID_TOKEN':
				self.match('ID_TOKEN')
			elif self.la == 'digit':
				self.match('digit')
			else:
				raise ParseError("Expecting (,digit or id ")


parser = MyParser()

with open('new.txt', 'r') as fp:
	parser.parse(fp)


