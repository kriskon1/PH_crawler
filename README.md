# PH_crawler
forums post web crawler
Logs into prohardver.hu forums, accesses "best buy" closed thread, checks the forums post, and sends an email with the posts containing links.
Goal is to run this every morning, so all the best buy items can be viewed in one email, without having to browse through all the forum posts.
Saves number id of already sent posts in data.txt to avoid duplicates.
Checks 3 pages back, which is sufficient if the script is ran every day.
