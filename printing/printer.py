import sys

try:
    from escpos.printer import Usb, Serial, Win32Raw
    ESCPOS_AVAILABLE = True
except ImportError:
    ESCPOS_AVAILABLE = False


class ReceiptPrinter:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self._p = None

    def _connect(self):
        conn = self.config.get("connection", "stdout")

        if conn == "win32raw":
            if not ESCPOS_AVAILABLE:
                raise RuntimeError("python-escpos not installed. Run: pip install python-escpos")
            self._p = Win32Raw(self.config.get("printerName"))
            self._p.open()

        elif conn == "usb":
            if not ESCPOS_AVAILABLE:
                raise RuntimeError("python-escpos not installed. Run: pip install python-escpos")
            vid = int(self.config.get("vendor_id", "0x04b8"), 16)
            pid = int(self.config.get("product_id", "0x0202"), 16)
            self._p = Usb(vid, pid)

        elif conn == "serial":
            if not ESCPOS_AVAILABLE:
                raise RuntimeError("python-escpos not installed. Run: pip install python-escpos")
            port = self.config.get("port", "COM1")
            baud = int(self.config.get("baudrate", 9600))
            self._p = Serial(port, baudrate=baud)

        elif conn == "file":
            self._p = _FilePrinter(self.config.get("path", "receipt.txt"))
            self._p.open()

        else:
            self._p = _StdoutPrinter()

    def printReceipt(self, data: dict, formatter) -> None:
        if self._p is None:
            self._connect()
        formatter(data, self._p)
        self._p.cut()
        self._p.close()


class _StdoutPrinter:
    def set(self, **_): pass
    def open(self): pass
    def textln(self, text=""): sys.stdout.buffer.write((str(text) + "\n").encode("utf-8"))
    def text(self, text=""): sys.stdout.buffer.write(str(text).encode("utf-8"))
    def cut(self): sys.stdout.buffer.write(("\n" + "-" * 32 + "\n").encode("utf-8"))
    def close(self): sys.stdout.buffer.flush()


class _FilePrinter:
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
