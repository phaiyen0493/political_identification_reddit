import json
import os
import praw
import datetime as dt
from pprint import pprint

# Maximum number of posts to retrieve with at one time. This is for every call,
# actual files pulled will be much higher!
PULL_LIMIT = 100

# Stats counters
STATS_USER_FILE_COUNT = 0
STATS_POST_COUNT = 0
STATS_EARLIEST = 999999999999
STATS_LATEST = 0

REPUBLICAN_SUBREDDITS = [
    'republicans'
]
DEMOCRAT_SUBREDDITS = [
    'democrats'
]
POLITICAL_SUBREDDITS = [
    'politics',
    'republicans',
    'democrats'
]

# Get client's info to connect to Reddit
with open('client_info.json', 'r') as f:
    client_info = json.loads(f.read())
# Reddit API instance
print("Connecting to Reddit...")
REDDIT = praw.Reddit(client_id=client_info['client_id'],
                     client_secret=client_info['client_secret'],
                     user_agent=client_info['user_agent'],
                     username=client_info['username'],
                     password=client_info['password'])


def users_from_subreddit(subreddit):
    '''Get users that post to a given subreddit'''
    # Users list to return
    redditors = []
    # Submissions from subreddit
    new_submissions = subreddit.new(limit=PULL_LIMIT)
    hot_submissions = subreddit.hot(limit=PULL_LIMIT)

    def append_redditors(submissions):
        '''Nested function that appends redditors to the return list'''
        i = 1
        for submission in submissions:
            print(f"Processing submission #{i}/{PULL_LIMIT}")
            try:
                print(f'{submission.author.id}: {submission.author.name}')
                redditors.append(
                    (submission.author.id, submission.author.name))
            except:
                print("No author found for submission...")
            i += 1
            j = 1
            for comment in submission.comments:
                print(f"Processing comment #{j}/{submission.num_comments}")
                try:
                    print(f'{comment.author.id}: {comment.author.name}')
                    redditors.append((comment.author.id, comment.author.name))
                except:
                    print("No author found for submission...")
                j += 1
    print("Processing new submissions")
    append_redditors(new_submissions)
    print("Processing hot submissions")
    append_redditors(hot_submissions)
    return redditors


REDDITORS = []
print("Obtaining republican redditors' information")
for subreddit in REPUBLICAN_SUBREDDITS:
    REDDITORS += users_from_subreddit(REDDIT.subreddit(subreddit))
print("Obtaining democrat redditors' information")
for subreddit in DEMOCRAT_SUBREDDITS:
    REDDITORS += users_from_subreddit(REDDIT.subreddit(subreddit))
# Create a map from redditor ids to redditor info including names
REDDITOR_MAP = {}
for redditor in REDDITORS:
    rid, rname = redditor
    REDDITOR_MAP[rid] = {
        "name": rname,
        "posts": [],
        "republican_score": 0,
        "democrat_score": 0
    }

# Loop through all the redditors in the map
i = 1
for k, v in REDDITOR_MAP.items():
    print(f'Processing redditor #{i}/{len(REDDITOR_MAP)}')
    # For each redditor, we want to access a Redditor object, which we do using their name
    redditor = praw.models.Redditor(REDDIT, v['name'])
    # We will want to process each of their submissions
    for submission in redditor.submissions.new(limit=PULL_LIMIT):
        # Extract info from the submissions
        subreddit = submission.subreddit.display_name
        # Only include political posts
        if subreddit in POLITICAL_SUBREDDITS:
            title = submission.title
            try:
                text = submission.self_text
            except:
                text = ""
            # UPDATE STATS
            t = submission.created_utc
            if t < STATS_EARLIEST:
                STATS_EARLIEST = t
            if t > STATS_LATEST:
                STATS_LATEST = t
            STATS_POST_COUNT += 1
            # Add the user's posts to their collection of posts
            v['posts'].append(
                {'subreddit': subreddit, 'text': title + '\n' + text, 'time': t})
            # Score the user based on where they post
            if subreddit in REPUBLICAN_SUBREDDITS:
                v['republican_score'] += 1
            if subreddit in DEMOCRAT_SUBREDDITS:
                v['democrat_score'] += 1
    # Also process every comment
    for comment in redditor.comments.new(limit=PULL_LIMIT):
        # Extract info from the submissions
        subreddit = comment.subreddit.display_name
        # Only include political posts
        if subreddit in POLITICAL_SUBREDDITS:
            text = comment.body
            # UPDATE STATS
            t = comment.created_utc
            if t < STATS_EARLIEST:
                STATS_EARLIEST = t
            if t > STATS_LATEST:
                STATS_LATEST = t
            STATS_POST_COUNT += 1
            # Add the user's posts to their collection of posts
            v['posts'].append(
                {'subreddit': subreddit, 'text': text, 'time': t})
            # Score the user based on where they post
            if subreddit in REPUBLICAN_SUBREDDITS:
                v['republican_score'] += 1
            if subreddit in DEMOCRAT_SUBREDDITS:
                v['democrat_score'] += 1
    i += 1

pprint(REDDITOR_MAP)

print("SAVING USERS!")
for k, v in REDDITOR_MAP.items():
    netScore = v['republican_score'] - v['democrat_score']
    # If score is sufficiently right, save to republicans folder
    if netScore >= 3:
        with open(f'./republican_users/{k}.json', 'w') as f:
            f.write(json.dumps(v))
        # Update stats
        STATS_USER_FILE_COUNT += 1
    # If score is sufficiently left, save to democrats folder
    elif netScore <= -3:
        with open(f'./democrat_users/{k}.json', 'w') as f:
            f.write(json.dumps(v))
        # Update stats
        STATS_USER_FILE_COUNT += 1

print(f"Number of User Files: {STATS_USER_FILE_COUNT}")
print(f"Number of Posts: {STATS_POST_COUNT}")
print(f"UTC Most Recent Post: {STATS_LATEST}")
print(f"UTC Oldest Posts: {STATS_EARLIEST}")
