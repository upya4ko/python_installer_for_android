make_magisk_module: 
	zip -r python_installer_for_android.zip \
	META-INF \
    LICENSE \
	README.md \
	module.prop \
	customize.sh \
	system

push:
	adb push python_installer_for_android.zip /sdcard/

clean: 
	rm python_installer_for_android.zip
