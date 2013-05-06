#!/bin/sh
BUGADDR="flying-sheep@web.de"
PROJECT="markdowner"
_dir="$PWD"

cd ..
find . -name '*.py' | sort > infiles.list

xgettext --from-code=UTF-8 -L python -k -ki18n -kki18n \
	--msgid-bugs-address="$BUGADDR" \
	--files-from=infiles.list -D . -o "$_dir/$PROJECT.pot" || { echo "error while calling xgettext. aborting."; exit 1; }

rm infiles.list

#msgfmt -o de.mo de.po