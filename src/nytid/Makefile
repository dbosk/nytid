SUBDIR_GOALS=	all clean distclean

SUBDIR+=	cli
SUBDIR+=	storage
SUBDIR+=	courses
SUBDIR+=	signup

MODULES+=	schedules.py schedules.tex
MODULES+=	prompt.py prompt.tex

.PHONY: all
all: ${MODULES}


.PHONY: clean
clean:
	${RM} -R ${MODULES} __pycache__
	${RM} *.tex


INCLUDE_MAKEFILES=../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
include ${INCLUDE_MAKEFILES}/subdir.mk
