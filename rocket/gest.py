with open("gestimate.csv", "r") as f:
    lines = f.readlines()
    for line in lines:
        line = line.replace("\n","")
        lsplit=line.split("&")
        distc = float(lsplit[0])
        dists = float(lsplit[1])
        print("${:e}$ & ${:e}$ & ${}$ \\\\".format(distc, dists, lsplit[2]).replace("e+0", "\\;10^"))
        print("\\hline")

