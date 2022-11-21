"""
Birdwatch snapshots a profile page when given a URL or an exported list of `following` from the official Twitter exporter.

Many thanks to: https://www.scrapingbee.com/blog/web-scraping-twitter/
for the inspiration.

Major adjustments to make UX a lot smoother.

By: ProgrammingIncluded
"""
import re
import os
import json
import random
import argparse
import shutil
import time

from dataclasses import dataclass

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

LOGO = """
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,'''''''',,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,''',;;:;;:cllollllccc:;,'.',,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,'';:codxkkkkkkkkkkkkkkkkkkxocc:;',,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,;,'';coxkkkkkkkkkkkkkkkkkkkkkkkkkkkkxl:,',,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,'.,:dkkkkkkkkkkkkkkkkkxocdkkkkkkkkkkxdxxd:,',,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,'.';lxkkkkkkkkkolxkkkkkkkkl;:okkkkkkkkxxxddxxo;.',,,,,,,,,,,,,,,,,,
,,,,,,,,'...,:cdxxxkkkkkkkkx;;xkkkkkkkko;cooxkkkkkkkxdocldxdl,',,,,,,,,,,,,,,,,,
,,,,,,,,,. .',,;:oxkkkkkkkxl::dkkkkkkkko,cOkcdkxxxkkkxl;,;:lol:,,,,,,,,,,,,,,,,,
,,,,,,,,,,,''..:oxkkkkxdxkocl,:kkkkkxxkl,:ONklokxodkkkxc,;;;:coc,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,;oxkkkkkkolxx:dk::okkkkxxkl,cONNOccddcokkkl':lcccldc,,,,,,,,,,,,,,,
,,,,,,,,,,,.:xkxxkkkkxllo:;kkodcoxkkxddc';ccll:..,,'lkkl,:lcclloo,',,,,,,,,,,,,,
,,,,,,,,,'.,dxxxxkkkkdlxd,':;':c:oxkkc,,.;:,'....;. .cxc,lo:;cloo;.',,,,,,,,,,,,
,,,,,,,,'.;ooldxxxkkkoll;;c:'.  ,l:cx:.'.;'     'Ox.':;;:oo:;ollol;',,,,,,,,,,,,
,,,,,,,'..''''cxdxkkko,.lXx.    ;00xo:oKOx'     ;XO'lk:cooo;dNdcoodl,,,;,,,,,,,,
,,,,,,,,''',,',oc;dkkl..kWo     ;XWWWXNWMNo    .xWOdOocoool;d0oloodxdc,',,,,,,,,
,,,,,,,,,,,,,,',..;dkl..dWO.    lNMWWWWWWWXl..,dNWWXdcloooc,:lloooodxxdc'.,,,,,,
,,,,,,,,,,,,,,;,.',,::coONNc   :KWWWWWWWWWWWXKKXNNXdcloooo;,looooooooddxd:.',,,,
,,,,,,,,,,,,,,,;,.,;'.'kWWWKdokXWWWWNNWWWWWWWWNNNXd:looooc,;clooolcooo::ox:.,;,,
,,,,,,,,,,,,,,,'.';;;.;0NXXNNWWWWWWWXNWWWWWWWWWXKd:looooc,:c,:doo;.,ll',oo;.,;,,
,,,,,,,,,,,,''''',;:;..cxk0KXNNNNNXXNNNKOkxollcc,'cooooc,:oc.'odl'.',,.;o;.',,,,
,,,,,,,,,,,...''.':c;';c;,,:ool:,,,;ldxl,',;,;lc';oool;;:c;...:l,.,;;'',,',,,,,,
,,,,,,,,,,,,,,,,,',;',::,..,lc'.......;oddkXKd;..;l:,.',,'',;,''.'''...',,,,,,,,
,,,,,,,,,,,,,,,,,,'...   ..,dxd:,.. .:xkkONWWWO;'clc'.......,;::cll.    .,,,,,,,
,,,,,,,,,,,,,,,,,,.,ooc'...'O0:'...  ':okOXWWWWl;o;.    ....kOddo0K,    .,,,,,,,
,,,,,,,,,,,,,,,,'.'xWX0Od, .d:.. ......;dk0kxOO'.'.     ...:xc,;;k0,     ',,,,,,
,,,,,,,,,,,,,,,. ;xONWXOkl..d:.  ,::,. ,oodd,..    .     .xXX0O00XX;     .;,,,,,
,,,,,,,,,,,,,,,. ;OOXWXk:'..dk,.  .. .,kXOOO,      .     .kWNWWWWWNc     .,,,,,,
,,,,,,,,,,,,,,,. .xkOK0k, .'lOkc,'..;oO00xOK,      .      dWWWWWWNWd.    .,,,,,,
,,,,,,,,,,,,,,,'. ;kkxxko.'xOOOOOOkOOOOOOdOK:. .;;..      :XWWWWNXKx.    .,,,,,,
,,,,,,,,,,,,,,,,,..;odk00d,'d00KKKK0KKK0OkKKdxxoo, .      .;lccc:;,'....',,,,,,,
,,,,,,,,,,,,,,,,,,;';oxkxxl..looooooooollll:'..   ''........''',,,;;,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,;,'',.                   ..lXO;,;,;,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,,,,......         ...',,;xKo',,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,;;,,,,,''',,,,,,,,,,;;'',,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,;,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

"""
TITLE = """
 ____  _         _               _       _     
|  _ \(_)       | |             | |     | |    
| |_) |_ _ __ __| |_      ____ _| |_ ___| |__  
|  _ <| | '__/ _` \ \ /\ / / _` | __/ __| '_ \ 
| |_) | | | | (_| |\ V  V / (_| | || (__| | | |
|____/|_|_|  \__,_| \_/\_/ \__,_|\__\___|_| |_|
                                               
"""

SCRAPE_N_TWEETS = 20
IS_DEBUG = False

@dataclass(init=True, repr=True, unsafe_hash=True)
class Tweet:
    id: str
    tag_text: str
    name: str
    tweet_text: str
    retweet_count: str
    handle: str
    timestamp: str
    like_count: str
    reply_count: str
    potential_boost: bool

def print_debug(text):
    if IS_DEBUG:
        print(text)

def ensures_or(f, otherwise="NULL"):
    try:
        return f()
    except Exception as e:
        print_debug("Could not obtain using {} instead. Error: {}".format(otherwise, str(e)))

    return otherwise

def remove_elements(driver, elements, remove_parent=True):
    elements = ["'{}'".format(v) for v in elements]
    if remove_parent:
        # Some weird elements are better removing parent to
        # remove render artifacts.
        driver.execute_script("""
        const values = [{}];
        for (let i = 0; i < values.length; ++i) {{
            var element = document.querySelector(`[data-testid='${{values[i]}}']`);
            if (element)
                element.parentNode.parentNode.removeChild(element.parentNode);
        }}
        """.format(",".join(elements)))

    driver.execute_script("""
    const values = [{}];
    for (let i = 0; i < values.length; ++i) {{
        var element = document.querySelector(`[data-testid='${{values[i]}}']`);
        if (element)
            element.parentNode.removeChild(element);
    }}
    """.format(",".join(elements)))

def calc_average(percentage):
    def _func(lst):
        if len(lst) < 4:
            return sum(lst) / len(lst)
    
        cut_off = int(len(lst) * percentage)
        s = sorted(lst)[cut_off:len(lst) - cut_off]
        return sum(s) / len(s)
    return _func

def window_average(window):
    def _func(lst):
        v = lst[:-min(window, len(lst))]
        if len(v) == 0:
            return lst[-1]
        return sum(v) / len(v)
    return _func


def constant(const):
    def _func(lst):
        return const
    return _func

def remove_ads(driver):
    return driver.execute_script("""
        var elems = document.querySelectorAll("*"),
            res = Array.from(elems).find(v => v.textContent == 'Promoted Tweet');

        if (res) {
            let p = res.parentNode.parentNode.parentNode;
            p.innerHTML="";
            return true;
        }
        return false;
    """)


def fetch_html(driver, url, fpath, load_times, offset_func, force=False, number_posts_to_cap=SCRAPE_N_TWEETS, bio_only=False):
    driver.get(url)
    state = ""
    while state != "complete":
        print("loading not complete")
        time.sleep(random.uniform(3, 5))
        state = driver.execute_script("return document.readyState")

    WebDriverWait(driver, 30).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '[data-testid="tweet"]')))

    # Remove initial popups.
    remove_elements(driver, ["sheetDialog", "confirmationSheetDialog", "mask"])

    # delete bottom element
    remove_elements(driver, ["BottomBar"])

    metadata = {}
    metadata["bio"] = ensures_or(lambda: driver.find_element(By.CSS_SELECTOR,'div[data-testid="UserDescription"]').text)
    metadata["name"], metadata["username"] = ensures_or(lambda: driver.find_element(By.CSS_SELECTOR,'div[data-testid="UserName"]').text.split('\n'), ("NULL", "NULL"))
    metadata["location"] = ensures_or(lambda: driver.find_element(By.CSS_SELECTOR,'span[data-testid="UserLocation"]').text)
    metadata["website"] = ensures_or(lambda: driver.find_element(By.CSS_SELECTOR,'a[data-testid="UserUrl"]').text)
    metadata["join_date"] = ensures_or(lambda: driver.find_element(By.CSS_SELECTOR,'span[data-testid="UserJoinDate"]').text)
    metadata["following"] = ensures_or(lambda: driver.find_element(By.XPATH, "//span[contains(text(), 'Following')]/ancestor::a/span").text) 
    metadata["followers"] = ensures_or(lambda: driver.find_element(By.XPATH, "//span[contains(text(), 'Followers')]/ancestor::a/span").text)

    if metadata.get("username", "NULL") == "NULL":
        raise RuntimeError("Fatal error, unable to resolve username {}".format(metadata))

    # Change the fpath and resolve username
    username = metadata["username"]
    username = username[1:] if username.startswith("@") else username

    fpath = os.path.join(fpath, username) 
    if not force and os.path.exists(fpath):
        print("Folder already exists, skipping: {}".format(fpath))
        return
    elif force and os.path.exists(fpath):
        shutil.rmtree(fpath)

    os.makedirs(fpath)

    # Force utf-8
    # Save a copy of the metadata
    with open(os.path.join(fpath, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False)

    # Save a screen shot of the bio
    driver.save_screenshot(os.path.join(fpath, "profile.png"))

    if bio_only:
        return

    # Create tweets folder
    tweets_path = os.path.join(fpath, "tweets")
    os.makedirs(tweets_path)

    tweets_metadata = []
    id_tracker = 0
    last_id = id_tracker
    last_id_count = 0
    tweets_tracker = set()
    boosted_tracker = set()
    estimated_height = 0
    height_diffs = []
    div_track = set()
    try:
        last_height = 0
        new_height = 0
        time.sleep(random.uniform(load_times, load_times + 2))
        while True:
            if id_tracker >= number_posts_to_cap - 1:
                break
            elif last_id_count > 5:
                print("No more data to load?")
                break

            if last_id == id_tracker:
                last_id_count += 1
            else:
                last_id = id_tracker
                last_id_count = 0

            tweets = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
            for tweet in tweets:
                # Try to scroll there first and retry 2x load times before giving up.
                # Then bump up global load times by one.
                try:
                    div_id = tweet.get_attribute("aria-labelledby")
                    if div_id in div_track:
                        continue

                    div_track.add(div_id)
                    driver.execute_script("return arguments[0].scrollIntoView();", tweet)
                    driver.execute_script("window.scrollTo(0, window.pageYOffset - 50);")

                    ad = remove_ads(driver)
                    if ad:
                        continue
                except:
                    continue

                height = float(driver.execute_script("return window.scrollTop || window.pageYOffset;"))
                if height < estimated_height:
                    continue
                height_diffs.append(height - estimated_height)
                estimated_height = height

                tm = {"id": id_tracker}
                tm["tag_text"] = ensures_or(lambda: tweet.find_element(By.CSS_SELECTOR,'div[data-testid="User-Names"]').text)
                try:
                    tm["name"], tm["handle"], _, tm["timestamp"] = ensures_or(lambda: tm["tag_text"].split('\n'), tuple(["UKNOWN" for _ in range(4)]))
                except Exception as e:
                    tm["name"], tm["handle"], tm["timestamp"] = tm["tag_text"], "ERR", "ERR"
    
                tm["tweet_text"] = ensures_or(lambda: tweet.find_element(By.CSS_SELECTOR,'div[data-testid="tweetText"]').text)
                tm["retweet_count"] = ensures_or(lambda: tweet.find_element(By.CSS_SELECTOR,'div[data-testid="retweet"]').text)
                tm["like_count"] = ensures_or(lambda: tweet.find_element(By.CSS_SELECTOR,'div[data-testid="like"]').text)
                tm["reply_count"] = ensures_or(lambda: tweet.find_element(By.CSS_SELECTOR,'div[data-testid="reply"]').text)

                if tm["tweet_text"] != "NULL":
                    if tm["tweet_text"] in boosted_tracker:
                        # We need to go back in time to find the boosted post!
                        for t in tweets_metadata:
                            if t["tweet_text"] == tm["tweet_text"]:
                                t["potential_boost"] = True
                                break

                    tm["potential_boost"] = False
                    boosted_tracker.add(tm["tweet_text"])
                else:
                    tm["potential_boost"] = False

                dtm = Tweet(**tm)
                if dtm in tweets_tracker:
                    print("ARLEAD {}".format(dtm))
                    continue

                try:
                    # Try to remove elements before screenshot
                    remove_elements(driver, ["sheetDialog", "confirmationSheetDialog", "mask"])
                    tweet.screenshot(os.path.join(tweets_path, "{}.png".format(id_tracker)))
                except Exception as e:
                    # Failure to screenshot maybe because the tweet is too stale. Skip for now.
                    continue

                id_tracker += 1
                tweets_metadata.append(tm)
                tweets_tracker.add(dtm)

                if id_tracker > number_posts_to_cap:
                    break
    
            # Scroll!
            driver.execute_script("window.scrollTo(0, {});".format(estimated_height + offset_func(height_diffs)))
            time.sleep(random.uniform(load_times, load_times + 2))
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    except selenium.common.exceptions.StaleElementReferenceException as e:
        print("Tweet limit reached, for {} unable to fetch more data. Authentication is required.".format(username))
        print("Or you can try to bump loading times.")
        raise e
    except Exception as e:
        raise e
    finally:
        # Dump all metadata
        with open(os.path.join(tweets_path, "tweets.json"), "w", encoding="utf-8") as f:
            json.dump(tweets_metadata, f, ensure_ascii=False)

def parse_args():
    parser = argparse.ArgumentParser(description="Process Twitter Account Metadata")
    parser.add_argument("--force", "-f", help="Force re-download everything. WARNING, will delete outputs.", action="store_true")
    parser.add_argument("--posts", "-p", help="Max number of posts to screenshot.", default=SCRAPE_N_TWEETS, type=int)
    parser.add_argument("--bio-only", "-b", help="Only store bio, no snapshots or tweets.", action="store_true")
    parser.add_argument("--debug", help="Print debug output.", action="store_true")
    parser.add_argument("--login", help="Prompt user login to remove limits / default filters. USE AT OWN RISK.", action="store_true")
    parser.add_argument("--scroll-load-time", "-s", help="Number of seconds (float). The higher, the stabler the fetch.", default=5, type=int)
    parser.add_argument("--scroll-algorithm", help="Type of algorithm to calculate scroll offset.", choices=["percentile", "window", "constant"], default="window")
    parser.add_argument("--scroll-value", default=5, type=float, help=("Value used by --scroll-algorithm."
                                                                        "If percentile, percentage of percentile calculated. "
                                                                        "If window, the size of window average."
                                                                        "If constant, size of pixel to scroll by."))

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--input-json", "-i", help="Input json file", default="input.json")
    group.add_argument("--url", "-u", help="Specify a profile url directly.")
    return parser.parse_args()

def main():
    args = parse_args()
    global IS_DEBUG
    IS_DEBUG = args.debug

    print(LOGO)
    print(TITLE)

    output_folder = "snapshots"
    os.makedirs(output_folder, exist_ok=True)
    extra_args = {"force": args.force, "bio_only": args.bio_only, "load_times": args.scroll_load_time, "number_posts_to_cap": args.posts}
    f = None
    if args.scroll_algorithm == "percentile":
        assert args.scroll_value <= 1.0 and args.scroll_value >= 0.0
        f = calc_average(args.scroll_value)
    elif args.scroll_algorithm == "window":
        f = window_average(args.scroll_value)
    else:
        f = constant(args.scroll_value)

    extra_args["offset_func"] = f

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    if args.login:
        driver.get("https://twitter.com/login")
        input("Please logging then press any key in CLI to continue...")

    data = []
    if args.url:
        fetch_html(driver, args.url, fpath=output_folder, **extra_args)
    else:
        weird_opening = "window\..* = (\[[\S\s]*)"
        with open(args.input_json) as f:
            txt = f.read()
            match = re.match(weird_opening, txt)
            if match.group(1):
                txt = match.group(1)
            # Remove the first line metadata
            data = json.loads(txt)
    
        for d in data:
            account = d["following"]
            fetch_html(driver, account["userLink"], fpath=output_folder, **extra_args)

    print("ALL SCRAPING COMPLETED!")

if __name__ == "__main__":
    main()
