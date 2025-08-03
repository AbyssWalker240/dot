# dot

CLI todo list written in python

## dependencies

Written in Python 3.13.5

Uses these python packages:
* rich - for pretty terminal output
* dateparser - to specify dates with natural language

### arch linux
* python            (core)
* python-rich       (extra)
* python-dateparser (extra)

``pacman -Syu python python-rich python-dateparser``

## installation

1) ``git clone https://github.com/AbyssWalker240/dot.git``

2) Copy/move 'src/dot' into '\~/.local/bin/dot'

**--OR--**

2) I recommend making a symbolic link in '\~/.local/bin/' that points to the script in 'src/', which will enable update by performing ``git pull``
