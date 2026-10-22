# 📚 Memory Aid Project - File Index and Documentation

## 📂 Complete Project Structure

### Root Project Directory
```
Context Recognition/
├── memory_aid/              # Main project folder
├── venv/                    # Virtual environment (already activated)
└── PROJECT_SUMMARY.md       # This project's complete overview
```

### Project Files (18 Total)

#### 🎬 **Main Application Files**
1. **`memory_aid/app.py`** (600+ lines)
   - Main application entry point
   - Integrates all modules
   - Handles video input (webcam/file)
   - Real-time frame processing
   - Logging and metrics

2. **`memory_aid/config.py`** (60+ lines)
   - Centralized configuration
   - Model parameters
   - Reminder templates
   - Activity labels
   - Settings for all modules

3. **`memory_aid/__init__.py`**
   - Package initialization
   - Exports main classes

#### 🗄️ **Database Module**
4. **`memory_aid/database/db_manager.py`** (300+ lines)
   - SQLite database manager
   - 5 tables: objects, activities, reminders, tasks, logs
   - CRUD operations
   - Statistics queries
   - Data cleanup

5. **`memory_aid/database/__init__.py`**
   - Database package init

#### 🧠 **AI/ML Modules**
6. **`memory_aid/modules/object_detector.py`** (200+ lines)
   - YOLOv8 integration
   - Real-time object detection
   - Bounding box drawing
   - Location inference
   - Mock detector for testing

7. **`memory_aid/modules/activity_recognizer.py`** (250+ lines)
   - Motion detection
   - Posture estimation
   - Activity classification
   - Activity history tracking
   - Mock recognizer for development

8. **`memory_aid/modules/reminder_engine.py`** (200+ lines)
   - Reminder generation
   - Context-aware messages
   - Text-to-speech (pyttsx3)
   - Cooldown management
   - Async voice synthesis

9. **`memory_aid/modules/__init__.py`**
   - Modules package init

#### 🎨 **Web Interface**
10. **`memory_aid/ui/dashboard.py`** (350+ lines)
    - 6-page Streamlit dashboard
    - Task management interface
    - Reminder viewer
    - Detection logs
    - Statistics and analytics
    - System settings

11. **`memory_aid/ui/__init__.py`**
    - UI package init

#### 📋 **Documentation**
12. **`memory_aid/README.md`** (500+ lines)
    - Complete project documentation
    - Usage instructions
    - Feature descriptions
    - Troubleshooting guide
    - API documentation
    - Future enhancements

13. **`memory_aid/QUICKSTART.md`** (100+ lines)
    - Quick start guide
    - Command examples
    - Basic troubleshooting
    - Dashboard features

14. **`memory_aid/PROJECT_SUMMARY.md`** (400+ lines)
    - Project completion status
    - Technology stack
    - Architecture overview
    - Use cases

#### 🔧 **Configuration & Setup**
15. **`memory_aid/requirements.txt`**
    - Python dependencies
    - Package versions

16. **`memory_aid/setup_test.py`** (150+ lines)
    - Installation verification
    - Package checks
    - Database testing
    - Module validation

17. **`memory_aid/run.bat`**
    - Windows launcher script
    - Interactive menu
    - Easy mode selection

18. **`FILE_INDEX.md`** (This file)
    - Complete file documentation
    - File descriptions
    - Usage guide

---

## 🗂️ Detailed File Descriptions

### Core Application (`app.py`)
**Purpose**: Main system orchestrator
**Key Classes**:
- `MemoryAidSystem`: Main application class
  - `__init__()`: Initialize all components
  - `process_frame()`: Process single frame
  - `run()`: Main loop with display
  - `run_headless()`: Background operation
  - `cleanup()`: Resource cleanup

**Key Methods**: 15+
**Lines of Code**: 600+
**Dependencies**: All modules

### Database Manager (`db_manager.py`)
**Purpose**: Persistent data storage
**Key Classes**:
- `DatabaseManager`: SQLite manager
  - `init_database()`: Create schema
  - `log_object_detection()`: Record objects
  - `log_activity()`: Record activities
  - `add_reminder()`: Create reminders
  - `add_task()`: Create tasks
  - `get_statistics()`: Analyze data
  - `cleanup_old_data()`: Maintenance

**Tables** (5):
1. `object_detections` - Detected objects
2. `activity_log` - Detected activities
3. `reminders` - Generated reminders
4. `user_tasks` - User's tasks
5. `system_logs` - System events

### Object Detector (`object_detector.py`)
**Purpose**: Real-time object recognition
**Key Classes**:
- `ObjectDetector`: YOLOv8-based detector
  - `detect()`: Detect objects in frame
  - `get_object_location()`: Determine position
  - `get_top_objects()`: Get best detections

- `MockObjectDetector`: For testing

**Features**:
- 80+ object types
- Confidence scoring
- Location inference
- Bounding box visualization

### Activity Recognizer (`activity_recognizer.py`)
**Purpose**: User activity inference
**Key Classes**:
- `ActivityRecognizer`: Motion and posture based
  - `detect_motion()`: Frame-to-frame motion
  - `estimate_pose()`: Posture analysis
  - `recognize_activity()`: Activity classification
  - `get_activity_duration()`: Time tracking

- `MockActivityRecognizer`: For testing

**Supported Activities**: 8 types
- sitting, standing, walking, running
- reading, working, eating, sleeping

### Reminder Engine (`reminder_engine.py`)
**Purpose**: Generate and send reminders
**Key Classes**:
- `ReminderEngine`: Smart reminder system
  - `generate_object_reminder()`: Object-based
  - `generate_activity_reminder()`: Activity-based
  - `generate_task_reminder()`: Task-based
  - `send_reminder()`: Delivery

- `MockReminderEngine`: For testing

**Features**:
- Context-aware messages
- Voice notifications
- Cooldown system
- Database persistence

### Streamlit Dashboard (`dashboard.py`)
**Purpose**: Web-based user interface
**Pages** (6):
1. **Dashboard**: Metrics overview
2. **Tasks**: Task management CRUD
3. **Reminders**: Reminder viewer
4. **Detection Logs**: Browse history
5. **Statistics**: Analytics & charts
6. **Settings**: System configuration

**Features**:
- Real-time updates
- Interactive tables
- Charts and graphs
- Database integration

### Configuration (`config.py`)
**Purpose**: Centralized settings
**Main Constants**:
- `CONFIDENCE_THRESHOLD`: 0.5
- `MOTION_THRESHOLD`: 10
- `REMINDER_COOLDOWN`: 300s
- `DB_PATH`: SQLite location
- `YOLO_MODEL`: "yolov8n.pt"

### Setup Test (`setup_test.py`)
**Purpose**: Verify installation
**Tests**:
1. Package availability
2. Database functionality
3. Module imports
4. System readiness

---

## 🚀 How to Use Each File

### Running the Application
```bash
# Basic usage
python app.py                          # Webcam
python app.py --mock                   # Test mode
python app.py --video file.mp4         # Video file
python app.py --headless --duration 30 # Background
```

### Launching Dashboard
```bash
streamlit run ui/dashboard.py
```

### Verifying Installation
```bash
python setup_test.py
```

### Windows Quick Launch
```bash
run.bat
```

---

## 📊 Code Statistics

| Component | Lines | Classes | Methods |
|-----------|-------|---------|---------|
| app.py | 600+ | 1 | 15+ |
| db_manager.py | 300+ | 1 | 20+ |
| object_detector.py | 200+ | 2 | 12+ |
| activity_recognizer.py | 250+ | 2 | 15+ |
| reminder_engine.py | 200+ | 2 | 15+ |
| dashboard.py | 350+ | 0 | 6 pages |
| **Total** | **1,900+** | **8** | **77+** |

---

## 🔗 Dependencies by File

### app.py
- cv2 (OpenCV)
- ultralytics (YOLOv8)
- All internal modules

### database/db_manager.py
- sqlite3
- datetime

### modules/object_detector.py
- cv2
- numpy
- ultralytics

### modules/activity_recognizer.py
- cv2
- numpy
- collections
- datetime

### modules/reminder_engine.py
- pyttsx3
- threading
- queue
- datetime
- logging

### ui/dashboard.py
- streamlit
- pandas
- numpy
- All other modules

---

## 🎯 Quick Navigation

**Want to...**
- ✅ Run the app? → `python app.py --mock`
- ✅ See dashboard? → `streamlit run ui/dashboard.py`
- ✅ Check setup? → `python setup_test.py`
- ✅ Configure settings? → Edit `config.py`
- ✅ Understand it? → Read `README.md`
- ✅ Quick start? → Read `QUICKSTART.md`
- ✅ Modify object detection? → Edit `modules/object_detector.py`
- ✅ Change activities? → Edit `modules/activity_recognizer.py`
- ✅ Customize reminders? → Edit `modules/reminder_engine.py`
- ✅ Add dashboard page? → Edit `ui/dashboard.py`

---

## 📚 Documentation Files

1. **README.md** - Full technical documentation
2. **QUICKSTART.md** - Get started in 5 minutes
3. **PROJECT_SUMMARY.md** - Project overview
4. **FILE_INDEX.md** - This file

---

## ✅ Installation Checklist

- [x] Virtual environment created
- [x] Dependencies installed
- [x] Database module created
- [x] ML modules created
- [x] Web dashboard created
- [x] Main app integrated
- [x] Documentation written
- [x] Tests passing
- [x] Ready to use

---

## 🎉 You're All Set!

The Memory Aid system is complete and functional. Start with:

```bash
python app.py --mock
```

Then explore the dashboard and documentation!

---

**Last Updated**: December 3, 2025
**Status**: ✅ Complete and Ready
**Version**: 1.0.0
