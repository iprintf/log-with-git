import os, subprocess
import kyo

def checkEditRun(ids): #{
    """
    检测文档是否正在编辑
    """
    cmd = 'ps -e --format cmd | grep "vim.*' + ids + '" | grep -v grep'
    out = shell_exec(cmd, False)
    #  print(out, type(out), isinstance(out, bool))
    if not isinstance(out, bool) or out == True:
        return True
    return False
#}

def cs(content, color = '0'): #{
    """
    组合带颜色的字符串
    """
    return '\033[' + color + 'm' + str(content) + '\033[0m'
#}

def shell_exec(cmd, out = True): #{
    """
    执行shell命令
    判断shell命令返回值
        返回值为0则返回标准输出, 标准输出为空返回True
        返回值不为0则返回False
    """
    out = None if out else subprocess.PIPE
    p = subprocess.Popen(cmd, shell = True, stdout = out)
    p.wait()
    if p.returncode != 0:
        return False
    if out != None:
        so = p.stdout.read()
        if len(so) != 0:
            return so
    return True
#}

def editContent(content=None):
    """ Edit the content with vi editor, the input
    'content' is byte, the returned one is byte also
    """
    tmpfile = kyo.creatRunFile()
    if content:
        tmpfile.write(content)
        tmpfile.flush()

    isVim = True if kyo.kconfig['editor'][0:4] == 'vim ' else False
    if kyo.isPipe and kyo.isEditor and isVim:
        cmd = 'vim - "+r' + tmpfile.name + '" "+w!' + tmpfile.name + '"'
        cmd += ' ' + kyo.kconfig['vimopt']
    else:
        cmd = kyo.kconfig['editor'] + tmpfile.name

    out = shell_exec(cmd)
    if out == False:
        return content

    content = open(tmpfile.name, 'rb').read()

    if kyo.isPipe and kyo.isAdd:
        return content[0:-1]

    return content
