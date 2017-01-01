import os, shlex
import tempfile, subprocess
import kyo

def editContent(content=None):
    """ Edit the content with vi editor, the input
    'content' is byte, the returned one is byte also
    """
    tmpfile = kyo.creatRunFile()
    if content:
        tmpfile.write(content)
        tmpfile.flush()
    if kyo.isPipe and kyo.isEditor  \
            and kyo.kconfig['editor'].find('vim ') != -1:
        cmd = 'vim - "+r' + tmpfile.name + '" "+w!' + tmpfile.name + '"'
        cmd += ' ' + kyo.kconfig['vimopt']
    else:
        cmd = kyo.kconfig['editor'] + tmpfile.name
    p = subprocess.Popen(shlex.split(cmd))
    p.communicate()
    p.wait()
    content = open(tmpfile.name, 'rb').read()
    return content
