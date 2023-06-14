import os
import sys
from mutagen.flac import FLAC
from PyQt5 import QtWidgets, QtCore, QtMultimedia

class AudioPlayer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.playlist = QtMultimedia.QMediaPlaylist()
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setPlaylist(self.playlist)

        self.play_button = QtWidgets.QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play)

        self.stop_button = QtWidgets.QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaStop))
        self.stop_button.clicked.connect(self.stop)

        self.next_button = QtWidgets.QPushButton()
        self.next_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipForward))
        self.next_button.clicked.connect(self.next_track)

        self.previous_button = QtWidgets.QPushButton()
        self.previous_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipBackward))
        self.previous_button.clicked.connect(self.previous_track)

        self.track_list = QtWidgets.QListWidget()
        self.track_list.itemDoubleClicked.connect(self.play_selected_track)

        self.track_duration_label = QtWidgets.QLabel('--:--')
        self.track_duration_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)
        self.volume_slider.setTickInterval(10)
        self.volume_slider.valueChanged.connect(self.set_volume)

        self.play_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.play_slider.setRange(0, 0)
        self.play_slider.sliderMoved.connect(self.set_position)

        self.main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QtWidgets.QVBoxLayout(self.main_widget)

        track_controls_layout = QtWidgets.QHBoxLayout()
        track_controls_layout.addWidget(self.previous_button)
        track_controls_layout.addWidget(self.play_button)
        track_controls_layout.addWidget(self.stop_button)
        track_controls_layout.addWidget(self.next_button)

        playlist_controls_layout = QtWidgets.QHBoxLayout()
        playlist_controls_layout.addWidget(self.track_list)
        playlist_controls_layout.addWidget(self.track_duration_label)

        volume_layout = QtWidgets.QHBoxLayout()
        volume_layout.addWidget(self.volume_slider)

        self.main_layout.addLayout(track_controls_layout)
        self.main_layout.addLayout(playlist_controls_layout)
        self.main_layout.addWidget(self.play_slider)
        self.main_layout.addLayout(volume_layout)

        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)

    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')

        open_file_action = QtWidgets.QAction('Open File', self)
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        open_folder_action = QtWidgets.QAction('Open Folder', self)
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)

    def open_file(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Audio File', filter='FLAC Files (*.flac)')
        if file_name:
            self.add_file_to_playlist(file_name)

    def open_folder(self):
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Audio Folder')
        if folder_name:
            for file_name in os.listdir(folder_name):
                if file_name.lower().endswith('.flac'):
                    file_path = os.path.join(folder_name, file_name)
                    self.add_file_to_playlist(file_path)

    def add_file_to_playlist(self, file_name):
        media_content = QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(file_name))
        if not self.playlist.mediaCount():
            track_info = get_track_info(file_name)
            if track_info:
                artist, title = track_info
                text = f'{artist} - {title}'
            else:
                text = 'Track Info'
            self.track_duration_label.setText(text)
        self.playlist.addMedia(media_content)

    def play(self):
        if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def stop(self):
        self.player.stop()

    def next_track(self):
        self.playlist.next()

    def previous_track(self):
        self.playlist.previous()

    def set_volume(self, volume):
        self.player.setVolume(volume)

    def update_position(self, position):
        self.play_slider.setValue(position)

    def set_position(self, position):
        self.player.setPosition(position)

    def update_duration(self, duration):
        self.play_slider.setRange(0, duration)
        self.play_slider.setEnabled(duration > 0)
        self.track_duration_label.setText(format_time(duration))

    def play_selected_track(self, item):
        index = self.track_list.row(item)
        self.playlist.setCurrentIndex(index)
        self.player.play()

def get_track_info(file_path):
    audio = FLAC(file_path)
    if 'artist' in audio:
        artist = audio['artist'][0]
    else:
        artist = ''
    if 'title' in audio:
        title = audio['title'][0]
    else:
        title = ''
    return artist, title

def format_time(milliseconds):
    seconds = milliseconds // 1000
    minutes = seconds // 60
    seconds %= 60
    return f'{minutes:02d}:{seconds:02d}'

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    player = AudioPlayer()
    player.create_menu()  # Create the menu
    player.show()
    sys.exit(app.exec())
