all: prezentacija.pdf dokumentacija.pdf

dokumentacija.pdf: dokumentacija.tex
	latexmk -pdf $^

prezentacija.pdf: prezentacija.tex
	make -C mtheme/ sty
	cp mtheme/*.sty .
	latexmk -pdf $^
