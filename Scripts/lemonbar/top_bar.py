#!/usr/bin/env python3

#Written by Cosmophile
import os, sys, select, datetime, subprocess, atexit

def output_of(cmd):
    try:
        return subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    except:
        return None

class Widget(object):
    @staticmethod
    def available():
        """Determines if widget is available/makes sense on this system."""
        return True

    def __init__(self, pipe, hooks):
        """Initialize widget. The widget may spawn a subprocess and feed its stdout
        into pipe. The main loop runs through all lines received on all widget pipes
        and calls hooks based on the first word in a line. If
        hooks["my_trigger"] = self
        is set, this widget's update function will be called if the main loop sees
        a line starting with 'my_trigger'."""
        pass

    def update(self, line):
        """Update widget's internal state based on data received via the main loop."""
        pass

    def render(self):
        """Render the widget."""
        return ''

class PulseAudio(Widget):
    #Icons don't work in debian's version of lemonbar,
    #and I'm not bothering with compiling the fork that has this feature.
    #icon_loud = ' \ue05d '
    #icon_mute = ' \ue04f '
    @staticmethod
    def available():
        try:
            subprocess.run(['pactl', 'info'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False
    def __init__(self, pipe, hooks):
        client = subprocess.Popen(['pactl', 'subscribe'], stdout=pipe)
        atexit.register(client.kill)
        self.volume = 0
        self.mute = False
        hooks["Event 'change' on sink"] = self
    def update(self, line):
        painfo = output_of(['pactl', 'info']).splitlines()
        look_for = None
        for l in painfo:
            if l.startswith('Default Sink:'):
                look_for = l.split(':')[1].strip()
                break
        in_sink = False
        look_for = 'Name: ' + look_for
        sink_list = output_of(['pactl', 'list', 'sinks']).splitlines()
        for l in sink_list:
            if not in_sink:
                if look_for in l:
                    in_sink = True
            else:
                if 'Mute:' in l:
                    if l.split(':')[1].strip() == 'yes':
                        self.mute = True
                    else:
                        self.mute = False
                elif 'Volume:' in l:
                    self.volume = int(l.split('/', 2)[1].strip()[:-1])
                    return
    def render(self):
        if self.mute:
            return 'volume: muted' #self.icon_mute + 'muted'
        else:
            return 'volume: ' + str(self.volume) + r'%' #self.icon_loud + str(self.volume) + r'%'

class Text(Widget):
    def __init__(self, text):
        super(Widget, self)
        self.text = text
    def render(self):
        return self.text


class Clock(Widget):
    def render(self):
        return datetime.datetime.now().strftime('%a %b %d %H:%M')


separator = '  ||  '

widgets = ['%{l}', '%{c}', PulseAudio, separator, Clock]

if __name__ == '__main__':
    sread, swrite = os.pipe()
    hooks = {}

    ws = []
    for wc in widgets:
        if type(wc) is str:
            w = Text(wc)
            ws.append(w)
        elif wc.available():
            w = wc(swrite, hooks)
            w.update(None)
            ws.append(w)

    print(''.join(w.render() for w in ws))
    sys.stdout.flush()

    while True:
        ready, _, _ = select.select([sread], [], [], 5)
        # poll / update widgets (rerender only on updates that match hooks,
        # or on regular timeouts)
        updated = False
        if len(ready) > 0:
            for p in ready:
                lines = os.read(p, 4096).decode('utf-8').splitlines()
                for line in lines:
                    for first, hook in hooks.items():
                        if line.startswith(first):
                            updated = True
                            hook.update(line)
        else:
            updated = True
        # render
        if updated:
            print(''.join(w.render() for w in ws))
            sys.stdout.flush()

