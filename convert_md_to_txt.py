import markdown
from bs4 import BeautifulSoup
html = markdown.markdown(open("CHANGELOG.md").read()).split("\n")

def obtain_info_by_date(html):
    idxs =[ i for i, pattern in enumerate(html) if '<p>New updates' in pattern ]
    dates = {}
    i = 0
    for i in range(0, len(idxs)):
        date = html[idxs[i]]
        real_date = date.split(">")[1].split("<")[0]
        start = idxs[i]
        if len(idxs) == i + 1:
            end = len(html)
        else:
            end = idxs[i+1]
        sublist = html[start+1:end]
        sublist = [x.split("<p>")[1].split("Updated on")[0] for x in sublist if "<p>" in x]
        sublist = [x.split(" To include on the web")[0] for x in sublist if "To include on the web" in x]
        if len(sublist) > 0:
            dates[real_date] = sublist
    return dates

def write_txt(dates):
    with open("changelog.txt","w") as chlog:
        for date in dates:
            date_write = "<b>"+date+"</b>\n"
            chlog.write(date_write)
            updates = dates[date]
            for line in updates:
                line_write = "<li>"+line+"</li>\n"
                chlog.write(line_write)


write_txt(obtain_info_by_date(html))
