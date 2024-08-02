PACKAGE_NAME=publish-container-tools
PACKAGE_NAME_FORMATTED=$(subst -,_,${PACKAGE_NAME})

.PHONY: install-dev
install-dev: venv
	${VENV}/pip install -r requirements-dev.txt

.PHONY: uninstall-dev
uninstall-dev: venv
	${VENV}/pip uninstall -y -r requirements-dev.txt

include Makefile.venv