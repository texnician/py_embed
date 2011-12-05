%module(directors="1") mtd_lib

#define _SWIG_ 1

%{
#include <memory>
#include "mtd_lib.h"    
#include "idb_cmd.h"
#include "swig.h"
#include "stackless_client.h"
%}
%include <windows.i>
%include <pybuffer.i>
%pybuffer_mutable_string(char *out_buf);
%pybuffer_string(char *in_buf);

%include "std_string.i"
%include "stl.i"
namespace std {
%template(vectori) vector<int>;
}

%include <std_shared_ptr.i>
%shared_ptr(IHWDBCursor)

%feature("director") ScriptSkillCallback;

%feature("director:except") {
    if ($error != NULL) {
        PyErr_Print();
    }
}

%wrapper %{
  // ... code in wrapper section ...
%}


%extend SkillCaller {
  int* CallVoid()
  {
    $self->CallVoid();
    return NULL;
    
  }
  }
%include "exception.i"

%exception SkillCaller::CallVoid {
   try {
        $action
    } catch(RangeError) {
        SWIG_exception(SWIG_ValueError, "Range Error");
    } catch(DivisionByZero) {
        SWIG_exception(SWIG_DivisionByZero, "Division by zero");
    } catch(OutOfMemory) {
        SWIG_exception(SWIG_MemoryError, "Out of memory");
    } catch(...) {
        SWIG_exception(SWIG_RuntimeError,"Unknown exception");
    }
 }

%inline {
PyObject* SWIGNewCliEvent(CliEvent* ev)
{
  PyObject* self = NULL;
  PyObject* py_ev = SWIG_NewPointerObj(SWIG_as_voidptr(ev), SWIGTYPE_p_CliEvent, SWIG_POINTER_OWN |  0 );
  return py_ev;
}
 
CliEvent* SWIGConvertCliEvent(PyObject* py_ev)
{
  void* ev;
  SWIG_ConvertPtr(py_ev, &ev, SWIGTYPE_p_CliEvent,  0);
  return (CliEvent*)ev;
}
 
PyObject* SWIGNewStacklessClient(StacklessClient* cli)
{
  PyObject* self = NULL;
  PyObject* py_cli = SWIG_NewPointerObj(SWIG_as_voidptr(cli), SWIGTYPE_p_StacklessClient, 0);
  return py_cli;
}
}
%ignore SkillCaller::CallVoid;

%include "mtd_lib.h"


%include "idb_cmd.h"
%include "stackless_client.h"
