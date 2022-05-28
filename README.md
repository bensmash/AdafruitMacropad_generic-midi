# AdafruitMacropad_generic-midi
Generic MIDI controller for Adafruit Macropad

Controller has three modes:
1) Control change messages: when any key is held down and the encoder is turned, a control change message is sent. Keys map to CCs 20-31.
2) MIDI note on/off. Defaults bottom left key (key 9) to note C3 (MIDI 48) and then moving from left to right, top to bottom, keys map to additional half steps up. Moving the encoder wheel will change the octave up/down.
3) MIDI channel change: Selects MIDI out channel for send messages in modes 1 and 2. Keys or encoder can be used to select channel from 1 to 12.

Adapted from: https://learn.adafruit.com/adafruit-macropad-rp2040/macropad-midi
Requires Adafruit Macropad and rainbowio librarys
