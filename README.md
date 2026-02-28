# 🤖 Project IRIS
### *Intelligent Robotic Intelligence System*

> *"IRIS online. All systems operational, Boss."*

![Python](https://img.shields.io/badge/Python-3.14-blue?style=for-the-badge&logo=python)
![Ollama](https://img.shields.io/badge/Ollama-Mistral_7B-orange?style=for-the-badge)
![YOLO](https://img.shields.io/badge/YOLO-v8-purple?style=for-the-badge)
![ESP32](https://img.shields.io/badge/ESP32-CAM-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-red?style=for-the-badge)

---

## 👁️ What is IRIS?

**Project IRIS** is a fully offline, locally hosted AI vision system built around **FRIDAY** — a personal AI assistant powered by Mistral 7B via Ollama. IRIS combines natural language intelligence with real-time computer vision (YOLOv8) and a robotic pan-tilt camera system (ESP32-CAM + Servos) to create an autonomous, room-aware AI that can **see**, **think**, and **respond**.

No cloud. No subscriptions. Just raw local AI power. 🔥

---

## ✨ Features

- 🧠 **FRIDAY AI** — Local LLM assistant powered by Mistral 7B via Ollama
- 💬 **Personality System** — Custom humor, tone and engineering-focused responses
- 🧩 **Long Term Memory** — Remembers past conversations across sessions
- 👁️ **YOLOv8 Vision** — Real-time object and person detection
- 📷 **ESP32-CAM Integration** — WiFi-streamed camera feed
- 🎯 **Pan-Tilt Servo Tracking** — Camera physically tracks detected targets
- ⚡ **GPU Accelerated** — Runs on NVIDIA RTX 3050 (CUDA)
- 🔒 **100% Offline** — Your data never leaves your machine

---

## 🛠️ Hardware Requirements

| Component | Details |
|-----------|---------|
| GPU | NVIDIA RTX 3050 6GB (or better) |
| RAM | 16GB recommended |
| ESP32-CAM | OV2640 camera module |
| Servos | 2x SG90 or MG996R (pan + tilt) |
| Mount | Pan-tilt bracket for ESP32-CAM |
| Network | Local WiFi for ESP32 streaming |

---

## 💻 Software Requirements

```bash
pip install ultralytics opencv-python requests pyserial
```

- [Ollama](https://ollama.ai) — for running Mistral locally
- [Mistral 7B](https://ollama.ai/library/mistral) — the brain of FRIDAY
- Python 3.10+
- Arduino IDE — for ESP32 firmware

---

## 🚀 Installation

**1. Clone the repo:**
```bash
git clone https://github.com/a-d-it-ya/Project-IRIS.git
cd Project-IRIS
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Install and run Ollama:**
```bash
ollama pull mistral
```

**4. Flash ESP32 firmware:**
- Open `esp32/esp32_firmware.ino` in Arduino IDE
- Add your WiFi credentials in `config.py`
- Flash to your ESP32-CAM

**5. Run IRIS:**
```bash
python main.py
```

---

## 📁 Project Structure

```
Project-IRIS/
├── main.py                  # Entry point
├── requirements.txt
├── .gitignore
├── friday/
│   ├── friday.py            # Core FRIDAY assistant
│   ├── friday_prompt.txt    # System personality prompt
│   ├── friday_personality.json
│   └── memory_manager.py   # Long term memory system
├── vision/
│   ├── yolo_detector.py    # YOLOv8 object detection
│   └── esp32_stream.py     # ESP32-CAM stream handler
├── servo/
│   └── servo_controller.py # Pan-tilt servo control
└── esp32/
    └── esp32_firmware.ino  # ESP32 Arduino firmware
```

---

## 🗺️ Roadmap

- [x] FRIDAY AI with Mistral 7B
- [x] Long term memory system
- [x] Custom personality and humor
- [ ] YOLOv8 real-time detection
- [ ] ESP32-CAM WiFi stream integration
- [ ] Pan-tilt servo tracking
- [ ] Voice I/O (Whisper + edge-tts)
- [ ] Web dashboard for IRIS
- [ ] Gesture control
- [ ] Intruder alert system

---

## ⚙️ How It Works

```
ESP32-CAM (WiFi Stream)
        ↓
YOLOv8 Object Detection
        ↓
FRIDAY (Mistral 7B) Interprets Scene
        ↓
Commands sent to ESP32
        ↓
Servos track the target
```

---

## 🧠 Meet FRIDAY

FRIDAY is the AI core of IRIS — an offline assistant with:
- Engineering and AI focused knowledge
- Persistent memory across conversations
- A sharp sense of humor 😄
- Runs entirely on your local GPU

---

## 📜 License

MIT License — free to use, modify and build upon.

---

## 🌟 Show Some Love

If you find this project cool, drop a ⭐ on GitHub — it helps a lot!

---

*Built with 🔥 by [a-d-it-ya](https://github.com/a-d-it-ya)*
