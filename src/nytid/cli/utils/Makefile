SUBDIR_GOALS=	all clean distclean

MODULES+=	freerooms.py

.PHONY: all
all: ${MODULES}

.PHONY: clean
clean:
	${RM} -R ${MODULES} __pycache__
	${RM} *.tex


INCLUDE_MAKEFILES=../../../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
include ${INCLUDE_MAKEFILES}/subdir.mk
