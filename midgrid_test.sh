set -e

target="${1}"
if [ '!' "${target}" ]
then
	target=fugue_satb_registration
fi
if [ -f "${1}".midgrid ]
then
	python midgrid_parser.py "${1}".midgrid "${1}".mid
fi
python midgrid_emitter.py "${1}".mid >"${1}"2.midgrid
python midgrid_parser.py "${1}"2.midgrid "${1}"2.mid
python midgrid_emitter.py "${1}"2.mid > "${1}"3.midgrid

if [ -f "${1}".midgrid ]
then
    printf "${1}.midgrid:\n"
    cat "${1}".midgrid
fi
printf "${1}2.midgrid:\n"
cat "${1}"2.midgrid
printf "${1}3.midgrid:\n"
cat "${1}"3.midgrid
