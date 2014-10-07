#!/bin/sh

PYTHON=python2
BASE_DIR=$(dirname $(readlink -e $0))
CONFIG=$HOME/.satori-uploader/


$PYTHON "${BASE_DIR}/uploader.py" --config $CONFIG "$@"

