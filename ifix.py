import os
from time import *

def parseErrFileName(runPath, filename): #{
    """
    判断是否为运行文件并且解析文件名提取信息
    """
    if filename.find('.') != -1 or len(filename) != 12:
        return False

    op = filename[0:1]
    if not (op == 'E' or op == 'A'):
        return False

    res = {}
    res['op'] = op
    res['id'] = filename[1:7] if op == 'E' else '      '
    res['file'] = runPath + '/' + filename
    s = os.stat(res['file'])
    res['time'] = strftime("%Y-%m-%d %H:%M", localtime(s.st_mtime))
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
        msg += cs(errfile['id'], '33') + ' '
        msg += cs(errfile['op'], '36;1') + '  '
        msg += errfile['time'] + ' '
        msg += errfile['file'].replace(os.environ['HOME'], '~')
        print(msg)
        n = n + 1
#}

def cs(content, color = '0'): #{
    #  组合带颜色的字符串
    return '\033[' + color + 'm' + str(content) + '\033[0m'
#}

def _subMenuRun(errFile, ind, run = None): #{
    if run == None:
        if os.path.exists(errFile['file']):
            os.system('less -XRF ' + errFile['file'])
        else:
            print(cs(errFile['file'] + ' 文件已经不存在啦!', '31;1'))
        return
    run(errFile, ind)
#}


def _subMenu(title, helpStr, errFileLists, run = None): #{
    """
    子菜单 选择错误列表文件进行操作
    支持最终操作回调
    """
    errLen = len(errFileLists)
    if errLen == 1:
        _subMenuRun(errFileLists.pop(0), 0, run)
        return

    if helpStr.find('\t') == -1:
        helpStr = '\tSelect Error File List \033[32;1mN\033[0m, '+ helpStr +'.'
    while True:
        print("\n--- " + title + " Help ---")
        print(helpStr)
        print('\t\033[34;1mq\033[0m -- Return Main Menu.')
        print('\t\033[34;1ml\033[0m -- Show Error File List.')
        i = input(cs(title, '34;1') + '>> ')
        if i == 'q': break
        elif i == 'l':
            lastSaveErrorPormpt(errFileLists)
            continue

        num = int(i) if i.isdigit() else 0
        if num < 1 or num > errLen: continue

        _subMenuRun(errFileLists[num - 1], num - 1, run)
#}

def _list(errFileLists): #{
    #  交互命令 - 列出错误文件
    lastSaveErrorPormpt(errFileLists)
#}

def _error(errFileLists): #{
    #  交互命令 - 进入错误信息输出子菜单
    def run(errFile, ind):
        efile = errFile['file'] + '.err'
        if os.path.exists(efile):
            os.system('less -XRF ' + efile)
        else:
            print(cs('发生了不可预见的错误!', '31;1'))
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
            print(cs('添加失败操作没有原日志内容!', '31;1'))
            return
        os.system('log list ' + errFile['id'])
    _subMenu('Source', 'Show Source Content', errFileLists, run)
#}

def _open(errFileLists): #{
    #  交互命令 - 打开
    def run(errFile, ind):
        if errFile['op'] == 'A':
            print(cs('添加失败操作没有原日志内容!', '31;1'))
            return
        os.system('log list ' + errFile['id'])
    _subMenu('Source', 'Show Source Content', errFileLists, run)
#}

def _repair(errFileLists): #{
    #  交互命令 - 自动修复
    def run(errFile, ind):
        if errFile['op'] == 'E':
            print(cs('编辑失败操作没有原日志内容!', '31;1'))
            return
        os.system('log add  < ' + errFile['file'])
        if os.path.exists(errFile['file']):
            os.unlink(errFile['file'])
        if os.path.exists(errFile['file'] + '.err'):
            os.unlink(errFile['file'] + '.err')
        del errFileLists[ind]
    _subMenu('Repair', 'Auto Repair Error', errFileLists, run)
#}

def _delete(errFileLists): #{
    #  交互命令 - 删除错误文件
    def run(errFile, ind):
        msg = 'add' if errFile['op'] == 'A' else 'edit'
        msg += ' ' + errFile['time'] + ' ' + errFile['file'] + '? '
        i = input(msg)
        if i == 'y' or i == 'Y':
            if os.path.exists(errFile['file']):
                os.unlink(errFile['file'])
            if os.path.exists(errFile['file'] + '.err'):
                os.unlink(errFile['file'] + '.err')
            del errFileLists[ind]
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
