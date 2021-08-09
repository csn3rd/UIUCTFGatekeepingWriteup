f = open('synth.v','r')
h = open('log.txt','w')

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

# ignore clock and reset_n
# DFS starting with GOOD=True, reverse until 6 states left (uiuctf)
# statecount keeps track of the number of states visited so far

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
                statecount += 1
                if statecount > 20:
                    continue
                visited += [(rh,rh)]
                b[(rh,rh)] = bo
                dfs(rh,rh,statecount)
            else:
                c = 0
                s = rh+str(statecount)
                visited += [(s,rh)]
                b[(s,rh)] = bo
                dfs(s,rh,statecount)

visited += [("GOOD", "GOOD")]
b[("GOOD", "GOOD")] = 'T'
dfs("GOOD", "GOOD",0)

# go through each set of bytes and get the character formed
# since we started from the end, we must go from the bytes
# with largest statecount to the bytes with the smallest

flag = ""
for i in range(1,21):
    currbyte = ""
    for j in range(8):
        if b[("BYTE["+str(j)+"]"+str(i),"BYTE["+str(j)+"]")] == 'T':
            currbyte = "1"+currbyte
        else:
            currbyte = "0"+currbyte
    flag = chr(int(currbyte,2))+flag

print("Flag: uiuctf{}".format(flag))
f.close()
h.close()