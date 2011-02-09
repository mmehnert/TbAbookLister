
from parser import Builder

ID_PAB_TABLE          = 1
ID_DELETEDCARDS_TABLE = 2

kPabTableKind = "ns:addrbk:db:table:kind:pab"
kCardRowScope = "ns:addrbk:db:row:scope:card:all"
kListRowScope = "ns:addrbk:db:row:scope:list:all"
kDataRowScope = "ns:addrbk:db:row:scope:data:all"

kFirstName = 'FirstName'
kLastName = 'LastName'
kDisplayName = 'DisplayName'
kNickName = 'NickName'
kPrimaryEmail = 'PrimaryEmail'
kSecondEmail = 'SecondEmail'


class TbAbookMorkParser:

	def getEmails(self):
		return self.emails

	def IsCardRowScopeToken(self, scope):
		return scope == self.m_CardRowScopeToken

	def IsDataRowScopeToken(self, scope):
		return scope == self.m_DataRowScopeToken

	def IsListRowScopeToken(self, scope):
		return scope == self.m_ListRowScopeToken
		

	def feed(self, f):
		self.emails = []

		p = Builder(f)
		p.parse()


		self.m_PabTableKind = p.store.StringToToken(kPabTableKind)
		self.m_CardRowScopeToken = p.store.StringToToken(kCardRowScope)
		self.m_ListRowScopeToken = p.store.StringToToken(kListRowScope)
		self.m_DataRowScopeToken = p.store.StringToToken(kDataRowScope)
		self.m_DataRowScopeToken = p.store.StringToToken(kDataRowScope)


		self.firstNameToken = p.store.StringToToken(kFirstName)
		self.lastNameToken = p.store.StringToToken(kLastName)
		self.displayNameToken = p.store.StringToToken(kDisplayName)
		self.nickNameToken = p.store.StringToToken(kNickName)
		self.primaryEmailToken = p.store.StringToToken(kPrimaryEmail)
		self.secondEmailToken = p.store.StringToToken(kSecondEmail)

		if not p.store.table_space.has_key((ID_PAB_TABLE, self.m_CardRowScopeToken)):
			return

		for row in p.store.table_space[(ID_PAB_TABLE, self.m_CardRowScopeToken)].rows.values():
			if self.IsCardRowScopeToken(row.oid.scope):
				# print row.cells[self.firstNameToken], \
				# 	row.cells[self.lastNameToken], \
				# 	row.cells[self.displayNameToken], \
				# 	row.cells[self.nickNameToken], \
				# 	row.cells[self.primaryEmailToken], \
				# 	row.cells[self.secondEmailToken]
				name = row.cells[self.displayNameToken].atom.strip()
				if name == '':
					name = row.cells[self.firstNameToken].atom.strip()
					lname = row.cells[self.lastNameToken].atom.strip()
					if name != '' and lname != '':
						name += ' ' + lname
					elif name == '' and lname != '':
						name = lname
					else:
						name = row.cells[self.nickNameToken].atom.strip()
				if name == '': name = None
				mail1 = row.cells[self.primaryEmailToken].atom.strip()
				mail2 = row.cells[self.secondEmailToken].atom.strip()
				if mail1 != '':
					self.emails += [(name, mail1)]
				if mail2 != '':
					self.emails += [(name, mail2)]

