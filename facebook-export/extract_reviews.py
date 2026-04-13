#!/usr/bin/env python3
"""Extract all reviews from a Facebook page using the GraphQL API."""

import json
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime

PAGE_ID = "61569612563299"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

COOKIES = os.environ.get("FB_COOKIES", "")
FB_DTSG = os.environ.get("FB_DTSG", "")
LSD = os.environ.get("FB_LSD", "")
USER_ID = os.environ.get("FB_USER_ID", "")
DOC_ID = "26706360375718971"  # ProfileCometReviewsFeedRefetchQuery

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": COOKIES,
    "Referer": f"https://www.facebook.com/profile.php?id={PAGE_ID}&sk=reviews",
    "x-fb-friendly-name": "ProfileCometReviewsFeedRefetchQuery",
    "x-fb-lsd": LSD,
    "Origin": "https://www.facebook.com",
    "sec-fetch-site": "same-origin",
}


def build_variables(cursor=None):
    variables = {
        "count": 10,
        "cursor": cursor,
        "feedLocation": "PAGE_SURFACE_RECOMMENDATIONS",
        "feedbackSource": 0,
        "focusCommentID": None,
        "privacySelectorRenderLocation": "COMET_STREAM",
        "referringStoryRenderLocation": None,
        "renderLocation": "timeline",
        "scale": 2,
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
        "fb_api_req_friendly_name": "ProfileCometReviewsFeedRefetchQuery",
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


def extract_reviews(data):
    """Recursively extract review data from the GraphQL response."""
    reviews = []
    comments = []

    def walk(obj, path="", depth=0):
        if not isinstance(obj, (dict, list)) or depth > 30:
            return

        if isinstance(obj, dict):
            # Detect a review/recommendation node
            # Reviews have "recommendation_type" field (POSITIVE/NEGATIVE)
            if "recommendation_type" in obj:
                review = {
                    "recommendation": obj.get("recommendation_type"),
                }
                # Get the message
                if "message" in obj and isinstance(obj["message"], dict):
                    review["text"] = obj["message"].get("text", "")
                # Get creation time
                if "creation_time" in obj:
                    review["timestamp"] = obj["creation_time"]
                # Get author
                if "author" in obj and isinstance(obj["author"], dict):
                    author = obj["author"]
                    review["author"] = author.get("name", "")
                    review["author_url"] = author.get("url", "")
                # Get URL
                if "url" in obj:
                    review["url"] = obj["url"]
                if review.get("text") or review.get("recommendation"):
                    reviews.append(review)

            # Also look for story nodes that contain review data
            if obj.get("__typename") == "Story" and "message" in obj:
                msg = obj["message"]
                if isinstance(msg, dict) and msg.get("text"):
                    # Check if this is under a review context
                    pass

            # Look for comment/reply data (page owner responses)
            if "body" in obj and isinstance(obj["body"], dict) and "text" in obj["body"]:
                comment = {"text": obj["body"]["text"]}
                if "author" in obj and isinstance(obj["author"], dict):
                    comment["author"] = obj["author"].get("name", "")
                if "created_time" in obj:
                    comment["timestamp"] = obj["created_time"]
                comments.append(comment)

            for k, v in obj.items():
                walk(v, f"{path}.{k}", depth + 1)

        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]", depth + 1)

    walk(data)
    return reviews, comments


def extract_cursor(data):
    """Find the next pagination cursor in the response."""
    cursors = []

    def walk(obj, depth=0):
        if depth > 20:
            return
        if isinstance(obj, dict):
            if "page_info" in obj:
                pi = obj["page_info"]
                if isinstance(pi, dict) and pi.get("has_next_page"):
                    end_cursor = pi.get("end_cursor")
                    if end_cursor:
                        cursors.append(end_cursor)
            for v in obj.values():
                walk(v, depth + 1)
        elif isinstance(obj, list):
            for v in obj:
                walk(v, depth + 1)

    walk(data)
    return cursors[-1] if cursors else None


def main():
    all_reviews = []
    all_comments = []
    seen_texts = set()
    cursor = None
    page_num = 0
    max_pages = 10

    print(f"Extracting reviews from page {PAGE_ID}...")
    print()

    while page_num < max_pages:
        page_num += 1
        print(f"--- Request {page_num} (cursor={'initial' if cursor is None else 'yes'}) ---")

        try:
            raw = make_request(cursor)
        except Exception as e:
            print(f"  Request failed: {e}")
            break

        # Save raw response
        raw_path = os.path.join(OUTPUT_DIR, f"raw_reviews_{page_num}.json")
        with open(raw_path, "w") as f:
            f.write(raw)

        # Parse (Facebook returns multiple JSON objects per line)
        parts = raw.strip().split("\n")
        all_data = []
        for part in parts:
            part = part.strip()
            if part:
                try:
                    all_data.append(json.loads(part))
                except json.JSONDecodeError:
                    pass

        new_reviews = []
        new_comments = []
        next_cursor = None

        for data in all_data:
            reviews, comments = extract_reviews(data)
            new_reviews.extend(reviews)
            new_comments.extend(comments)
            c = extract_cursor(data)
            if c:
                next_cursor = c

        # Deduplicate reviews
        unique_new = []
        for r in new_reviews:
            key = r.get("text", "") + r.get("author", "")
            if key and key not in seen_texts:
                seen_texts.add(key)
                unique_new.append(r)

        all_reviews.extend(unique_new)
        all_comments.extend(new_comments)

        print(f"  Found {len(unique_new)} new reviews, {len(new_comments)} comments")
        print(f"  Total: {len(all_reviews)} reviews")

        for r in unique_new:
            author = r.get("author", "Unknown")
            rec = r.get("recommendation", "?")
            preview = r.get("text", "")[:80].replace("\n", " ")
            print(f"    [{rec}] {author}: {preview}")

        if not next_cursor:
            print("\n  No more pages.")
            break

        cursor = next_cursor
        time.sleep(1)

    # Save results
    print(f"\n=== DONE: {len(all_reviews)} reviews ===\n")

    # Save JSON
    reviews_json = os.path.join(OUTPUT_DIR, "all_reviews.json")
    with open(reviews_json, "w") as f:
        json.dump(all_reviews, f, indent=2, ensure_ascii=False)
    print(f"Saved to {reviews_json}")

    # Save readable markdown
    reviews_md = os.path.join(OUTPUT_DIR, "all_reviews.md")
    with open(reviews_md, "w") as f:
        f.write("# Reviews - Little Black Horse Barefoot Trims\n\n")
        f.write(f"**Total: {len(all_reviews)} reviews**\n\n---\n\n")
        for i, r in enumerate(all_reviews, 1):
            author = r.get("author", "Unknown")
            rec = r.get("recommendation", "Unknown")
            ts = r.get("timestamp", "")
            url = r.get("url", "")
            text = r.get("text", "(no text)")

            ts_str = "Unknown date"
            if ts:
                try:
                    dt = datetime.fromtimestamp(ts)
                    ts_str = dt.strftime("%Y-%m-%d")
                except:
                    ts_str = str(ts)

            rec_str = "Recommends" if rec == "POSITIVE" else ("Doesn't recommend" if rec == "NEGATIVE" else rec)

            f.write(f"### {i}. {author} - {rec_str}\n")
            f.write(f"**Date:** {ts_str}\n\n")
            if url:
                f.write(f"**Link:** {url}\n\n")
            f.write(f"{text}\n\n---\n\n")

    print(f"Saved to {reviews_md}")


if __name__ == "__main__":
    main()
