
function! KyoLogRepairCommonOpt()
    exec 'normal gg'
    exec 'normal dd'
    setlocal buflisted
    setlocal bufhidden=delete
    setlocal buftype=nofile
    setlocal nomodifiable
    setlocal noswapfile
    exec 'wincmd w'
endfunction

function! KyoLogRepairOpenSet(filename)
    if filereadable(a:filename.'.err')
        exec 'botright 5 split 错误信息'
        exec 'r '.a:filename.'.err'
        call KyoLogRepairCommonOpt()
    endif
    exec 'leftabove vert diffsplit 编辑失败内容'
    exec 'r '.a:filename
    exec 'diffupdate'
    call KyoLogRepairCommonOpt()
    exec 'redraw!'
endfunction

