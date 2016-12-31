import os
from time import *

def getErrFileMsg(filename): #{
    errFile = filename.split('.lock.err')
    if len(errFile) == 1:
        return False
    errFile = errFile.pop(0)
    i = errFile.find('_')
    if i == -1:
        return False
    res = {}
    res['id'] = errFile[0:i]
    if res['id'] == 'add':
        res['id'] = '0'
    res['tmpfile'] = errFile[i:].replace('_', '/')
    return res
#}

def lastSaveErrorPormpt(errFileLists): #{
    """
    上次存储失败提示信息
    """
    msg = '你有 \033[31m'
    msg += str(len(errFileLists))
    msg += '\033[0m 条日志存储失败:'
    print(msg)
    print('\033[32;1m    N    ID   Op       Time           TmpFile\033[0m')

    n = 1
    errFileLists.sort(key = lambda x: x['id'])
    for errfile in errFileLists:
        msg = '    ' + str(n) + ': '
        if errfile['id'] == '0':
            msg += "       \033[31;1mA\033[0m  "
        else:
            msg += "\033[33m" + errfile['id'] + " \033[36;1mE\033[0m  "
        msg += errfile['time'] + " " + errfile['tmpfile']
        print(msg)
        n = n + 1
#}

def cs(content, color = '0'): #{
    return '\033[' + color + 'm' + content + '\033[0m'
#}

def _subMenu(title, helpStr, errFileLists, run = None): #{
    errLen = len(errFileLists)
    while True:
        print("\n--- " + title + " Help ---")
        print('\tSelect Error File List N, Show '+ helpStr +'.')
        print('\tq -- Return Main Menu.')
        print('\tl -- Show Error File List.')
        i = input(cs(title, '34;1') + '>> ')
        if i == 'q':
            break
        elif i == 'l':
            lastSaveErrorPormpt(errFileLists)
            continue

        num = int(i) if i.isdigit() else 0
        if num < 1 or num > errLen:
            continue
        if run == None:
            os.system('less -XRF ' + errFileLists[num - 1]['runfile'])
        else:
            run(errFileLists[num - 1])
#}

def _list(errFileLists): #{
    lastSaveErrorPormpt(errFileLists)
#}
def _error(errFileLists): #{
    _subMenu('Error', 'Error Message', errFileLists)
#}
def _tmpfile(errFileLists): #{
    def run(errFile):
        os.system('less -XRF ' + errFile['tmpfile'])
    _subMenu('TmpFile', 'tmpFile Content', errFileLists, run)
#}

def _source(errFileLists): #{
    def run(errFile):
        ids = errFile['id']
        if ids == '0': return
        os.system('log list ' + ids)
    _subMenu('Source', 'Source Content', errFileLists, run)
#}

def _open(errFileLists): #{
    print('hello')
#}
def _repair(errFileLists): #{
    print('hello')
#}
def _delete(errFileLists): #{
    print('hello')
#}

def lastSaveErrorChk(runPath): #{
    """
    检测以前是否有保存失败的日志，如果有则提示并且询问是否启动处理流程
    """
    fileLists = os.listdir(runPath)
    errFileLists = []
    for filename in fileLists:
        errFileMsg = getErrFileMsg(filename)
        if not errFileMsg:
            continue
        s = os.stat(runPath + '/' + filename)
        errFileMsg['time'] = strftime("%Y-%m-%d %H:%M", localtime(s.st_mtime))
        errFileMsg['runfile'] = runPath + '/' + filename
        errFileLists.append(errFileMsg)

    lastSaveErrorPormpt(errFileLists)

    cmdDict = {
                'list': _list, 'l': _list, '1': _list,
                'error': _error, 'e': _error, '2': _error,
                'tmpfile': _tmpfile, 't': _tmpfile, '3': _tmpfile,
                'source': _source, 's': _source, '4': _source,
                'open': _open, 'o': _open, '5': _open,
                'repair': _repair, 'r': _repair, '6': _repair,
                'delete': _delete, 'd': _delete, '7': _delete,
              }

    while True:
        msg = '\n*** Commands ***\n'
        msg += '    1: \033[34;1ml\033[0mist'
        msg += '    2: \033[34;1me\033[0mrror '
        msg += '    3: \033[34;1mt\033[0mmpfile'
        msg += '    4: \033[34;1ms\033[0mource\n'
        msg += '    5: \033[34;1mo\033[0mpen'
        msg += '    6: \033[34;1mr\033[0mepair'
        msg += '    7: \033[34;1md\033[0melete '
        msg += '    8: \033[34;1mq\033[0muit\n'
        print(msg)
        i = input(cs('What now', '34;1') + '> ')
        if i == 'q' or i == 'quit' or (i.isdigit() and int(i) == 8):
            print('Bye.')
            break
        if i in cmdDict:
            cmdDict[i](errFileLists)
        else:
            print(cs('Huh (' + i + ')?', '31;1'))
    len(errFileLists) != 0 and exit(0)
#}
