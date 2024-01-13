PYTHON ?= python3.11
REMOTE = git@github.com:Mic92/python-mpd2
VERSION = $(shell $(PYTHON) -c "import mpd; print('.'.join(map(str,mpd.VERSION)))")

test:
	tox
release: test
	test "$(git symbolic-ref --short HEAD)" = "master" || (echo "not on master branch"; exit 1)
	git pull --rebase origin master
	$(PYTHON) setup.py sdist bdist_wheel
	$(PYTHON) -m twine check dist/python-mpd2-$(VERSION).tar.gz dist/python_mpd2-$(VERSION)-py2.py3-none-any.whl
	git tag "v$(VERSION)"
	git push --tags git@github.com:Mic92/python-mpd2 "v$(VERSION)"
	$(PYTHON) -m twine upload dist/python-mpd2-$(VERSION).tar.gz dist/python_mpd2-$(VERSION)-py2.py3-none-any.whl
clean:
	$(PYTHON) setup.py clean

.PHONY: test release clean
