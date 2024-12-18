---
title: different DSPF files for each corner
date: 2023-01-29 22:25:20
tags:
categories:
- cad
---

Create a new file with an extension **scs** like *myDSPF_Files.scs*

```
* DSPF files to use with Corner Definitions
* This is an example file showing how to define different dspf files for different corners
* using model files for individual components as the
* building blocks.
simulator lang=spectre
library dspf_files_corners

section rctyp_25
dspf_include "DSPF_RC_TYPNOM25.spf"
endsection rctyp_25

section rctyp_125
dspf_include "DSPF_RC_TYP125.spf"
endsection rctyp_125

section rcworst_25
dspf_include "DSPF_RC_WORSE25.spf"
end section rcworst_25

section rcworst_125
dspf_include "DSPF_RC_WORSE125.spf"
end section rcworst_125

endlibrary dspf_files_corners
```

Add the file created above ‘*myDSPF_File.scs*’  in ‘*Add/Edit Model Files*’ of Corners setup form

![image-20230129223248655](dspf-in-corner/image-20230129223248655.png)
