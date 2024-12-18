
You will need to do this to add cedar sim registry:
```
pkg> registry add https://github.com/CedarEDA/PublicRegistry
pkg> registry add General
```
Follow the instructions on setting up CedarSim on https://github.com/CedarEDA/CedarSim.jl 
Pay Special attention to this subnote in the instructions. I am using this build of julia.
* You may set up the blessed version of julia via running bash contrib/julia_build/juliaup_cedar.sh to get a +cedar channel available in juliaup. Then start julia via julia +cedar --project=. to run that blessed release with CedarSim as the current project.
* Install PyJulia (if you got this far on this minimal instruction list - I believe in you!)
