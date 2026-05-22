"""
Printer backends. ReceiptPrinter picks the right backend based on config.

Supported connections (set via config["connection"]):
  stdout   — prints to terminal, good for testing (default)
  file     — writes to a text file (config["path"])
  win32raw — sends to a Windows printer by name (config["printerName"])
  usb      — USB ESC/POS printer (config["vendor_id"], config["product_id"])
  serial   — serial ESC/POS printer (config["port"], config["baudrate"])

If win32raw fails (e.g. missing pywin32 or no printer), it silently falls back to stdout.
"""
import sys

try:
    from escpos.printer import Usb, Serial, Win32Raw
    ESCPOS_AVAILABLE = True
except ImportError:
    ESCPOS_AVAILABLE = False


class ReceiptPrinter:
    """Connects to a printer backend and exposes printWith() for sending receipts."""
    def __init__(self, config: dict = None, debug: bool = False):
        self.config = config or {}
        self.debug = debug
        self._p = None
        self._ip = None
        if self.config.get("saveImages") and self.debug:
            from printing.imagePrinter import ImagePrinter
            self._ip = ImagePrinter(self.config, outputDir=self.config.get("outputDir", "output"))

    def _fallback(self):
        """Return StdoutPrinter in debug mode, NullPrinter otherwise."""
        return StdoutPrinter() if self.debug else NullPrinter()

    def _connect(self):
        conn = self.config.get("connection", "stdout")

        if conn == "win32raw":
            try:
                if not ESCPOS_AVAILABLE:
                    raise RuntimeError("escpos not available")
                self._p = Win32Raw(self.config.get("printerName"))
                self._p.open()
                font = self.config.get("escposFont", "a")
                if font != "a":
                    self._p = FontWrapper(self._p, font)
                if self.config.get("useCardImages"):
                    self._p = CardAwareWrapper(self._p, self.config)
            except Exception:
                self._p = self._fallback()

        elif conn == "usb":
            if not ESCPOS_AVAILABLE:
                raise RuntimeError("python-escpos not installed. Run: pip install python-escpos")
            vid = int(self.config.get("vendor_id", "0x04b8"), 16)
            pid = int(self.config.get("product_id", "0x0202"), 16)
            in_ep = int(self.config.get("in_ep", "0x82"), 16)
            out_ep = int(self.config.get("out_ep", "0x01"), 16)
            self._p = Usb(vid, pid, in_ep=in_ep, out_ep=out_ep)
            font = self.config.get("escposFont", "a")
            if font != "a":
                self._p = FontWrapper(self._p, font)

        elif conn == "serial":
            if not ESCPOS_AVAILABLE:
                raise RuntimeError("python-escpos not installed. Run: pip install python-escpos")
            port = self.config.get("port", "COM1")
            baud = int(self.config.get("baudrate", 9600))
            self._p = Serial(port, baudrate=baud)

        elif conn == "file":
            self._p = FilePrinter(self.config.get("path", "receipt.txt"))
            self._p.open()

        elif conn == "image":
            from printing.imagePrinter import ImagePrinter
            output_dir = self.config.get("outputDir", "output")
            self._p = ImagePrinter(self.config, outputDir=output_dir)

        else:
            self._p = self._fallback()

    def printWith(self, fn) -> None:
        """Call fn(p) to write content, then cut the paper."""
        if self._p is None:
            self._connect()
        try:
            fn(self._p)
            self._p.cut()
        except Exception as e:
            print(f"[Tulostin: virhe tulostuksessa — {e}]")
            self._p = None
            return
        # win32raw batches everything into one spooler job until close() is called.
        # Wait briefly for the printer to process the receipt, then purge the whole
        # queue so offline jobs never accumulate between sessions.
        if self.config.get("connection") == "win32raw":
            self._p.close()
            self._p = None
            import time
            time.sleep(self._getWin32PurgDelay())
            self._win32PurgeAll(self.config.get("printerName"))
        if self._ip is not None:
            fn(self._ip)
            self._ip.cut()

    def _getWin32PurgDelay(self) -> float:
        return float(self.config.get("win32PurgeDelaySec", 2.0))

    def _win32DeleteJobs(self, printerName: str, jobs) -> None:
        try:
            import win32print
            handle = win32print.OpenPrinter(printerName)
            try:
                for job in jobs:
                    try:
                        win32print.SetJob(handle, job["JobId"], 0, None, win32print.JOB_CONTROL_PAUSE)
                    except Exception:
                        pass
                    try:
                        win32print.SetJob(handle, job["JobId"], 0, None, win32print.JOB_CONTROL_DELETE)
                    except Exception:
                        pass
            finally:
                win32print.ClosePrinter(handle)
        except Exception:
            pass

    def _win32PurgeAll(self, printerName: str) -> None:
        try:
            import win32print
            handle = win32print.OpenPrinter(printerName)
            jobs = win32print.EnumJobs(handle, 0, 99, 1)
            win32print.ClosePrinter(handle)
            self._win32DeleteJobs(printerName, jobs)
        except Exception:
            pass

    def _win32PurgeStuck(self, printerName: str) -> None:
        _STUCK = 0x0002 | 0x0020 | 0x0040  # ERROR | OFFLINE | PAPEROUT
        try:
            import win32print
            handle = win32print.OpenPrinter(printerName)
            jobs = [j for j in win32print.EnumJobs(handle, 0, 99, 1) if j["Status"] & _STUCK]
            win32print.ClosePrinter(handle)
            self._win32DeleteJobs(printerName, jobs)
        except Exception:
            pass

    def close(self) -> None:
        if self._p is not None:
            self._p.close()
            self._p = None
        if self._ip is not None:
            self._ip.close()
            self._ip = None

    def printReceipt(self, data: dict, formatter) -> None:
        if self._p is None:
            self._connect()
        formatter(data, self._p)
        self._p.cut()
        self._p.close()


class NullPrinter:
    """Silently discards all output. Used in normal mode to suppress terminal receipt output."""
    def set(self, **_): pass
    def open(self): pass
    def textln(self, text=""): pass
    def text(self, text=""): pass
    def cut(self): pass
    def close(self): pass
    def printWith(self, fn): pass


class StdoutPrinter:
    def __init__(self):
        self._num = 0
        self._started = False

    def set(self, **_): pass
    def open(self): pass

    def _startIfNeeded(self):
        if not self._started:
            self._num += 1
            sys.stdout.buffer.write(f"\n~~~ RECEIPT {self._num} START ~~~\n".encode("utf-8"))
            sys.stdout.buffer.flush()
            self._started = True

    def textln(self, text=""):
        self._startIfNeeded()
        sys.stdout.buffer.write((str(text) + "\n").encode("utf-8"))
        sys.stdout.buffer.flush()

    def text(self, text=""):
        self._startIfNeeded()
        sys.stdout.buffer.write(str(text).encode("utf-8"))
        sys.stdout.buffer.flush()

    def cut(self):
        sys.stdout.buffer.write(f"~~~ RECEIPT {self._num} END ~~~\n".encode("utf-8"))
        sys.stdout.buffer.flush()
        self._started = False

    def close(self):
        sys.stdout.buffer.flush()


class FontWrapper:
    """Injects a default ESC/POS font into every set() call so formatters don't need to know about it."""
    def __init__(self, printer, font):
        self._p = printer
        self._font = font

    def set(self, **kwargs):
        kwargs.setdefault("font", self._font)
        self._p.set(**kwargs)

    def textln(self, text=""):    self._p.textln(text)
    def text(self, text=""):      self._p.text(text)
    def image(self, img):         self._p.image(img)
    def cut(self):                self._p.cut()
    def close(self):              self._p.close()


class CardAwareWrapper:
    """Wraps a real ESC/POS printer to render card text rows as images instead of Unicode text."""
    def __init__(self, printer, config):
        self._p = printer
        self._config = config
        self._style = {}

    def set(self, **kwargs):
        self._style.update(kwargs)
        self._p.set(**kwargs)

    def textln(self, text=""):
        if self._style.get("double_width") or self._style.get("double_height"):
            from printing.imagePrinter import _parseCards, _buildCardRowImage
            cards = _parseCards(str(text))
            if cards:
                img = _buildCardRowImage(cards, self._config)
                if img is not None:
                    self._p.set(invert=False)
                    self._p.image(img)
                    return
        self._p.textln(text)

    def text(self, text=""):
        self._p.text(text)

    def cut(self):
        self._p.cut()

    def close(self):
        self._p.close()


class FilePrinter:
    def __init__(self, path: str):
        self.path = path
        self._buf = []

    def open(self):
        self._buf = []

    def set(self, **_): pass

    def textln(self, text=""):
        self._buf.append(str(text))

    def text(self, text=""):
        self._buf.append(str(text))

    def cut(self):
        self._buf.append("\n" + "-" * 32)

    def close(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("\n".join(self._buf))
        print(f"[Receipt saved to {self.path}]")
