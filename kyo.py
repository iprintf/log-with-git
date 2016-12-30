import re
from timeutils import isodatetime
from time import *

global kconfig

interactive = False

def init(config, args): #{
    ln = len(args)
    if ln == 1:
        args.extend(['list', '-f', '\033[33m%i\033[37m(%mtk)\033[0m: %s'])

    if ln == 2 and args[1] == 'edit':
        args.append('-1')

    getConf(config)

    global interactive
    if '-i' in args:
        interactive = True
        args.remove("-i")

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
               'delim': '# Log Info {\n%s\n# Log Info }'}

    confKeys = config.keys()
    kconfig['tag'] = 'defaultTag' in confKeys and config['defaultTag']
    kconfig['scene'] = 'defaultScene' in confKeys and config['defaultScene']
    kconfig['people'] = 'defaultPeople' in confKeys and config['defaultPeople']
    kconfig['delim'] = 'infoDelim' in confKeys and config['infoDelim']
    kconfig['cline'] = 'listCL' in confKeys and config['listCL']
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

def editHeadInfo(data, args):#{
    """
    编辑打开时对比文件头信息重新生成(如果文件头存在才生成)
    """
    if interactive:
        return data

    dataStr = data.decode()
    info = parseInfo(dataStr)
    if len(info) == 0:
        return data

    loginfo = parseInfoString(infoPad(info), args)

    #  print(loginfo)
    #  exit(0)
    reg = kconfig['delim']%('(.*)')
    reg = reg.replace(' ', ' ?')
    return re.sub(re.compile(reg, re.S|re.I), loginfo, dataStr).encode()
#}

def addHeadInfo(args):#{
    """
    添加新日志获取文件头字段信息
    根据命令参数及默认值自动生成文件头信息
    """
    if interactive:
        return b''

    tag = args['tag'] if args['tag'] else kconfig['tag']
    loginfo = tag + '\n\n' + parseInfoString(kconfig, args)

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
    #  print(row['data'])
    #  exit(0)
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
    #  print(dataInfo)
    #  exit(0)
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
