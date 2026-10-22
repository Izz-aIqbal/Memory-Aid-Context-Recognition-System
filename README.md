# Memory Aid with Context Recognition

An intelligent AI-powered system that helps users remember tasks, locate objects, and manage daily routines through object detection, activity recognition, and context-aware reminders.

## 🎯 Features

- **Real-time Object Detection**: Uses YOLOv8 to detect and recognize everyday objects
- **Activity Recognition**: Infers user activities (sitting, standing, working, reading, etc.)
- **Context-Aware Reminders**: Generates intelligent reminders based on detected objects and activities
- **Task Management**: Organize and track daily tasks
- **Voice Notifications**: Text-to-speech alerts for reminders
- **Web Dashboard**: Interactive Streamlit interface for monitoring and management
- **SQLite Database**: Stores detection logs, activities, reminders, and tasks
- **Real-time Visualization**: Live video feed with annotations

## 📋 Project Structure

```
memory_aid/
├── app.py                 # Main application entry point
├── config.py              # Configuration and settings
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── database/
│   ├── __init__.py
│   └── db_manager.py     # Database management
├── modules/
│   ├── __init__.py
│   ├── object_detector.py    # YOLOv8 object detection
│   ├── activity_recognizer.py # Activity inference
│   └── reminder_engine.py     # Reminder generation and sending
└── ui/
    ├── __init__.py
    └── dashboard.py      # Streamlit web interface
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam or video file
- Windows, macOS, or Linux

### Installation

1. **Clone/Navigate to project**:
```bash
cd "Context Recognition/memory_aid"
```

2. **Create and activate virtual environment** (already done):
```bash
# On Windows
venv\Scripts\Activate.ps1

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

### Usage

#### Run with Webcam (Real-time Detection)

```bash
python app.py
```

Use mock models for testing (no YOLOv8 training needed):
```bash
python app.py --mock
```

#### Run with Video File

```bash
python app.py --video path/to/video.mp4
```

#### Run in Headless Mode (No Display)

```bash
python app.py --headless --duration 30
```

#### Launch Web Dashboard

```bash
streamlit run ui/dashboard.py
```

Then open your browser to `http://localhost:8501`

## 🎮 Command Line Options

| Option | Description |
|--------|-------------|
| `--mock` | Use mock models instead of YOLOv8 (for testing) |
| `--video <path>` | Use video file instead of webcam |
| `--headless` | Run without GUI display |
| `--duration <minutes>` | Run for specified duration |
| `--no-voice` | Disable voice reminders |

## 📊 Dashboard Features

### Dashboard Tab
- Real-time metrics (objects detected, active tasks, reminders)
- Recent detections overview
- Recent activities summary

### Tasks Tab
- Create new tasks
- Mark tasks as complete
- View pending tasks

### Reminders Tab
- View pending reminders
- Create custom reminders
- Mark reminders as read

### Detection Logs Tab
- View detailed detection history
- Filter by time range
- Object detection statistics

### Statistics Tab
- Usage statistics over time
- Top detected objects chart
- Activity frequency analysis

### Settings Tab
- Configure notifications
- Set reminder cooldown
- Database maintenance options

## 🗄️ Database Schema

### Tables

**object_detections**: Logs of detected objects
- object_name, confidence, location, timestamp, frame_id

**activity_log**: Logs of recognized activities
- activity_name, confidence, timestamp, duration

**reminders**: Generated reminders
- reminder_type, object_name, activity_name, message, created_at, sent_at, is_sent, is_acknowledged

**user_tasks**: User-created tasks
- task_name, description, due_time, is_completed, created_at, completed_at

**system_logs**: System events and errors
- log_level, message, timestamp

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Object Detection Settings
CONFIDENCE_THRESHOLD = 0.5
YOLO_MODEL = "yolov8n.pt"

# Activity Recognition
MOTION_THRESHOLD = 10
FRAME_BUFFER_SIZE = 30

# Reminders
REMINDER_COOLDOWN = 300  # 5 minutes
VOICE_ENABLED = True

# Database
DB_PATH = "memory_aid/database/memory_aid.db"
```

## 🎯 How It Works

### 1. **Object Detection**
- Captures video frames from webcam
- Uses YOLOv8 nano model for fast inference
- Detects everyday objects (keys, phone, wallet, etc.)
- Draws bounding boxes and labels

### 2. **Activity Recognition**
- Analyzes motion between frames
- Estimates user posture/activity
- Combines multiple signals for activity inference
- Maintains activity history

### 3. **Context-Aware Reminders**
- Matches detected objects with user habits
- Generates intelligent reminder messages
- Enforces cooldown to avoid spam (5 min default)
- Sends via text and optional voice

### 4. **Data Storage**
- SQLite database for lightweight storage
- Automatic data cleanup after 30 days
- Full query support for analytics

## 📈 Performance

- **Object Detection**: ~30-60 FPS on modern hardware (YOLOv8 nano)
- **Activity Recognition**: Real-time inference
- **Memory Usage**: ~200-500 MB
- **Database**: Handles thousands of records efficiently

## 🔧 Troubleshooting

### Webcam not detected
```bash
python app.py --mock  # Use mock data for testing
```

### YOLOv8 model not loading
- First run will download the model (~35MB)
- Ensure stable internet connection
- Model cached in `~/.local/share/ultralytics/`

### Voice not working (pyttsx3)
- On Linux: `sudo apt-get install espeak`
- On macOS: Should work out of the box
- On Windows: Native TTS available

### Database issues
- Delete `memory_aid/database/memory_aid.db` to reset
- System recreates schema automatically

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `opencv-python` | Video processing |
| `ultralytics` | YOLOv8 object detection |
| `pyttsx3` | Text-to-speech |
| `streamlit` | Web dashboard |
| `pandas` | Data manipulation |
| `numpy` | Numerical computing |
| `pillow` | Image processing |

## 📝 Example Reminders

The system generates intelligent reminders:

- 📍 "You left your keys on the left top"
- 📍 "Your phone is on the center middle"
- 🎯 "You've been sitting for too long. Time to move!"
- 🎯 "You've been reading for a while. Take a break!"
- 📋 "Reminder: Complete project proposal"

## 🚀 Future Enhancements

- [ ] Multi-camera support
- [ ] Cloud sync for reminders
- [ ] Custom object training
- [ ] Advanced pose estimation
- [ ] Integration with calendar/email
- [ ] Mobile app
- [ ] Gesture recognition
- [ ] Emotion detection

## 📄 License

This project is provided as-is for educational and personal use.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the configuration options
3. Check database integrity with dashboard

---

**Made with ❤️ for better memory and productivity**
