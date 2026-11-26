-- 用 PowerPoint 导出 PDF 或 MP4。文件先由 shell 用 `open -a` 打开（系统自动授予该文件的访问权限），
-- 这里只按文件名找到演示文稿并另存到固定导出目录 out/_pp（只需授权一次）。
on run argv
	set fname to item 1 of argv
	set outPath to item 2 of argv
	set mode to item 3 of argv
	tell application "Microsoft PowerPoint"
		set p to missing value
		repeat 90 times
			try
				set p to presentation fname
				exit repeat
			end try
			delay 1
		end repeat
		if p is missing value then error "PowerPoint 没有打开 " & fname
		if mode is "pdf" then
			save p in (POSIX file outPath) as save as PDF
			close p saving no
		else
			save p in (POSIX file outPath) as save as movie
		end if
	end tell
end run
