import re
from timeutils import isodatetime

global kconfig

interactive = False

def init(config, args):
    global interactive

    getConf(config)
    if '-i' in args:
        interactive = True
        args.remove("-i")

def getConf(config):#{
    """
    获取kyo自定义配置信息
    默认字段值及文件头信息定界符设置
    """
    global kconfig

    kconfig = {'tag': '', 'scene': '', 'people': '',
               'delim': '# Log Info {\n%s\n# Log Info }'}

    confKeys = config.keys()
    kconfig['tag'] = 'defaultTag' in confKeys and config['defaultTag']
    kconfig['scene'] = 'defaultScene' in confKeys and config['defaultScene']
    kconfig['people'] = 'defaultPeople' in confKeys and config['defaultPeople']
    kconfig['delim'] = 'infoDelim' in confKeys and config['infoDelim']
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

def stripInfo(row):#{
    """
    列表不显示文件头信息
    """
    if not 'data' in row:
        return
    reg = kconfig['delim']%('(.*)')
    reg = reg.replace(' ', ' ?')
    row['data'] = re.sub(re.compile(reg, re.S|re.I), '', row['data'])
#}

def parseInfo(data): #{
    """
    解析文件头返回字段字典
    """
    reg = kconfig['delim']%('(.*)')
    reg = reg.replace(' ', ' ?')
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

    if not 'tag' in dataInfo:
        dataInfo['tag'] = args['tag']
    if not 'scene' in dataInfo:
        dataInfo['scene'] = args['scene']
    if not 'people' in dataInfo:
        dataInfo['people'] = args['people']
    if not 'time' in dataInfo:
        dataInfo['time'] = args['time']

    #  print(args)
    #  print(data)
    #  exit(0)

    return dataInfo
#}
