import os

l = []
with open("../obj.names") as list_in:
    for line in list_in:
        l.append(line[:-1])


def make_labels(s):
    for idx, cls in enumerate(l):
        os.system("convert -fill black -background white -bordercolor white -border 4 -font /System/Library/Fonts/Supplemental/Songti.ttc -pointsize %d label:\"%s\" \"%d_%d.png\"" % (s, cls, idx, s/12-1))


for i in [12, 24, 36, 48, 60, 72, 84, 96]:
    make_labels(i)
