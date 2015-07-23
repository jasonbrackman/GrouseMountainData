# Why this project?
I'm personally interested in my Grouse Grind stats and hope to find more ways of understanding my time in comparison to
other 'Grinders'. I was also looking for a way to expand my understanding of Github, PyCharm, and some Python libraries
I haven't really delved into before.

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

The Grouse Grind is a 3000ft climb over approximates 3km distance.  The Grouse Mountain website claims that over 150 000
people hike the trail every year.

From a data collection standpoint the Grouse Mountain Resort provides those who want to spend 20 dollars on a 'Grind for
Kids' card.  The 'Grind for Kids' program raises money for different causes that help children.  This year, for example,
money goes to BC Children's hospital.  The cards allow users to electronically swipe in at the bottom and again at the top, so people can track their times, and possibly promote themselves to their friends, coworkers, and family to help raise money.  However, many people just do the Grind and compete to simply best themselves or even to get on a top ten list.  Each user can also log into the GrouseMountain website and check out their personal history, and some other simple stats, like your overall ranking.

So I'm one of those people who like to do the Grind and am often wondering about things like:
- How many people have done more than three grinds in a day?
- Are there trends that lead people to better times? Time of day? Weather? Number of attempts?
- I often do 40 or more Grinds a season -- how common is this?

When I log into the Grouse Mountain website you log into a sandboxed portion of their website that contains specific information, such as birthday, possibly a personal picture, and some specifics that relate to your Grind Timer still being active (it needs to be renewed each year).

When I want to look at my specific stats page, the website points to a regular html page that is no longer sandboxed.  It is a page that is likely intended to be shared, but is also not URL friendly since it looks something like: http://www.grousemountain.com/grind_stats/10000000000
More interesting is that the website provides additional personal tidbits that are likely more socially acceptable to be shared on a sport related site.  Items such as approximate age, sex, full name, along with all the Grinds, when they occurred, and when they ended are all available.  On top of that there are clues to how big the database is since the stats include how many active users there are for the season so far and how many there are total.  They do this by sharing with me where I rank in this season and overall and against other males and against everyone.

The only problem is obtaining the eleven digit account numbers to get access to the pages.  And for this I just kept climbing the mountain and asking what people's numbers were (they wear them around their necks so they are always readily available).

In all cases they end in numbers like 5000 or 15000, 6000, or 16000, etc.   So I scraped all the numbers based on these endings and was able to obtain around 3800 of the approximate 11000 accounts.  Enough to do some digging into the data.

# The dataset
The dataset is saved out as JSON data and is currently 64MB.  Is this big? Its a simple key value dictionary of the UUID linked to the name, age, sex, and a list of grinds that contain each date, the start time, the end time, and duration.

I haven't posted the database as I don't know yet if its in the cleanest state.   However, the script that collected it is the accounts.py file.

The account.py contains all the tools needed to collect the account data.  Unfortunately, something happened in late June and while I was able to get access to more than the first 100 grinds, the entire site seems to be unable to serve those pages anymore.  The account.py file is currently using a backup plan to get only the first 100 items, which is, for most users way more than the majority will ever do.  Obviously outliers are very interesting, and so would like to see this part of their site return.

If you need a small subset of the data to simply test out the content -- you can comment out all but one of the account number endings .. and you'll get a smaller, but significant dataset.

# The GUI
I know a lot of people are going to hate on this, but its all done in tkinter and matplotlib.  While tkinter may be old, it got the job done -- and my exploration into qt was wrought with hardship on my Mac.  One day I'll figure out how to switch over I guess.

I've never used matplotlib and it was probably too much fun to work with -- I ended up getting a bit distracted by it since you can play with so much.

There are a few things I have not yet figured out, such as how to make the plot area slightly larger to allow more room for the 'data source' comment.  

Anyway, once the GUI starts it will load the database (searches in your user directory) and will provide you a list of names that when selected, will provide the specific data and will plot them on the graph based on attempts.
- I have not yet figured out how to divide the items up by dates instead

You can then select someone else and the plot will draw over the old one for comparisson.  If you need to clear the plots uses the file menu.


