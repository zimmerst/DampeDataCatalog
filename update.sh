#!/bin/bash

git pull
python setup.py sdist
tarball=$(ls -r dist | tail -n 1)
tarfile=$(greadlink -f dist/${tarball})
echo "tarfile ${tarfile}"
source ~/Envs/DFC/bin/activate
RC=$?
if (( ${RC}!=0 ))
then
    echo "cannot activate environment"
else
    pip install ${tarfile}
    deactivate
fi