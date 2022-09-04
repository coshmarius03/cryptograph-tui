import requests
import time
import datetime
import sys, tty, termios
import threading
import os
coins = ["BNBBTC","ETHUSDT"]
coin = 'BTCUSDT'
interval = '1m'
size = os.get_terminal_size()
boxsize = [size[0]-12,size[1]-4]
scol = [1]
graphviews = [4,5,7]
graphviewsalt = ['close','vol1','vol2']
graphviewsnames = ['Price','Vol '+coin[:3],'Vol '+coin[3:]]
gview = 0
ipt = ''
symbols = [['█','▄'],['▉',' '],['▊',' '],['❚',' '],['❙',' '],['❘',' ']]
symbol = 0
r = requests.get('https://www.binance.com/api/v3/uiKlines?limit=1000&symbol={}&interval={}'.format(coin,interval))
if not r.ok: exit("API ERROR")
r = r.json()
viewidx = len(r)

def printing():
    global size
    global boxsize
    global viewidx
    while True:
        try:
            size = os.get_terminal_size()
            boxsize = [size[0]-14,size[1]-4]
            #viewidx = len(r)-boxsize[0]
            content = [' '*size[0] for i in range(size[1])]
            #for i,c in enumerate(content.copy()):
            #    content[i] = str(i).center(size[0])
            maxval = 0
            minval = 999999999999999
            rmax = 0
            rmin = 999999999999999
            data = r[viewidx-boxsize[0]:viewidx]
            for i in data:
                if float(i[graphviews[gview]]) > maxval: maxval = float(i[graphviews[gview]])
                if float(i[graphviews[gview]]) < minval: minval = float(i[graphviews[gview]])
                if float(i[graphviews[gview]]) > rmax: rmax = float(i[graphviews[gview]])
                if float(i[graphviews[gview]]) < rmin: rmin = float(i[graphviews[gview]])
            maxval += maxval-(maxval+minval)/2
            minval -= (maxval+minval)/2-minval
            if minval < 0: minval = 0
            cf = (maxval-minval)//(boxsize[1]-10)
            slr = data[boxsize[0]-min(scol)]
            sl = {
                'date':datetime.datetime.fromtimestamp(slr[0] / 1e3).strftime("%m/%d/%Y %H:%M:%S"),
                'open':str(slr[1]).split('.')[0]+'.'+str(slr[1]).split('.')[1][:2],
                'high':str(slr[2]).split('.')[0]+'.'+str(slr[2]).split('.')[1][:2],
                'low':str(slr[3]).split('.')[0]+'.'+str(slr[3]).split('.')[1][:2],
                'close':str(slr[4]).split('.')[0]+'.'+str(slr[4]).split('.')[1][:2],
                'vol1':str(slr[5]).split('.')[0]+'.'+str(slr[5]).split('.')[1][:2],
                'vol2':str(slr[7]).split('.')[0]+'.'+str(slr[7]).split('.')[1][:2]
            }
            if len(scol)>1:
                slr = data[boxsize[0]-max(scol)]
                sl['date'] = datetime.datetime.fromtimestamp(slr[0] / 1e3).strftime("%m/%d/%Y %H:%M:%S")+' - '+sl['date']
                sl['open'] = str(slr[1]).split('.')[0]+'.'+str(slr[1]).split('.')[1][:2]
                for sc in scol.copy():
                    slr = data[boxsize[0]-sc]
                    if float(slr[2]) > float(sl['high']): sl['high'] = str(slr[2]).split('.')[0]+'.'+str(slr[2]).split('.')[1][:2]
                    if float(slr[3]) < float(sl['low']): sl['low'] = str(slr[3]).split('.')[0]+'.'+str(slr[3]).split('.')[1][:2]
            sl['change'] = str((float(sl['close'])/(float(sl['open']))*100)-100)
            sl['change'] = ('+' if float(sl['change'])>0 else '')+sl['change'].split('.')[0]+'.'+sl['change'].split('.')[1][:3]+'%'
            if float(sl['close']) > float(sl['open']): sl['a'] = ['\033[0;32m▲\033[0m','\033[0;32m╹\033[0m']
            else: sl['a'] = ['\033[0;31m╻\033[0m','\033[0;31m▼\033[0m']
            high = False
            low = False
            sel = False
            lp = False
            for i in range(boxsize[1]):
                ptr = ''
                for j, d in enumerate(data):
                    vrel = int(float(d[graphviews[gview]])-minval)/cf
                    if vrel+0.6 >= boxsize[1]-i:
                        if j in [boxsize[0]-rs for rs in scol]:
                            if sel == False:sel = True
                            if vrel >= boxsize[1]-i: ptr += '\033[0;95m{}\033[0m'.format(symbols[symbol][0])
                            else: ptr += '\033[0;95m{}\033[0m'.format(symbols[symbol][1])
                        elif float(d[graphviews[gview]]) == rmax:
                            if high == False:high = True
                            if vrel >= boxsize[1]-i: ptr += '\033[0;92m{}\033[0m'.format(symbols[symbol][0])
                            else: ptr += '\033[0;92m{}\033[0m'.format(symbols[symbol][1])
                        elif float(d[graphviews[gview]]) == rmin:
                            if low == False:low = True
                            if vrel >= boxsize[1]-i: ptr += '\033[0;91m{}\033[0m'.format(symbols[symbol][0])
                            else: ptr += '\033[0;91m{}\033[0m'.format(symbols[symbol][1])
                        elif interval == '1m' and j==len(data)-1 and r[-1][0]==d[0]:
                            if lp == False:lp = True
                            if vrel >= boxsize[1]-i: ptr += '\033[93m'+symbols[symbol][0]+'\033[0m'
                            else: ptr += '\33[93m'+symbols[symbol][1]+'\033[0m'   
                        else:
                            if vrel >= boxsize[1]-i: ptr += '\33[90m'+symbols[symbol][0]+'\033[0m'
                            else: ptr += '\33[90m'+symbols[symbol][1]+'\033[0m'
                    else:
                        ptr += ' '
                rdata = [float(sl[graphviewsalt[gview]]),float(data[-1][graphviews[gview]]),rmin,rmax]
                for j,rd in enumerate(rdata):
                    if rd>100000:
                        rdata[j] = str(int(rd)//1000)+'K'
                    else: rdata[j]="{:.2f}".format(rd)
                if sel:
                    content[i] = ptr+'\033[0;90m┃\033[0;95m◀\033[0;35m '+(rdata[0]).ljust(size[0]-3-boxsize[0])
                    sel = None
                elif lp:
                    content[i] = ptr+'\033[0;90m┃\033[0;93m⊲\033[0;33m'+' '+(rdata[1]).ljust(size[0]-3-boxsize[0])
                    lp = None
                elif low:
                    content[i] = ptr+'\033[0;90m┃\033[0;91m⊲\033[0;31m'+' '+(rdata[2]).ljust(size[0]-3-boxsize[0])
                    low = None
                elif high:
                    content[i] = ptr+'\033[0;90m┃\033[0;92m⊲\033[0;32m'+' '+(rdata[3]).ljust(size[0]-3-boxsize[0])
                    high = None
                else: content[i] = ptr+'\033[0;90m┃\033[0m '+' '*(size[0]-2-boxsize[0])
                if sel == True: sel = None
                if lp == True: lp = None
                if low == True: low = None
                if high == True: high = None
            content[0] = ('             '+('\033[0;32m' if sl['change'][0]=='+' else '\033[0;31m')+sl['change'].center(9)+'\033[0m')+content[0][(22):]
            content[1] = (' Open: '+sl['open']).ljust(17)+(sl['a'][0]+'   \033[0;31mLow: '+sl['low']+'\033[0m')+content[1][(len(sl['low'])+26):]
            content[2] = ('Close: '+sl['close']).ljust(17)+(sl['a'][1]+'  \033[0;32mHigh: '+sl['high']+'\033[0m')+content[2][(len(sl['high'])+26):]
            content[3] = content[3][:-13]+('Max: '+str(len(r))).center(13)
            content[4] = content[4][:-13]+'\033[0;90m━━━━━━━━━━━━━'
            svd = len(coin)
            if True:
                content[0] = content[0][:-30-svd]+'\033[0;33m╭─'+'─'*svd+'─╮'+content[0][-26:]
                content[1] = content[1][:-30-svd]+'\033[0;33m│ '+coin+' │'+content[1][-26:]
                content[2] = content[2][:-30-svd]+'\033[0;33m╰─'+'─'*svd+'─╯'+content[2][-26:]
            view = graphviewsnames[gview]
            if False:
                content[0] = content[0][:-34-svd]+'╭─'+'─'*len(view)+'─╮'+content[0][-30-svd:]
                content[1] = content[1][:-34-svd]+'│ '+view+' │'+content[1][-30-svd:]
                content[2] = content[2][:-34-svd]+'╰─'+'─'*len(view)+'─╯'+content[2][-30-svd:]
            if interval=='1m' and viewidx == len(r):
                content[0] = content[0][:-48-svd]+'\033[0;91m╭────────╮'+content[0][-38-svd:]
                content[1] = content[1][:-48-svd]+'\033[0;91m│  Live  │'+content[1][-38-svd:]
                content[2] = content[2][:-48-svd]+'\033[0;91m╰────────╯'+content[2][-38-svd:]
            if len(scol)==1:
                content[0] = content[0][:-13]+('Index: '+str(viewidx+1-scol[0])).center(13)
            else:
                content[1] = content[1][:-13]+('Per: '+str(len(scol))+interval[-1]).center(13)
                if scol[-1]>scol[0]: content[0] = content[0][:-13]+('I: '+str(viewidx+1-scol[-1])+'-'+str(viewidx+1-scol[0])).center(13)
                else: content[0] = content[0][:-13]+('I: '+str(viewidx+1-scol[0])+'-'+str(viewidx+1-scol[-1])).center(13)
            content[2] = content[2][:-13]+('◀ '+str(viewidx-boxsize[0])+' '+str(len(r)-viewidx)+' ▶').center(13)
            content[-4] = '\033[0;90m'+'━'*boxsize[0]+'┛\033[0m'
            content[-3] = (sl['date']+(' ('+str(len(scol))+interval[-1]+')' if len(scol)>1 else '')).center(size[0])
            #content[-2] = (str(len(data))+' '+str(len(content))+' '+str(maxval)+' '+str(minval)).center(size[0])
            content[-1] = ('>'+('' if len(ipt)>0 else 'Type a command')+ipt).center(size[0])



            print("\033[F"*size[1]+''.join(content), end="")
        except Exception as e:
            print(e)
        time.sleep(0.05)
def pricecheck():
    global r
    global viewidx
    while True:
        if interval == '1m':
            live = requests.get('https://www.binance.com/api/v3/uiKlines?limit=1&symbol={}&interval={}'.format(coin,interval))
            if live.ok:
                live = live.json()[0]
                if int(r[-1][0]) < int(live[0]):
                    if viewidx == len(r):
                        r.append(live)
                        viewidx = len(r)
                    else: r.append(live)
                else: r[-1][4] = live[4]
        time.sleep(1)
threading.Thread(target=printing, daemon=True).start()
threading.Thread(target=pricecheck, daemon=True).start()
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch
def command(cmd):
    global viewidx
    global r
    global scol
    global interval
    global symbol
    while '  ' in cmd:
        cmd = cmd.replace('  ',' ')
    cmd = cmd.split(' ')
    cmd[0] = cmd[0].lower()
    if len(cmd) > 0:
        if cmd[0] in ['q','quit', 'exit']:
            exit('Bye')
        elif cmd[0] == 'interval':
            if cmd[1] == 'live': cmd[1] = '1m'
            interval = cmd[1]
            r = requests.get('https://www.binance.com/api/v3/uiKlines?limit=1000&symbol={}&interval={}'.format(coin,interval))
            if not r.ok: exit('API ERROR')
            r = r.json()
            viewidx = len(r)
            scol = [1]
        elif cmd[0] == 'jump':
            cmd[1] = int(cmd[1])
            scol = [boxsize[0]//2]
            if not cmd[1]>0 and not cmd[1]<=len(r):return
            if cmd[1]-1+scol[0]<=boxsize[0]:
                viewidx=boxsize[0]
                scol = [boxsize[0]+1-cmd[1]]
            elif cmd[1]-1+scol[0]>=len(r):
                viewidx=len(r)
                scol = [len(r)+1-cmd[1]]
            else:viewidx=cmd[1]-1+scol[0]
            #scol = [scol[0]]
            #if int(cmd[1])>=boxsize[0]: viewidx=int(cmd[1])
        elif cmd[0] == 'bars':
            try:
                cmd[1] = int(cmd[1])
                if cmd[1]<=len(symbols) and cmd[1]>0: symbol=cmd[1]-1
            except:
                if len(cmd[1])==1:
                    symbols.append([cmd[1],' '])
                    symbol=len(symbols)-1

#r = requests.get('https://www.binance.com/api/v3/ticker/price?symbols=[%22{}%22]'.format('%22,%22'.join(coins)))

comboch = None
while True:
    ch = getch()
    if comboch:
        if comboch == '\x1b' and ch == '[': comboch = '\x1b['
        elif comboch == '\x1b[': comboch += ch
        elif comboch == '\x1b[1': comboch += ch
        elif comboch == '\x1b[1;': comboch += ch
        elif comboch in ['\x1b[6','\x1b[5']: comboch += ch
        elif comboch in ['\x1b[1;2','\x1b[1;5']: comboch += ch
        else: comboch = None
        if comboch in ['\x1b[D','\x1b[A','\x1b[C','\x1b[B']:
            if comboch == '\x1b[D':
                if len(scol)>1:
                    scol = [scol[-1]]
                if scol[-1] < boxsize[0]: scol = [scol[-1]+1]
                elif viewidx > boxsize[0]:
                    viewidx-=1
            elif comboch == '\x1b[C':
                if len(scol)>1:
                    scol = [scol[-1]]
                if scol[0] > 1: scol = [scol[-1]-1]
                elif viewidx < len(r):
                    viewidx+=1
            comboch = None
        elif comboch in ['\x1b[1;2D','\x1b[1;2A','\x1b[1;2C','\x1b[1;2B']:
            if comboch == '\x1b[1;2D' and scol[-1] < boxsize[0]:
                sti = scol[0]+(scol[-1]-scol[0])+1
                if sti in scol and sti-1 in scol and len(scol)>1: scol.remove(sti-1)
                else: scol.append(sti)
            elif comboch == '\x1b[1;2C' and scol[-1] > 1:
                sti = scol[0]-(scol[0]-scol[-1])-1
                if sti in scol and sti+1 in scol and len(scol)>1: scol.remove(sti+1)
                else: scol.append(sti)
            comboch = None
        elif comboch in ['\x1b[1;5D','\x1b[1;5A','\x1b[1;5C','\x1b[1;5B']:
            if comboch == '\x1b[1;5D':
                if viewidx > boxsize[0]: viewidx-=1
            elif comboch == '\x1b[1;5C':
                if viewidx < len(r): viewidx+=1
            comboch = None
        elif comboch in ['\x1b[6~','\x1b[5~']:
            if comboch == '\x1b[5~':
                if gview+1<len(graphviews):gview=gview+1
                else:gview=0
            elif comboch == '\x1b[6~':
                if gview-1>=0:gview=gview-1
                else:gview=len(graphviews)-1
            comboch = None
        continue
    if ch == '\x1b':
        comboch = ch
        continue
    #elif ch == 's':
    #    if symbol+1 >= len(symbols): symbol = 0
    #    else: symbol += 1
    elif ch == '\r':
        command(ipt)
        ipt = ''
    elif ch == '\x7f': ipt = ipt[:-1]
    else: ipt += ch
    #print(ch)
