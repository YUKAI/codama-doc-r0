#!/usr/bin/env bash
pushd "$( dirname "${BASH_SOURCE[0]}" )" > /dev/null
RPI_SETUP_DIR="$( pwd )"

# Disable the built-in audio output so there is only one audio
# device in the system
sudo sed -i -e 's/^dtparam=audio=on/#dtparam=audio=on/' /boot/config.txt

# Enable the i2s device tree
sudo sed -i -e 's/#dtparam=i2s=on/dtparam=i2s=on/' /boot/config.txt

echo "Installing Raspberry Pi kernel headers"
sudo apt-get install -y raspberrypi-kernel-headers

# Build loader and insert it into the kernel
if [ "`uname -m`" = "armv6l" ] ; then
    sed -i 's/3f203000\.i2s/20203000\.i2s/' loader/loader.c
    sed -i 's/fe203000\.i2s/20203000\.i2s/' loader/loader.c
elif [ "`cat /proc/device-tree/model | grep -a "Raspberry Pi 4" | wc -l`" -eq "1" ] ; then
    sed -i 's/20203000\.i2s/fe203000\.i2s/' loader/loader.c
    sed -i 's/3f203000\.i2s/fe203000\.i2s/' loader/loader.c
else
    sed -i 's/20203000\.i2s/3f203000\.i2s/' loader/loader.c
    sed -i 's/fe203000\.i2s/3f203000\.i2s/' loader/loader.c
fi
pushd $RPI_SETUP_DIR/loader > /dev/null
make i2s_slave
popd > /dev/null
sudo cp $RPI_SETUP_DIR/loader/loader.ko /lib/modules/`uname -r`/kernel/sound/drivers/
sudo depmod -ae
if ! grep -q "loader" /etc/modules-load.d/modules.conf; then
    sudo sed -i -e '$ a loader' /etc/modules-load.d/modules.conf
fi

# Move existing files to back up
if [ -e ~/.asoundrc ] ; then
    chmod a+w ~/.asoundrc
    cp ~/.asoundrc ~/.asoundrc.bak
    sudo cp /root/.asoundrc /root/.asoundrc.bak
fi
if [ -e /usr/share/alsa/pulse-alsa.conf ] ; then
    sudo mv /usr/share/alsa/pulse-alsa.conf  /usr/share/alsa/pulse-alsa.conf.bak
    #sudo mv ~/.config/lxpanel/LXDE-pi/panels/panel ~/.config/lxpanel/LXDE-pi/panels/panel.bak
fi
if [ -e ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-mixer.xml ] ; then
  cp ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-mixer.xml ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-mixer.xml.bak
fi

# Check args for asoundrc selection. Default to VF Stereo.
dpkg -s lxplug-volumepulse > /dev/null 2>&1
if [ $? -eq 0 ]; then
    if [ ! -e /etc/asound.conf ]; then
        sudo cp $RPI_SETUP_DIR/resources/asoundrc_vf /etc/asound.conf
    else
        if ! grep -q "VocalFusion" /etc/asound.conf; then
            cp $RPI_SETUP_DIR/resources/asoundrc_vf ~/.asoundrc
            sudo cp $RPI_SETUP_DIR/resources/asoundrc_vf /root/.asoundrc
        fi
    fi
else
    cp $RPI_SETUP_DIR/resources/asoundrc_vf ~/.asoundrc
    sudo cp $RPI_SETUP_DIR/resources/asoundrc_vf /root/.asoundrc
fi
cp $RPI_SETUP_DIR/resources/panel ~/.config/lxpanel/LXDE-pi/panels/panel
mkdir -p ~/.config/xfce4/xfconf/xfce-perchannel-xml/
cp $RPI_SETUP_DIR/resources/xfce4-mixer.xml ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-mixer.xml
chmod 700 ~/.config/xfce4/xfconf/xfce-perchannel-xml

# Make the asoundrc file read-only otherwise lxpanel rewrites it
# as it doesn't support anything but a hardware type device
chmod a-w ~/.asoundrc
sudo chmod a-w /root/.asoundrc


# Apply changes
sudo /etc/init.d/alsa-utils restart


# Configure the I2C - disable the default built-in driver
if [ "`uname -r | cut -d. -f1`" -le "4" ] ; then
    sudo sed -i -e 's/#\?dtparam=i2c_arm=on/dtparam=i2c_arm=off/' /boot/config.txt
    if ! grep -q "i2c-bcm2708" /etc/modules-load.d/modules.conf; then
        sudo sh -c 'echo i2c-bcm2708 >> /etc/modules-load.d/modules.conf'
    fi
    if ! grep -q "i2c-dev" /etc/modules-load.d/modules.conf; then
        sudo sh -c 'echo i2c-dev >> /etc/modules-load.d/modules.conf'
    fi
    if ! grep -q "options i2c-bcm2708 combined=1" /etc/modprobe.d/i2c.conf; then
        sudo sh -c 'echo "options i2c-bcm2708 combined=1" >> /etc/modprobe.d/i2c.conf'
    fi

    # Build a new I2C driver
    if [ "`uname -r | cut -d. -f1-2`" != "4.19" ] ; then
        pushd $RPI_SETUP_DIR/i2c-gpio-param > /dev/null
        make || exit $?
        popd > /dev/null
        sudo cp $RPI_SETUP_DIR/i2c-gpio-param/i2c-gpio-param.ko /lib/modules/`uname -r`/kernel/drivers/i2c/
        sudo depmod -ae
        if ! grep -q "i2c-gpio-param" /etc/modules-load.d/modules.conf; then
            sudo sed -i -e '$ a i2c-gpio-param' /etc/modules-load.d/modules.conf
        fi
        if ! grep -q "options i2c-gpio-param busid=1 sda=2 scl=3 udelay=5 timeout=100 sda_od=0 scl_od=0 scl_oo=0" /etc/modprobe.d/i2c.conf; then
            sudo sed -i -e '$ a options i2c-gpio-param busid=3 sda=2 scl=3 udelay=5 timeout=100 sda_od=0 scl_od=0 scl_oo=0' /etc/modprobe.d/i2c.conf
        fi
    else
        if ! grep -q "dtoverlay=i2c-gpio,bus=3,i2c_gpio_sda=2,i2c_gpio_scl=3,i2c_gpio_delay_us=5,timeout-ms=100" /boot/config.txt; then
             sudo sed -i -e '$ a dtoverlay=i2c-gpio,bus=3,i2c_gpio_sda=2,i2c_gpio_scl=3,i2c_gpio_delay_us=5,timeout-ms=100' /boot/config.txt
        fi
    fi
else
    # Enable the I2C device tree
    sudo raspi-config nonint do_i2c 1
    sudo raspi-config nonint do_i2c 0

    # Set the I2C baudrate to 100k
    sudo sed -i -e '/^dtparam=i2c_arm_baudrate/d' /boot/config.txt
    sudo sed -i -e 's/dtparam=i2c_arm=on$/dtparam=i2c_arm=on\ndtparam=i2c_arm_baudrate=100000/' /boot/config.txt

    if ! grep -q "i2c-dev" /etc/modules-load.d/modules.conf; then
        sudo sh -c 'echo i2c-dev >> /etc/modules-load.d/modules.conf'
    fi
fi


if ! grep -q "# Run Alsa at startup so that alsamixer configures" /etc/rc.local; then
    sudo sed -i -e '$i \# Run Alsa at startup so that alsamixer configures' /etc/rc.local
    sudo sed -i -e '$i \arecord -d 1 > /dev/null 2>&1' /etc/rc.local
    sudo sed -i -e '$i \aplay dummy > /dev/null 2>&1' /etc/rc.local
fi

# setup Utils
if [ "`uname -m`" = "aarch64" ] ; then
  if [ "`uname -r | cut -d. -f1`" -le "4" ] ; then
    sudo cp -p ../utils/codama_i2c-64 /usr/local/bin/codama_i2c
    sudo cp -p ../utils/codama_dfu_i2c-64 /usr/local/bin/codama_dfu_i2c
  else
    sudo cp -p ../utils/codama_i2c-64.kernel5 /usr/local/bin/codama_i2c
    sudo cp -p ../utils/codama_dfu_i2c-64.kernel5 /usr/local/bin/codama_dfu_i2c
  fi
  sudo cp -p ../utils/codama_usb-64 /usr/local/bin/codama_usb
else
  if [ "`uname -r | cut -d. -f1`" -le "4" ] ; then
    sudo cp -p ../utils/codama_i2c /usr/local/bin/codama_i2c
    sudo cp -p ../utils/codama_dfu_i2c /usr/local/bin/codama_dfu_i2c
  else
    sudo cp -p ../utils/codama_i2c.kernel5 /usr/local/bin/codama_i2c
    sudo cp -p ../utils/codama_dfu_i2c.kernel5 /usr/local/bin/codama_dfu_i2c
  fi
  sudo cp -p ../utils/codama_usb /usr/local/bin/codama_usb
fi

REQUIRED_LIB_READLINE="libreadline.so.7"
REQUIRED_LIB_READLINE_PATH=$(find /lib/ -name $REQUIRED_LIB_READLINE)
if [ -z "$REQUIRED_LIB_READLINE_PATH" ]; then # if the version of libreadline.so codama_dfu_i2c requires does not exsist
    # Use latest libreadline instead. See #issue1
    LATEST_LIB_READLINE_PATH=$(find /lib/ -name "libreadline.so*" | sort | tail -1)
    LIB_READLINE_DIR=$(dirname $LATEST_LIB_READLINE_PATH)
    sudo ln -s $LATEST_LIB_READLINE_PATH $LIB_READLINE_DIR/$REQUIRED_LIB_READLINE
fi

echo "To enable I2S and I2C, this Raspberry Pi must be rebooted."

popd > /dev/null
