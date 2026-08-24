%% Give every Voice its own MIDI channel.
%%
%% LilyPond's default packs all voices of a staff onto one channel. That is fine
%% for a single line, but an engraving that writes two voices on one staff --
%% BWV 565's toccata does, with `<< { ... } \\ { ... } >>` and s32 spacers -- then
%% loses information no later stage can recover: where the two voices share a
%% pitch, one voice's note-off ends the other voice's SUSTAINED note. The held
%% lower notes of 565's broken-chord figures simply vanish, and the passage comes
%% out as an undifferentiated run of equal semiquavers.
%%
%% A top-level \midi block supplies defaults to every \midi in the file, so this
%% needs no edit to the engraving itself.
\midi {
  \context {
    \Score
    midiChannelMapping = #'voice
  }
}
