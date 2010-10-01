# This file is part of RestAuthClient.py.
#
#    RestAuthClient.py is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RestAuthClient.py.  If not, see <http://www.gnu.org/licenses/>.

NAME="RestAuthClient"
MODULES=RestAuthClient.restauth_user RestAuthClient.group RestAuthClient.errors RestAuthClient.common
DOC_DIR="doc"
HTML_DIR="${DOC_DIR}/html"
PDF_DIR="${DOC_DIR}/pdf"

doc: doc/pdf doc/html

doc/pdf:

doc/html:
	mkdir -p ${HTML_DIR}
	epydoc -v --html -o ${HTML_DIR} --name ${NAME} --redundant-details --no-private ${MODULES}

check:
	epydoc --no-private --no-imports --check ${MODULES}

clean:
	rm -rf ${DOC_DIR}
	rm -f *.pyc
