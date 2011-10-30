%module mtd_lib

#define _SWIG_ 1

%{
#include "mtd_lib.h"    
#include "idb_cmd.h"
%}
%include <windows.i>
%include <pybuffer.i>
%pybuffer_mutable_string(char *out_buf);
%pybuffer_string(char *in_buf);


%include "mtd_lib.h"
%include "idb_cmd.h"
