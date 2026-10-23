SUBDIR_GOALS=all clean distclean

SUBDIR+=	src/nytid
SUBDIR+=	doc

version=$(shell sed -n 's/^ *version *= *\"\([^\"]\+\)\"/\1/p' pyproject.toml)

.PHONY: all publish check-package

all:

publish: all check-package
	poetry build
	poetry publish
	git push
	gh release create -t v${version} v${version} doc/nytid.pdf

# The wheel includes src/**/*.py and *.sh whatever .gitignore says, so a
# file left behind in src/ would be published. The generated ones are
# ignored, so anything untracked and not ignored is such a stray.
check-package:
	@stray=$$(git ls-files --others --exclude-standard -- src \
	          | grep -E '\.(py|sh)$$'); \
	if test -n "$$stray"; then \
	  echo "error: these untracked files would ship in the wheel:" >&2; \
	  echo "$$stray" >&2; \
	  exit 1; \
	fi


.PHONY: clean distclean
clean:
distclean:
	${RM} -Rf dist

INCLUDE_MAKEFILES=makefiles
include ${INCLUDE_MAKEFILES}/subdir.mk
