
import logging

import chars as mork_chars
from store import *


class ParseException(BaseException): pass


class Interface:
	"""
	This is dummy interface which should be implemented by any mork parser/builder.
	"""
	def on_alias(self, in_mid): pass
	def on_cell_form(self, in_charset_format): pass
	def on_minus_cell(self): pass
	def on_minus_row(self): pass
	def on_new_cell(self, in_mid, in_buf): pass
	def on_new_dict(self): pass
	def on_new_meta(self): pass
	def on_new_port(self): pass
	def on_new_row(self, in_mid, in_cut_all_cols): pass
	def on_new_table(self, in_mid, in_cut_all_rows): pass
	def on_value_mid(self, in_mid): pass
	def on_value(self, in_buf): pass
	def on_row_pos(self, row_pos): pass
	def on_new_group(self, group_id): pass
	###
	def on_cell_end(self): pass
	def on_dict_end(self): pass
	def on_meta_end(self): pass
	def on_port_end(self): pass
	def on_row_end(self): pass
	def on_table_end(self): pass
	def on_group_commit_end(self): pass
	###
	def error(self, msg, *args): raise ParseException(msg % (args))
	def warning(self, msg, *args): logging.getLogger().warning(msg % (args))
  ###
	def EofInsteadOfHexError(self):
		self.error("eof instead of hex error")
	def ExpectedHexDigitError(self, c):
		self.error("expected hex digit, found: %s", c)
	def ExpectedEqualError(self):
		self.error("unexpected equal error")
	def UnexpectedByteInMetaWarning(self):
		self.warning("unexpected byte in meta")
	def UnexpectedEofError(self):
		self.error("unexpected eof error")
	def NewError(self, msg):
		self.error(msg)



class Parser(Interface):
	"""
	The main mork parser. It only parses the file and calls the interface callbacks.
	"""
	def __init__(self, f):
		if f is None:
			raise ParseException("Cannot parse None")

		self.buffered = None
		self.file = f
		
		self.buff = ''
		self.buff_len = 512
		self.pos = self.buff_len # to force reset on next read

		self.mid = Mid() # current alias being parsed
		self.table_mid = Mid()
		self.row_mid = Mid()
		self.cell_mid = Mid()
		
		self.in_table = False
		self.in_dict = False
		self.in_meta = False
		self.in_cell = False

		self.table_change = None

		self.change = None
		
		self.table_status = None


	def parse(self):
		"""
		Parse the mork file.
		"""
		self.change = None
		self.start_parse()
		self.on_port_state()


	def start_parse(self):
		self.in_cell = False
		self.in_meta = False
		self.in_dict = False
		self.in_port_row = False
		
		self.row_mid.clear_mid()
		self.table_mid.clear_mid()
		self.cell_mid.clear_mid()
		
		self.group_id = 0
		self.in_port = True


	def on_port_state(self):
		self.in_port = True
		self.on_new_port()
		while self.read_content(False): pass
		self.in_port = False 
		self.on_port_end()

	def read_content(self, in_inside_group):
		while True:
			c = self.next_char()
			if c == None: break
			#
			if c == '[':
				self.read_row('[')
			elif c == '{':
				self.read_table()
			elif c == '<':
				self.read_dict()
			elif c == '@':
				return self.read_at(in_inside_group)
			else:
				self.warning('unexpected byte in read_content: %s', c)
		return c != None
	
	def read_hex(self):
		"""
		zm:Hex   ::= [0-9a-fA-F] /* a single hex digit */
		zm:Hex+  ::= zm:Hex | zm:Hex zm:Hex+
		"""
		hex = 0
		c = self.next_char()
		if c != None:
			if mork_chars.is_hex(c):
				while True:
					if mork_chars.is_digit(c): # '0' through '9'?
						v = ord(c) - ord('0')
					elif mork_chars.is_upper(c): # 'A' through 'F'?
						v = ord(c) - (ord('A') - 10) # c = (c - 'A') + 10;
					else: # 'a' through 'f'?
						v = ord(c) - (ord('a') - 10) # // c = (c - 'a') + 10;
					hex = (hex << 4) + v
					c = self.getc()
					if not (c != None and mork_chars.is_hex(c)): break
			else:
				self.ExpectedHexDigitError(c)
		if c == None:
			self.EofInsteadOfHexError()
		return hex, c

	def hex_to_byte(self, inFirstHex, inSecondHex):
		if not mork_chars.is_hex(inFirstHex): inFirstHex = ''
		if not mork_chars.is_hex(inSecondHex): inSecondHex = '0'
		if inFirstHex == '' and inSecondHex == '': return 0
		return int(inFirstHex + inSecondHex, 16)

	def read_row(self, c):
		"""
		zm:Row       ::= zm:S? '[' zm:S? zm:Id zm:RowItem* zm:S? ']'
		zm:RowItem   ::= zm:MetaRow | zm:Cell
		zm:MetaRow   ::= zm:S? '[' zm:S? zm:Cell* zm:S? ']' /* meta attributes */
		zm:Cell      ::= zm:S? '(' zm:Column zm:S? zm:Slot? ')'
		"""
		if self.change != None:
			self.row_change = self.change

		cutAllRowCols = False

		if c == '[':
			c = self.next_char()
			if c == '-':
				cutAllRowCols = True
			elif c != None:
				self.ungetc(c)

			if self.read_mid(self.row_mid):
				self.in_row = True
				self.on_new_row(self.row_mid, cutAllRowCols)

				self.row_change = None
				self.change = None

				while True:
					c = self.next_char()
					if not (c != None and c != ']'): break
					#
					if c == '(': # cell
						self.read_cell()
					elif c == '[': # meta
						self.read_meta(']')
					elif c == '-': # minus
						self.on_minus_cell()
					else:
						self.warning("unexpected byte in row: %s", c)

				c = self.next_char()
				if c == '!':
					self.read_row_pos()
				elif c != None:
					self.ungetc(c)
				self.in_row = False
				self.on_row_end()

		else: # c != '['
			self.ungetc(c)
			if self.read_mid(self.row_mid):
				self.in_row = True
				self.on_new_row(self.row_mid, cutAllRowCols)

				self.change = None
				self.row_change = None
				
				c = self.next_char()
				if c  == '!':
					self.read_row_pos()
				elif c != None:
					self.ungetc(c)

				self.in_row = False
				self.on_row_end()

	def read_row_pos(self):
		row_pos, c = self.read_hex()
		if c != None: # should put back byte after hex?
			self.ungetc(c)
		self.on_row_pos(row_pos)

	def read_table(self):
		"""
		zm:Table     ::= zm:S? '{' zm:S? zm:Id zm:TableItem* zm:S? '}'
		zm:TableItem ::= zm:MetaTable | zm:RowRef | zm:Row
		zm:MetaTable ::= zm:S? '{' zm:S? zm:Cell* zm:S? '}' /* meta attributes */
		"""
		if self.change != None:
			self.table_change = self.change

		cutAllTableRows = False
		
		c = self.next_char()
		if c == '-':
			cutAllTableRows = True
		elif c != None:
			self.ungetc(c)
		
		if self.read_mid(self.table_mid):
			self.in_table = True
			self.on_new_table(self.table_mid, cutAllTableRows)

			self.change = None
			self.table_change = None

			while True:
				c = self.next_char()
				if not (c != None and c != '}'): break
				#
				if mork_chars.is_hex(c):
					self.read_row(c)
				else:
					if c == '[': # row
						self.read_row('[')
					elif c == '{': # meta
						self.read_meta('}')
					elif '-': # minus
						self.on_minus_row()
					else:
						self.warning("unexpected byte in table: %s", c)

			self.in_table = False
			self.on_table_end()

	def match_pattern(self, inPattern):
		for byte in inPattern:
			c = self.getc()
			if c != byte:
				self.error("byte not in expected pattern: %s", inPattern)
				return False
		return True

	def read_group(self):

		self.group_id, next = self.read_hex()
		if next == '{':
			c = self.getc()
			if c == '@':
				#FIXME: Here we should save position, then find the content end
				# and if it is ok and commited seek to the start parse it and
				# save to storage...
				# FIXME: s->Seek(ev, startPos, &outPos);
				self.on_new_group(self.group_id)
				self.read_content(True)
				self.on_group_commit_end()
			else:
				self.error("expected '@' after @$${id{")
		else:
			self.error("expected '{' after @$$id")

	def read_at(self, in_inside_group):
		"""
		groups must be ignored until properly terminated
		zm:Group       ::= zm:GroupStart zm:Content zm:GroupEnd /* transaction */
		zm:GroupStart  ::= zm:S? '@$${' zm:Hex+ '{@' /* xaction id has own space */
		zm:GroupEnd    ::= zm:GroupCommit | zm:GroupAbort
		zm:GroupCommit ::= zm:S? '@$$}' zm:Hex+ '}@'  /* id matches start id */
		zm:GroupAbort  ::= zm:S? '@$$}~~}@' /* id matches start id */
		We must allow started transactions to be aborted in summary files.
		Note '$$' will never occur unescaped in values we will see in Mork.
		"""
		if self.match_pattern("$$"):
			c = self.getc()
			if c == '{' or c == '}':
				if c == '{': # start of new group?
					if not in_inside_group:
						self.read_group()
					else:
						self.error("nested @$${ inside another group")
				else: # c == '}' // end of old group?
					if in_inside_group:
						self.read_end_group_id()
						self.group_id = 0
					else:
						self.error("unmatched @$$} outside any group")
			else:
				self.error("expected '{' or '}' after @$$")
		return True

	def find_group_end(self):
		foundEnd = False
		# char gidBuf[ 64 ]; // to hold hex pattern we want
		# (void) ev->TokenAsHex(gidBuf, mParser_GroupId);
		while True:
			c = self.getc()
			if not (c != None and not foundEnd): break
			#
			if c == '@': # maybe start of group ending?
				c = self.getc()
				if c == '$': # '$' follows '@' ?
					c = self.getc()
					if c == '$': # '$' follows "@$" ?
						c = self.getc()
						if c == '}':
							foundEnd = self.read_end_group_id()
						else:
							self.error("expected '}' after @$$")
				if not foundEnd and c == '@':
					self.ungetc(c)
		return foundEnd


	def read_end_group_id(self):
		outSawGroupId = False
		c = self.getc()
		if c != None:
			if c == '~': # transaction is aborted?
				self.match_pattern("~}@") # finish rest of pattern
			else: # push back byte and read expected trailing hex id
				self.ungetc(c)

				endGroupId, next = self.read_hex()
				if endGroupId == self.group_id: # matches start?
					if next == '}': # '}' after @$$}id ?
						c = self.getc()
						if c == '@': # '@' after @$$}id} ?
							# looks good, so return with no error
							outSawGroupId = True
						else:
							self.error("expected '@' after @$$}id}")
					else:
						self.error("expected '}' after @$$}id")
				else:
					self.error("end group id mismatch")
		return outSawGroupId


	def read_dict(self):
		self.in_dict = True
		self.on_new_dict()
		while True:
			c = self.next_char()
			if not (c != None and c != '>'): break
			#
			if c == '(': # alias
				self.read_alias()
			elif c == '<': # meta
				self.read_meta('>')
			else:
				self.warning("unexpected byte in dict %s", c)
		self.in_dict = False
		self.on_dict_end()


	def read_alias(self):
		"""
		zm:Alias     ::= zm:S? '(' ('#')? zm:Hex+ zm:S? zm:Value ')'
		zm:Value   ::= '=' ([^)$\] | '\' zm:NonCRLF | zm:Continue | zm:Dollar)*
		"""
		
		hex, c = self.read_hex()

		self.mid.clear_mid()
		self.mid.oid.id = hex
		
		if mork_chars.is_white(c):
			c = self.next_char()
		
		if c == '<':
			self.read_dict_form()
			c = self.next_char()
			
		if c == '=':
			self.mid.buf = self.read_value()
			if self.mid.buf != None:
				self.on_alias(self.mid)
		else:
			self.ExpectedEqualError()

	def read_dict_form(self):
		"""TODO: Anyone seen this? let me know..."""
		nextChar = self.next_char()
		if nextChar == '(':
			nextChar = self.next_char()
			if nextChar == chr(Store.kFormColumn):
				nextChar = self.next_char()
				if nextChar == '=':
					dictForm = self.next_char()
					nextChar = self.next_char()
				elif nextChar == '^':
					dictForm, nextChar = self.read_hex()
				else:
					self.warning("unexpected byte in dict form")
					return
				# FIXME: mParser_ValueCoil.mText_Form = dictForm
				if nextChar == ')':
					nextChar = self.next_char()
					if nextChar == '>':
						return
		self.warning("unexpected byte in dict form")


	def read_meta(self, in_end_meta):
		"""
		zm:MetaDict  ::= zm:S? '<' zm:S? zm:Cell* zm:S? '>' /* meta attributes */
		zm:MetaTable ::= zm:S? '{' zm:S? zm:Cell* zm:S? '}' /* meta attributes */
		zm:MetaRow   ::= zm:S? '[' zm:S? zm:Cell* zm:S? ']' /* meta attributes */
		"""
		self.in_meta = True
		self.on_new_meta()

		# until end meta
		more = True
		while True:
			if not more: break
			c = self.next_char()
			if c == None: break
			#
			if c == '(': # cell
				self.read_cell()
			elif c == '>': # maybe end meta?
				if in_end_meta == '>': # stop reading meta
					more = False
				else:
					self.UnexpectedByteInMetaWarning()
			elif c == '}': # maybe end meta?
				if in_end_meta == '}': # stop reading meta
					more = False
				else:
					self.UnexpectedByteInMetaWarning()
			elif c == ']': # maybe end meta?
				if in_end_meta == ']': # stop reading meta
					more = False
				else:
					self.UnexpectedByteInMetaWarning()
			elif c == '[': # maybe table meta row?
				if self.in_table:
					self.read_row('[')
				else:
					self.UnexpectedByteInMetaWarning()
			else:
				if self.in_table and mork_chars.is_hex(c):
					self.read_row(c)
				else:
					self.UnexpectedByteInMetaWarning()
		self.in_meta = False
		self.on_meta_end()

	def read_cell_form(self, c):
		assert ord(c) == Store.kFormColumn
		nextChar = self.next_char()
		if nextChar == '=':
			cellForm = self.next_char()
			nextChar = self.next_char()
		elif nextChar == '^':
			cellForm, nextChar = self.read_hex()
		else:
			self.warning("unexpected byte in cell form")
			return

		## ### not sure about this. Which form should we set?
		##    mBuilder_CellForm = mBuilder_RowForm = cellForm;
		if nextChar == ')':
			self.on_cell_form(cellForm)
			return
		self.warning("unexpected byte in cell form")


	def read_mid(self, outMid):
		outMid.clear_mid();
		outMid.oid.id, c = self.read_hex()
		if c == ':':
			c = self.getc()
			if c != None:
				if c == '^':
					outMid.oid.scope, next = self.read_hex()
					self.ungetc(next)
				elif mork_chars.is_name(c):
					outMid.buf = self.read_name(c)
				else:
					self.NewError("expected name or hex after ':' following ID")
			if c == None:
				self.UnexpectedEofError()
		else:
			self.ungetc(c)
		return True


	def read_cell(self):
		
		self.cell_mid.clear_mid()
		cell_mid = None # if mid syntax is used for column
		cell_buf = None # if naked string is used for column

		c = self.getc()
		if c != None:
			if c == '^':
				cell_mid = self.cell_mid
				self.read_mid(cell_mid)
			else:
				if self.in_meta and ord(c) == Store.kFormColumn:
					self.read_cell_form(c)
					return
				else:
					cell_buf = self.read_name(c)

			self.in_cell = True
			self.on_new_cell(cell_mid, cell_buf)

			self.cell_change = None
			c = self.next_char()
			if c != None:
				if c == '=':
					buf = self.read_value()
					if buf != None:
						self.on_value(buf)
				elif c == '^':
					if self.read_mid(self.mid):
						c = self.next_char()
						if c != None:
							if c != ')':
								self.error("expected ')' after cell ^ID value")
						elif c == None:
							self.UnexpectedEofError()
						self.on_value_mid(self.mid)
				elif c == 'r' or c == 't' or c == '"' or c == '\'':
					self.error("cell syntax not yet supported")
				else:
					self.error("unknown cell syntax %s" % c)
			
			self.in_cell = False
			self.on_cell_end()

		self.cell_change = None

		if c == None:
			self.UnexpectedEofError()


	def read_name(self, c):
		if not mork_chars.is_name(c):
			self.error("not a name char %s", c)

		name = c
		c = self.getc()
		while c != None and mork_chars.is_more(c):
			name += c
			c = self.getc()

		if c != None:
			self.ungetc(c)
		else:
			self.UnexpectedEofError()

		return name


	def read_value(self):
		outBuf = ''
		while True:
			c = self.getc()
			if not (c != None and c != ')'): break
			#
			if c == '\\': # next char is escaped by '\'? 
				c = self.getc()
				if c == chr(0xA) or c == chr(0xD): # linebreak after \?
					c = self.eat_line_break(c)
					if c == ')' or c == '\\' or c == '$':
						self.ungetc(c) # just let while loop test read this again
						continue # goto next iteration of while loop
				if c == None:
					break # end while loop
			elif c == '$': # "$" escapes next two hex digits?
				c = self.getc()
				if c != None:
					first = c # first hex digit
					c = self.getc()
					if c != None:
						second = c # second hex digit
						c = chr(self.hex_to_byte(first, second))
					else:
						break # end while loop
				else:
					break # end while loop
			outBuf += c
			# end while
		if c == None:
			self.UnexpectedEofError()
		return outBuf

	# TODO: Reading should be refactored out into a Reader class
	# def tell(self):
	# 	return self.file.tell() + self.pos - len(self.buff)
	# def seek(self, pos):
	# 	self.file.seek(pos)
	# 	self.pos = 1;
	# 	self.buff = []

	def getc(self):
		"""
		Returns one character from input or None if EOF. If buffered is
		> 0 return char from buffer first.
		"""
		self.pos += 1
		if self.pos >= len(self.buff):
			self.buff = self.file.read(self.buff_len)
			self.pos = 0
			if len(self.buff) == 0:
				return None
		return self.buff[self.pos]

	def ungetc(self, c):
		"""
		Returns one character back to buffer
		"""
		if self.pos > 0:
			self.pos -= 1
		else:
			self.buff = c + self.buff

	def next_char(self):
		c = self.getc()
		while c != None:
			if c == '/':
				c = self.eat_comment()
			elif c == chr(0xA) or c == chr(0xD):
				c = self.eat_line_break(c)
			elif c == '\\':
				c = self.eat_line_continue()
			elif mork_chars.is_white(c):
				c = self.getc()
			else:
				break
		return c

	def eat_line_continue(self):
		c = self.getc()
		if ord(c) == 0xA or ord(c) == 0xD: # linebreak follows \ as expected?
			c = self.eat_line_break(c)
		else:
			self.warning('expected linebreak')
		return c

	def eat_comment(self):
		c = self.getc()
		if c == '/':
			# C++ style comment?
			while c != None and c != chr(0xA) and c != chr(0xD):
				c = self.getc()
			if c == chr(0xA) or c == chr(0xD):
				c = self.eat_line_break(c)
		elif c == '*':
			# C style comment?
			# count depth of comments until depth reaches zero
			depth = 1

			while depth > 0 and c != None:
				c = self.getc()
				while c != None and c != '/' and c != '*':
					if c == chr(0xA) or c == chr(0xD):
						# need to count a line break?
						c = self.eat_line_break(c)
						if c == '/' or c == '*':
							# end while loop
							break
					c = self.getc()

				if c == '*':
					c = self.getc()
					# end of comment?
					if c == '/':
						# depth of comments has decreased by one
						depth -= 1
						# comments all done?
						if depth != 0:
							# return the byte after end of comment
							c = self.getc()
					# need to put the char back?
					elif c != None:
						# especially need to put back '*', 0xA, or 0xD
						self.ungetc(c)
				elif c == '/':
					c = self.getc()
					# nested comment?
					if c == '*':
						# depth of comments has increased by one
						depth += 1
					# need to put the char back?
					elif c != None:
						# especially need to put back '/', 0xA, or 0xD
						self.ungetc(c)

			if c == None and depth > 0:
				self.warning("EOF before end of comment")
		else:
			self.warning("expected / or *")
		return c

	def eat_line_break(self, in_last):
		# get next char after 0xA or 0xD
		c = self.getc()
		# another line break character?
		if c == chr(0xA) or c == chr(0xD):
			if c != in_last: # not the same as the last one?
				c = self.getc() # get next char after two-byte linebreak
		return c


class Builder(Parser):
	def __init__(self, f):
		Parser.__init__(self, f)
		
		# TODO: Store() -> None and enter from outside ?
		self.store = Store()
		
		self.table = None
		self.row = None
		self.cell = None
		
		# initial scope
		self.port_form = None
		self.port_row_scope = ord('r')
		self.port_atom_scope = ord('v')
		
		self.table_form = None
		self.table_row_scope = ord('r')
		self.table_atom_scope = ord('v')
		self.table_kind = None
		
		self.row_form = None
		self.row_row_scope = ord('r')
		self.row_atom_scope = ord('v')
		
		self.cell_form = None
		self.cell_atom_scope = ord('v')
		
		self.dict_form = None
		self.dict_atom_scope = ord('v')
		
		self.do_cut_row = False
		self.do_cut_cell = False

	def on_new_port(self):
		self.port_form = None
		self.port_row_scope = ord('r')
		self.port_atom_scope = ord('v')
	
	def on_new_dict(self):
		self.cell_form = self.dict_form = self.port_form
		self.cell_atom_scope = self.dict_atom_scope = self.port_atom_scope

	def on_new_meta(self): pass
	
	def on_new_cell(self, in_mid, in_buf):
		
		if self.do_cut_cell:
			cell_change = Change.kCut
		else:
			cell_change = Change.kAdd
		
		self.do_cut_cell = False
		self.cell_atom_scope = self.row_atom_scope
	
		self.cell = None # nil until determined for a row
		scope = Store.kColumnSpaceScope
		
		temp_mid = Mid() # space for local and modifiable cell mid
		cell_mid = temp_mid # default to local if inMid==0
	
		if in_mid != None: # mid parameter is actually provided?
			cell_mid = in_mid # bitwise copy for modifiable local mid
			if cell_mid.oid.scope == None:
				if cell_mid.buf != None:
					scope = self.store.BufToToken(cell_mid.buf)
					cell_mid.buf = None # don't do scope lookup again
					self.warning("column mids need column scope")
				cell_mid.oid.scope = scope
		elif in_buf != None: # buf points to naked column string name?
			cell_mid.clear_mid()
			cell_mid.oid.id = self.store.BufToToken(in_buf)
			cell_mid.oid.scope = scope # kColumnSpaceScope
		else:
			self.NilPointerError() # either inMid or inBuf must be non-nil
	
		column = cell_mid.oid.id
		if self.row != None: # this cell must be inside a row
				cell = Cell()
				cell.SetColumnAndChange(column, cell_change)
				cell.atom = None
				self.cell = cell
				self.row.addCell(cell)
		elif self.in_meta: # cell is in metainfo structure?
			if scope == Store.kColumnSpaceScope:
				if self.in_table: # metainfo for table?
					if column == Store.kKindColumn:
						self.meta_token_slot = "table_kind"
					elif column == Store.kStatusColumn:
						self.meta_token_slot = "table_status"
					elif column == Store.kRowScopeColumn:
						self.meta_token_slot = "table_row_scope"
					elif column == Store.kAtomScopeColumn:
						self.meta_token_slot = "table_atom_scope"
					elif column == Store.kFormColumn:
						self.meta_token_slot = "table_form"
				elif self.in_dict: # metainfo for dict?
					if column == Store.kAtomScopeColumn:
						self.meta_token_slot = "dict_atom_scope"
					elif column == Store.kFormColumn:
						self.meta_token_slot = "dict_form"
				elif self.in_row: # metainfo for row?
					if column == Store.kAtomScopeColumn:
						self.meta_token_slot = "row_atom_scope"
					elif column == Store.kRowScopeColumn:
						self.meta_token_slot = "row_row_scope"
					elif column == Store.kFormColumn:
						self.meta_token_slot = "row_form"
			else:
				self.warning("expected column scope")

	def on_new_table(self, in_mid, in_cut_all_rows):
		self.table_form = self.port_form
		self.table_row_scope = self.port_row_scope
		self.table_atom_scope = self.port_atom_scope
		self.table_kind = Store.kNoneToken
	
		self.table_priority = morkPriority_kLo
		self.table_is_unique = False
		self.table_is_verbose = False
		
		# XXX: default table scope should be c - column
		if in_mid.buf == None and in_mid.oid.scope == None:
			in_mid.oid.scope = Store.kColumnSpaceScope
		table = self.store.MidToTable(in_mid)
		self.table = table
		self.table_row_scope = table.oid.scope
		if in_cut_all_rows:
			table.CutAllRows()
	
	def on_new_row(self, in_mid, in_cut_all_cols):
		self.cell_form = self.row_form = self.table_form
		self.cell_atom_scope = self.row_atom_scope = self.table_atom_scope
		self.row_row_scope = self.table_row_scope
		
		if in_mid.buf == None and in_mid.oid.scope == None:
			mid = in_mid.clone()
			mid.oid.scope = self.row_row_scope
			self.row = self.store.MidToRow(mid)
		else:
			self.row = self.store.MidToRow(in_mid)
		
		if in_cut_all_cols:
			self.row.CutAllColumns()
	
		if self.table != None and self.row != None:
			if self.in_meta:
				meta_row = self.table.meta_row
				if meta_row == None:
					self.table.meta_row = self.row
					self.table.meta_row_oid = self.row.oid
				elif meta_row != self.row: # not identical?
					self.error("duplicate table meta row")
			else:
				if self.do_cut_row:
					self.table.CutRow(self.row)
				else:
					self.table.AddRow(self.row)

		# else // it is now okay to have rows outside a table:
		# this->NilBuilderTableError(ev);
		self.do_cut_row = False

	
	def on_value(self, in_buf):
		if self.cell != None:
			self.cell.SetAtom(in_buf)
		elif self.in_meta:
			if self.meta_token_slot != None:
				token = self.store.BufToToken(in_buf)
				self.__dict__[self.meta_token_slot] = token
		else:
			self.NilBuilderCellError()
			
	
	def on_value_mid(self, in_mid):
		
		if in_mid.buf != None:
			if in_mid.oid.scope == None:
				in_mid.oid = self.store.MidToOid(in_mid)
		elif in_mid.oid.scope == None:
			in_mid.oid.scope = self.cell_atom_scope
	
		if self.cell != None:
			atom = self.store.MidToAtom(in_mid)
			if atom != None:
				self.cell.SetAtom(atom)
			else:
				self.error("undefined cell value alias %s", atom)
		elif self.in_meta:
			if self.meta_token_slot != None:
				valScope = in_mid.oid.scope
				if valScope == None or valScope == Store.kColumnSpaceScope:
					if in_mid.oid.id != None: # XXX: valMid.HasSomeId():
						self.__dict__[self.meta_token_slot] = in_mid.oid.id
						if self.meta_token_slot == 'table_kind': # // table kind?
							if self.in_table and self.table != None:
								self.table.kind = in_mid.oid.id
							else:
								self.warning("mBuilder_TableKind not in table")
						elif self.meta_token_slot == 'table_status': # table status?
							if self.in_table and self.table != None:
								pass
								# XXX: $$ what here??
							else:
								self.warning("mBuilder_TableStatus not in table")
				else:
					self.NonColumnSpaceScopeError()
		else:
			self.NilBuilderCellError()
	
	def on_alias(self, in_mid):
		if self.in_dict:
			mid = in_mid.clone()
			mid.oid.scope = self.dict_atom_scope
			self.store.add_alias(mid, self.dict_form)
		else:
			self.error("alias not in dict")
	
	def on_minus_row(self):
		self.do_cut_row = True

	def on_minus_cell(self):
		self.do_cut_cell = True

	def on_cell_form(self, in_charset_format):
		# TODO: I am not really sure what is this good for..
		pass 
	
	def on_row_pos(self, row_pos):
		### TODO: not implemented
		pass

	def on_new_group(self, group_id): pass

	def on_group_commit_end(self): pass
	
	def on_cell_end(self):
		self.meta_token_slot = None
		self.cell_atom_scope = self.row_atom_scope
	
	def on_meta_end(self): pass
	
	def on_dict_end(self):
		self.dict_form = None
		self.dict_atom_scope = None
	
	def on_row_end(self):
		self.row = None
		self.cell = None
		self.do_cut_cell = False
		self.do_cut_row = False
	
	def on_table_end(self):
		if self.table != None:
			self.table.priority = self.table_priority
			if self.table_is_unique: self.table.SetTableUnique()
			if self.table_is_verbose: self.table.SetTableVerbose()
		else:
			self.NilBuilderTableError()

		self.row = None
		self.cell = None
	
		self.table_priority = morkPriority_kLo
		self.table_is_unique = False
		self.table_is_verbose = False

		if self.table_kind == Store.kNoneToken:
			print self.table
			self.error("missing table kind")

		self.cell_atom_scope = self.row_atom_scope
		self.table_atom_scope = self.port_atom_scope

		self.do_cut_cell = False
		self.do_cut_row = False
	
	def on_port_end(self): pass


if __name__ == '__main__':
	import sys
	for file_name in sys.argv[1:]:
		try:
			f = file(file_name)
			p = Parser(f)
			p.parse()
			print 'File "%s" parsed successfully.' % file_name
		except Exception, e:
			print e
		finally:
			f.close()

