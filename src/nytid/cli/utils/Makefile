SUBDIR_GOALS=	all clean distclean

MODULES+=	__init__.py init.tex
MODULES+=	defaults.py defaults.tex
MODULES+=	rooms.py rooms.tex
MODULES+=	labels.py labels.tex

.PHONY: all
all: ${MODULES}

.intermediate: init.py
__init__.py: init.py
	${MV} $< $@

.PHONY: clean
clean:
	${RM} -R ${MODULES} __pycache__
	${RM} *.tex


INCLUDE_MAKEFILES=../../../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
include ${INCLUDE_MAKEFILES}/subdir.mk
