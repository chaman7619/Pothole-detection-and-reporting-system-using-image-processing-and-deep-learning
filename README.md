# 🚧 Real-Time Pothole Detection and Reporting System Using Image Processing and Deep Learning

## 📌 Overview
The **Real-Time Pothole Detection and Reporting System** is an intelligent computer vision application that detects potholes from road images and live video streams using deep learning. The system uses the YOLOv8 object detection model to identify potholes, classify severity levels, log detection data, and send automated alerts.

The project aims to improve road safety by enabling automatic detection and reporting of road damage, reducing reliance on manual inspection.

---

## 🎯 Objectives
- Detect potholes in real-time using deep learning
- Classify potholes based on severity levels
- Log detection data (date, time, confidence, location)
- Provide dashboard visualization
- Send automated email alerts for high severity potholes
- Enable offline execution as standalone application

---

## 🧠 Features

✅ Real-time pothole detection using webcam/dashcam  
✅ Image upload detection  
✅ YOLOv8 deep learning model  
✅ Severity classification (Low / Medium / High)  
✅ CSV logging of detections  
✅ Geographic location tracking  
✅ Automated email notification  
✅ User-friendly dashboard  
✅ Offline executable support  

---

## 🏗️ System Architecture

The system follows a modular architecture consisting of:

1. Input Acquisition (Camera/Image Upload)
2. Preprocessing
3. YOLOv8 Detection Model
4. Severity Classification
5. CSV Logging
6. Email Notification
7. Dashboard Interface

---

## ⚙️ Tech Stack

### Programming Language
- Python

### Libraries & Frameworks
- OpenCV
- NumPy
- Pandas
- Ultralytics YOLOv8
- TensorFlow / PyTorch
- Flask
- Matplotlib

### Tools
- Roboflow Dataset
- LabelImg (annotation)
- PyInstaller (executable build)

---

## 📂 Dataset
The model is trained on a pothole dataset containing approximately **3,490 images** with various lighting and road conditions.

Dataset Source: Roboflow

---

## 🧪 Methodology

1️⃣ Data Collection  
Images collected from dataset with varied road conditions  

2️⃣ Data Preprocessing  
Resizing, normalization, augmentation  

3️⃣ Model Training  
YOLOv8 trained on annotated dataset  

4️⃣ Real-Time Detection  
Frames extracted from video feed  

5️⃣ Severity Classification  
Based on bounding box size and confidence  

6️⃣ Logging  
Detection details stored in CSV  

7️⃣ Notification  
Email alerts for high severity potholes  

---

## 📊 Results
- High accuracy pothole detection
- Real-time performance with minimal delay
- Successful logging and alert generation
- Reliable severity classification

---
## 🖥️ Installation

### 1️⃣ Clone Repository
```bash
git clone https://github.com/yourusername/pothole-detection.git
cd pothole-detection


