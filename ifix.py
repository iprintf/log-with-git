import os
from time import *
from common import checkEditRun, cs, shell_exec

def parseErrFileName(runPath, filename): #{
    """
    判断是否为运行文件并且解析文件名提取信息
    """
    if filename.find('.') != -1 or len(filename) != 12:
        return False

    op = filename[0:1]
    if not (op == 'E' or op == 'A') or checkEditRun(filename):
        return False

    res = {}
    res['op'] = op
    res['id'] = filename[1:7] if op == 'E' else '      '
    res['file'] = runPath + '/' + filename
    s = os.stat(res['file'])
    res['time'] = strftime("%Y-%m-%d %H:%M", localtime(s.st_mtime))
    return res
#}

def listPrompt(errFileLists): #{
    """
    上次存储失败文件列表显示及命令提示信息
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
        msg += cs(errfile['id'], '33') + ' '
        msg += cs(errfile['op'], '36;1') + '  '
        msg += errfile['time'] + ' '
        msg += errfile['file'].replace(os.environ['HOME'], '~')
        print(msg)
        n = n + 1
#}

def _subMenuRun(errFile, ind, run = None): #{
    filename = os.path.basename(errFile['file'])
    print(cs('--- ' + filename + ':', '33;1'))
    if run == None:
        if os.path.exists(errFile['file']):
            out = shell_exec('less -XRF ' + errFile['file'])
            if out == False:
                print(cs('--- 临时文件无法查看!', '31;1'))
        else:
            print(cs('--- ' + errFile['file'] + ' 文件已经不存在啦!', '31;1'))
        return
    run(errFile, ind)
#}

def _subMenu(title, helpStr, errFileLists, run = None): #{
    """
    子菜单 选择错误列表文件进行操作
    支持最终操作回调
    """
    errLen = len(errFileLists)
    if errLen == 0:
        return
    elif errLen == 1:
        _subMenuRun(errFileLists[0], 0, run)
        return

    if helpStr.find('\t') == -1:
        helpStr = '\tSelect Error File List \033[32;1mN\033[0m, '+ helpStr +'.'

    di = 1
    while len(errFileLists) != 0:
        print("\n--- " + title + " Help ---")
        print(helpStr)
        print('\tJust Press Enter to Select Default.')
        print('\t\033[34;1mq\033[0m -- Return Main Menu.')
        print('\t\033[34;1ml\033[0m -- Show Error File List.')
        i = input(cs(title, '34;1') + '(' + str(di) + ')>> ')

        if len(i) == 0:
            i = str(di)

        if i == 'q': break
        elif i == 'l':
            listPrompt(errFileLists)
            continue

        num = int(i) if i.isdigit() else 0
        if num < 1 or num > errLen: continue

        di = 1 if di >= errLen else num + 1

        _subMenuRun(errFileLists[num - 1], num - 1, run)
#}

def _error(errFileLists): #{
    #  交互命令 - 进入错误信息输出子菜单
    def run(errFile, ind):
        efile = errFile['file'] + '.err'
        if os.path.exists(efile):
            out = shell_exec('less -XRF ' + efile)
            if out == False:
                print(cs('--- 错误文件有问题，无法查看!', '31;1'))
        else:
            print(cs('--- 发生了不可预见的错误!', '31;1'))
    _subMenu('Error', 'Show Error Message', errFileLists, run)
#}

def _tmpfile(errFileLists): #{
    #  交互命令 - 进入查看编辑文件子菜单
    _subMenu('TmpFile', 'Show tmpFile Content', errFileLists)
#}

def _source(errFileLists): #{
    #  交互命令 - 进入查看编辑原日志菜单(只有编辑错误才有效查看)
    def run(errFile, ind):
        if errFile['op'] == 'A':
            print(cs('--- 添加失败操作没有原日志内容!', '31;1'))
            return
        out = shell_exec('note list ' + errFile['id'])
        if out == False:
            print(cs('--- 没有对应的日志，建议修复或删除此错误!', '31;1'))

    _subMenu('Source', 'Show Source Content', errFileLists, run)
#}

def _delErrFile(ind, errFileLists): #{
    """
    删除错误相关文件及错误列表元素
    """
    errFile = errFileLists[ind]
    if os.path.exists(errFile['file']):
        os.unlink(errFile['file'])
    if os.path.exists(errFile['file'] + '.err'):
        os.unlink(errFile['file'] + '.err')
    del errFileLists[ind]
#}

def _open(errFileLists): #{
    #  交互命令 - 打开
    def run(errFile, ind):
        cmd = ''
        if errFile['op'] == 'A':
            cmd = 'note add -e < ' + errFile['file']
        elif errFile['op'] == 'E':
            cmd = 'note edit ' + errFile['id'] + ' -e -r ' + errFile['file']
        out = shell_exec(cmd)
        if out == True:
            _delErrFile(ind, errFileLists)
    _subMenu('Open', 'Open File Diff Edit', errFileLists, run)
#}

def _repair(errFileLists): #{
    #  交互命令 - 自动修复
    def run(errFile, ind):
        cmd = ''
        if errFile['op'] == 'A':
            cmd = 'note add < ' + errFile['file']
        elif errFile['op'] == 'E':
            cmd = 'note edit ' + errFile['id'] + ' -s -r ' + errFile['file']
        out = shell_exec(cmd)
        if out == True:
            _delErrFile(ind, errFileLists)
            print(cs('\t--- 提示: 自动修复成功! ---\n', '32;1'))
        else:
            print(cs('\t--- 自动修复失败! ---\n', '31;1'))
    _subMenu('Repair', 'Auto Repair Error', errFileLists, run)
#}

def _delete(errFileLists): #{
    #  交互命令 - 删除错误文件
    def run(errFile, ind):
        msg = 'add' if errFile['op'] == 'A' else 'edit'
        msg += ' ' + errFile['time'] + ' ' + errFile['file'] + '? '
        i = input(msg)
        if i == 'y' or i == 'Y':
            _delErrFile(ind, errFileLists)
            print(cs('\t--- 提示: 错误删除成功! ---\n', '32;1'))
    _subMenu('Delete', 'Delete Error File', errFileLists, run)
#}

def lastSaveErrorChk(runPath): #{
    """
    检测以前是否有保存失败的日志，如果有则提示并且询问是否启动处理流程
    """
    fileLists = os.listdir(runPath)
    errFileLists = []
    for filename in fileLists:
        errFileMsg = parseErrFileName(runPath, filename)
        if not errFileMsg:
            continue
        errFileLists.append(errFileMsg)

    errLen = len(errFileLists)
    if errLen == 0:
        return
    elif errLen == 1:
        errFile = errFileLists[0]
        if errFile['op'] == 'E':
            msg = '--- 日志ID为' + cs(errFile['id'], '33;1') + '编辑'
        else:
            msg = '--- 上一次添加日志'
        msg += '失败，是否尝试自动修复? (y/N): '
        i = input(msg)
        if i == 'y' or i == 'Y':
            _repair(errFileLists)
            return

    listPrompt(errFileLists)

    cmdDict = {
                'list': listPrompt, 'l': listPrompt, '1': listPrompt,
                'error': _error, 'e': _error, '2': _error,
                'tmpfile': _tmpfile, 't': _tmpfile, '3': _tmpfile,
                'source': _source, 's': _source, '4': _source,
                'open': _open, 'o': _open, '5': _open,
                'repair': _repair, 'r': _repair, '6': _repair,
                'delete': _delete, 'd': _delete, '7': _delete,
              }

    while len(errFileLists) != 0:
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

    #  len(errFileLists) != 0 and exit(0)
    exit(0)
#}
