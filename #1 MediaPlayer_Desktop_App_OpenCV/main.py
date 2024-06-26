import math
import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QSizePolicy, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QIcon
from main_ui import Ui_MainWindow  # Import the generated class
from setting import SettingWindow
from datetime import timedelta

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up the user interface from the generated class
        self.setupUi(self)

        # Set flags to remove the default title bar
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Connect the maximizeRestoreAppBtn button to the maximize_window method
        self.maximizeRestoreAppBtn.clicked.connect(self.maximize_window)

        # Connect the closeAppBtn button to the close method
        self.closeAppBtn.clicked.connect(self.close)

        # Connect the minimizeAppBtn button to the showMinimized method
        self.minimizeAppBtn.clicked.connect(self.showMinimized)

        # Connect the btnBrowse button to open file dialog
        self.btnBrowse.clicked.connect(self.open_file_dialog)

        # Connect the btnPlayPause button to toggle play/pause
        self.btnPlayPause.clicked.connect(self.toggle_play_pause)

        # Connect the btnStepBackward button to step backward
        self.btnStepBackward.clicked.connect(self.step_backward)

        # Connect the btnStepUpward button to step upward
        self.btnStepUpward.clicked.connect(self.step_upward)

        # Connect the btnEnd button to end the video
        self.btnEnd.clicked.connect(self.end_video)

        # Connect the btnDecreaseSpeed button to decrease speed
        self.btnDecreaseSpeed.clicked.connect(self.decrease_speed)

        # Connect the btnIncreaseSpeed button to increase speed
        self.btnIncreaseSpeed.clicked.connect(self.increase_speed)

        # Initialize videoLabel size policy and alignment
        self.videoLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.videoLabel.setAlignment(Qt.AlignCenter)


        # Initialize video player variables
        self.video_file_path = None
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        # Variable to track play/pause state
        self.playing = False

        # Variable to track playback speed
        self.speed = 1.0
        self.videoPrograssBar.mousePressEvent = self.change_video_position

        self.btnSetting.clicked.connect(self.settingWindow)

        # Video information
        self.video_info = None
       
    def settingWindow(self):
        if self.video_info:
           self.setting_window = SettingWindow(self, self.video_info)
           self.setting_window.show()
        else:
           print("No video loaded. Cannot open settings window.")

    def set_video_mode(self, mode):
        if self.cap is not None:
            print("Mode:", mode)  # Print the received mode
            if mode == 'grayscale':
                self.cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)
            elif mode == 'blackwhite':
                self.cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)
                self.cap.set(cv2.CAP_PROP_MONOCHROME, 1)
            elif mode == 'normal':
                self.cap.set(cv2.CAP_PROP_CONVERT_RGB, 1)
                self.cap.set(cv2.CAP_PROP_MONOCHROME, 0)


    def update_progress_bar(self):
        if self.cap is not None and self.cap.isOpened():
            total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            progress_percentage = (current_frame / total_frames) * 100

            # Check if the decimal part of progress_percentage is less than 0.5
            if progress_percentage % 1 < 0.5:
                progress_percentage = math.floor(progress_percentage)
            else:
                progress_percentage = math.ceil(progress_percentage)

            self.videoPrograssBar.setValue(progress_percentage)
    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv)", options=options)
        if file_name:
            try:
                self.video_file_path = file_name
                self.txtBrowsePath.setText(file_name)
                self.play_video()
                self.display_message("Video loaded successfully.")

                # Get total duration of the video
                if self.cap is not None and self.cap.isOpened():
                    total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    fps = self.cap.get(cv2.CAP_PROP_FPS)
                    total_seconds = total_frames / fps
                    total_time = str(timedelta(seconds=total_seconds))
                    self.lblTotalTime.setText(total_time)

                # Store video information
                if self.cap is not None and self.cap.isOpened():
                    height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    fps = int(self.cap.get(cv2.CAP_PROP_FPS))
                    frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    duration_sec = frame_count / fps
                    duration_str = str(timedelta(seconds=duration_sec))
                    self.video_info = f"Height: {height}\nWidth: {width}\nFPS: {fps}\nFrame Count: {frame_count}\nDuration: {duration_str}"
            except Exception as e:
                print("Error:", e)


  
    def play_video(self):
        try:
            if self.video_file_path is not None:
                self.cap = cv2.VideoCapture(self.video_file_path)
                if not self.cap.isOpened():
                    print("Error: Unable to open video file")
                    return

                # Start the timer to update the frame
                self.timer.start(33)  # Update frame every ~33 milliseconds (about 30 frames per second)
        except Exception as e:
            print("Error in play_video:", e)

    def update_frame(self):
        try:
            if self.cap is None or not self.cap.isOpened():
                return

            ret, frame = self.cap.read()
            if ret:
                # Convert the frame to QPixmap
                pixmap = self.convert_cv_to_pixmap(frame)

                # Scale the QPixmap to fit the QLabel while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(self.videoLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # Set the scaled QPixmap to the QLabel
                self.videoLabel.setPixmap(scaled_pixmap)

                # Update progress bar
                self.update_progress_bar()

                # Update running time
                if self.cap.isOpened():
                    current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                    fps = self.cap.get(cv2.CAP_PROP_FPS)
                    current_seconds = current_frame / fps
                    current_time = str(timedelta(seconds=current_seconds)).split('.', 1)[0]  # Remove milliseconds
                    self.lblRunningTime.setText(current_time)
        except Exception as e:
            print("Error in update_frame:", e)


    def convert_cv_to_pixmap(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(q_img)

    def maximize_window(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def toggle_play_pause(self):
        if self.playing:
            # Pause the video
            self.timer.stop()
            self.playing = False
            # Change button icon to play
            self.btnPlayPause.setIcon(QIcon(":/icons/images/icons/cil-media-play.png"))
            self.display_message("Video paused.")
        else:
            # Play the video
            self.timer.start(33)  # Update frame every ~33 milliseconds (about 30 frames per second)
            self.playing = True
            # Change button icon to pause
            self.btnPlayPause.setIcon(QIcon(":/icons/images/icons/cil-media-pause.png"))
            self.display_message("Video resumed.")

    def step_backward(self):
        if self.cap is not None and self.cap.isOpened():
            current_position = self.cap.get(cv2.CAP_PROP_POS_MSEC)
            new_position = max(0, current_position - 4000)  # Step back 4 seconds
            self.cap.set(cv2.CAP_PROP_POS_MSEC, new_position)
            self.display_message("Stepped backward 4 seconds.")

    def step_upward(self):
        if self.cap is not None and self.cap.isOpened():
            current_position = self.cap.get(cv2.CAP_PROP_POS_MSEC)
            duration = self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.cap.get(cv2.CAP_PROP_FPS) * 1000
            new_position = min(duration, current_position + 4000)  # Step forward 4 seconds
            self.cap.set(cv2.CAP_PROP_POS_MSEC, new_position)
            self.display_message("Stepped forward 4 seconds.")

    def end_video(self):
        if self.cap is not None and self.cap.isOpened():
            self.timer.stop()
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.display_message("Video ended. Returned to the beginning.")
            self.btnPlayPause.setIcon(QIcon(":/icons/images/icons/cil-media-play.png"))


    def decrease_speed(self):
        self.speed = max(0.1, self.speed - 0.1)
        if self.cap is not None:
            # Decrease playback speed by reducing frame rate
            self.cap.set(cv2.CAP_PROP_FPS, self.cap.get(cv2.CAP_PROP_FPS) * self.speed)
            self.display_message(f"Playback speed decreased to {self.speed:.2f}x.")
    
    def increase_speed(self):
        self.speed += 0.1
        if self.cap is not None:
            # Increase playback speed by increasing frame rate
            self.cap.set(cv2.CAP_PROP_FPS, self.cap.get(cv2.CAP_PROP_FPS) * self.speed)
            self.display_message(f"Playback speed increased to {self.speed:.2f}x.")


    
    def display_message(self, message):
        self.message.setText(message)
        QTimer.singleShot(10000, self.clear_message)

    def clear_message(self):
        self.message.clear()
    def change_video_position(self, event):
        # Calculate the new position based on the mouse click event
        new_position = (event.pos().x() / self.videoPrograssBar.width()) * 100

        # Set the new position in the video
        if self.cap is not None and self.cap.isOpened():
            total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            new_frame = (new_position / 100) * total_frames
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
