import re
import sys, os
from timeutils import isodatetime
from time import *
import traceback
from ifix import lastSaveErrorChk

global kconfig, interactive, isEdit, isEditor, isPipe, stdinNo, isAdd
global runFile, logID

interactive = False
isEdit      = False
isAdd       = False
isEditor    = False
isPipe      = False
stdinNo     = False
runFile     = False
logID       = False

def parseArgs(args): #{
    """
    处理程序参数
    """
    ln = len(args)
    #  如果没有参数则进入单行列表
    if ln == 1:
        args.extend(['list', '-f', '\033[33m%i\033[37m(%mtk)\033[0m: %s'])

    #  如果是编辑日志，修改编辑标识，如果没有参数则默认编辑最后一条日志
    global isEdit
    if ln >= 2 and args[1] == 'edit':
        isEdit = True
        ln == 2 and args.append('-1')

    #  如果是添加日志，修改添加标识
    global isAdd
    if ln >= 2 and args[1] == 'add':
        isAdd = True

    #  判断是否有-e选项，修改标识
    global isEditor
    if '-e' in args:
        isEditor = True
        args.remove("-e")

    #  判断是否需要交互收集日志信息
    global interactive
    if '-i' in args:
        interactive = True
        args.remove("-i")
#}

def creatRunFile(tmpfile): #{
    global runFile
    if logID:
        runFile += logID[0:6]
    runFile += tmpfile.replace('/', '_') + '.lock'
    try:
        fp = open(runFile, 'w+')
        fp.close()
    except:
        quit(runFile + '\n错误: 锁文件生成失败!', 1)
#}

def runConfig(config): #{
    """
    运行配置，添加或编辑状态记录
    """
    if (isPipe and not isEditor) or not (isAdd or isEdit):
        return

    global runFile
    runPath = config['dataDir'] + '/run'
    if not os.path.exists(runPath):
        os.mkdir(runPath)

    lastSaveErrorChk(runPath)

    opTxt = 'add' if isAdd else ''
    runFile = runPath + '/' + opTxt
#}

def init(config, args): #{
    """
    初始化操作，截取程序参数处理
    """
    parseArgs(args)

    #  获取处理配置文件的选项
    getConf(config)

    #  判断数据来源是否为管道或标准输入
    global stdinNo
    global isPipe
    stdinNo = sys.stdin.fileno()
    isPipe = not os.isatty(stdinNo)

    if isPipe and isEdit:
        quit('错误: 编辑不支持管道或标准输入!', 1)

    #  运行状态记录配置
    runConfig(config)

    return kconfig
#}

def listDate(second=None): #{
    """
    单行列表时间显示格式
    """
    if not second: second = time.time()
    nowYear = strftime("%Y", localtime(time()))
    year = strftime("%Y", localtime(second))
    if nowYear == year:
        return strftime('%m-%d %H:%M', localtime(second))
    return strftime('%y-%m-%d %H', localtime(second))
#}

def getConf(config):#{
    """
    获取kyo自定义配置信息
    默认字段值及文件头信息定界符设置
    """
    global kconfig

    kconfig = {'tag': '', 'scene': '', 'people': '', 'cline': 10,
               'editor': 'vim ', 'vimopt': '"+set ff=unix" "+set foldlevel=0"',
               'delim': '# Log Info {\n%s\n# Log Info }'}

    confKeys = config.keys()
    kconfig['tag'] = 'defaultTag' in confKeys and config['defaultTag']
    kconfig['scene'] = 'defaultScene' in confKeys and config['defaultScene']
    kconfig['people'] = 'defaultPeople' in confKeys and config['defaultPeople']
    kconfig['delim'] = 'infoDelim' in confKeys and config['infoDelim']
    kconfig['cline'] = 'listCL' in confKeys and config['listCL']
    kconfig['vimopt'] = 'vimOpt' in confKeys and config['vimOpt']
    kconfig['editor'] = 'editor' in confKeys and config['editor'] + ' '
    if kconfig['editor'] == 'vim ':
        kconfig['editor'] += kconfig['vimopt'] + ' '
    kconfig['time'] = isodatetime()

    return kconfig
#}

def parseInfoString(info, args):#{

    time = args['time'] if args['time'] else info['time']
    tag = args['tag'] if args['tag'] else info['tag']
    scene = args['scene'] if args['scene'] else info['scene']
    people = args['people'] if args['people'] else info['people']

    loginfo = '#    time   = ' + time
    if scene:
        loginfo += '\n#    scene  = ' + scene
    if people:
        loginfo += '\n#    people = ' + people
    if tag:
        loginfo += '\n#    tag    = ' + tag

    return kconfig['delim']%(loginfo)
#}

def infoPad(info): #{
    """
    检查文件头字段填充必备字段值
    """
    if not 'tag' in info:
        info['tag'] = ''
    if not 'scene' in info:
        info['scene'] = ''
    if not 'people' in info:
        info['people'] = ''
    if not 'time' in info:
        info['time'] = ''

    return info
#}

def editHeadInfo(subject, data, args):#{
    """
    编辑打开时对比文件头信息重新生成(如果文件头存在才生成)
    """
    if interactive:
        subject = subject.encode()
        if data:
            subject += b'\n\n' + data
        return subject

    dataStr = data if isinstance(data, str) else data.decode()
    info = parseInfo(dataStr)
    if len(info) != 0:
        loginfo = parseInfoString(infoPad(info), args)
        #  quit(loginfo, 0)
        reg = kconfig['delim']%('(.*)')
        reg = reg.replace(' ', ' ?')
        data = re.sub(re.compile(reg, re.S|re.I), loginfo, dataStr)

    data = data if isinstance(data, bytes) else data.encode()
    return subject.encode() + b'\n\n' + data
#}

def addHeadInfo(subject, data, args):#{
    """
    添加新日志获取文件头字段信息
    根据命令参数及默认值自动生成文件头信息
    """
    if interactive:
        if not subject:
            return b''
        subject = subject.encode()
        if data:
            subject += b'\n\n' + data.encode()
        return subject

    if not subject:
        subject = args['tag'] if args['tag'] else kconfig['tag']
    loginfo = subject + '\n\n' + parseInfoString(kconfig, args) + '\n\n' + data

    return loginfo.encode()
#}

def stripHead(row):#{
    """
    列表内容过滤文件头信息
    """
    if not 'data' in row:
        return
    reg = kconfig['delim']%('(.*)')
    reg = reg.replace(' ', ' ?')
    row['data'] = re.sub(re.compile(reg, re.S|re.I), '', row['data'])
#}

def stripEmptyLine(row, limitLine = True):#{
    """
    列表内容去除空行及限制内容显示行数
    """
    if not 'data' in row:
        return

    msgLine = row['data'].split('\n')
    count = 0
    newStr = ""
    for line in msgLine:
        if len(line) == 0:
            continue
        count = count + 1
        if limitLine and count == kconfig['cline']:
            break
        newStr += line + '\n'
    row['data'] = newStr.rstrip('\n')
    #  quit(row['data'])
#}

def rGenData(data): #{
    """
    重建列表生成嚣数据并且去除空行和限制显示内容行数
    """
    limitLine = False if len(data) == 1 else True
    for row in data:
        stripEmptyLine(row, limitLine)
        yield row
#}

def formater(data): #{
    """
    将列表数据获取去除空行，限制显示行数以及去除文件头信息
    """
    lData = []
    for row in data:
        stripHead(row)
        lData.append(row)

    return rGenData(lData)
#}

def parseInfo(data): #{
    """
    解析文件头返回字段字典
    """
    reg = kconfig['delim']%('(.*)')
    reg = reg.replace(' ', ' ?')
    #  print(data)
    #  print(reg, type(data))
    #  print(re.sub(re.compile(reg, re.S|re.I), '', data))
    info = re.findall(reg, data, re.S|re.I)
    if len(info) == 0:
        return []

    fields = {}
    for line in info.pop(0).split('\n'):
        line = line.lstrip('#').strip()
        if len(line) == 0:
            continue
        #  print(line)

        line = line.split('=')
        l  = len(line)
        if l <= 1 or l > 2:
            continue
        fields[line[0].strip()] = line[1].strip()

    return fields
#}

def readMany(dataInfo, args): #{
    """
    读取日志文件的特殊段并解析日志文件信息字段
    """
    if len(dataInfo) == 0:
        return args

    #  print(args)
    #  quit(dataInfo)
    if not 'tag' in dataInfo:
        dataInfo['tag'] = args['tag']
    if not 'scene' in dataInfo:
        dataInfo['scene'] = args['scene']
    if not 'people' in dataInfo:
        dataInfo['people'] = args['people']
    if not 'time' in dataInfo:
        dataInfo['time'] = args['time']

    return dataInfo
#}

def splitSubject(message): #{
    splitStr = message.find('\n\n') == -1 and '\\n\\n' or '\n\n'
    msgLines = message.rstrip('\n').split(splitStr)
    subject  = msgLines.pop(0)
    data = '\n\n'.join(msgLines)
    return subject, data
#}

def getTmpFile(ext = ''): #{
    """
    从锁文件名中截取临时文件名
    """
    tmpfile = os.path.basename(runFile).split('.lock' + ext).pop(0)
    i = tmpfile.find('_')
    return False if i == -1 else tmpfile[i:].replace('_', '/')
#}

def quit(errMsg = False, errCode = 0): #{
    """
    程序退出函数，可以退出前打印信息和指定程序错误码
    如果不正常退出则保存锁文件等待下一次处理
    """
    if errCode != 0:
        traceback.print_exc()

    #  print("kyoQuit: ", runFile, "errCode: ", errCode)

    if errMsg:
        print(errMsg, file = sys.stderr)

    if runFile and os.path.exists(runFile):
        tmpfile = getTmpFile()
        os.unlink(runFile)
        if errCode == 0:
            if os.path.exists(tmpfile):
                os.unlink(tmpfile)
        else:
            traceback.print_exc(file = open(runFile + '.err', 'w+'))
            print('存储失败, 数据存储于临时文件: ', tmpfile, file = sys.stderr)

    exit(errCode)
#}
