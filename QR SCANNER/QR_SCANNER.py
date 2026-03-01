# -*- coding: utf-8 -*-

from com.github.sarxos.webcam import Webcam
from javax.swing import JFrame, JLabel, JButton, JPanel, ImageIcon
from java.lang import Thread
from javax.imageio import ImageIO
from java.io import File, FileInputStream
from java.net import InetAddress
from java.awt import BorderLayout, Dimension
from com.sun.net.httpserver import HttpsServer, HttpsConfigurator
from java.net import InetSocketAddress
from javax.net.ssl import SSLContext, KeyManagerFactory, TrustManagerFactory
from java.security import KeyStore
from java.sql import DriverManager, Statement
from java.lang import Class
import time
import os

from com.google.zxing import BarcodeFormat
from com.google.zxing.qrcode import QRCodeWriter
from com.google.zxing.client.j2se import MatrixToImageWriter


class QR_Image_Server(Thread):

    def __init__(self):

        self.webcam = Webcam.getDefault()
        sizes = self.webcam.getViewSizes()
        self.webcam.setViewSize(sizes[-1])
        self.webcam.open(True)

        if not os.path.exists("output"):
            os.makedirs("output")
        
        self.photo_counter = self.get_next_photo_number()

        self.port = 8000
        self.start_server()

        if not os.path.exists("OUTPUT"):
            os.makedirs("OUTPUT")

        self.frame = JFrame("Image → QR Style")
        self.video_label = JLabel()
        self.video_label.setPreferredSize(Dimension(1000, 700))
        self.qr_label = JLabel()

        self.capture_btn = JButton(
            "Capture & Generate QR",
            actionPerformed=self.capture
        )

        panel = JPanel()
        panel.add(self.capture_btn)

        self.frame.add(self.video_label, BorderLayout.CENTER)
        self.frame.add(self.qr_label, BorderLayout.EAST)
        self.frame.add(panel, BorderLayout.SOUTH)

        self.frame.setSize(1400, 900)
        self.frame.setVisible(True)
        self.frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE)

        Thread.__init__(self)

    def get_next_photo_number(self):

        files = os.listdir("output")
        numbers = []

        for f in files:
            if f.startswith("photo_") and f.endswith(".png"):
                try:
                    num = int(f.replace("photo_", "").replace(".png", ""))
                    numbers.append(num)
                except:
                    pass

        if numbers:
            return max(numbers) + 1
        else:
            return 1

    def connect_db(self):
        Class.forName("com.mysql.cj.jdbc.Driver")
        url = "jdbc:mysql://localhost:3306/qr_system"
        user = "root"
        password = "YourNewPassword123!"
        return DriverManager.getConnection(url, user, password)

    def start_server(self):

        password = list("13022003")

        ks = KeyStore.getInstance("JKS")
        fis = FileInputStream("keystore.jks")
        ks.load(fis, password)

        kmf = KeyManagerFactory.getInstance("SunX509")
        kmf.init(ks, password)

        tmf = TrustManagerFactory.getInstance("SunX509")
        tmf.init(ks)

        sslContext = SSLContext.getInstance("TLS")
        sslContext.init(kmf.getKeyManagers(), tmf.getTrustManagers(), None)

        self.server = HttpsServer.create(InetSocketAddress(self.port), 0)
        self.server.setHttpsConfigurator(HttpsConfigurator(sslContext))

        def handler(exchange):
            path = exchange.getRequestURI().getPath()[1:]
            file = File("output/" + path)
            if file.exists():
                bytes = open("output/" + path, "rb").read()
                exchange.sendResponseHeaders(200, len(bytes))
                os_stream = exchange.getResponseBody()
                os_stream.write(bytes)
                os_stream.close()
            else:
                exchange.sendResponseHeaders(404, 0)
                exchange.close()

        self.server.createContext("/", handler)
        self.server.setExecutor(None)
        self.server.start()

    def capture(self, event):

        image = self.webcam.getImage()
        if image is None:
            return

        current_id = self.photo_counter

        filename = "photo_" + str(current_id) + ".png"
        image_path = "output/" + filename
        ImageIO.write(image, "PNG", File(image_path))

        ip = InetAddress.getLocalHost().getHostAddress()
        url = "https://" + ip + ":" + str(self.port) + "/" + filename

        writer = QRCodeWriter()
        matrix = writer.encode(url, BarcodeFormat.QR_CODE, 300, 300)

        qr_filename = "qr_" + str(current_id) + ".png"
        qr_path = "output/" + qr_filename
        qr_file = File(qr_path)
        MatrixToImageWriter.writeToPath(matrix, "PNG", qr_file.toPath())

        qr_img = ImageIO.read(qr_file)
        self.qr_label.setIcon(ImageIcon(qr_img))

        conn = self.connect_db()

        insert_stmt = conn.prepareStatement(
            "INSERT INTO qr_images (image_data, qr_data, image_url) VALUES (?, ?, ?)",
            Statement.RETURN_GENERATED_KEYS
        )

        img_stream = FileInputStream(File(image_path))
        qr_stream = FileInputStream(File(qr_path))

        insert_stmt.setBinaryStream(1, img_stream, File(image_path).length())
        insert_stmt.setBinaryStream(2, qr_stream, File(qr_path).length())
        insert_stmt.setString(3, url)

        insert_stmt.executeUpdate()

        img_stream.close()
        qr_stream.close()
        insert_stmt.close()
        conn.close()

        self.photo_counter += 1

    def run(self):

        while self.webcam.isOpen():
            image = self.webcam.getImage()
            if image is not None:
                self.video_label.setIcon(ImageIcon(image))
            time.sleep(0.05)


if __name__ == "__main__":
    app = QR_Image_Server()
    app.start()