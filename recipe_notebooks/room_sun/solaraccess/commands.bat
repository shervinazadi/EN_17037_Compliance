#!/usr/bin/env bash



cd ./room_sun/solaraccess

/usr/local/radiance/bin/oconv -f scene/opaque/room_sun..opq.mat scene/opaque/room_sun..opq.rad scene/glazing/room_sun..glz.mat scene/glazing/room_sun..glz.rad sky/analemma.rad > room_sun.oct
/usr/local/radiance/bin/rcontrib -aa 0.0 -ab 0 -ad 512 -ar 16 -as 128 -dc 1.0 -dj 0.0 -dp 64 -ds 0.5 -dr 0 -dt 0.0 -I -lr 4 -lw 0.05 -M ./sky/analemma.mod -ss 0.0 -st 0.85 -y 3 room_sun.oct < room_sun.pts > result/room_sun.dc
/usr/local/radiance/bin/rmtxop -c 47.4 119.9 11.6 -fa result/room_sun.dc > result/room_sun.ill