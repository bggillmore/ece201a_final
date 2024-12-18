# mkdir
#
err_dir = "bad_parse"
if !isdir(err_dir)
    mkdir(err_dir)
end
for fname in readdir()
    try
        SpectreNetlistParser.parsefile(fname)
    catch e
        mv(fname, err_dir)
    end
end
