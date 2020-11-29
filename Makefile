make_magisk_module: 
	zip -r microG_installer_Q.zip \
	META-INF \
    LICENSE \
	README.md \
	module.prop \
	customize.sh \
	service.sh \
	system

push:
	adb push microG_installer_Q.zip /sdcard/

clean: 
	rm microG_installer_Q.zip
