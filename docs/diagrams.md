# Sơ Đồ Hệ Thống Điều Khiển Đèn Giao Thông Thông Minh

Tài liệu này chứa các sơ đồ dưới dạng code có thể chuyển sang hình ảnh UML.
- **Mermaid**: Có thể render trực tiếp trên GitHub, GitLab, Notion, hoặc dùng [Mermaid Live Editor](https://mermaid.live)
- **PlantUML**: Dùng [PlantUML Online](https://www.plantuml.com/plantuml)

---

## 1. Sơ Đồ Kiến Trúc Tổng Quan (System Architecture)

### Mermaid

```mermaid
graph TB
    subgraph INPUT["📹 NGUỒN ĐẦU VÀO"]
        VIDEO[Video File<br/>MP4/AVI/MOV]
        WEBCAM[Webcam<br/>Real-time]
    end

    subgraph CORE["⚙️ HỆ THỐNG XỬ LÝ CHÍNH"]
        MAIN[TrafficControlSystem<br/>main.py]
        
        subgraph DETECTION["🔍 Module Phát Hiện"]
            DETECTOR[VehicleDetector<br/>vehicle_detector.py]
            YOLO[YOLOv8n Model<br/>yolov8n.pt]
        end
        
        subgraph COUNTING["📊 Module Đếm"]
            COUNTER[TrafficCounter<br/>traffic_counter.py]
            ZONES[Zone Polygons<br/>N/S/E/W]
        end
        
        subgraph CONTROL["🚦 Module Điều Khiển"]
            CONTROLLER[TrafficLightController<br/>traffic_light_controller.py]
            STATE[State Machine<br/>GREEN/YELLOW/RED]
        end
        
        subgraph UI["🖥️ Module Giao Diện"]
            DASHBOARD[UIDashboard<br/>ui_dashboard.py]
            ZONE_EDITOR[ZoneEditor<br/>zone_editor.py]
        end
        
        subgraph LOGGING["📝 Module Ghi Log"]
            LOGGER[Logger<br/>logger.py]
        end
        
        CONFIG[Config<br/>config.py]
    end

    subgraph OUTPUT["📤 ĐẦU RA"]
        DISPLAY[Hiển Thị<br/>OpenCV Window]
        VIDEO_OUT[Video Output<br/>output_video.mp4]
        CSV[Traffic Logs<br/>traffic_logs.csv]
        SUMMARY[Summary<br/>traffic_summary.txt]
    end

    VIDEO --> MAIN
    WEBCAM --> MAIN
    MAIN --> DETECTOR
    DETECTOR --> YOLO
    YOLO --> DETECTOR
    DETECTOR --> COUNTER
    COUNTER --> ZONES
    ZONES --> COUNTER
    COUNTER --> CONTROLLER
    CONTROLLER --> STATE
    STATE --> CONTROLLER
    CONFIG --> MAIN
    CONFIG --> DETECTOR
    CONFIG --> CONTROLLER
    CONFIG --> DASHBOARD
    MAIN --> DASHBOARD
    MAIN --> ZONE_EDITOR
    MAIN --> LOGGER
    DASHBOARD --> DISPLAY
    MAIN --> VIDEO_OUT
    LOGGER --> CSV
    LOGGER --> SUMMARY

    style INPUT fill:#e3f2fd
    style CORE fill:#fff3e0
    style OUTPUT fill:#e8f5e9
    style DETECTION fill:#fce4ec
    style COUNTING fill:#f3e5f5
    style CONTROL fill:#fff8e1
    style UI fill:#e0f7fa
    style LOGGING fill:#f1f8e9
```

### PlantUML

```plantuml
@startuml System_Architecture
!theme plain
skinparam componentStyle rectangle

package "Nguồn Đầu Vào" {
    [Video File] as VIDEO
    [Webcam] as WEBCAM
}

package "Hệ Thống Xử Lý Chính" {
    [TrafficControlSystem\nmain.py] as MAIN
    
    package "Module Phát Hiện" {
        [VehicleDetector\nvehicle_detector.py] as DETECTOR
        [YOLOv8n Model] as YOLO
    }
    
    package "Module Đếm" {
        [TrafficCounter\ntraffic_counter.py] as COUNTER
        [Zone Polygons] as ZONES
    }
    
    package "Module Điều Khiển" {
        [TrafficLightController\ntraffic_light_controller.py] as CONTROLLER
        [State Machine] as STATE
    }
    
    package "Module Giao Diện" {
        [UIDashboard\nui_dashboard.py] as DASHBOARD
        [ZoneEditor\nzone_editor.py] as ZONE_EDITOR
    }
    
    [Logger\nlogger.py] as LOGGER
    [Config\nconfig.py] as CONFIG
}

package "Đầu Ra" {
    [Display Window] as DISPLAY
    [Video Output] as VIDEO_OUT
    [CSV Logs] as CSV
    [Summary] as SUMMARY
}

VIDEO --> MAIN
WEBCAM --> MAIN
MAIN --> DETECTOR
DETECTOR --> YOLO
DETECTOR --> COUNTER
COUNTER --> ZONES
COUNTER --> CONTROLLER
CONTROLLER --> STATE
CONFIG --> MAIN
CONFIG --> DETECTOR
CONFIG --> CONTROLLER
MAIN --> DASHBOARD
MAIN --> ZONE_EDITOR
MAIN --> LOGGER
DASHBOARD --> DISPLAY
MAIN --> VIDEO_OUT
LOGGER --> CSV
LOGGER --> SUMMARY

@enduml
```

---

## 2. Sơ Đồ Lớp (Class Diagram)

### Mermaid

```mermaid
classDiagram
    class TrafficControlSystem {
        -video_path: str
        -model_path: str
        -output_path: str
        -detector: VehicleDetector
        -counter: TrafficCounter
        -controller: TrafficLightController
        -dashboard: UIDashboard
        -logger: Logger
        -cap: VideoCapture
        -writer: VideoWriter
        -is_paused: bool
        -show_dashboard: bool
        -edit_mode: bool
        +__init__(video_path, model_path, output_path, show)
        +run(): void
        +process_frame(frame): tuple
        +cleanup(): void
        -_handle_keyboard(key): bool
        -_save_screenshot(frame): void
    }

    class VehicleDetector {
        -model: YOLO
        -confidence_threshold: float
        -vehicle_classes: list
        -total_detections: int
        -frame_count: int
        +__init__(model_path, confidence_threshold)
        +detect(frame): List~dict~
        +draw_detections(frame, detections): ndarray
        +get_statistics(): dict
        -_filter_vehicles(results): List~dict~
    }

    class TrafficCounter {
        -zones: dict
        -zone_colors: dict
        -vehicle_counts: dict
        -total_counts: dict
        +__init__(frame_width, frame_height)
        +count_vehicles(detections): dict
        +draw_zones(frame): ndarray
        +point_in_zone(point, polygon): bool
        +get_statistics(): dict
        +update_zone(direction, points): void
        +get_zones(): dict
    }

    class TrafficLightController {
        -min_green_time: float
        -max_green_time: float
        -yellow_time: float
        -threshold: int
        -current_green: str
        -green_start_time: float
        -is_yellow: bool
        -switch_count: int
        -directions: list
        +__init__(min_green, max_green, yellow, threshold)
        +get_light_state(vehicle_counts): dict
        +draw_lights(frame, states, shape): ndarray
        +get_statistics(counts): dict
        -_should_switch(elapsed, current, others): bool
        -_get_next_direction(counts): str
    }

    class UIDashboard {
        -width: int
        -colors: dict
        -font: int
        -font_scale: float
        +__init__(width)
        +draw_dashboard(frame, stats): ndarray
        -_draw_header(panel, y): int
        -_draw_vehicle_counts(panel, counts, y): int
        -_draw_light_status(panel, states, y): int
        -_draw_statistics(panel, stats, y): int
    }

    class Logger {
        -csv_path: str
        -summary_path: str
        -logs: list
        -start_time: float
        +__init__(output_dir)
        +log(timestamp, counts, states, fps): void
        +export_summary(stats): void
        +get_log_count(): int
        -_write_csv_header(): void
    }

    class ZoneEditor {
        -counter: TrafficCounter
        -selected_zone: str
        -selected_point: int
        -drag_start: tuple
        -is_dragging: bool
        +__init__(counter)
        +handle_mouse(event, x, y, flags, param): void
        +draw_edit_overlay(frame): ndarray
        +save_zones(filepath): void
        +load_zones(filepath): void
        -_find_nearest_point(x, y): tuple
    }

    TrafficControlSystem --> VehicleDetector : uses
    TrafficControlSystem --> TrafficCounter : uses
    TrafficControlSystem --> TrafficLightController : uses
    TrafficControlSystem --> UIDashboard : uses
    TrafficControlSystem --> Logger : uses
    TrafficControlSystem --> ZoneEditor : uses
    TrafficCounter <-- ZoneEditor : modifies
```

### PlantUML

```plantuml
@startuml Class_Diagram
!theme plain
skinparam classAttributeIconSize 0

class TrafficControlSystem {
    - video_path: str
    - model_path: str
    - output_path: str
    - detector: VehicleDetector
    - counter: TrafficCounter
    - controller: TrafficLightController
    - dashboard: UIDashboard
    - logger: Logger
    - cap: VideoCapture
    - writer: VideoWriter
    - is_paused: bool
    - show_dashboard: bool
    - edit_mode: bool
    --
    + __init__(video_path, model_path, output_path, show)
    + run(): void
    + process_frame(frame): tuple
    + cleanup(): void
    - _handle_keyboard(key): bool
    - _save_screenshot(frame): void
}

class VehicleDetector {
    - model: YOLO
    - confidence_threshold: float
    - vehicle_classes: list
    - total_detections: int
    - frame_count: int
    --
    + __init__(model_path, confidence_threshold)
    + detect(frame): List[dict]
    + draw_detections(frame, detections): ndarray
    + get_statistics(): dict
    - _filter_vehicles(results): List[dict]
}

class TrafficCounter {
    - zones: dict
    - zone_colors: dict
    - vehicle_counts: dict
    - total_counts: dict
    --
    + __init__(frame_width, frame_height)
    + count_vehicles(detections): dict
    + draw_zones(frame): ndarray
    + point_in_zone(point, polygon): bool
    + get_statistics(): dict
    + update_zone(direction, points): void
    + get_zones(): dict
}

class TrafficLightController {
    - min_green_time: float
    - max_green_time: float
    - yellow_time: float
    - threshold: int
    - current_green: str
    - green_start_time: float
    - is_yellow: bool
    - switch_count: int
    - directions: list
    --
    + __init__(min_green, max_green, yellow, threshold)
    + get_light_state(vehicle_counts): dict
    + draw_lights(frame, states, shape): ndarray
    + get_statistics(counts): dict
    - _should_switch(elapsed, current, others): bool
    - _get_next_direction(counts): str
}

class UIDashboard {
    - width: int
    - colors: dict
    - font: int
    - font_scale: float
    --
    + __init__(width)
    + draw_dashboard(frame, stats): ndarray
    - _draw_header(panel, y): int
    - _draw_vehicle_counts(panel, counts, y): int
    - _draw_light_status(panel, states, y): int
    - _draw_statistics(panel, stats, y): int
}

class Logger {
    - csv_path: str
    - summary_path: str
    - logs: list
    - start_time: float
    --
    + __init__(output_dir)
    + log(timestamp, counts, states, fps): void
    + export_summary(stats): void
    + get_log_count(): int
    - _write_csv_header(): void
}

class ZoneEditor {
    - counter: TrafficCounter
    - selected_zone: str
    - selected_point: int
    - drag_start: tuple
    - is_dragging: bool
    --
    + __init__(counter)
    + handle_mouse(event, x, y, flags, param): void
    + draw_edit_overlay(frame): ndarray
    + save_zones(filepath): void
    + load_zones(filepath): void
    - _find_nearest_point(x, y): tuple
}

TrafficControlSystem --> VehicleDetector
TrafficControlSystem --> TrafficCounter
TrafficControlSystem --> TrafficLightController
TrafficControlSystem --> UIDashboard
TrafficControlSystem --> Logger
TrafficControlSystem --> ZoneEditor
ZoneEditor --> TrafficCounter

@enduml
```

---

## 3. Lưu Đồ Thuật Toán Điều Khiển Đèn Giao Thông

### Mermaid

```mermaid
flowchart TD
    START([Bắt đầu]) --> GET_COUNTS[Nhận số lượng xe<br/>từ TrafficCounter]
    GET_COUNTS --> GET_TIME[Tính thời gian đèn xanh<br/>elapsed = now - green_start_time]
    
    GET_TIME --> CHECK_YELLOW{Đang ở<br/>trạng thái VÀNG?}
    
    CHECK_YELLOW -->|Có| CHECK_YELLOW_TIME{elapsed >= yellow_time<br/>3 giây?}
    CHECK_YELLOW_TIME -->|Có| SWITCH_GREEN[Chuyển sang đèn XANH<br/>cho hướng tiếp theo]
    CHECK_YELLOW_TIME -->|Không| KEEP_YELLOW[Giữ đèn VÀNG]
    KEEP_YELLOW --> RETURN_STATE
    
    SWITCH_GREEN --> RESET_TIMER[Reset green_start_time<br/>is_yellow = False]
    RESET_TIMER --> RETURN_STATE
    
    CHECK_YELLOW -->|Không| GET_CURRENT[Lấy số xe hướng hiện tại<br/>current_count]
    GET_CURRENT --> GET_OTHERS[Lấy số xe max<br/>các hướng khác]
    
    GET_OTHERS --> CHECK_MAX{elapsed >= max_green_time<br/>30 giây?}
    CHECK_MAX -->|Có| START_YELLOW[Bắt đầu đèn VÀNG<br/>is_yellow = True]
    
    CHECK_MAX -->|Không| CHECK_MIN{elapsed >= min_green_time<br/>5 giây?}
    CHECK_MIN -->|Không| KEEP_GREEN[Giữ đèn XANH]
    KEEP_GREEN --> RETURN_STATE
    
    CHECK_MIN -->|Có| CHECK_THRESHOLD{current_count < threshold<br/>hoặc<br/>other_max > current + threshold?}
    
    CHECK_THRESHOLD -->|Có| START_YELLOW
    CHECK_THRESHOLD -->|Không| KEEP_GREEN
    
    START_YELLOW --> SELECT_NEXT[Chọn hướng tiếp theo<br/>= hướng có nhiều xe nhất]
    SELECT_NEXT --> RETURN_STATE
    
    RETURN_STATE[Trả về trạng thái đèn<br/>cho tất cả các hướng] --> END([Kết thúc])

    style START fill:#4CAF50,color:#fff
    style END fill:#f44336,color:#fff
    style CHECK_YELLOW fill:#FFC107
    style CHECK_YELLOW_TIME fill:#FFC107
    style CHECK_MAX fill:#2196F3,color:#fff
    style CHECK_MIN fill:#2196F3,color:#fff
    style CHECK_THRESHOLD fill:#9C27B0,color:#fff
    style SWITCH_GREEN fill:#4CAF50,color:#fff
    style START_YELLOW fill:#FF9800,color:#fff
    style KEEP_GREEN fill:#8BC34A
    style KEEP_YELLOW fill:#FFEB3B
```

### PlantUML

```plantuml
@startuml Traffic_Light_Algorithm
!theme plain
start

:Nhận số lượng xe từ TrafficCounter;
:Tính thời gian đèn xanh
elapsed = now - green_start_time;

if (Đang ở trạng thái VÀNG?) then (Có)
    if (elapsed >= yellow_time (3s)?) then (Có)
        :Chuyển sang đèn XANH
        cho hướng tiếp theo;
        :Reset green_start_time
        is_yellow = False;
    else (Không)
        :Giữ đèn VÀNG;
    endif
else (Không)
    :Lấy current_count (số xe hướng hiện tại);
    :Lấy other_max (max xe các hướng khác);
    
    if (elapsed >= max_green_time (30s)?) then (Có)
        #orange:Bắt đầu đèn VÀNG
        is_yellow = True;
        :Chọn hướng tiếp theo
        = hướng có nhiều xe nhất;
    else (Không)
        if (elapsed >= min_green_time (5s)?) then (Có)
            if (current_count < threshold\nHOẶC\nother_max > current + threshold?) then (Có)
                #orange:Bắt đầu đèn VÀNG
                is_yellow = True;
                :Chọn hướng tiếp theo
                = hướng có nhiều xe nhất;
            else (Không)
                #lightgreen:Giữ đèn XANH;
            endif
        else (Không)
            #lightgreen:Giữ đèn XANH;
        endif
    endif
endif

:Trả về trạng thái đèn
cho tất cả các hướng;

stop
@enduml
```

---

## 4. Sơ Đồ Tuần Tự Xử Lý Frame (Sequence Diagram)

### Mermaid

```mermaid
sequenceDiagram
    autonumber
    participant Main as TrafficControlSystem
    participant Detector as VehicleDetector
    participant YOLO as YOLOv8n Model
    participant Counter as TrafficCounter
    participant Controller as TrafficLightController
    participant Dashboard as UIDashboard
    participant Logger as Logger

    loop Mỗi Frame
        Main->>Main: Đọc frame từ video/webcam
        
        rect rgb(255, 235, 238)
            Note over Main,YOLO: Phát hiện phương tiện
            Main->>Detector: detect(frame)
            Detector->>YOLO: Inference
            YOLO-->>Detector: Raw detections
            Detector->>Detector: Lọc vehicle classes (car, motorcycle, bus, truck)
            Detector-->>Main: List[{bbox, confidence, class, center}]
        end
        
        rect rgb(243, 229, 245)
            Note over Main,Counter: Đếm xe theo vùng
            Main->>Counter: count_vehicles(detections)
            Counter->>Counter: point_in_zone() cho mỗi detection
            Counter-->>Main: {north: N, south: S, east: E, west: W}
        end
        
        rect rgb(255, 248, 225)
            Note over Main,Controller: Điều khiển đèn
            Main->>Controller: get_light_state(vehicle_counts)
            Controller->>Controller: Kiểm tra thời gian & ngưỡng
            Controller->>Controller: Quyết định chuyển đèn
            Controller-->>Main: {north: 'green', south: 'red', ...}
        end
        
        rect rgb(232, 245, 233)
            Note over Main,Dashboard: Vẽ giao diện
            Main->>Detector: draw_detections(frame, detections)
            Detector-->>Main: frame with bounding boxes
            Main->>Counter: draw_zones(frame)
            Counter-->>Main: frame with zone overlays
            Main->>Controller: draw_lights(frame, states)
            Controller-->>Main: frame with traffic lights
            Main->>Dashboard: draw_dashboard(frame, stats)
            Dashboard-->>Main: frame with statistics panel
        end
        
        rect rgb(241, 248, 233)
            Note over Main,Logger: Ghi log
            Main->>Logger: log(timestamp, counts, states, fps)
            Logger->>Logger: Append to CSV
        end
        
        Main->>Main: Hiển thị frame / Ghi video output
    end
```

### PlantUML

```plantuml
@startuml Sequence_Frame_Processing
!theme plain

participant "TrafficControlSystem" as Main
participant "VehicleDetector" as Detector
participant "YOLOv8n Model" as YOLO
participant "TrafficCounter" as Counter
participant "TrafficLightController" as Controller
participant "UIDashboard" as Dashboard
participant "Logger" as Logger

loop Mỗi Frame
    Main -> Main: Đọc frame từ video/webcam
    
    == Phát hiện phương tiện ==
    Main -> Detector: detect(frame)
    Detector -> YOLO: Inference
    YOLO --> Detector: Raw detections
    Detector -> Detector: Lọc vehicle classes
    Detector --> Main: List[{bbox, confidence, class, center}]
    
    == Đếm xe theo vùng ==
    Main -> Counter: count_vehicles(detections)
    Counter -> Counter: point_in_zone() cho mỗi detection
    Counter --> Main: {north: N, south: S, east: E, west: W}
    
    == Điều khiển đèn ==
    Main -> Controller: get_light_state(vehicle_counts)
    Controller -> Controller: Kiểm tra thời gian & ngưỡng
    Controller -> Controller: Quyết định chuyển đèn
    Controller --> Main: {direction: 'green'/'yellow'/'red'}
    
    == Vẽ giao diện ==
    Main -> Detector: draw_detections(frame, detections)
    Main -> Counter: draw_zones(frame)
    Main -> Controller: draw_lights(frame, states)
    Main -> Dashboard: draw_dashboard(frame, stats)
    
    == Ghi log ==
    Main -> Logger: log(timestamp, counts, states, fps)
    Logger -> Logger: Append to CSV
    
    Main -> Main: Hiển thị / Ghi video output
end

@enduml
```

---

## 5. Sơ Đồ Trạng Thái Đèn Giao Thông (State Diagram)

### Mermaid

```mermaid
stateDiagram-v2
    [*] --> North_Green: Khởi tạo

    state "Bắc XANH" as North_Green {
        [*] --> NG_Active
        NG_Active: Bắc: XANH
        NG_Active: Nam, Đông, Tây: ĐỎ
    }

    state "Bắc VÀNG" as North_Yellow {
        [*] --> NY_Active
        NY_Active: Bắc: VÀNG
        NY_Active: Nam, Đông, Tây: ĐỎ
    }

    state "Nam XANH" as South_Green {
        [*] --> SG_Active
        SG_Active: Nam: XANH
        SG_Active: Bắc, Đông, Tây: ĐỎ
    }

    state "Nam VÀNG" as South_Yellow {
        [*] --> SY_Active
        SY_Active: Nam: VÀNG
        SY_Active: Bắc, Đông, Tây: ĐỎ
    }

    state "Đông XANH" as East_Green {
        [*] --> EG_Active
        EG_Active: Đông: XANH
        EG_Active: Bắc, Nam, Tây: ĐỎ
    }

    state "Đông VÀNG" as East_Yellow {
        [*] --> EY_Active
        EY_Active: Đông: VÀNG
        EY_Active: Bắc, Nam, Tây: ĐỎ
    }

    state "Tây XANH" as West_Green {
        [*] --> WG_Active
        WG_Active: Tây: XANH
        WG_Active: Bắc, Nam, Đông: ĐỎ
    }

    state "Tây VÀNG" as West_Yellow {
        [*] --> WY_Active
        WY_Active: Tây: VÀNG
        WY_Active: Bắc, Nam, Đông: ĐỎ
    }

    North_Green --> North_Yellow: should_switch = True
    North_Yellow --> South_Green: yellow_time elapsed\n& Nam có nhiều xe nhất
    North_Yellow --> East_Green: yellow_time elapsed\n& Đông có nhiều xe nhất
    North_Yellow --> West_Green: yellow_time elapsed\n& Tây có nhiều xe nhất

    South_Green --> South_Yellow: should_switch = True
    South_Yellow --> North_Green: yellow_time elapsed\n& Bắc có nhiều xe nhất
    South_Yellow --> East_Green: yellow_time elapsed\n& Đông có nhiều xe nhất
    South_Yellow --> West_Green: yellow_time elapsed\n& Tây có nhiều xe nhất

    East_Green --> East_Yellow: should_switch = True
    East_Yellow --> North_Green: yellow_time elapsed\n& Bắc có nhiều xe nhất
    East_Yellow --> South_Green: yellow_time elapsed\n& Nam có nhiều xe nhất
    East_Yellow --> West_Green: yellow_time elapsed\n& Tây có nhiều xe nhất

    West_Green --> West_Yellow: should_switch = True
    West_Yellow --> North_Green: yellow_time elapsed\n& Bắc có nhiều xe nhất
    West_Yellow --> South_Green: yellow_time elapsed\n& Nam có nhiều xe nhất
    West_Yellow --> East_Green: yellow_time elapsed\n& Đông có nhiều xe nhất
```

### PlantUML

```plantuml
@startuml State_Traffic_Light
!theme plain
skinparam state {
    BackgroundColor<<green>> LightGreen
    BackgroundColor<<yellow>> LightYellow
    BackgroundColor<<red>> LightCoral
}

[*] --> North_Green

state "Bắc XANH" as North_Green <<green>> {
    state "Bắc: XANH\nNam, Đông, Tây: ĐỎ" as NG
}

state "Bắc VÀNG" as North_Yellow <<yellow>> {
    state "Bắc: VÀNG\nNam, Đông, Tây: ĐỎ" as NY
}

state "Nam XANH" as South_Green <<green>> {
    state "Nam: XANH\nBắc, Đông, Tây: ĐỎ" as SG
}

state "Nam VÀNG" as South_Yellow <<yellow>> {
    state "Nam: VÀNG\nBắc, Đông, Tây: ĐỎ" as SY
}

state "Đông XANH" as East_Green <<green>> {
    state "Đông: XANH\nBắc, Nam, Tây: ĐỎ" as EG
}

state "Đông VÀNG" as East_Yellow <<yellow>> {
    state "Đông: VÀNG\nBắc, Nam, Tây: ĐỎ" as EY
}

state "Tây XANH" as West_Green <<green>> {
    state "Tây: XANH\nBắc, Nam, Đông: ĐỎ" as WG
}

state "Tây VÀNG" as West_Yellow <<yellow>> {
    state "Tây: VÀNG\nBắc, Nam, Đông: ĐỎ" as WY
}

North_Green --> North_Yellow : should_switch
North_Yellow --> South_Green : next = south
North_Yellow --> East_Green : next = east
North_Yellow --> West_Green : next = west

South_Green --> South_Yellow : should_switch
South_Yellow --> North_Green : next = north
South_Yellow --> East_Green : next = east
South_Yellow --> West_Green : next = west

East_Green --> East_Yellow : should_switch
East_Yellow --> North_Green : next = north
East_Yellow --> South_Green : next = south
East_Yellow --> West_Green : next = west

West_Green --> West_Yellow : should_switch
West_Yellow --> North_Green : next = north
West_Yellow --> South_Green : next = south
West_Yellow --> East_Green : next = east

@enduml
```

---

## 6. Sơ Đồ Luồng Dữ Liệu (Data Flow Diagram)

### Mermaid

```mermaid
flowchart LR
    subgraph External["Nguồn Bên Ngoài"]
        VIDEO[(Video File)]
        WEBCAM[(Webcam)]
        USER((Người dùng))
    end

    subgraph Process["Xử Lý"]
        P1[1.0<br/>Đọc Video]
        P2[2.0<br/>Phát hiện<br/>Phương tiện]
        P3[3.0<br/>Đếm xe<br/>theo vùng]
        P4[4.0<br/>Điều khiển<br/>đèn giao thông]
        P5[5.0<br/>Vẽ giao diện]
        P6[6.0<br/>Ghi log]
    end

    subgraph DataStore["Kho Dữ Liệu"]
        D1[(YOLOv8n Model)]
        D2[(Zone Config)]
        D3[(Light State)]
        D4[(Traffic Logs)]
    end

    subgraph Output["Đầu Ra"]
        DISPLAY[/Màn hình\]
        VIDEO_OUT[(Video Output)]
        CSV[(CSV File)]
        SUMMARY[(Summary)]
    end

    VIDEO --> P1
    WEBCAM --> P1
    USER -.->|Keyboard| P1
    USER -.->|Edit Zones| P3

    P1 -->|frame| P2
    D1 -->|model weights| P2
    P2 -->|detections| P3
    D2 -->|zone polygons| P3
    P3 -->|vehicle_counts| P4
    D3 <-->|state| P4
    P4 -->|light_states| P5
    P3 -->|counts| P5
    P2 -->|detections| P5
    P5 -->|annotated frame| DISPLAY
    P5 -->|annotated frame| VIDEO_OUT
    P4 -->|states| P6
    P3 -->|counts| P6
    P6 --> D4
    D4 --> CSV
    D4 --> SUMMARY

    style P1 fill:#BBDEFB
    style P2 fill:#F8BBD9
    style P3 fill:#E1BEE7
    style P4 fill:#FFF9C4
    style P5 fill:#C8E6C9
    style P6 fill:#DCEDC8
```

### PlantUML (DFD Style)

```plantuml
@startuml Data_Flow_Diagram
!theme plain

' External Entities
actor "Người dùng" as USER
entity "Video File" as VIDEO
entity "Webcam" as WEBCAM

' Processes
usecase "1.0\nĐọc Video" as P1
usecase "2.0\nPhát hiện\nPhương tiện" as P2
usecase "3.0\nĐếm xe\ntheo vùng" as P3
usecase "4.0\nĐiều khiển\nđèn giao thông" as P4
usecase "5.0\nVẽ giao diện" as P5
usecase "6.0\nGhi log" as P6

' Data Stores
database "YOLOv8n Model" as D1
database "Zone Config" as D2
database "Light State" as D3
database "Traffic Logs" as D4

' Outputs
storage "Màn hình" as DISPLAY
storage "Video Output" as VIDEO_OUT
storage "CSV File" as CSV
storage "Summary" as SUMMARY

VIDEO --> P1 : video stream
WEBCAM --> P1 : video stream
USER ..> P1 : keyboard input
USER ..> P3 : edit zones

P1 --> P2 : frame
D1 --> P2 : model weights
P2 --> P3 : detections
D2 --> P3 : zone polygons
P3 --> P4 : vehicle_counts
D3 <--> P4 : state
P4 --> P5 : light_states
P3 --> P5 : counts
P2 --> P5 : detections
P5 --> DISPLAY : annotated frame
P5 --> VIDEO_OUT : annotated frame
P4 --> P6 : states
P3 --> P6 : counts
P6 --> D4 : log entry
D4 --> CSV
D4 --> SUMMARY

@enduml
```

---

## 7. Thuật Toán Ray Casting (Kiểm tra điểm trong đa giác)

### Mermaid

```mermaid
flowchart TD
    START([Bắt đầu]) --> INPUT[/Nhập: point(x,y), polygon[]/]
    INPUT --> INIT[inside = False<br/>n = số đỉnh polygon<br/>p1 = polygon[0]]
    
    INIT --> LOOP{i từ 1 đến n}
    
    LOOP -->|Còn đỉnh| GET_P2[p2 = polygon[i mod n]]
    GET_P2 --> CHECK_Y1{y > min(p1.y, p2.y)?}
    
    CHECK_Y1 -->|Không| NEXT[p1 = p2]
    CHECK_Y1 -->|Có| CHECK_Y2{y <= max(p1.y, p2.y)?}
    
    CHECK_Y2 -->|Không| NEXT
    CHECK_Y2 -->|Có| CHECK_X{x <= max(p1.x, p2.x)?}
    
    CHECK_X -->|Không| NEXT
    CHECK_X -->|Có| CALC_XINTERS[Tính xinters =<br/>(y-p1.y)*(p2.x-p1.x)/(p2.y-p1.y) + p1.x]
    
    CALC_XINTERS --> CHECK_CROSS{p1.x == p2.x<br/>hoặc x <= xinters?}
    
    CHECK_CROSS -->|Có| TOGGLE[inside = NOT inside]
    CHECK_CROSS -->|Không| NEXT
    
    TOGGLE --> NEXT
    NEXT --> LOOP
    
    LOOP -->|Hết đỉnh| RETURN[/Trả về inside/]
    RETURN --> END([Kết thúc])

    style START fill:#4CAF50,color:#fff
    style END fill:#f44336,color:#fff
    style TOGGLE fill:#2196F3,color:#fff
    style CHECK_Y1 fill:#FF9800
    style CHECK_Y2 fill:#FF9800
    style CHECK_X fill:#FF9800
    style CHECK_CROSS fill:#9C27B0,color:#fff
```

---

## 8. Sơ Đồ Component (Component Diagram)

### PlantUML

```plantuml
@startuml Component_Diagram
!theme plain

package "Traffic Control System" {
    
    component [main.py] as Main
    component [config.py] as Config
    
    package "AI/Detection Layer" {
        component [vehicle_detector.py] as Detector
        component [yolov8n.pt] as Model
    }
    
    package "Business Logic Layer" {
        component [traffic_counter.py] as Counter
        component [traffic_light_controller.py] as Controller
    }
    
    package "Presentation Layer" {
        component [ui_dashboard.py] as Dashboard
        component [zone_editor.py] as ZoneEditor
    }
    
    package "Data Layer" {
        component [logger.py] as Logger
        database "traffic_logs.csv" as CSV
        database "zones_config.json" as ZonesJSON
    }
}

' External
cloud "OpenCV" as OpenCV
cloud "Ultralytics" as Ultralytics
cloud "NumPy" as NumPy

' Connections
Main --> Detector
Main --> Counter
Main --> Controller
Main --> Dashboard
Main --> ZoneEditor
Main --> Logger
Main --> Config

Detector --> Model
Detector --> Counter
Counter --> Controller
Controller --> Dashboard
ZoneEditor --> Counter
Logger --> CSV
ZoneEditor --> ZonesJSON

Config --> Detector
Config --> Counter
Config --> Controller
Config --> Dashboard

Detector ..> Ultralytics
Detector ..> OpenCV
Dashboard ..> OpenCV
Counter ..> NumPy

@enduml
```

---

## Hướng Dẫn Sử Dụng

### Render Mermaid

1. **GitHub/GitLab**: Đặt code trong block ` ```mermaid ` sẽ tự động render
2. **VS Code**: Cài extension "Markdown Preview Mermaid Support"
3. **Online**: Copy code vào [mermaid.live](https://mermaid.live)

### Render PlantUML

1. **Online**: Copy code vào [plantuml.com/plantuml](https://www.plantuml.com/plantuml)
2. **VS Code**: Cài extension "PlantUML"
3. **IntelliJ/PyCharm**: Cài plugin PlantUML Integration

### Export sang hình ảnh

- Mermaid Live Editor: Export PNG/SVG
- PlantUML: Export PNG/SVG/PDF
- VS Code: Right-click > Export diagram

---

## Tham Khảo Code Gốc

| Sơ đồ | File tham chiếu |
|-------|-----------------|
| Class Diagram | Tất cả file .py |
| Thuật toán điều khiển đèn | `traffic_light_controller.py:41-99` |
| Ray Casting | `traffic_counter.py:61-88` |
| Luồng xử lý frame | `main.py:process_frame()` |
