f = open('synth.v','r')
g = open('graph.gv','w')
h = open('log.txt','w')

# visuals
g.write("digraph {\n")
g.write("    ranksep=1\n")
g.write("    bgcolor=\"#122436\"\n")
g.write("    pad=5\n")
g.write("    splines=polyline\n")
g.write("    node [style=\"filled\" fontsize=25 nodesep=0.5]\n")
g.write("    edge [color=\"#f4fff9\" penwidth=3.0 arrowhead=none]\n")
g.write("    \"logo\" [image=\"logo2.png\" label=\"\" style=\"\" color=\"none\"]\n")
g.write("    \"title\" [label=\"GATEKEEPING               \" labeljust=c fontsize=500 fontcolor=\"#edffcd\" style=\"\" color=\"none\"]\n")
g.write("    \"logo\"->\"title\" [style=\"invis\"]\n")
g.write("    {rank=\"same\";logo;title}\n")

# part 1 - go through synth.v and store the important lines

# d - synth.v definitions, e - synth.v equations
d,e={},{} 

for l in f:
    if '=' not in l:
        continue
    line = l.split('=')
    if 'assign' in line[0]:
        line[0] = line[0].replace('assign','')
    line[0] = line[0].replace('<','')
    line[0] = line[0].replace(' ','')

    e[line[0]] = line[1]

    line[1] = line[1].replace('(','')
    line[1] = line[1].replace(')','')
    line[1] = line[1].replace('&','')
    line[1] = line[1].replace('|','')
    line[1] = line[1].replace('~','')
    line[1] = line[1].replace(';','')

    x = line[1].split()
    for rh in x:
        if line[0] in d:
            d[line[0]] += [rh]
        else:
            d[line[0]] = [rh]

# part 2 - figure out the values of each wire and register.

# DFS starting with GOOD = True, reverse until 6 states left (uiuctf)
# statecount keeps track of the number of states visited so far
# Assume every value is on the positive edge of the clock
# Reset signal will be T/F depending on what will make the statement evaluate truthfully

# b - solved boolean values, visited - visited nodes and their names
b={}
visited = []
def dfs(currnodename, currnode, statecount):
    global visited
    if currnode in d:
        x = d[currnode]
        bo = 'F'
        if b[(currnodename,currnode)] == 'T':
            if '&' in e[currnode]:
                bo = 'T'
            elif '~' in e[currnode] and '|' in e[currnode]:
                bo = 'F'
            elif '~' in e[currnode]:
                bo = 'F'
            else:
                bo = 'T'
        else:
            if '~' in e[currnode] and '&' in e[currnode]:
                bo = 'T'
            elif '|' in e[currnode]:
                bo = 'F'
            elif '~' in e[currnode]:
                bo = 'T'
            else:
                bo = 'F'

        h.write("{}:{}".format(b[(currnodename,currnode)],e[currnode]))
        h.write(bo+"\n")

        ind = 0
        for rh in x:
            ind += 1
            if 'RESET_N' in rh:
                continue
            if 'state' in rh:
                g.write("    \"{}\"->\"{}\"\n".format(currnodename,rh))
                statecount += 1
                if statecount > 20:
                    continue
                visited += [(rh,rh)]
                b[(rh,rh)] = bo
                dfs(rh,rh,statecount)
            else:
                c = 0
                s = rh+str(statecount)
                g.write("    \"{}\"->\"{}\"\n".format(currnodename,s))
                visited += [(s,rh)]
                b[(s,rh)] = bo
                dfs(s,rh,statecount)

visited += [("GOOD", "GOOD")]
b[("GOOD", "GOOD")] = 'T'
dfs("GOOD", "GOOD",0)

# visuals
for i in visited:
    if i[1] == "GOOD":
        g.write("    \"{}\" [label=\"{}\" fillcolor=\"lime\"]\n".format(i[0],i[1]))
        continue
    l = i[1]
    if "BYTE" in i[1]:
        l = i[1].replace("BYTE","B")    
    if b[i] == 'T':
        g.write("    \"{}\" [label=\"{}\" fillcolor=\"limegreen\"]\n".format(i[0],l))
    else:
        g.write("    \"{}\" [label=\"{}\" fillcolor=\"cyan3\"]\n".format(i[0],l))


# PART 3 - getting the flag

# go through each set of bytes and get the character formed
# since we started from the end, we must go from the bytes
# with largest statecount to the bytes with the smallest

binary = ""
flag = ""
for i in range(1,21):
    currbyte = ""
    for j in range(8):
        if b[("BYTE["+str(j)+"]"+str(i),"BYTE["+str(j)+"]")] == 'T':
            currbyte = "1"+currbyte
        else:
            currbyte = "0"+currbyte

    # visuals
        if j > 0:
            g.write("    \"{}\"->\"{}\"\n".format("BYTE["+str(j)+"]"+str(21-i),"BYTE["+str(j-1)+"]"+str(21-i)))
    g.write("    {rank = \"same\"");
    for j in range(8):
        g.write("; \"{}\"".format("BYTE["+str(j)+"]"+str(21-i)))
    g.write(" }\n")

    binary += " "+currbyte
    flag = chr(int(currbyte,2))+flag

print("Flag: uiuctf{}".format(flag))

# visuals
binary = binary.split()
for i in range(1,21):
    for j in range(8):
        g.write("    \"{}\"->\"{}\"\n".format("BYTE["+str(j)+"]"+str(i), "2BYTE["+str(j)+"]"+str(i)))
        if binary[i-1][7-j] == '1':
            g.write("    \"{}\" [label=\" {} \" fillcolor=\"lime\" fontsize=50]\n".format("2BYTE["+str(j)+"]"+str(i), binary[i-1][7-j]))
        else:
            g.write("    \"{}\" [label=\" {} \" fillcolor=\"cyan\" fontsize=50]\n".format("2BYTE["+str(j)+"]"+str(i), binary[i-1][7-j]))
        if j > 0:
            g.write("    \"{}\"->\"{}\"\n".format("2BYTE["+str(j)+"]"+str(i),"2BYTE["+str(j-1)+"]"+str(i)))
        else:
            g.write("    \"{}\"->\"{}\"\n".format("2BYTE["+str(j)+"]"+str(i), str(i)+"char"))
        
        g.write("    \"{}\" [label=<<B> {} </B>> fillcolor=\"#9633ed\" fontsize=140 fontcolor=\"#f4fff9\"]\n".format(str(i)+"char", chr(int(binary[i-1],2))))
    
    if i > 1:
        g.write("    \"{}\"->\"{}\"\n".format(str(i)+"char",str(i-1)+"char"))

# visuals
g.write("    \"state[11]\" [label=\"state[11]\" fillcolor=\"#f69afe\" fontcolor=\"#f4fff9\"]\n")
g.write("    \"state[11]\"->\"wrapper\"\n")
g.write("    \"wrapper\"->\"20char\"\n")
g.write("    \"wrapper\" [label=<<B>uiuctf</B>> fillcolor=\"#9633ed\" fontsize=140 fontcolor=\"#f4fff9\"]\n")
g.write("    {rank = \"same\"; \"wrapper\"")
for i in range(1,21):
    g.write("; \""+str(21-i)+"char\"")
g.write(" }\n")
g.write('}\n')

f.close()
g.close()
h.close()