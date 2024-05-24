.PHONY: all
all: nytid.pdf

LATEXFLAGS+=	-shell-escape -xelatex
TEX_PYTHONTEX=	yes
PYTHONTEXFLAGS=	--interpreter "python:poetry run python3"

nytid.pdf: ../src/nytid/cli/init.tex
nytid.pdf: ../src/nytid/cli/courses.tex
nytid.pdf: ../src/nytid/cli/schedule.tex
nytid.pdf: ../src/nytid/cli/signupsheets.tex
nytid.pdf: ../src/nytid/cli/hr.tex

nytid.pdf: ../src/nytid/storage/init.tex
nytid.pdf: ../src/nytid/storage/afs.tex

nytid.pdf: ../src/nytid/courses/init.tex
nytid.pdf: ../src/nytid/courses/registry.tex

nytid.pdf: ../src/nytid/schedules.tex
nytid.pdf: ../src/nytid/signup/hr/hr.tex
nytid.pdf: ../src/nytid/signup/sheets.tex
nytid.pdf: ../src/nytid/signup/utils.tex

nytid.pdf: ../src/nytid

FIGS+=		figs/nytid-storage.pdf
FIGS+=		figs/timesheet-dbosk.pdf

nytid.pdf: preamble.tex abstract.tex ../LICENSE ${FIGS}

${FIGS}:
	${MAKE} -C $(dir $@) $(notdir $@)

../src/nytid::
	${MAKE} -C $@ all

../%::
	${MAKE} -C $(dir $@) $(notdir $@)


.PHONY: clean
clean:
	${RM} nytid.pdf
	#${MAKE} -C ../src/nytid/cli clean
	${MAKE} -C ../src/nytid clean
	${MAKE} -C figs clean

.PHONY: distclean
distclean:
	${RM} -Rf __pycache__
	#${MAKE} -C ../src/nytid/cli distclean
	${MAKE} -C ../src/nytid distclean
	${MAKE} -C figs distclean



INCLUDE_MAKEFILES=../makefiles
include ${INCLUDE_MAKEFILES}/tex.mk
