TARGETS=	nytid-storage.pdf
TARGETS+=	timesheet-dbosk.pdf

.PHONY: all
all: ${TARGETS}

nytid-storage.pdf: nytid-storage.svg
timesheet-dbosk.pdf: timesheet-dbosk.xlsx
	loffice --convert-to pdf $<

.PHONY: clean
clean:
	${RM} ${TARGETS}

.PHONY: distclean
distclean:

INCLUDE_MAKEFILES=../../makefiles
include ${INCLUDE_MAKEFILES}/doc.mk
