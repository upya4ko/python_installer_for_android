#!/system/bin/sh
# -*- mode: sh; tab-width: 4; indent-tabs-mode: nil -*-
if [ -z "$IMAGE" ]; then
    IMAGE="{{ config.device_image_file }}"
fi
if [ -z "$MOUNTPOINT" ]; then
    MOUNTPOINT="{{ config.device_mount_point }}"
fi

is_mounted() {
    mount | grep -q "$MOUNTPOINT"
    return $?
}

init_script_exists() {
    test -f "$MOUNTPOINT/{{ config.init_script }}"
    return $?
}

do_chroot() {
    chroot "$MOUNTPOINT" $*
}

mount_debian() {
    mkdir -p "$MOUNTPOINT"
    busybox mount -o loop "$IMAGE" "$MOUNTPOINT"
    {% for (mount, target) in config.bind_mounts %}
    mkdir -p "$MOUNTPOINT/{{ mount }}"
    busybox mount -o bind "{{ target }}" "$MOUNTPOINT/{{ mount }}"
    {% endfor %}
}

umount_debian() {
    {% for (mount, _) in config.bind_mounts|reverse %}
    umount "$MOUNTPOINT/{{ mount }}"
    {% endfor %}
    umount "$MOUNTPOINT"
}

start_debian() {
    if is_mounted; then true; else
        mount_debian
    fi
    if init_script_exists; then
        do_chroot "{{ config.init_script }}" start
    fi
    echo nameserver $(getprop net.dns1) > "$MOUNTPOINT/etc/resolv.conf"
}

stop_debian() {
    if init_script_exists; then
        do_chroot "{{ config.init_script }}" stop
    fi
    if is_mounted; then
        umount_debian
    fi
}

do_login() {
    if init_script_exists; then
        do_chroot "{{ config.init_script }}" login
    else
        do_chroot /bin/bash
    fi
}

status() {
    if is_mounted; then
        echo "+ Debian mounted."
    else
        echo "- Debian NOT mounted."
    fi
}

deploy() {
    mount -o remount,rw /system
    cp $0 /system/xbin/deb
    busybox chmod +x /system/xbin/deb
    mount -o remount,ro /system
}

case "$1" in
    ""|login)
        start_debian
        do_login
        ;;
    mount|m|start)
        start_debian
        ;;
    unmount|umount|u|stop)
        stop_debian
        ;;
    status)
        status
        ;;
    deploy)
        deploy
        ;;
    *)
        echo "Usage: deb [ login ]"
        echo "       deb m | mount | start"
        echo "       deb u | umount|  unmount | stop"
        echo "       deb status"
        echo "       deb deploy"
        ;;
esac
