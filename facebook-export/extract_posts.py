#!/usr/bin/env python3
"""Extract all posts from a Facebook page using the GraphQL API."""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

PAGE_ID = "61569612563299"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

COOKIES = os.environ.get("FB_COOKIES", "")
FB_DTSG = os.environ.get("FB_DTSG", "")
LSD = os.environ.get("FB_LSD", "")
USER_ID = os.environ.get("FB_USER_ID", "")
DOC_ID = "34812124858433456"  # ProfileCometTimelineFeedRefetchQuery

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": COOKIES,
    "Referer": f"https://www.facebook.com/people/Little-Black-Horse-Barefoot-Trims/{PAGE_ID}/",
    "x-fb-friendly-name": "ProfileCometTimelineFeedRefetchQuery",
    "x-fb-lsd": LSD,
    "Origin": "https://www.facebook.com",
    "sec-fetch-site": "same-origin",
}


def build_variables(cursor=None):
    variables = {
        "afterTime": None,
        "beforeTime": None,
        "count": 3,
        "cursor": cursor,
        "feedLocation": "TIMELINE",
        "feedbackSource": 0,
        "focusCommentID": None,
        "memorializedSplitTimeFilter": None,
        "omitPinnedPost": True,
        "postedBy": {"group": "OWNER"},
        "privacy": None,
        "privacySelectorRenderLocation": "COMET_STREAM",
        "referringStoryRenderLocation": None,
        "renderLocation": "timeline",
        "scale": 2,
        "stream_count": 1,
        "taggedInOnly": None,
        "trackingCode": None,
        "useDefaultActor": False,
        "id": PAGE_ID,
        "__relay_internal__pv__GHLShouldChangeAdIdFieldNamerelayprovider": True,
        "__relay_internal__pv__GHLShouldChangeSponsoredDataFieldNamerelayprovider": True,
        "__relay_internal__pv__CometFeedStory_enable_post_permalink_white_space_clickrelayprovider": False,
        "__relay_internal__pv__CometUFICommentActionLinksRewriteEnabledrelayprovider": False,
        "__relay_internal__pv__CometUFICommentAvatarStickerAnimatedImagerelayprovider": False,
        "__relay_internal__pv__IsWorkUserrelayprovider": False,
        "__relay_internal__pv__TestPilotShouldIncludeDemoAdUseCaserelayprovider": False,
        "__relay_internal__pv__FBReels_deprecate_short_form_video_context_gkrelayprovider": True,
        "__relay_internal__pv__FBReels_enable_view_dubbed_audio_type_gkrelayprovider": True,
        "__relay_internal__pv__CometImmersivePhotoCanUserDisable3DMotionrelayprovider": False,
        "__relay_internal__pv__WorkCometIsEmployeeGKProviderrelayprovider": False,
        "__relay_internal__pv__IsMergQAPollsrelayprovider": False,
        "__relay_internal__pv__FBReelsMediaFooter_comet_enable_reels_ads_gkrelayprovider": True,
        "__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider": False,
        "__relay_internal__pv__CometUFICommentAutoTranslationTyperelayprovider": "ORIGINAL",
        "__relay_internal__pv__CometUFIShareActionMigrationrelayprovider": True,
        "__relay_internal__pv__CometUFISingleLineUFIrelayprovider": False,
        "__relay_internal__pv__CometUFI_dedicated_comment_routable_dialog_gkrelayprovider": True,
        "__relay_internal__pv__FBReelsIFUTileContent_reelsIFUPlayOnHoverrelayprovider": True,
        "__relay_internal__pv__GroupsCometGYSJFeedItemHeightrelayprovider": 206,
        "__relay_internal__pv__ShouldEnableBakedInTextStoriesrelayprovider": False,
        "__relay_internal__pv__StoriesShouldIncludeFbNotesrelayprovider": False,
    }
    return json.dumps(variables)


def make_request(cursor=None):
    data = {
        "av": USER_ID,
        "__user": USER_ID,
        "__a": "1",
        "fb_dtsg": FB_DTSG,
        "jazoest": "25385",
        "lsd": LSD,
        "__comet_req": "15",
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "ProfileCometTimelineFeedRefetchQuery",
        "server_timestamps": "true",
        "variables": build_variables(cursor),
        "doc_id": DOC_ID,
    }

    encoded = urllib.parse.urlencode(data)
    req = urllib.request.Request(
        "https://www.facebook.com/api/graphql/",
        data=encoded.encode(),
        headers=HEADERS,
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        raw = resp.read().decode("utf-8")
        return raw


def extract_text_and_images(data):
    """Recursively extract text content and image URLs from the GraphQL response."""
    posts = []
    images = set()

    def walk(obj, path=""):
        if isinstance(obj, dict):
            # Look for story/post text
            if "message" in obj and isinstance(obj["message"], dict):
                text = obj["message"].get("text", "")
                if text:
                    post = {"text": text}
                    # Try to get timestamp
                    if "creation_time" in obj:
                        post["timestamp"] = obj["creation_time"]
                    # Try to get post URL
                    if "url" in obj:
                        post["url"] = obj["url"]
                    posts.append(post)

            # Look for images
            if "uri" in obj and isinstance(obj.get("uri"), str):
                uri = obj["uri"]
                if "scontent" in uri and uri.endswith((".jpg", ".png", ".jpeg")) or "scontent" in uri:
                    images.add(uri)
            if "image" in obj and isinstance(obj["image"], dict):
                uri = obj["image"].get("uri", "")
                if uri and "scontent" in uri:
                    images.add(uri)

            for k, v in obj.items():
                walk(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]")

    walk(data)
    return posts, images


def extract_cursor(data):
    """Find the next pagination cursor in the response."""
    cursors = []

    def walk(obj):
        if isinstance(obj, dict):
            if "page_info" in obj:
                pi = obj["page_info"]
                if isinstance(pi, dict) and pi.get("has_next_page"):
                    end_cursor = pi.get("end_cursor")
                    if end_cursor:
                        cursors.append(end_cursor)
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(data)
    return cursors[-1] if cursors else None


def main():
    all_posts = []
    all_images = set()
    cursor = None
    page_num = 0
    max_pages = 30  # safety limit

    print(f"Extracting posts from page {PAGE_ID}...")
    print()

    while page_num < max_pages:
        page_num += 1
        print(f"--- Request {page_num} (cursor={'initial' if cursor is None else 'yes'}) ---")

        try:
            raw = make_request(cursor)
        except Exception as e:
            print(f"  Request failed: {e}")
            break

        # Save raw response for debugging
        raw_path = os.path.join(OUTPUT_DIR, f"raw_response_{page_num}.json")
        with open(raw_path, "w") as f:
            f.write(raw)

        # Facebook returns multiple JSON objects separated by newlines
        parts = raw.strip().split("\n")
        all_data = []
        for part in parts:
            part = part.strip()
            if part:
                try:
                    all_data.append(json.loads(part))
                except json.JSONDecodeError:
                    pass

        new_posts = []
        new_images = set()
        next_cursor = None

        for data in all_data:
            posts, images = extract_text_and_images(data)
            new_posts.extend(posts)
            new_images.update(images)
            c = extract_cursor(data)
            if c:
                next_cursor = c

        # Deduplicate posts by text
        seen_texts = {p["text"] for p in all_posts}
        unique_new = [p for p in new_posts if p["text"] not in seen_texts]

        all_posts.extend(unique_new)
        all_images.update(new_images)

        print(f"  Found {len(unique_new)} new posts, {len(new_images)} images")
        print(f"  Total: {len(all_posts)} posts, {len(all_images)} images")

        for p in unique_new:
            preview = p["text"][:100].replace("\n", " ")
            ts = p.get("timestamp", "?")
            print(f"    [{ts}] {preview}...")

        if not next_cursor:
            print("\n  No more pages.")
            break

        cursor = next_cursor
        time.sleep(1)  # be polite

    # Save results
    print(f"\n=== DONE: {len(all_posts)} posts, {len(all_images)} unique images ===\n")

    # Save posts
    posts_path = os.path.join(OUTPUT_DIR, "all_posts.json")
    with open(posts_path, "w") as f:
        json.dump(all_posts, f, indent=2, ensure_ascii=False)
    print(f"Saved posts to {posts_path}")

    # Save as readable markdown
    md_path = os.path.join(OUTPUT_DIR, "all_posts.md")
    with open(md_path, "w") as f:
        f.write(f"# All Posts - Little Black Horse Barefoot Trims\n\n")
        f.write(f"Total: {len(all_posts)} posts\n\n---\n\n")
        for i, post in enumerate(all_posts, 1):
            ts = post.get("timestamp", "")
            if ts:
                from datetime import datetime
                try:
                    dt = datetime.fromtimestamp(ts)
                    ts_str = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    ts_str = str(ts)
            else:
                ts_str = "Unknown date"
            url = post.get("url", "")
            f.write(f"## Post {i} ({ts_str})\n\n")
            if url:
                f.write(f"**Link:** {url}\n\n")
            f.write(post["text"])
            f.write("\n\n---\n\n")
    print(f"Saved readable posts to {md_path}")

    # Save image URLs
    imgs_path = os.path.join(OUTPUT_DIR, "all_image_urls.txt")
    with open(imgs_path, "w") as f:
        for url in sorted(all_images):
            f.write(url + "\n")
    print(f"Saved {len(all_images)} image URLs to {imgs_path}")


if __name__ == "__main__":
    main()
