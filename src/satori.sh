#!/bin/sh

PYTHON=python2
BASE_DIR=$(dirname $(readlink -e $0))
CONFIG=$HOME/.satori-uploader/

pushd $BASE_DIR > /dev/null

$PYTHON uploader.py --config $CONFIG "$@"

popd > /dev/null
