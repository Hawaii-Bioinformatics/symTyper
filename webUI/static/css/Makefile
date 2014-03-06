all: style.css sequences.css

style.css: style.less
	lessc -x --yui-compress style.less > style.css
sequences.css: sequences.less
	lessc -x --yui-compress  sequences.less >  sequences.css
