#!/bin/bash

# Exit immediately if any command exits with a nonzero exit value
set -e

# Fast-downward planner with the desired version
PLANNER_NAME=fast-downward-19.06

TARBALL="${PLANNER_NAME}.tar.gz"
TARBALL_URL="http://www.fast-downward.org/Releases/19.06?action=AttachFile&do=get&target=${TARBALL}"

# Install paths
INSTALL_DIR_ROOT="/opt/ropod/task-planner/bin"
INSTALL_DIR_NAME="fast-downward"
INSTALL_DIR=$INSTALL_DIR_ROOT/$INSTALL_DIR_NAME

# Pre-install cleanup
if [ -d $INSTALL_DIR ]; then
  echo "Removing existing planner from ${INSTALL_DIR} ..."
  rm -rf $INSTALL_DIR
fi

# Fresh Installation
echo "Installing LAMA planner"
cd $INSTALL_DIR_ROOT
wget $TARBALL_URL -O $TARBALL
tar sxvf $TARBALL
mv $PLANNER_NAME $INSTALL_DIR_NAME
rm -f $TARBALL
python $INSTALL_DIR_NAME/build.py
