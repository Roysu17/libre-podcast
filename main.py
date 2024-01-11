"""
The player in Streaming_player uses ffmpeg's fplayer, need to install ffmepg for your distribution
https://www.ffmpeg.org/download.html
"""
import ssl
import feedparser
import requests
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from streaming_player import AudioPlayer
from PodcastManager import PodcastManager
from datetime import datetime
import validators

CHUNK_SIZE = 1024 * 24

def play_audio_downloaded(file_name):
    # Initialize Pygame mixer
    pygame.init()
    pygame.mixer.init()

    # Load and play the downloaded MP3 file
    pygame.mixer.music.load(file_name)
    pygame.mixer.music.play()

    # Wait for music to finish or for the user to pause it
    paused = False
    quit_requested = False

    while not quit_requested:
        if paused:
            command = input("Press 'p' to pause, 'r' to resume, or 'q' to quit: ")
            if command.lower() == 'r':
                pygame.mixer.music.unpause()
                paused = False
            elif command.lower() == 'q':
                quit_requested = True
        if not paused:
            command = input("Press 'p' to pause, 'r' to resume, or 'q' to quit: ")
            if command.lower() == 'p':
                pygame.mixer.music.pause()
                paused = True
            elif command.lower() == 'q':
                quit_requested = True

    # Clean up when the music finishes or is stopped
    pygame.mixer.quit()
    pygame.quit()

def download_and_play(audio_url, title, progress):
    headers = {'Range': f'bytes={0}-{CHUNK_SIZE}'}
    testing_response = requests.get(audio_url, headers=headers, stream=True)
    
    if testing_response.status_code == 206:  # If Partial content status code
        print("Streaming the audio...")
        streaming = AudioPlayer(audio_url, progress)
        return streaming.start_audio()
    else:
        print("Streaming failed, downloading the file, please wait")
        # Download the MP3 file
        response = requests.get(audio_url)
        file_name = f"{title}.mp3"
        with open(file_name, "wb") as file:
            file.write(response.content)
        play_audio_downloaded(file_name)
        
def display_episodes(feed, start_index, num_episodes):
    # Display details of episodes starting from 'start_index' up to 'start_index + num_episodes'
    end_index = min(start_index + num_episodes, len(feed.entries))
    for idx, item in enumerate(feed.entries[start_index:end_index], start=start_index + 1):
        # Get the audio URL from the enclosure tag
        audio_url = item.enclosures[0].href

        # Extract only the first 100 characters of the description
        truncated_description = item.description[:100] + '...' if len(item.description) > 100 else item.description

        # Get and format the publication date
        pub_date = item.published
        #formatted_pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d")

        # Get the iTunes episode number (if available)
        itunes_episode_number = item.get('itunes_episode', 'N/A')

        # Print episode details
        print(f"Index Number: {idx}")
        print(f"Title: {item.title}", f", (Podcast Episode Number: {itunes_episode_number})")
        print(f"Truncated Description: {truncated_description}")
        print(f"Publication Date: {pub_date}")
        print(f"Audio URL: {audio_url}\n")

    return end_index

def play_audio_from_feed(feed_url, podcast_manager):
    # Parse the RSS feed
    feed = feedparser.parse(feed_url)
    print()
    # Print podcast title and description
    print(f"Podcast Title: {feed.feed.title}")
    print(f"Podcast Description: {feed.feed.description}\n")

    podcast_manager.add_feed(feed_url, feed.feed.title, feed.feed.description)
    added_feeds = podcast_manager.get_added_feeds()
    selected_feed_id = added_feeds[-1][0]  # Assuming the latest added feed ID corresponds to the feed just added

    episodes_to_display = 20
    start_index = 0
    total_episodes = len(feed.entries)

    while start_index < total_episodes:
        # Display the next 20 episodes or less if fewer episodes are remaining
        end_index = display_episodes(feed, start_index, episodes_to_display)

        # Ask the user for further action
        choice = input("Enter 'n' to view next 20 episodes, 'p' to play an episode, or 'q' to quit: ")
        if choice.lower() == 'n':
            start_index = end_index
        elif choice.lower() == 'p':
            try:
                episode_number = int(input(f"Enter the index number of the episode to listen (1 - {end_index}): "))
                if 1 <= episode_number <= end_index:
                    selected_episode = feed.entries[episode_number - 1]
                    selected_audio_url = selected_episode.enclosures[0].href
                    episode_progress = podcast_manager.check_existing_episode(feed.feed.title, selected_episode.title)
                    if episode_progress is not None:
                        print(f"Using existing progress: {episode_progress}")
                        played_progress_bytes = download_and_play(selected_audio_url, selected_episode.title, episode_progress)
                    else:
                        podcast_manager.add_episode(selected_feed_id, selected_episode.title, selected_audio_url)
                        played_progress_bytes = download_and_play(selected_audio_url, selected_episode.title, 0)

                    #podcast_manager.add_episode(selected_feed_id, selected_episode.title, selected_audio_url)
                    episode_id = podcast_manager.get_episode_id(selected_feed_id, selected_episode.title)
                    #played_progress_bytes = download_and_play(selected_audio_url, selected_episode.title, 0)
                    podcast_manager.update_progress(episode_id, played_progress_bytes) #The progress should be here
                else:
                    print("Please enter a valid index number.")
            except ValueError:
                print("Invalid input. Enter a valid index number.")
        elif choice.lower() == 'q':
            break
        else:
            print("Invalid choice. Enter 'n' to view next episodes, 'p' to play an episode, or 'q' to quit.")
    print("End of episodes.")


def display_menu():
    print("\nMenu:")
    print("1. Add new RSS feed")
    print("2. Listen to unfinished episodes")
    print("3. Browse added feeds")
    print("q. Quit")

def add_new_feed(podcast_manager):
    rss_feed_url = input("Enter the RSS feed URL (or 'q' to quit): ")
    if rss_feed_url.lower() == 'q':  # Check if 'q' is entered to quit
        return  # Exit the function

    # Validate the entered URL
    if not validators.url(rss_feed_url):
        print("Invalid URL. Please enter a valid URL.")
        return  # Exit the function if URL is invalid

    play_audio_from_feed(rss_feed_url, podcast_manager)


def listen_unfinished_episodes(podcast_manager):
    # Retrieve and display unfinished episodes
    unfinished_episodes = podcast_manager.get_unfinished_episodes()
    if unfinished_episodes:
        for idx, episode in enumerate(unfinished_episodes, start=1):
            print(f"{idx}. {episode['episode_title']}")
        try:
            choice = int(input(f"Enter the number to listen (1 - {len(unfinished_episodes)}): "))
            if 1 <= choice <= len(unfinished_episodes):
                selected_episode = unfinished_episodes[choice - 1]
                selected_audio_url = selected_episode['episode_url']
                selected_episode_progress_bytes = int(selected_episode['progress'])
                print(selected_episode_progress_bytes)
                
                # Retrieve the episode ID and play the audio
                episode_id = selected_episode['id']
                played_progress_bytes = download_and_play(selected_audio_url, selected_episode['episode_title'], selected_episode_progress_bytes)
                print("Main: ", played_progress_bytes, type(played_progress_bytes))
                podcast_manager.update_progress(episode_id, played_progress_bytes)
            else:
                print("Please enter a valid number.")
        except ValueError:
            print("Invalid input. Enter a valid number.")
    
def browse_added_feeds(podcast_manager):
    added_feeds = podcast_manager.get_added_feeds()
    if not added_feeds:
        print("No feeds added yet.")
        return

    print("Added Feeds:")
    for idx, feed in enumerate(added_feeds, start=1):
        print(f"{idx}. {feed[1]}")

    try:
        choice = int(input("Enter the number of the feed to browse: "))
        if 1 <= choice <= len(added_feeds):
            selected_feed_id = added_feeds[choice - 1][0]
            selected_feed_url = podcast_manager.get_feed_url(selected_feed_id)
            play_audio_from_feed(selected_feed_url, podcast_manager)
        else:
            print("Please enter a valid number.")
            browse_added_feeds(podcast_manager)
    except ValueError:
        print("Invalid input. Enter a valid number.")

def run_podcast_manager():
    podcast_manager = PodcastManager()
    #podcast_manager.show_feeds()
    ssl._create_default_https_context = ssl._create_unverified_context
    
    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            add_new_feed(podcast_manager)
        elif choice == '2':
            listen_unfinished_episodes(podcast_manager)
        elif choice == '3':
            browse_added_feeds(podcast_manager)      
        elif choice == 'q':
            break
        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    run_podcast_manager()
