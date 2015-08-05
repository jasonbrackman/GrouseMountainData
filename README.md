# Why this project?
I'm interested in my Grouse Grind stats and hope to find interesting ways of seeing my time in comparison to
other 'Grinders'. I was also looking for a way to expand my understanding of Github, PyCharm, and some Python libraries,
such as tkinter, Matplotlib, and Beautifulsoup.

Finally -- my wife is done with me talking about the Grind, so I used this project as a way to focus the obsession
somewhere else.

# Additional Details
- This is a Python 3.x project
- Written and tested on a Mac OSX Yosemite 10.10.4 and a Windows 7 machine.
- On the Mac I could not get the official Python 3.4x installers to work with the program.  I had to install the
Anaconda version of Python.
-- The problem was the tkinter listbox would fail with my Macbook Pro trackpad.  The trackpad callback was triggering an
exception.  It is a known bug, but is also supposed to be fixed in the official Python releases, but I couldn't get it
to work.
- Matplotlib, numpy are needed for UI purposes
- BeautifulSoup4 is needed for scraping

# GrouseMountainData
If you live in Vancouver for any amount of time at all someone is bound to ask if you have hiked the Grouse Grind trail.

The Grouse Grind is a 3000ft climb over a 3km distance.  The Grouse Mountain website claims that over 150 000
people hike the trail every year.  While the trail is cared for by Metro Vancouver, the mountain itself is privately
owned.

From a data collection standpoint the Grouse Mountain Resort provides a unique option to 'swipe' in at the base and at
the top of the Grouse Grind Trail.  An electronic keycard can be purchased at the lodge to do this.  The Grind Timer
makes the data comparable from Grind to Grind. Many people just do the Grind and compete to simply best themselves while
others may attempt to get on a top ten list for time.  Each user can also log into the GrouseMountain website and check
their personal history, and some other stats such as gender standing, age group standing, and placement for the season.

# Questions
Each user has their personal Grind history as well as access to top ten lists.  However, most of the top ten lists are
populated by the same people.  More obscure questions cannot be asked.  These might include:
- How many people have done more than three grinds in a day?
- Are there trends that lead people to better times? Time of day? Weather? Number of attempts?
- I often do 40 or more Grinds a season -- how common is this?
- Can I see the Grind history of me and my five friends?

# Understanding The Website
When I log into the Grouse Mountain website you log into a sandboxed portion of their website that contains specific
information, such as birthday, possibly a personal picture, and some specifics that relate to your Grind Timer still
being active (it needs to be renewed each year).

When I want to look at my specific stats page, the website points to a regular html page that is no longer sandboxed. It
is a page that is likely intended to be shared, but its also not personal and looks something like:
http://www.grousemountain.com/grind_stats/10000000000

This portion of the website provides additional datapoints socially acceptable for a sport related event.  Items such as
approximate age, sex, full name, along with all the Grinds, when they occurred, and when they ended are all available.
There are also clues as to how big the database is since the stats include how many active users there are for both the
season and for all time.

# Account Numbers
The majority of account numbers are based on an seven to twelve digit account number.  Google has only cached a few of
these pages, but too few to make any kind of reduction to where a web scraper might look for the greatest number of
hits.  Without some sort of reduction, the scraper would have to test against ALL combinations, which would take a long
time.

Every time I would climb the mountain I would ask a few people what their grind numbers were.  They wear them
around their necks so they are always readily available and this isn't as awkward sounding as it might seem. In four
weeks of casually asking, there was a pattern that slowly emerged.  Each person's number ended with the last
three digits always being zeroes.  A majority numbers like 5000 or 15000, 6000, or 16000, etc.   So I began scraping all
the numbers based on these endings.  This netted around 7000~9000 of the approximate 11000 accounts.

The rest of the accounts were simply testing every number starting from '0' and moving up to '250000', stopping only
because accounts stopped being hit.  The reason why I started at such a low number was because of the five accunts that
Google did appear to spider, one was one of these low numbers.

# The dataset
The dataset is saved out into two JSON files.  One contains the successful hits, while the other contains the
"Not Found" results.  Its important to keep them both for future checks to skip already checked numbers and to only
update valid accounts.  The data is a simple key value dictionary of the UUID linked to the name, age, sex, and a list
of grinds that contain each date, the start time, the end time, and duration.

I haven't posted the database as I don't know yet if its in the cleanest state.   However, the script that collected it
is the accounts.py file.

The account.py contains all the tools needed to collect the account data.  Unfortunately, something happened in late
June and while I was able to get access to more than the first 100 grinds, the entire site seems to be unable to serve
those pages anymore.  The account.py file is currently using a backup plan to get only the first 100 items, which is,
for most users way more than the majority will ever do.  Obviously outliers are very interesting, and so would like to
see this part of their site return.

If you need a small subset of the data to simply test out the content -- you can comment out all but one of the account
number endings .. and you'll get a smaller, but significant dataset.

# The GUI
I know a lot of people are going to hate on this, but its all done in tkinter and matplotlib.  While tkinter may be old,
it got the job done -- and my exploration into qt was wrought with hardship on my Mac.  Whatever my next project will be
will attempt to figure this out.

I've never used matplotlib before and it was probably too much fun to work with.  I ended up getting a bit distracted by
it since you can play with so much.

Once the GUI starts it will load the database (searches in your user directory) and will provide you a list of names
that when selected, will provide the specific data and will plot them on the graph based on attempts.

You can then select someone else and the plot will draw over the old one for comparison.  The file menu also includes
other options such as 'clear', to clear away all the plots currently shown.


