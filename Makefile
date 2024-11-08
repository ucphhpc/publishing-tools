# Copyright (C) 2024  The publishing-tools Project by the Science HPC Center at UCPH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

PACKAGE_NAME=publishing-tools
PACKAGE_NAME_FORMATTED=$(subst -,_,${PACKAGE_NAME})

.PHONY: all
all: install

.PHONY: clean
clean: distclean venv-clean
	rm -fr .pytest_cache
	rm -fr tests/__pycache__

.PHONY: dist
dist: venv
	${VENV}/python setup.py sdist bdist_wheel

.PHONY: distclean
distclean:
	rm -fr dist build ${PACKAGE_NAME}.egg-info ${PACKAGE_NAME_FORMATTED}.egg-info

.PHONY: maintainer-clean
maintainer-clean: venv-clean clean
	@echo 'This command is intended for maintainers to use; it'
	@echo 'deletes files that may need special tools to rebuild.'

.PHONY: install
install: venv install-dep
	${VENV}/pip install .

.PHONY: uninstall
uninstall: venv
	${VENV}/pip uninstall -y ${PACKAGE_NAME}

.PHONY: install-dep
install-dep: venv
	${VENV}/pip install -r requirements.txt

.PHONY: uninstall-dep
uninstall-dep: venv
	${VENV}/pip uninstall -y -r requirements.txt

.PHONY: install-dev
install-dev: venv
	${VENV}/pip install -r requirements-dev.txt

.PHONY: uninstall-dev
uninstall-dev: venv
	${VENV}/pip uninstall -y -r requirements-dev.txt

.PHONY: uninstalltest
uninstalltest: venv
	${VENV}/pip uninstall -y -r tests/requirements.txt

.PHONY: installtest
installtest: venv install-dep
	${VENV}/pip install -r tests/requirements.txt

.PHONY: test
test: venv installtest
	. ${VENV}/activate; pytest -s -v tests/

include Makefile.venv