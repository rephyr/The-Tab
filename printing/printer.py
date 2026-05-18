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
            name = self.config.get("printerName")
            self._p = Win32Raw(name)
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

        else:
            self._p = _StdoutPrinter()

    def printReceipt(self, text: str) -> None:
        if self._p is None:
            self._connect()
        self._p.text(text)
        if hasattr(self._p, "cut"):
            self._p.cut()


class _StdoutPrinter:
    def text(self, content: str) -> None:
        print(content)


class _FilePrinter:
    def __init__(self, path: str):
        self.path = path

    def text(self, content: str) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[Receipt saved to {self.path}]")
