MODULES+=	__init__.py
MODULES+=	afs.py

.PHONY: all
all: ${MODULES}

.INTERMEDIATE: init.py
__init__.py: init.py
	${MV} $< $@

.PHONY: clean
clean:
	${RM} -R ${MODULES} __pycache__
	${RM} *.tex


INCLUDE_MAKEFILES=../../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
