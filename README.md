# XREF explorer

Script which works on top of HexRays decompiler via [HRAST](https://github.com/sibears/HRAST).

### Description

This isn't a detailed but brief description of how it works.

This script is a try to solve problem of resolving virtual functions calls inside of binary files. In hexrays view virtual calls looks like sequence of tokens - `cot_call`, `cot_cast`(optional), `cot_memptr`, then other tokens (it's not interesting for us). In c-style it looks like `foo.vtable->virtual_function(...)`. So this script is trying to solve the problem, matching pieces of function's AST in HexRays and post-processing it then.
