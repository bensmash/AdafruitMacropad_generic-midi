# Generic midi controller and note player
# adapted from https://learn.adafruit.com/adafruit-macropad-rp2040/macropad-midi
# updated 5/26/22

from adafruit_macropad import MacroPad
from rainbowio import colorwheel

CCNUM = [
        20, 21, 22,
        23, 24, 25,
        26, 27, 28,
        29, 30, 31]  # CC numbers for each key

MIDI_NUM = [
        57, 58, 59,
        54, 55, 56,
        51, 52, 53,
        48, 49, 50]  # Base Midi note numbers

NOTE = ["A", "A#/B-", "B", "F#/G-", "G", "G#/A-",
        "D#/E-", "E", "F", "C", "C#/D-", "D"]  #Base letter notes

macropad = MacroPad()  # create the macropad object, rotate orientation

mode = 0 #toggle mode

# encoder setup #
last_knob_pos = macropad.encoder #get encoder value

# variables #
octave = 0 # octave offset, default to middle C
wiggle = [0] * 12 # set the base control change value to 0 for each controller
key_active = [False] * 12 # set whether a key is held down active; default to inactive
MIDI_CHANNEL = 0 # midi channel set to 0 (automtically sends 1)

# colors #
macropad.pixels.brightness = 0.125
hotpink = (233, 47, 164)
for key in range(12):
    key_color = colorwheel(key * 10)
    macropad.pixels[key] = key_color

# text #
text_lines = macropad.display_text(title = "  Wigglez  ", title_scale = 2)
text_lines.show()

while True:
    macropad.encoder_switch_debounced.update()  # check the knob switch for press or release
    if macropad.encoder_switch_debounced.pressed:
        mode = (mode+1) % 3
        if mode == 0:  # mode 0 is controller knobs
            text_lines = macropad.display_text(title = "  Wigglez  ", title_scale = 2)
        elif mode == 1:  # mode 1 is MIDI note send
            text_lines = macropad.display_text(title = "   Notez   ", title_scale = 2)
        else:  # mode 2 is MIDI channel select
            text_lines = macropad.display_text(title = "  Channel  ", title_scale = 2)
            text_lines[1].text = ("     Channel = %d" % (MIDI_CHANNEL + 1))
        text_lines.show()

    key_event = macropad.keys.events.get()
    if key_event:
        num = key_event.key_number
        if mode == 0:
            if key_event.pressed:  # press key for active/editable controller
                macropad.pixels[num] = hotpink
                key_active[num] = True
                text_lines[1].text = ("       CC %d: %d" % (CCNUM[num], wiggle[num]))  # show CC number and output value

            if key_event.released:  # release key for no active controller
                macropad.pixels[num] = colorwheel(num*10)
                key_active[num] = False
                text_lines[1].text = ""

        elif mode == 1:
            if key_event.pressed:  # key press to play note
                macropad.pixels[num] = hotpink
                key_active[num] = True
                macropad.midi.send(macropad.NoteOn(MIDI_NUM[num] + (octave * 12), 127), MIDI_CHANNEL)
                text_lines[0].text = ("      MIDI: %d" % (MIDI_NUM[num] + (octave * 12)))  # show midi value w/ octave modifier
                text_lines[1].text = ("      Note: %s" % (NOTE[num]))  # show note letter
            if key_event.released:  # key release to stop note
                macropad.pixels[num] = colorwheel(num*10)
                key_active[num] = False
                macropad.midi.send(macropad.NoteOff(MIDI_NUM[num] + (octave * 12), 0), MIDI_CHANNEL)
                text_lines[0].text = ""
                text_lines[1].text = ""

        else:
            if key_event.pressed:
                macropad.pixels[num] = hotpink
                MIDI_CHANNEL = num
                text_lines[1].text = ("     Channel = %d" % (MIDI_CHANNEL + 1))
            if key_event.released:
                macropad.pixels[num] = colorwheel(num*10)

    if last_knob_pos is not macropad.encoder:  # knob has been turned
        knob_pos = macropad.encoder  # read encoder
        knob_delta = knob_pos - last_knob_pos  # compute knob_delta since last read
        last_knob_pos = knob_pos  # save new reading
        if mode == 0:
            for x in range(len(key_active)):
                if key_active[x] == True:
                    wiggle[x] = min(max(wiggle[x] + knob_delta, 0), 31)  # scale controller value
                    macropad.midi.send(macropad.ControlChange(CCNUM[x], int(wiggle[x]*4.1)), MIDI_CHANNEL)
                    text_lines[1].text = ("       CC %d: %d" % (CCNUM[x], int(wiggle[x]*4.1)))

        if mode == 1:
            octave_old = octave  # save old octave modifier so we can turn note off
            octave = min(max(octave + knob_delta, -4), 5)
            for x in range(len(key_active)):
                if key_active[x] == True:
                    macropad.midi.send(macropad.NoteOff(MIDI_NUM[x]+(octave_old * 12), 0), MIDI_CHANNEL)  # turn off old note
                    macropad.midi.send(macropad.NoteOn(MIDI_NUM[x]+(octave * 12), 127), MIDI_CHANNEL)  # turn on new note
                    text_lines[0].text = ("      MIDI: %d" % (MIDI_NUM[x] + (octave * 12)))

        if mode == 2:
            MIDI_CHANNEL = min(max(MIDI_CHANNEL + knob_delta, 0), 11)
            text_lines[1].text = ("     Channel = %d" % (MIDI_CHANNEL + 1))

    macropad.display.refresh()
