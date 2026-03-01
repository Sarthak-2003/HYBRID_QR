# HYBRID_QR
Secure Image Capture &amp; QR-Based HTTPS Server built with Jython and Java. Captures webcam images, stores them as BLOBs in MySQL, generates QR codes containing secure HTTPS URLs, and serves images via an embedded SSL-enabled server. Demonstrates secure networking, database integration, and full-stack system design.

📌 Project Overview
      This project is a secure image capture and QR-based image access system built using:
      Jython (Python on JVM)
      Java Swing (GUI)
      HTTPS Server (SSL/TLS)
      MySQL Database (BLOB storage)
      ZXing QR Code Library
      Webcam Capture API
The system captures images from a webcam, stores them securely in a MySQL database as BLOB data, generates a QR code containing a secure HTTPS URL, and serves the stored image via an embedded HTTPS server.

Features
  ✔ Real-time webcam image capture
  ✔ Automatic image storage in sequential order
  ✔ Secure HTTPS server using SSL keystore
  ✔ QR code generation for each captured image
  ✔ MySQL BLOB storage for images and QR codDatabase Schemaes
  ✔ Auto-increment database integration
  ✔ Local image storage inside /output directory
  ✔ Full GUI interface using Java Swing

Database Schema
CREATE TABLE qr_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_data LONGBLOB,
    qr_data LONGBLOB,
    image_url VARCHAR(255)
);

Prerequisites
  Java 8+
  Jython installed
  MySQL Server running
  SSL keystore generated (keystore.jks)
  Required JARs inside /libs

Security Considerations
  TLS encryption enabled
  Images served only via HTTPS
  Secure keystore-based certificate handling
  Prepared statements prevent SQL injection
