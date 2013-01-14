VERSION=`python -c "import mpd; print('.'.join(map(str,mpd.VERSION)))"`

test:
	python setup.py test
release: test
	git tag $(VERSION)
	python setup.py sdist upload
clean:
	python setup.py clean
