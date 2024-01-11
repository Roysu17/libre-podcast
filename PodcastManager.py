import sqlite3

class PodcastManager:
    def __init__(self, db_path="podcasts_manager.db"):
        self.db_path = db_path
        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables for feeds and episodes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feeds (
                id INTEGER PRIMARY KEY,
                rss_feed_url TEXT,
                feed_title TEXT,
                feed_description TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY,
                feed_id INTEGER,
                episode_title TEXT,
                episode_url TEXT,
                progress REAL,  -- Change INTEGER to REAL for handling non-integer values
                FOREIGN KEY(feed_id) REFERENCES feeds(id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_feed(self, rss_feed_url, feed_title, feed_description):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if the feed already exists based on RSS feed URL
        cursor.execute('SELECT id FROM feeds WHERE rss_feed_url = ?', (rss_feed_url,))
        existing_feed = cursor.fetchone()

        if existing_feed:
            pass
        else:
            cursor.execute('''
                INSERT INTO feeds (rss_feed_url, feed_title, feed_description)
                VALUES (?, ?, ?)
            ''', (rss_feed_url, feed_title, feed_description))

            print("Feed added successfully.")

        conn.commit()
        conn.close()

    def add_episode(self, feed_id, episode_title, episode_url):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if the episode already exists for the given feed
        cursor.execute('''
            SELECT id FROM episodes 
            WHERE feed_id = ? AND episode_title = ? AND episode_url = ?
        ''', (feed_id, episode_title, episode_url))

        existing_episode = cursor.fetchone()

        if existing_episode:
            print("Episode already exists. Skipping...")
        else:
            cursor.execute('''
                INSERT INTO episodes (feed_id, episode_title, episode_url, progress)
                VALUES (?, ?, ?, ?)
            ''', (feed_id, episode_title, episode_url, 0))

            print("Episode added successfully.")

        conn.commit()
        conn.close()

    def show_feeds(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM feeds')
        feeds = cursor.fetchall()

        for feed in feeds:
            print(f"Feed ID: {feed[0]}")
            print(f"RSS Feed URL: {feed[1]}")
            print(f"Feed Title: {feed[2]}")
            print(f"Feed Description: {feed[3]}\n")

            cursor.execute('SELECT * FROM episodes WHERE feed_id = ?', (feed[0],))
            episodes = cursor.fetchall()

            print("Episodes:")
            for episode in episodes:
                print(f"- ID: {episode[0]}")
                print(f"- Title: {episode[2]}")
                print(f"  URL: {episode[3]}")
                print(f"  Progress: {episode[4]} Bytes\n")

        conn.close()

    def update_progress(self, episode_id, progress):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('UPDATE episodes SET progress = ? WHERE id = ?', (progress, episode_id))
        
        if progress == 'Completed':  # Assuming 100% represents completion
            cursor.execute('DELETE FROM episodes WHERE id = ?', (episode_id,))

        conn.commit()
        conn.close()

    
    def check_existing_episode(self, feed_title, episode_title):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT episodes.progress
            FROM episodes
            JOIN feeds ON episodes.feed_id = feeds.id
            WHERE feeds.feed_title = ? AND episodes.episode_title = ?
        ''', (feed_title, episode_title))

        progress = cursor.fetchone()

        conn.close()

        if progress:
            return int(progress[0])
        else:
            return None

    
    def get_unfinished_episodes(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT episodes.id, episodes.episode_title, episodes.episode_url, episodes.progress, feeds.feed_title
            FROM episodes
            JOIN feeds ON episodes.feed_id = feeds.id
            WHERE episodes.progress != 'Completed' OR episodes.progress IS NULL
        ''')


        unfinished_episodes = cursor.fetchall()
        episode_details = [
            {
                'id': episode[0],
                'episode_title': episode[1],
                'episode_url': episode[2],
                'progress' : episode[3],
                'feed_title': episode[4]
            }
            for episode in unfinished_episodes
        ]

        conn.close()
        return episode_details
    
    def get_added_feeds(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT id, feed_title FROM feeds')
        added_feeds = cursor.fetchall()

        conn.close()
        return added_feeds

    def get_feed_url(self, feed_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT rss_feed_url FROM feeds WHERE id = ?', (feed_id,))
        feed_url = cursor.fetchone()[0]  # Fetch the URL

        conn.close()
        return feed_url

    def get_episode_id(self, feed_id, episode_title):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id FROM episodes
            WHERE feed_id = ? AND episode_title = ?
        ''', (feed_id, episode_title))

        episode_id = cursor.fetchone()
        
        conn.close()

        if episode_id:
            return episode_id[0]
        else:
            print("Episode not found.")
            return None

if __name__ == "__main__":
    # Usage example:
    podcast_manager = PodcastManager()

    # Add a feed and its details
    podcast_manager.add_feed(
        "https://feeds.megaphone.fm/STU4418364045",
        "Waveform: The MKBHD Podcast",
        "A tech podcast for the gadget lovers and tech heads among us from the mind of Marques Brownlee..."
    )

    # Add episodes to the feed
    podcast_manager.add_episode(
        1,  # Feed ID (as returned by the database)
        "Waveform Awards: Looking Back and Peeking Ahead!",
        "https://www.podtrac.com/pts/redirect.mp3/pdst.fm/e/chrt.fm/track/524GE/traffic.megaphone.fm/VMP9852531180.mp3?updated=1703266879"
    )

    # Update progress of an episode (for example, byte = 12312)
    podcast_manager.update_progress(1, 12312)  # Use the correct episode ID from the database
    print("One")
    print(podcast_manager.get_unfinished_episodes())

    podcast_manager.update_progress(1, 'Completed')
    print("Two")
    print(podcast_manager.get_unfinished_episodes())

    podcast_manager.show_feeds()
