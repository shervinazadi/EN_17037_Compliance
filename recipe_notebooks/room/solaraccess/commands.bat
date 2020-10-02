#!/usr/bin/env bash



cd ./room/solaraccess

/usr/local/radiance/bin/oconv -f scene/opaque/room..opq.mat scene/opaque/room..opq.rad scene/glazing/room..glz.mat scene/glazing/room..glz.rad sky/analemma.rad > room.oct
/usr/local/radiance/bin/rcontrib -aa 0.0 -ab 0 -ad 512 -ar 16 -as 128 -dc 1.0 -dj 0.0 -dp 64 -ds 0.5 -dr 0 -dt 0.0 -I -lr 4 -lw 0.05 -M ./sky/analemma.mod -ss 0.0 -st 0.85 -y 3 room.oct < room.pts > result/room.dc
/usr/local/radiance/bin/rmtxop -c 47.4 119.9 11.6 -fa result/room.dc > result/room.ill