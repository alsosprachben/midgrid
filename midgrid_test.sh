python midgrid_parser.py fugue_satb_registration.midgrid fugue_satb_registration.mid
python midgrid_emitter.py fugue_satb_registration.mid >fugue_satb_registration2.midgrid
python midgrid_parser.py fugue_satb_registration2.midgrid fugue_satb_registration2.mid
python midgrid_emitter.py fugue_satb_registration2.mid > fugue_satb_registration3.midgrid

printf "fugue_satb_registration.midgrid:\n"
cat fugue_satb_registration.midgrid
printf "fugue_satb_registration2.midgrid:\n"
cat fugue_satb_registration2.midgrid
printf "fugue_satb_registration3.midgrid:\n"
cat fugue_satb_registration3.midgrid