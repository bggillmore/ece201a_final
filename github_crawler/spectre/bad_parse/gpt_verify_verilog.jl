err_dir = "bad_parse"

# Create the error directory if it doesn't exist
if !isdir(err_dir)
    mkdir(err_dir)
end

# Loop through each file in the current directory
for fname in readdir()
    # Get the full file path
    full_path = joinpath(pwd(), fname)
    
    # Check if it's a file and not a directory
    if isfile(full_path)
        try
            # Try to parse the file
            SpectreNetlistParser.parsefile(full_path)
        catch e
            # If parsing throws an error, move the file to the error directory
            println("Error parsing file: $fname. Moving to $err_dir.")
            mv(full_path, joinpath(err_dir, fname))
        end
    end
end
