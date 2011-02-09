#!/usr/bin/python

#
#     Copyright (C) 2011  Maximilian Mehnert <maximilian.mehnert@gmx.de>
#
#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program; if not, write to the Free Software Foundation,
#     Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301,, USA.



from mork.abook import TbAbookMorkParser
import traceback
import os, os.path
import pickle
import sys
if __name__ == '__main__':

    configdir=os.path.expanduser("~/.TbAbookMorkParser")
    if not os.path.isdir(configdir):
        os.mkdir(configdir)
    address_books={}

    parser=TbAbookMorkParser()
    
    for address_book_fname in sys.argv[1:]:
        if not os.path.isfile(address_book_fname):
            print address_book_fname+" is not a file!"
            sys.exit(1)


        pickle_fname=configdir+"/"+os.path.abspath(address_book_fname).replace("/","_")+".pickle"

        reparse=True
        if os.path.isfile(pickle_fname) and \
             os.path.getmtime(pickle_fname)>os.path.getmtime(address_book_fname):
                try:
                    pkl_file = open(pickle_fname, 'rb')
                    address_books[pickle_fname]=pickle.load(pkl_file)
                    pkl_file.close()
                    reparse=False
                except Exception, e:
                    reparse=True
 
        if reparse==True:
            try:
                address_books[pickle_fname]=[]
                f = file(address_book_fname)
                parser.feed(f)   
                for name, email in parser.getEmails():
                    if name is None and email is None:
                        continue    
                    if name is None:
                        address_books[pickle_fname].append(email)
                        continue
                    elif email is None:
                        pass                   
                        continue
                    address_books[pickle_fname].append([email.strip(),name.strip()])
                pkl_file = open(pickle_fname, 'wb')
                pickle.dump(address_books[pickle_fname], pkl_file, -1)
                pkl_file.close()
            except Exception, e:
                print traceback.print_exc()
                sys.exit(1)
            finally:
                f.close()


    for pickle_file in address_books.keys():
        for address in address_books[pickle_file]:
            print address[0]+"\t"+address[1]

