.PHONY: all
all: __init__.py config.py

.INTERMEDIATE: init.py

__init__.py: init.py
	${MV} $^ $@

config.py: init.nw
	${NOTANGLE.py}


.PHONY: clean
clean:
	${RM} init.py __init__.py init.tex config.py


INCLUDE_MAKEFILES=../../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
