PYTHON?=python3.8
VERSION=$(shell $(PYTHON) -c "import mpd; print('.'.join(map(str,mpd.VERSION)))")

test:
	$(PYTHON) setup.py test
release: test
	git tag "v$(VERSION)"
	$(PYTHON) setup.py sdist bdist_wheel
	$(PYTHON) -m twine upload dist/python-mpd2-$(VERSION).tar.gz dist/python_mpd2-$(VERSION)-py2.py3-none-any.whl
clean:
	$(PYTHON) setup.py clean

.PHONY: test release clean
