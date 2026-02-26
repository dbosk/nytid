define find_tests
find ../src -type f | xargs grep "<<test \[\[[^.-]*\.py\]\]>>" | \
	sed -En "s/^(.*):.*<<test \[\[([^.-]*).py\]\]>>.*/test_\2.py:\1/p" | sort -u
endef

define def_target
$(shell echo $1 | cut -d: -f1): $(shell echo $1 | cut -d: -f2)
	notangle ${NOTANGLEFLAGS.py} "-Rtest [[$$(shell echo $$@ | sed 's/test_//')]]" $$^ > $$@
endef

TESTS=	$(shell ${find_tests})

.PHONY: all
all: $(foreach files,${TESTS},$(shell echo ${files} | cut -d: -f1))

$(foreach files,${TESTS},$(eval $(call def_target, ${files})))

.PHONY: test
test: all
	poetry run pytest ${PYTEST_FLAGS}

.PHONY: clean
clean:
	${RM} $(foreach files,${TESTS},$(shell echo ${files} | cut -d: -f1))
	${RM} -Rf __pycache__
	${RM} test_*.py
	${RM} ~/.config/pytest/config.json

.PHONY: distclean
distclean:



INCLUDE_MAKEFILES=../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
