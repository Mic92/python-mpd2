PYTHON ?= python3.13
REMOTE = git@github.com:Mic92/python-mpd2
VERSION = $(shell $(PYTHON) -c "import mpd; print('.'.join(map(str,mpd.VERSION)))")

test:
	tox
release: test
	test "$(shell git symbolic-ref --short HEAD)" = "master" || (echo "not on master branch"; exit 1)
	git pull --rebase origin master
	$(PYTHON) -m build
	$(PYTHON) -m twine check dist/python-mpd2-$(VERSION).tar.gz dist/python_mpd2-$(VERSION)-py3-none-any.whl
	git tag "v$(VERSION)"
	git push --tags git@github.com:Mic92/python-mpd2 "v$(VERSION)"
	$(PYTHON) -m twine upload --repository python-mpd2 dist/python-mpd2-$(VERSION).tar.gz dist/python_mpd2-$(VERSION)-py3-none-any.whl
clean:
	rm -rf dist build *.egg-info

bump-version:
	@if [ -z "$(NEW_VERSION)" ]; then \
		echo "Usage: make bump-version NEW_VERSION=x.y.z"; \
		exit 1; \
	fi
	@echo "Bumping version to $(NEW_VERSION)..."
	@# Convert x.y.z to (x, y, z) for mpd/base.py
	@VERSION_TUPLE=$$(echo "$(NEW_VERSION)" | sed 's/\./,\ /g'); \
	sed -i.bak "s/^VERSION = (.*/VERSION = ($$VERSION_TUPLE)/" mpd/base.py && rm mpd/base.py.bak
	@# Update version in pyproject.toml
	@sed -i.bak 's/^version = .*/version = "$(NEW_VERSION)"/' pyproject.toml && rm pyproject.toml.bak
	@echo "Version bumped to $(NEW_VERSION)"
	@# Commit the version bump
	@git add mpd/base.py pyproject.toml
	@git commit -m "Bump version to $(NEW_VERSION)"
	@echo "Committed version bump to $(NEW_VERSION)"

.PHONY: test release clean bump-version
