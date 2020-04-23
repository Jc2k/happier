#! /bin/sh
set -e

python -m black tests happier
python -m isort -rc tests happier
python -m black tests happier --check --diff
python -m flake8 tests happier
python -m pytest --cov=happier tests
python -m coverage html
