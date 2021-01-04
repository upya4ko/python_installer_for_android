magiskModuleName = $(shell basename `pwd`)

all: clean make-magisk-module adb-push
.PHONY: all

make-magisk-module: 
	zip -r ${magiskModuleName}.zip ./* --exclude .gitignore Makefile \*.zip .git/

adb-push:
	adb push ${magiskModuleName}.zip /sdcard/magiskModules/

clean: 
	rm ${magiskModuleName}.zip

