#!/bin/sh

set -e

STATIC_DIR=../static/samples/
THUMB_WIDTH=200
THUMB_HEIGHT=10000 # height: auto;

thumbnail() {
	echo "convert \"$1\" -thumbnail ${THUMB_WIDTH}x${THUMB_HEIGHT} \"${1%.*}-thumb.jpg\""
	magick "$1" -thumbnail ${THUMB_WIDTH}x${THUMB_HEIGHT} "${1%.*}-thumb.jpg"
	git add "$1" "${1%.*}-thumb.jpg" "$STATIC_DIR"samples.sha256
}

[ ! -f "$STATIC_DIR"samples.sha256 ] && touch "$STATIC_DIR"samples.sha256

find "$STATIC_DIR" -name '*.jpg' ! -name '*-thumb.jpg' -type f | while read -r f
do
        f_=$(echo "$f" | sed -E -e 's@([.])@\\\1@g')
	checksum=$(grep "$f_" "$STATIC_DIR"samples.sha256 || true)
	if [ -n "$checksum" ]
	then
		echo "$checksum" | sha256sum -c --status || {
			echo "File $f changed"
			sed -i "\\@$f_@ c\\
$(sha256sum "$f")
" "$STATIC_DIR"samples.sha256
			thumbnail "$f"
		}
	else
		echo "New file $f"
		sha256sum "$f" >> "$STATIC_DIR"samples.sha256
		thumbnail "$f"
	fi
done
