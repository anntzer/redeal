# vim: set fileencoding=utf-8
from __future__ import division, print_function, unicode_literals
import random
import sys
import threading
if sys.version_info.major < 3:
    import Tkinter as tk
else:
    import tkinter as tk

from . import globals
from . import redeal


def check_button(master, state, **kwargs):
    var = tk.IntVar()
    button = tk.Checkbutton(master, variable=var, **kwargs)
    button.get_value = var.get
    getattr(button, "select" if state else "deselect")()
    return button


def scrolled_text(master, **kwargs):
    frame = tk.Frame(master)
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text = tk.Text(frame, yscrollcommand=scrollbar.set, **kwargs)
    text.pack(side=tk.TOP)
    scrollbar.config(command=text.yview)
    return frame, text


class Application(tk.Frame):
    func_text_height = 5
    out_text_height = 20
    spinbox_width = 5

    def __init__(self, master, main):
        tk.Frame.__init__(self, master)
        self.main = main
        self.texts = []
        self.create_widgets()
        self.pack()

    def create_text(self, master, name, signature, default, height=None):
        frame = tk.Frame(master)
        proto = "def {name}({signature}):".format(
            name=name, signature=", ".join(signature))
        tk.Label(frame, text=proto).pack(side=tk.TOP, anchor="w")
        inner, text = scrolled_text(frame, height=height if height is not None
                                           else self.func_text_height)
        inner.pack(side=tk.TOP)
        text.insert("end", "\t" + default)
        frame.pack(side=tk.TOP)
        self.texts.append((name, signature, text))

    def create_widgets(self):
        # configurables, #1
        frame = tk.Frame(self)
        self.long = check_button(frame, self.main.args.long,
                                 text="long output for diagrams")
        self.long.pack(side=tk.LEFT)
        self.verbose = check_button(frame, self.main.args.verbose,
                                    text="be verbose")
        self.verbose.pack(side=tk.LEFT)
        frame.pack(side=tk.TOP)
        frame = tk.Frame(self)
        tk.Label(frame, text="RNG seed").pack(side=tk.LEFT)
        seed = tk.Entry(frame, width=8)
        seed.pack(side=tk.LEFT)
        tk.Button(frame, text="Reseed",
                  command=lambda: random.seed(int(seed.get()))).pack(side=tk.LEFT)
        frame.pack(side=tk.TOP)
        # configurables, #2
        for dest, text in [("n", "Number of requested deals:"),
                           ("max", "Maximum number of tries:")]:
            frame = tk.Frame(self)
            tk.Label(frame, text=text).pack(side=tk.LEFT)
            spinbox = tk.Spinbox(frame, from_=0, to=sys.maxsize,
                                 width=self.spinbox_width)
            spinbox.delete(0)
            spinbox.insert(tk.END, str(getattr(self.main.args, dest)))
            spinbox.pack(side=tk.LEFT)
            setattr(self, dest, spinbox)
            frame.pack(side=tk.TOP)
        # hands
        frame = tk.Frame(self)
        for seat, long_seat in zip(globals.SEATS, globals.LONG_SEATS):
            inner = tk.Frame(frame)
            tk.Label(inner, text=long_seat).pack(side=tk.TOP)
            seat_entry = tk.Entry(inner, width=16)
            seat_entry.insert(tk.END,
                self.main.predeal.get(seat, redeal.H("- - - -")).to_str())
            setattr(self, seat, seat_entry)
            seat_entry.pack(side=tk.TOP)
            inner.pack(side=tk.LEFT)
        frame.pack(side=tk.TOP)
        # functions
        for name, signature, body in self.main.given_funcs:
            self.create_text(self, name, signature, body)
        # run & quit
        frame = tk.Frame(self)
        self.run_button = tk.Button(frame, text="Run", command=self.run)
        self.run_button.pack(side=tk.LEFT)
        self.stop_button = tk.Button(frame, text="Stop", command=self.stop,
                                     state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        tk.Button(frame, text="Clear", command=self.clear).pack(side=tk.LEFT)
        tk.Button(frame, text="Quit", command=self.quit).pack(side=tk.LEFT)
        frame.pack(side=tk.TOP)
        # output
        inner, self.out = scrolled_text(self, height=self.out_text_height)
        inner.pack(side=tk.TOP)
        # copyright
        (tk.Label(self, text=globals.__copyright__, relief=tk.SUNKEN).
         pack(side=tk.BOTTOM, fill=tk.X))

    def run(self):
        _globals_SUITS_SYM = globals.SUITS_SYM
        globals.SUITS_SYM = globals.SUITS_SYM_UNICODE
        # override configurables #1
        redeal.Hand.set_str_style(
            redeal.Hand.LONG if self.long.get_value() else redeal.Hand.SHORT)
        redeal.Deal.set_str_style(
            redeal.Deal.LONG if self.long.get_value() else redeal.Deal.SHORT)
        _verbose = self.main.args.verbose
        self.main.args.verbose = self.verbose.get_value()
        # override configurables #1
        _n = self.main.args.n
        self.main.args.n = int(self.n.get())
        _max = self.main.args.max
        self.main.args.max = eval(self.max.get())
        # override hands
        _predeal = self.main.predeal.copy()
        for seat in globals.SEATS:
            self.main.predeal[seat] = redeal.H(getattr(self, seat).get())
        # override functions
        funcs = {name: self.main.create_func(name, signature,
                                             text.get(1.0, tk.END))
                 for name, signature, text in self.texts}
        # simulation
        def target():
            self.main.stop_flag = False
            self.run_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            try:
                self.main.generate(funcs)
            finally:
                self.run_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
            # reset settings
            self.main.args.verbose = _verbose
            self.main.args.n = _n
            self.main.args.max = _max
            self.main.predeal = _predeal
            globals.SUITS_SYM = _globals_SUITS_SYM
        threading.Thread(target=target).start()

    def stop(self):
        self.main.stop_flag = True

    def clear(self):
        self.out.delete(1.0, tk.END)


def run_gui(main):
    root = tk.Tk()
    root.title(globals.__fullname__)
    app = Application(root, main)
    _stdout = sys.stdout
    _stderr = sys.stderr

    class TkText(object):
        def write(self, text):
            app.out.insert(tk.END, text)

    sys.stdout = sys.stderr = TkText()

    try:
        app.mainloop()
        try:
            root.destroy()
        except tk.TclError:
            pass
    finally:
        sys.stdout = _stdout
        sys.stderr = _stderr
