# Data Matrix Quality Scanner

## Project Overview

**Project Name:** DataMatrix Quality Scanner  
**Project Type:** Industrial Quality Control Application  
**Core Functionality:** Real-time Data Matrix code scanning and quality evaluation using webcam, designed for conveyor belt inspection lines with continuous code changing.  
**Target Users:** Quality control engineers, production line operators, manufacturing supervisors

## ISO Standards Compliance

### Primary Standards
- **ISO/IEC 15415:2011** - Information technology - Automatic identification and data capture techniques - Bar code print quality test specification - Two-dimensional symbols
- **ISO/IEC 15416:2016** - Information technology - Automatic identification and data capture techniques - Bar code print quality test specification - Linear bar code symbols
- **AS9132** - Data Matrix for product labeling (aerospace industry reference)

### Quality Parameters Evaluated
1. **Symbol Contrast (SC)** - Minimum 0.80 (80%)
2. **Module Edge Determinacy (ED)** - Minimum 0.50 (50%)
3. **Overall Decode (DEC)** - Must be successful
4. **Axial Non-Uniformity (AN)** - Maximum 0.08 (8%)
5. **Grid Non-Uniformity (GN)** - Maximum 0.08 (8%)
6. **Unused Error Correction (UEC)** - Minimum 0.50 (50%)
7. **Fixed Pattern Damage (FPD)** - Minimum 0.60 (60%)

### Quality Grades
- **Grade A:** 4.0 - Excellent (≥ 3.5)
- **Grade B:** 3.0 - Good (≥ 2.5)
- **Grade C:** 2.0 - Acceptable (≥ 1.5)
- **Grade D:** 1.0 - Poor (≥ 0.5)
- **Grade F:** 0.0 - Failure (< 0.5)

## UI/UX Specification

### Window Structure

**Main Window (1200x800 minimum)**
- Single window application with integrated panels
- Resizable with minimum constraints
- Dark industrial theme for reduced eye strain

### Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ [Header: Logo + Title + Connection Status + Settings]           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────┐  ┌──────────────────────────────┐ │
│  │                         │  │ QUALITY METRICS              │ │
│  │   CAMERA PREVIEW        │  │ ─────────────────────────────│ │
│  │   (Live Feed)           │  │ Grade: A (4.2)               │ │
│  │                         │  │ Overall Score: 4.2/5.0       │ │
│  │   [Detection Box]       │  │                              │ │
│  │                         │  │ SC:  0.95  [████████░] ✓     │ │
│  │                         │  │ ED:  0.88  [███████░░] ✓     │ │
│  │                         │  │ AN:  0.03  [█████████] ✓     │ │
│  │                         │  │ GN:  0.05  [████████░] ✓     │ │
│  │                         │  │ UEC: 0.72  [██████░░] ✓     │ │
│  │                         │  │ DEC: PASS  [██████████] ✓   │ │
│  │                         │  │ FPD: 0.85  [███████░░] ✓     │ │
│  └─────────────────────────┘  └──────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────────┤
│  │ SCAN LOG                                                    ││
│  │ ─────────────────────────────────────────────────────────── ││
│  │ [Timestamp] [Code Data] [Grade] [Status]                    ││
│  │ 2026-05-25 13:45:01  SN123456789  A   ✓ PASS                ││
│  │ 2026-05-25 13:45:02  SN123456790  B   ✓ PASS                ││
│  └──────────────────────────────────────────────────────────────┤
├─────────────────────────────────────────────────────────────────┤
│ [Footer: Camera Controls | Export | Statistics | Language]     │
└─────────────────────────────────────────────────────────────────┘
```

### Visual Design

**Color Palette**
- Primary Background: `#1a1a2e` (Deep Navy)
- Secondary Background: `#16213e` (Dark Blue)
- Panel Background: `#0f3460` (Medium Blue)
- Primary Accent: `#00d9ff` (Cyan - Industrial)
- Success: `#00ff88` (Bright Green)
- Warning: `#ffaa00` (Amber)
- Error: `#ff4757` (Red)
- Text Primary: `#ffffff`
- Text Secondary: `#a0a0a0`
- Grade A Color: `#00ff88`
- Grade B Color: `#00d9ff`
- Grade C Color: `#ffaa00`
- Grade D Color: `#ff6b35`
- Grade F Color: `#ff4757`

**Typography**
- Font Family: "Segoe UI", system-ui, sans-serif
- Header: 24px Bold
- Subheader: 18px SemiBold
- Body: 14px Regular
- Metrics: 16px Mono (Consolas, monospace)
- Log entries: 12px Regular

**Spacing System**
- Base unit: 8px
- Panel padding: 16px
- Component margins: 8px
- Section gaps: 16px

**Visual Effects**
- Panel shadows: `0 4px 20px rgba(0, 0, 0, 0.3)`
- Rounded corners: 8px for panels, 4px for buttons
- Glow effect on detection: `0 0 20px rgba(0, 217, 255, 0.5)`
- Smooth transitions: 200ms ease

### Components

**Camera Preview Panel**
- Live video feed display (640x480 default, scalable)
- Green overlay rectangle when Data Matrix detected
- Pulsing animation on successful decode
- Cross-hair alignment guides

**Quality Metrics Panel**
- Individual metric bars with color coding
- Threshold indicators (pass/fail lines)
- Real-time value updates
- Large grade display with color

**Scan Log Table**
- Scrollable log with 1000 entry buffer
- Auto-scroll to newest entries
- Color-coded status indicators
- Export to CSV functionality

**Control Buttons**
- Start/Stop scanning toggle
- Camera selection dropdown
- Settings gear icon
- Export data button
- Statistics view toggle

### Interactive Behaviors

**Camera Preview**
- Hover: Show coordinate tooltip
- Click: Manual capture and analyze
- Double-click: Fullscreen mode
- Right-click: Camera settings menu

**Quality Metrics**
- Hover on metric: Show detailed explanation tooltip
- Click on metric: Expand to show measurement details

**Scan Log**
- Hover on entry: Highlight in preview
- Click on entry: Show detailed analysis popup
- Right-click: Copy code, export selection

## Functionality Specification

### Core Features

**1. Real-Time Data Matrix Detection**
- Continuous camera frame processing at 30 FPS
- Multi-threaded capture and processing
- Automatic detection of Data Matrix in frame
- Support for varying lighting conditions
- Auto-exposure and white balance adjustment

**2. Quality Evaluation (ISO/IEC 15415)**
- Symbol contrast measurement
- Module edge determinacy calculation
- Axial non-uniformity assessment
- Grid non-uniformity assessment
- Unused error correction analysis
- Fixed pattern damage detection
- Overall grade calculation (weighted average)

**3. Conveyor Mode Operation**
- Auto-trigger on code detection
- Configurable delay between scans
- Duplicate code filtering
- Configurable pass/fail thresholds
- Continuous logging without interruption
- Support for high-speed lines (up to 100 codes/minute)

**4. Multi-Camera Support**
- Enumerate available cameras on startup
- Camera selection dropdown
- Resolution configuration per camera
- Persistent camera preference

**5. Statistics and Reporting**
- Pass/Fail rate calculation
- Grade distribution histogram
- Hourly/daily production statistics
- Export to CSV format
- Print quality trend charts

**6. Alarm System**
- Visual alarm (red border flash)
- Audio beep on failure (configurable)
- Configurable alarm conditions

### User Interactions and Flows

**Startup Flow**
1. Application launches with splash screen
2. Auto-detect available cameras
3. Connect to preferred camera
4. Load previous settings from config
5. Begin live preview
6. Start scanning if auto-start enabled

**Scanning Flow**
1. Camera captures frame
2. Image preprocessing (contrast enhancement)
3. Data Matrix detection algorithm
4. If detected: Decode and quality analysis
5. Calculate ISO grade
6. Update UI with results
7. Log entry added to history
8. Trigger alarm if configured
9. Continue scanning loop

**Export Flow**
1. User clicks Export button
2. Date range selection dialog
3. Format selection (CSV/JSON)
4. File save dialog
5. Generate and save report

### Data Handling

**Local Storage**
- Configuration: JSON file in AppData
- Scan log: SQLite database (last 30 days)
- Statistics cache: JSON file

**Data Structures**
```python
@dataclass
class ScanResult:
    timestamp: datetime
    code_data: str
    grade: str
    score: float
    metrics: QualityMetrics
    image_path: Optional[str]
    camera_id: str

@dataclass
class QualityMetrics:
    symbol_contrast: float
    edge_determinacy: float
    axial_uniformity: float
    grid_uniformity: float
    unused_error_correction: float
    fixed_pattern_damage: float
    decode_success: bool
```

### Edge Cases and Error Handling

1. **No camera detected**: Show error dialog, offer retry
2. **Camera disconnected**: Auto-reconnect with notification
3. **Poor lighting**: Warning indicator, suggest adjustment
4. **No Data Matrix in frame**: Continuous preview, no error
5. **Decode failure**: Log as Grade F, show error message
6. **Very low quality code**: Still attempt decode, flag for review
7. **Rapid code changes**: Debounce mechanism (configurable)
8. **Database full**: Archive old records, notify user

## Technical Architecture

### Technology Stack
- **Language:** Python 3.10+
- **GUI Framework:** Customtkinter (modern UI)
- **Computer Vision:** OpenCV 4.x
- **Barcode Decoding:** pyzbar with zbar library
- **Database:** SQLite3
- **Packaging:** PyInstaller
- **Version Control:** Git + GitHub

### Project Structure
```
datamatrix-scanner/
├── main.py                 # Application entry point
├── scanner/
│   ├── __init__.py
│   ├── camera.py           # Camera handling
│   ├── detector.py         # Data Matrix detection
│   ├── quality_analyzer.py # ISO quality analysis
│   ├── database.py         # SQLite operations
│   └── alarm.py            # Alarm system
├── ui/
│   ├── __init__.py
│   ├── main_window.py     # Main window layout
│   ├── camera_panel.py     # Camera preview
│   ├── metrics_panel.py    # Quality metrics display
│   ├── log_panel.py        # Scan log table
│   └── settings_dialog.py  # Settings UI
├── utils/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   └── logger.py           # Logging utilities
├── resources/
│   ├── icon.ico            # Application icon
│   └── sounds/             # Alarm sounds
├── requirements.txt
├── config.json.example
├── README.md
├── LICENSE
├── .gitignore
└── SPEC.md
```

## Acceptance Criteria

### Functional Criteria
- [ ] Application starts without errors
- [ ] All available cameras are enumerated
- [ ] Live preview displays at minimum 15 FPS
- [ ] Data Matrix codes are detected within 200ms
- [ ] Quality grades match ISO 15415 calculations
- [ ] Scan log displays all scanned codes
- [ ] Export generates valid CSV files
- [ ] Settings are persisted between sessions

### Visual Criteria
- [ ] Dark industrial theme applied consistently
- [ ] Quality metric bars display correctly
- [ ] Grade colors match specification
- [ ] Animations are smooth (no lag)
- [ ] Text is readable on all panels
- [ ] Responsive layout on resize

### Performance Criteria
- [ ] Memory usage under 500MB
- [ ] CPU usage under 50% on modern hardware
- [ ] Startup time under 3 seconds
- [ ] Scan-to-display latency under 500ms

### Industrial Criteria
- [ ] Works 8+ hours continuously
- [ ] Handles 100+ scans per minute
- [ ] No memory leaks over extended use
- [ ] Works with standard USB webcams
