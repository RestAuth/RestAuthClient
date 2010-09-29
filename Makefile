NAME="RestAuthClient"
MODULES=restauth_user group errors common
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
