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
nytid.pdf: ../src/nytid/cli/track.tex
nytid.pdf: ../src/nytid/cli/todo.tex
nytid.pdf: ../src/nytid/prompt.tex
nytid.pdf: ../src/nytid/cli/zulip.tex
nytid.pdf: ../tests/conftest.tex
nytid.pdf: ../src/nytid/cli/utils/init.tex
nytid.pdf: ../src/nytid/cli/utils/defaults.tex
nytid.pdf: ../src/nytid/cli/utils/rooms.tex
nytid.pdf: ../src/nytid/cli/utils/labels.tex
nytid.pdf: ../src/nytid/cli/utils/output.tex
nytid.pdf: ../src/nytid/cli/utils/workweek.tex

nytid.pdf: ../src/nytid/storage/init.tex
nytid.pdf: ../src/nytid/storage/afs.tex

nytid.pdf: ../src/nytid/courses/init.tex
nytid.pdf: ../src/nytid/courses/registry.tex

nytid.pdf: ../src/nytid/schedules.tex
nytid.pdf: ../src/nytid/signup/hr/hr.tex
nytid.pdf: ../src/nytid/signup/hr/timesheet/init.tex
nytid.pdf: ../src/nytid/signup/sheets.tex
nytid.pdf: ../src/nytid/signup/utils.tex

nytid.pdf: ../src/nytid

FIGS+=		figs/nytid-storage.pdf
FIGS+=		figs/timesheet-dbosk.pdf
FIGS+=		figs/timeedit-csv-export.png

DEPENDS+=	didactic.sty
# minted highlights the woven code with a per-language Pygments lexer
# (noweb_lexer.py:Noweb<Lang>Lexer) emitted by noweave's tominted filter, so the
# lexer module must sit next to the PDF build. It ships with the makefiles
# submodule; copy it in.
DEPENDS+=	noweb_lexer.py

nytid.pdf: preamble.tex abstract.tex ../LICENSE ${FIGS}
nytid.pdf: ${DEPENDS}

${FIGS}:
	${MAKE} -C $(dir $@) $(notdir $@)

../src/nytid::
	${MAKE} -C $@ all

../%::
	${MAKE} -C $(dir $@) $(notdir $@)


.PHONY: clean
clean:
	${RM} nytid.pdf noweb_lexer.py
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
include ${INCLUDE_MAKEFILES}/noweb.mk

NOWEAVEFLAGS.tex+=-langrule 'sending signed time sheets=bash'

# tex.mk offers two ways to build a .bbl: bibtex(u) from the .aux and
# biber from the .bcf.  We are a biblatex+biber document, but latexmk
# runs with -use-make (that delegation is what runs PythonTeX for us
# with the interpreter in PYTHONTEXFLAGS), so on the first pass it asks
# make for the not-yet-existing .bbl -- and GNU make answers with the
# first matching pattern rule, the bibtex one, which then dies with "I
# found no \bibdata command".  latexmk recovers by running biber
# itself, so the build survives, but the log carries a bibtexu failure
# and a make Error 2 on every clean build.  An explicit rule for our
# own .bbl outranks both pattern rules and points the delegation at
# biber.
${TEX_OUTDIR}/nytid.bbl: ${TEX_OUTDIR}/nytid.bcf
	${BIBLIOGRAPHY.bcf}

INCLUDE_DIDACTIC=didactic
include ${INCLUDE_DIDACTIC}/didactic.mk
