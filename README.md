# dot

CLI todo list written in python

## planned features/commands

```
dot add           "" @ -d \[date\]
dot done   \[id\]
dot delete \[id\]
dot edit   \[id\] "" @ -d \[date\]

dot list \[all|done|due|overdue\] @

dot history restore \[id\]
dot history delete  \[id\]

dot history list \[all|on-time|overdue\] @
```

## dependencies

### archlinux
* python3           (core)
* python-rich       (extra)
* python-dateparser (extra)

## installation

* curl auto-install.sh run with bash, which will clone correct \[os\]-install.sh for system and run it

## uninstallation

* curl uninstall.sh run with bash, which will prompt to see if user wants to delete all files or just scripts
