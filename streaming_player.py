import subprocess
import threading
import os
import requests

class AudioPlayer:
    def __init__(self, mp3_url, start_byte):
        self.FIFO_NAME = "Temp_fifo"
        self.MP3_URL = mp3_url
        self.CHUNK_SIZE = 24 * 1024
        self.total_size = 0
        self.start_byte = start_byte

    def fetch_total_size(self):
        try:
            with requests.head(self.MP3_URL) as response:
                self.total_size = int(response.headers.get('content-length', 0))
        except Exception as e:
            print(f"Error fetching total size: {e}")

    def create_fifo(self):
        if not os.path.exists(self.FIFO_NAME):
            os.mkfifo(self.FIFO_NAME)

    def fetch_and_write_chunks(self):
        try:
            headers = {"Range": f"bytes={self.start_byte}-"}
            with requests.get(self.MP3_URL, stream=True, headers=headers) as response:
                self.total_size = int(response.headers.get('content-length', 0))
                print(self.total_size)
                with open(self.FIFO_NAME, "ab") as fifo_file:
                    for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                        if chunk:
                            fifo_file.write(chunk)
                        else:
                            break  # Exit loop when no more data is available
        except BrokenPipeError:
            pass  # Ignore BrokenPipeError and continue silently
        except Exception as e:
            print(f"Error fetching/writing chunks: {e}")

    def play_from_fifo(self):
        os.environ["FFREPORT"] = "file=saved_progress.log"  # Use the desired filename
        try:
            subprocess.call(["ffplay", "-hide_banner", "-autoexit", "-i", self.FIFO_NAME, '-report'])
        except KeyboardInterrupt:
            print("Stopping playback...")
        finally:
            try:
                os.remove(self.FIFO_NAME)
            except FileNotFoundError:
                pass  # Ignore if the file doesn't exist

    def start_audio(self):
        self.create_fifo()

        fetch_thread = threading.Thread(target=self.fetch_and_write_chunks)
        fetch_thread.start()

        try:
            self.play_from_fifo()
            fetch_thread.join()
            bytes_read = self.extract_info_from_log('saved_progress.log')
            progress_as_percentage = ((self.start_byte+bytes_read)/(self.start_byte+self.total_size))*100
            print(f"Played: {progress_as_percentage}%")
            if progress_as_percentage == 100:
                return 'Completed'
            return (self.start_byte + bytes_read)
        except KeyboardInterrupt:
            pass
        fetch_thread.join()
        return 0
        

    def extract_info_from_log(self, filename):
        """Extracts the required information from the log file.

        Args:
        filename: The path to the log file.

        Returns:
        A tuple containing:
            (bytes_read, second_last_line_number)
        """

        with open(filename, 'r') as file:
            lines = file.readlines()

        last_line = lines[-1]
        # Extract bytes read from the last line
        bytes_read_str = last_line.split("Statistics: ")[1].split()[0]
        try:
            bytes_read = int(bytes_read_str)
        except ValueError:
            raise ValueError(f"Invalid bytes read format in last line: {last_line}")

        return bytes_read

        

if __name__ == "__main__":
    MP3_URL = "https://www.podtrac.com/pts/redirect.mp3/pdst.fm/e/chrt.fm/track/524GE/traffic.megaphone.fm/VMP9852531180.mp3?updated=1703266879"
    
    audio_player = AudioPlayer(MP3_URL, 100000000)
    print(audio_player.start_audio())
    