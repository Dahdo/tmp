#!/bin/sh

# script restores file structure on an SD card

# 
mount /dev/mmcblk0p1 /mnt
cd /mnt

echo "Switch on a python webserver at the root directory of the project on your PC (python -m http.server)"

echo "Press 's' to confirm"
while : ; do
read -n 1 k <&1
if [[ $k = s ]] ; then
printf "\nQuitting from the program\n"
break
else
echo "Press 's' to confirm"
fi

rm boot.scr -f
wget http://p30314:8000/task3_uboot/boot.scr
cd user
rm Image -f
rm bcm2711-rpi-4-b.dtb -f
rm Image_admin -f
rm Image_util -f
wget http://p30314:8000/buildroot-2023.02_admin/output/images/bcm2711-rpi-4-b.dtb
wget http://p30314:8000/buildroot-2023.02_admin/output/images/u-boot.bin -O Image
wget http://p30314:8000/buildroot-2023.02_admin/output/images/Image -O Image_admin
wget http://p30314:8000/buildroot-2023.02_utility/output/images/Image -O Image_util


