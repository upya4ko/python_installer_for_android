#!/bin/sh
# -*- mode: sh; tab-width: 4; indent-tabs-mode: nil -*-
set -e
export PATH=/bin:/usr/bin:/sbin:/usr/sbin
export LC_ALL=C LANGUAGE=C LANG=C

echo "Performing first-time setup..."
echo "Running dash.preinst..."
/var/lib/dpkg/info/dash.preinst install

echo "Configuring all packages..."
dpkg --configure -a

echo "Adding Android users and groups..."

# Note: most of this, the code for the config changes in particular, was taken
# from the `andromize` package in the Debian Kit project:
# http://sven-ola.dyndns.org/repo/debian-kit-en.html

usergroupadd() {
    grep -q ^$2: /etc/group || groupadd -r -g $1 $2
    grep -q ^$2: /etc/passwd || useradd -r -g $1 -u $1 -d / $2
}

# See system/core/include/private/android_filesystem_config.h
usergroupadd 1000 aid_system
usergroupadd 1001 aid_radio
usergroupadd 1002 aid_bluetooth
usergroupadd 1003 aid_graphics
usergroupadd 1004 aid_input
usergroupadd 1005 aid_audio
usergroupadd 1006 aid_camera
usergroupadd 1007 aid_log
usergroupadd 1008 aid_compass
usergroupadd 1009 aid_mount
usergroupadd 1010 aid_wifi
usergroupadd 1011 aid_adb
usergroupadd 1012 aid_install
usergroupadd 1013 aid_media
usergroupadd 1014 aid_dhcp
usergroupadd 1015 aid_sdcard_rw
usergroupadd 1016 aid_vpn
usergroupadd 1017 aid_keystore
usergroupadd 1018 aid_usb
usergroupadd 1019 aid_drm
usergroupadd 1020 aid_mdnsr
usergroupadd 1021 aid_gps
# usergroupadd 1022 aid_unused1
usergroupadd 1023 aid_media_rw
usergroupadd 1024 aid_mtp
# usergroupadd 1025 aid_unused2
usergroupadd 1026 aid_drmrpc
usergroupadd 1027 aid_nfc
usergroupadd 1028 aid_sdcard_r
usergroupadd 1029 aid_clat
usergroupadd 1030 aid_loop_radio
usergroupadd 1031 aid_media_drm
usergroupadd 1032 aid_package_info
usergroupadd 1033 aid_sdcard_pics
usergroupadd 1034 aid_sdcard_av
usergroupadd 1035 aid_sdcard_all
usergroupadd 1036 aid_logd
usergroupadd 1037 aid_shared_relro

usergroupadd 2000 aid_shell
usergroupadd 2001 aid_cache
usergroupadd 2002 aid_diag

usergroupadd 3001 aid_net_bt_admin
usergroupadd 3002 aid_net_bt
usergroupadd 3003 aid_inet
usergroupadd 3004 aid_net_raw
usergroupadd 3005 aid_net_admin
usergroupadd 3006 aid_net_bw_stats
usergroupadd 3007 aid_net_bw_acct
usergroupadd 3008 aid_net_bt_stack

usergroupadd 9997 aid_everybody
usergroupadd 9998 aid_misc
usergroupadd 9999 aid_nobody

sed -i -e '
    s/^[[:space:]]*\([GU]ID_MIN[[:space:]]\+\)[[:digit:]]\+/\15000/
    s/^[[:space:]]*\([GU]ID_MAX[[:space:]]\+\)[[:digit:]]\+/\18999/
' /etc/login.defs

sed -i -e '
    s/^[[:space:]]*\(FIRST_[GU]ID[[:space:]]*=[[:space:]]*\)[[:digit:]]\+/\15000/
    s/^[[:space:]]*\(LAST_[GU]ID[[:space:]]*=[[:space:]]*\)[[:digit:]]\+/\18999/
    s/^[[:space:]]*#\?[[:space:]]*\(ADD_EXTRA_GROUPS[[:space:]]*=[[:space:]]*\)[[:digit:]]\+/\11/
    s/^[[:space:]]*#\?[[:space:]]*\(EXTRA_GROUPS[[:space:]]*=[[:space:]]*\).*/\1"aid_inet aid_sdcard_rw aid_sdcard_r"/
' /etc/adduser.conf

echo "Done."
