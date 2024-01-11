# README for Libre-Podcast

Libre-Podcast is a terminal-based podcast app that allows you to browse and listen to your favorite podcasts directly from the command line. This alpha release provides basic functionalities to add and play podcast episodes, manage feeds, and keep track of your listening progress.

## Prerequisites

Before using Libre-Podcast, make sure you have [FFmpeg](https://www.ffmpeg.org/download.html) installed on your system.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Roysu17/libre-podcast.git
    ```

2. Navigate to the project directory:

    ```bash
    cd libre-podcast
    ```

3. Install required Python libraries:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the podcast manager:

    ```bash
    python main.py
    ```

## Project Structure

The application is structured into three main components:

1. **main.py**: The entry point of the application. It handles user interactions through the command line, displaying the menu, and directing the flow of the program based on user input.

2. **PodcastManager.py**: This module manages the podcast feeds, episodes, and user progress. It communicates with the SQLite database to store and retrieve data about feeds, episodes, and their progress. It also provides methods to interact with the database and update user progress.

3. **streaming_player.py**: This module handles streaming and playing of podcast episodes. It utilizes the FFmpeg library to stream audio content and provides a seamless playback experience.

## Required Python Libraries

Libre-Podcast depends on the following Python libraries. Make sure to install them before running the application:

- [requests](https://docs.python-requests.org/en/master/): Used for making HTTP requests.
- [pygame](https://www.pygame.org/): Provides functionality for playing audio.
- [feedparser](https://pypi.org/project/feedparser/): Parses RSS and Atom feeds.
- [ssl](https://docs.python.org/3/library/ssl.html): Provides support for SSL/TLS protocols.
- [sqlite3](https://docs.python.org/3/library/sqlite3.html): Python interface for SQLite databases.
- [validators](https://pypi.org/project/validators/): Validates URLs.

You can install these libraries using the following command:

```bash
pip install requests pygame feedparser validators
```

## Features

### 1. Add New RSS Feed

Select option `1` from the main menu and enter the RSS feed URL when prompted. The app will fetch the podcast details and display them. You can then choose to play episodes, view the next 20 episodes, or quit.

### 2. Listen to Unfinished Episodes

Choose option `2` from the main menu to view and listen to unfinished episodes. The app will display a list of episodes with their progress status. Enter the number of the episode you want to listen to, and the app will resume playback from where you left off.

### 3. Browse Added Feeds

Option `3` allows you to browse through the feeds you have added. Select a feed to view its details and play episodes.

### 4. Quit

Choose option `q` to exit the app.

## Usage Example

Here's a simple example of how to use the podcast manager:

```bash
python podcast_manager.py
```

Follow the on-screen instructions to add a new RSS feed, listen to episodes, and manage your podcasts.

## Important Note

- **Podcast Streaming**: Libre-Podcast utilizes the [FFmpeg](https://www.ffmpeg.org/) library for streaming podcast episodes. Ensure that FFmpeg is installed on your system for proper functionality.

- **Incomplete Features**: This alpha release may lack some features and may contain bugs. Your feedback is valuable in improving the app.

## License

Libre-Podcast is released under the [MIT License](LICENSE).

---

Feel free to contribute to the development of Libre-Podcast or report any issues you encounter. Happy listening!

## Contributing

Feel free to contribute to the development of Libre-Podcast or report any issues you encounter. Visit the [GitHub repository](https://github.com/Roysu17/libre-podcast) for more details.

---

Your feedback is valuable in improving the app. Happy listening!
