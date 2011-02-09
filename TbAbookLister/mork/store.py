
import logging
log = logging.getLogger("store")


morkPriority_kLo  = 9 # worst priority
morkBookAtom_kMaxBodySize = 1024


class Change:
	"""
	I am not sure if this class is good for something.
	"""
	kAdd = 'a' # add member
	kCut = 'c' # cut member


class Oid:
	"""
	Oid is used as a key(id,scope) for almost everything in mork.
	"""
	def __init__(self):
		self.id = None
		self.scope = None
	def clone(self):
		o = Oid()
		o.id = self.id
		o.scope = self.scope
		return o
	def __str__(self):
		if self.scope == None:
			return ("Oid@ %X:None" % self.id)
		return ("Oid@ %X:%X" % (self.id, self.scope))

class Mid:
	def __init__(self):
		self.oid = Oid()
		self.buf = None
	def clear_mid(self):
		self.oid = Oid()
		self.buf = None
	def clone(self):
		m = Mid()
		m.buf = self.buf
		m.oid = self.oid.clone()
		return m
	def __str__(self):
		return str(self.oid) + '=' + str(self.buf)


class Cell:
	def __init__(self):
		self.atom = None
		self.in_col = None
	def SetColumnAndChange(self, in_col, in_change):
		if in_change == Change.kCut: # TODO: maybe need to cut value???
			pass
		self.in_col = in_col
	def SetAtom(self, atom):
		self.atom = atom
	def __str__(self):
		return '(%d=%s)' % (self.in_col, self.atom)


class Row:
	def __init__(self):
		self.oid = None
		self.cells = {}
	def addCell(self, cell):
		self.cells[cell.in_col] = cell
	def CutAllColumns(self):
		self.cells = {}
	def __str__(self):
		ret = 'Row(' + str(self.oid) + ')['
		for c in self.cells.values():
			ret += str(c)
		ret += ']'
		return ret


class Table:
	def __init__(self):
		self.meta_row = None
		self.rows = {}
		self.oid = None
	def CutAllRows(self):
		log.debug('cut_all_rows')
		self.rows = {}
	def CutRow(self, row):
		log.debug('cut_row %s', row.oid)
		if self.rows.has_key((row.oid.id, row.oid.scope)):
			del self.rows[(row.oid.id, row.oid.scope)]
	def AddRow(self, row):
		log.debug('add_row %s', row)
		self.rows[(row.oid.id, row.oid.scope)] = row
	def SetTableUnique(self): pass
	def SetTableVerbose(self): pass
	def __str__(self):
		ret = 'Table(' + str(self.oid) + ')'
		for c in self.rows.values():
			ret += '\n' + str(c)
		return ret


class Store:
	kGroundColumnSpace = ord('c') # for mStore_GroundColumnSpace
	kColumnSpaceScope = ord('c') #((mork_scope) 'c') # kGroundColumnSpace
	kValueSpaceScope = ord('v') # ((mork_scope) 'v')
	
	kNoneToken = ord('n')   #define morkStore_kNoneToken ((mork_token) 'n')
	kKindColumn = ord('k') #define morkStore_kKindColumn ((mork_column) 'k')
	kStatusColumn = ord('s')   #define morkStore_kStatusColumn ((mork_column) 's')
	kRowScopeColumn = ord('r') #define morkStore_kRowScopeColumn ((mork_column) 'r')
	kAtomScopeColumn = ord('a') #define morkStore_kAtomScopeColumn ((mork_column) 'a')
	kFormColumn = ord('f') #define morkStore_kFormColumn ((mork_column) 'f')
	kMetaScope = ord('m') #define morkStore_kMetaScope ((mork_scope) 'm')

	def __init__(self):
		self.row_space = {}
		self.table_space = {}
		self.atoms = {}
		self.columns_by_id = {}
		self.columns_by_val = {}

	def add_alias(self, in_mid, in_form):
		log.debug('Add alias %s %s %s', in_mid.oid, in_mid.buf, in_form)
#    if not self.atoms.has_key(in_mid.oid.scope):
#      self.atoms[in_mid.oid.scope] = {}
#    if self.atoms[in_mid.oid.scope].has_key(in_mid.oid.id):
#      self.error("duplicate alias ID %x", in_mid.oid.id)
#    else:
#      self.atoms[in_mid.oid.scope][in_mid.oid.id] = in_mid.buf
		if in_mid.oid.scope == Store.kColumnSpaceScope:
			self.columns_by_id[in_mid.oid.id] = in_mid.buf
			self.columns_by_val[in_mid.buf] = in_mid.oid.id
		else:
			# XXX: The a - ground atom scope has id 0x76 so we can save it this way.
			# XXX: Perhaps also the c - column can be saved this way...
			self.atoms[(in_mid.oid.id, in_mid.oid.scope)] = in_mid.buf

	def create_new_column_atom(self, value):
		id = max([0x7f] + self.columns_by_id.keys()) + 1
		self.columns_by_val[value] = id
		self.columns_by_id[id] = value
		return id

	def StringToToken(self, s):
		outToken = 0
		nonAscii = ord(s[0]) > 0x7F
		if nonAscii or (ord(s[0]) != 0 and ord(s[1]) != 0): # more than one byte?
			if not self.columns_by_val.has_key(s):
				return self.create_new_column_atom(s)
			return self.columns_by_val[s]
		else: #only a single byte in inTokenName string:
			outToken = ord(s[0])
		return outToken;

	def BufToToken(self, x):
		log.debug('totoken %s', x)
		nonAscii = ord(x[0]) > 0x7f
		if nonAscii or len(x) > 1:
			if len(x) <= morkBookAtom_kMaxBodySize:
				# XXX: I dont know if this token resolution is correct...
				if x == "mork:none":
					return Store.kNoneToken
				elif x == "atomScope":
					return Store.kAtomScopeColumn
				elif x == "rowScope":
					return Store.kRowScopeColumn
				elif x == "tableKind":
					return Store.kKindColumn
				elif x == "columnScope":
					return Store.kColumnSpaceScope
				# Here we insert new column token
				if not self.columns_by_val.has_key(x):
					return self.create_new_column_atom(x)
				return self.columns_by_val[x]
		else:
			return ord(x[0])
#// mork_column  mStore_TableScopeToken;  // token for "tableScope"  // fill=10
#// mork_column  mStore_CharsetToken;     // token for "charset"     // fill=7
#// mork_column  mStore_ColumnScopeToken; // token for "columnScope" // fill=11
#// mork_kind    mStore_TableKindToken;   // token for "tableKind"   // fill=9
#// mork_column  mStore_RowScopeToken;    // token for "rowScope"    // fill=8
#// mork_column  mStore_AtomScopeToken;   // token for "atomScope"   // fill=9
#// mork_token   mStore_MorkNoneToken;    // token for "mork:none"   // fill=9
	
	def MidToAtom(self, in_mid):
		oid = self.MidToOid(in_mid)
		log.debug('atom %s', oid)
		if oid.scope == Store.kColumnSpaceScope:
			if self.columns_by_id.has_key(oid.id):
				return self.columns_by_id[oid.id]
		if self.atoms.has_key((oid.id, oid.scope)):
			return self.atoms[(oid.id, oid.scope)]
		return None
	
	def MidToRow(self, in_mid):
		oid = self.MidToOid(in_mid)
		log.debug('row %s', oid)
		if not self.row_space.has_key((oid.id, oid.scope)):
			self.row_space[(oid.id, oid.scope)] = Row()
			self.row_space[(oid.id, oid.scope)].oid = oid
		return self.row_space[(oid.id, oid.scope)]

	def MidToTable(self, in_mid):
		log.debug('table %s', in_mid)
		oid = self.MidToOid(in_mid)
		log.debug('table %s', oid)
		if not self.table_space.has_key((oid.id, oid.scope)):
			self.table_space[(oid.id, oid.scope)] = Table()
			self.table_space[(oid.id, oid.scope)].oid = oid
		return self.table_space[(oid.id, oid.scope)]

	def MidToOid(self, in_mid):
		out_oid = in_mid.oid
		buf = in_mid.buf
		if buf != None and out_oid.scope == None:
			if len(buf) <= morkBookAtom_kMaxBodySize:
				if len(buf) == 1:
					out_oid.scope = ord(buf)
					return out_oid
				
				if not self.columns_by_val.has_key(buf):
					out_oid.scope = self.create_new_column_atom(buf)
					return out_oid
				out_oid.scope = self.columns_by_val[buf]
				return out_oid
		return out_oid


