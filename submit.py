import pandas as pd
from googleapiclient.discovery import build

def get_caption(youtube, video_id):
    try:
        captions_request = youtube.captions().list(
            part="snippet",
            videoId=video_id
        )
        captions_response = captions_request.execute()

        if captions_response['items']:
            caption_id = captions_response['items'][0]['id']
            caption_request = youtube.captions().download(
                id=caption_id,
                tfmt='srt'
            )
            return caption_request.execute().decode('utf-8')
    except Exception:
        return "No captions available"

def get_video_details(youtube, video_ids):
    video_details = []
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics,recordingDetails",
            id=",".join(video_ids[i:i+50])
        )
        response = request.execute()

        for item in response.get('items', []):
            snippet = item.get('snippet', {})
            content_details = item.get('contentDetails', {})
            statistics = item.get('statistics', {})
            recording_details = item.get('recordingDetails', {})

            captions = get_caption(youtube, item['id'])

            video_details.append({
                'Video URL': f"https://www.youtube.com/watch?v={item['id']}",
                'Title': snippet.get('title', ''),
                'Description': snippet.get('description', ''),
                'Channel Title': snippet.get('channelTitle', ''),
                'Keyword Tags': snippet.get('tags', []),
                'YouTube Video Category': snippet.get('categoryId', ''),
                'Video Published at': snippet.get('publishedAt', ''),
                'Video Duration': content_details.get('duration', ''),
                'View Count': statistics.get('viewCount', 0),
                'Comment Count': statistics.get('commentCount', 0),
                'Captions Available': 'true' if content_details.get('caption') == 'true' else 'false',
                'Caption Text': captions,
                'Location of Recording': recording_details.get('location', {})
            })
    return video_details

def search_videos(youtube, genre, max_results=100):
    video_ids = []
    next_page_token = None

    while len(video_ids) < max_results:
        request = youtube.search().list(
            part="snippet",
            maxResults=min(50, max_results - len(video_ids)),
            q=genre,
            type="video",
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get('items', []):
            video_ids.append(item['id']['videoId'])

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids

def main():
    genre = input("Enter the genre to search videos for: ")

    api_service_name = "youtube"
    api_version = "v3"
    api_key = "AIzaSyCZZo6RoEFZni17DFezDTOGccvypXu_Tkg"
    youtube = build(api_service_name, api_version, developerKey=api_key)

    print(f"Searching for videos in genre: {genre}...")
    video_ids = search_videos(youtube, genre)
    print(f"Found {len(video_ids)} videos.")

    print("Fetching video details...")
    video_details = get_video_details(youtube, video_ids)

    df = pd.DataFrame(video_details)
    df.insert(0, 'S.No', range(1, len(df) + 1))

    output_file = f"{genre}_videos.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()
