VERSION=`python -c "import mpd; print('.'.join(map(str,mpd.VERSION)))"`
PYTHON?=python3.8

test:
	python setup.py test
release: test
	git tag $(VERSION)
	$(PYTHON) setup.py sdist bdist_wheel
	$(PYTHON) -m twine upload dist/python-mpd2-$(VERSION).tar.gz dist/python_mpd2-$(VERSION)-py2.py3-none-any.whl
clean:
	python setup.py clean
