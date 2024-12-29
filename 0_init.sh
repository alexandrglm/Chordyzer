#!/bin/sh

echo 'Unpacking chord diagrams ....'
tar -zxvf ./diagrams/guitar_chords.tar.gz -C ./diagrams 
rm -rf ./diagrams/guitar_chords.tar.gz
echo 'Done. Enjoy'
exit 0