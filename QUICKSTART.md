# 🧠 Memory Aid with Context Recognition - Quick Start Guide

## ✅ Installation Complete!

Your Memory Aid system is fully set up and ready to use. Here are the next steps:

## 🚀 Getting Started

### 1. **Test the System (Recommended First)**
```bash
python app.py --mock
```
- Uses mock AI models (no camera needed)
- Perfect for testing the interface
- Press 'Q' to quit

### 2. **Run with Webcam**
```bash
python app.py
```
- Real-time object and activity detection
- Requires working webcam
- Models will download on first run (~100MB)
- Press 'Q' to quit

### 3. **Launch Web Dashboard**
```bash
streamlit run ui/dashboard.py
```
- Opens interactive web interface at `http://localhost:8501`
- Manage tasks and view reminders
- Access statistics and logs
- Press `Ctrl+C` to stop

### 4. **Run with Video File**
```bash
python app.py --video path/to/your/video.mp4
```
- Process recorded video instead of webcam

## 📊 Dashboard Features

Once you launch the dashboard, you can:

- ✅ **Dashboard**: Overview of system metrics
- 📋 **Tasks**: Create and manage daily tasks
- 🔔 **Reminders**: View and create reminders
- 📸 **Detection Logs**: Browse detection history
- 📈 **Statistics**: View usage analytics
- ⚙️ **Settings**: Configure system behavior

## 🎮 Advanced Commands

```bash
# Run headless (no GUI, for servers)
python app.py --headless --duration 30

# Disable voice notifications
python app.py --no-voice

# Use mock models with webcam
python app.py --mock
```

## 📁 Project Structure

```
memory_aid/
├── app.py              # Main application
├── config.py           # Configuration settings
├── requirements.txt    # Dependencies
├── README.md          # Full documentation
├── setup_test.py      # Verification script
│
├── database/
│   └── db_manager.py  # SQLite database
│
├── modules/
│   ├── object_detector.py      # YOLOv8 detection
│   ├── activity_recognizer.py  # Activity inference
│   └── reminder_engine.py       # Reminder system
│
└── ui/
    └── dashboard.py    # Streamlit interface
```

## 🎯 What It Does

### Object Detection
- 📍 Recognizes everyday objects (keys, phone, wallet, glasses, etc.)
- 📌 Detects their location in the frame
- 🔔 Generates "You left your X on the Y" reminders

### Activity Recognition
- 🚶 Identifies activities: sitting, standing, working, reading, etc.
- ⏱️ Tracks activity duration
- 💡 Provides context-aware suggestions

### Smart Reminders
- 🔊 Text and voice notifications
- 🎯 Context-aware suggestions
- ⏱️ Configurable cooldown to prevent spam
- 💾 All reminders logged in database

### Web Dashboard
- 📊 Real-time statistics
- 📋 Task management
- 🗂️ Detection history
- ⚙️ System configuration

## 🗄️ Database

SQLite database automatically created at:
```
memory_aid/database/memory_aid.db
```

Stores:
- Object detections
- Activity logs
- Reminders
- User tasks
- System logs

## ❓ Troubleshooting

### Webcam not working
```bash
python app.py --mock
```
Try mock mode first to ensure rest of system works.

### Models downloading slowly
- First run downloads YOLOv8 (~100MB)
- Internet connection required
- Models cached locally after first use

### Database errors
- Delete `memory_aid/database/memory_aid.db`
- Database recreates on startup
- Check disk space if issues persist

### Voice not working
- Ensure system speakers are connected
- Check volume settings
- Use `--no-voice` flag if TTS unavailable

## 📞 Next Steps

1. **Explore Features**: Run `python app.py --mock` to get familiar
2. **Try Dashboard**: Open `streamlit run ui/dashboard.py`
3. **Configure**: Edit `config.py` for custom settings
4. **Read Full Docs**: Check `README.md` for detailed documentation

## 🎓 Example Usage

### Complete Workflow
```bash
# Terminal 1: Start main application
cd memory_aid
python app.py --mock

# Terminal 2 (in same directory): Launch dashboard
streamlit run ui/dashboard.py
```

Then:
1. Watch real-time detections in Terminal 1
2. Monitor dashboard in browser at `http://localhost:8501`
3. Create tasks in dashboard
4. Receive reminders

## 📚 Configuration Tips

Edit `config.py` to customize:

```python
# Make reminders less frequent
REMINDER_COOLDOWN = 600  # 10 minutes (default 5)

# Increase detection sensitivity
CONFIDENCE_THRESHOLD = 0.3  # Default 0.5

# Disable voice
VOICE_ENABLED = False
```

## 🎉 Ready to Use!

Your Memory Aid system is fully operational. Start with:
```bash
python app.py --mock
```

Then explore the dashboard and other features!

---

**Enjoy your new Memory Aid Assistant!** 🧠✨
