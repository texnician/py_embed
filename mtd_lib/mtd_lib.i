%module(directors="1") mtd_lib

#define _SWIG_ 1

%{
#include <memory>
#include "mtd_lib.h"    
#include "idb_cmd.h"
#include "swig.h"
%}
%include <windows.i>
%include <pybuffer.i>
%pybuffer_mutable_string(char *out_buf);
%pybuffer_string(char *in_buf);

%include "std_string.i"
%include stl.i
namespace std {
%template(vectori) vector<int>;
}

%include <std_shared_ptr.i>
%shared_ptr(IHWDBCursor)

%feature("director") ScriptSkillCallback;

%include "mtd_lib.h"
%include "idb_cmd.h"
