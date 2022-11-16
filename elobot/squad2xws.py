"""get legacy-yasb link and convert it to XWS"""

def squad2xws(xws):
    xws = """ http://xwing-legacy.com/\
              ?f=Separatist%20Alliance\
              &d=v8ZsZ200Z421XWWWWY429XWWWWWWWY326XWWWW237\
              &sn=Unnamed%20Squadron&obs=" """
    regex_result = re.search("v\dZ.*", xws)
    separated_xws = regex_result.group().split("Z")
    
    pilots_uncut = separated_xws[3]
    print(pilots_uncut)
    
    pilots_cut = pilots_uncut[:pilots_uncut.find('&sn')]
    print(pilots_cut)
    
    separated_pilots = pilots_cut.split("Y")
    print(separated_pilots)

    return separated_pilots
