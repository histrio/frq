
build:
	wget -N https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2018/mono/cs.tok.gz
	test -f cs.tok || gunzip -qk cs.tok.gz
	cargo run --release > result01.txt
