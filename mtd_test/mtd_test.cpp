// mtd_test.cpp : ¶¨Òå¿ØÖÆÌ¨Ó¦ÓÃ³ÌÐòµÄÈë¿Úµã¡£
//

#include "stdafx.h"
#include "mtd_lib.h"
#include <stdint.h>
#include "Python.h"
#include "swig.h"
#include "idb_cmd.h"

class TestCursor : public IHWDBCursor
{
public:
    virtual ~TestCursor() {}

    virtual int GetRecordCount(void) { return 0; }
    
    virtual int GetFieldCount(void) { return 0; }
    
    virtual bool GetRecord(void) { return true; } 
    
    virtual const char * GetFieldValue(int index) { return "test"; }
    
    virtual int GetFieldLength(int index) { return 10; }

    virtual const char* GetFieldValueByName(const char *name) { return "10"; }

    virtual int GetFieldLengthByName(const char *name) { return 1; }
};

#include <windows.h>
bool py_init = false;
bool allow_exit = false;

PyObject *test_obj;

void TestException()
{
    PyObject *module, *scheduler;
    module = PyImport_ImportModule("test_exception");
    scheduler = PyObject_GetAttrString(module, "ScheduleTasklets");
    while (true) {
        PyObject *ret = PyObject_CallFunction(scheduler, "()");
        if (!ret) {
            PyErr_Print();
            break;
        }
        Py_XDECREF(ret);
        Sleep(1);
    }
}

DWORD WINAPI ThreadProc(LPVOID lpParam)
{
    printf("thread state %s initialized\n", PyEval_ThreadsInitialized() ? "is" : "is not");
    
    PyEval_InitThreads();

    printf("thread state %s initialized\n", PyEval_ThreadsInitialized() ? "is" : "is not");
    
    Py_Initialize();
    init_mtd_lib();

    py_init = true;
    
    TestException();
    
    PyObject *pName, *pModule, *pDict, *pFunc;

    // Py_BEGIN_ALLOW_THREADS
    int64_t a = 111111;

    auto x = strtoul("4294967295", (char **)NULL, 10);
    
	{
		std::vector<int> vci(GetConstIntVec());
	}
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    PyRun_SimpleString("print('blueblueblue')");
    PyGILState_Release(gstate);
	{
		std::vector<int> vi(GetIntVec());
	}
	{
		std::vector<std::string> v2 = GetConstStringVec();
	}
	{
		std::vector<std::string> v1 = GetStringVec();
	}
    // Py_END_ALLOW_THREADS
        
    PyObject* module = PyImport_ImportModule("hw");
    PyObject* func = PyObject_GetAttrString(module, "MakeTestObj");
    test_obj = PyObject_CallFunction(func, "()");
    Py_XDECREF(module);
    Py_XDECREF(func);

	// SWIG_init();
    
    /* Perform Python actions here. */
    PyRun_SimpleString("print('i am sub thread!')");
    /* evaluate result or handle exception */
    
    pName = PyString_FromString("mtd_lib");
    /* Error checking of pName left out */
    pModule = PyImport_Import(pName);
    PyObject* pHwName = PyString_FromString("hw");
    PyObject* pHw = PyImport_Import(pHwName);
	if (pHw == NULL) {
		PyErr_Print();
		exit(1);
	}
    PyObject* pHwDict = PyModule_GetDict(pHw);

	PyObject* pTest = PyDict_GetItemString(pHwDict, "TestCallback");

    if (PyCallable_Check(pTest)) {
        PyObject_CallObject(pTest, NULL);
    }
    else {
        PyErr_Print();
    }

	SkillData d;
	d.data.push_back(1);
	d.data.push_back(2);
	d.data.push_back(3);
	auto result = g_caller->Call(d);
    g_caller->CallVoid();

    Py_DECREF(pName);
    Py_DECREF(pHwName);
    Py_DECREF(pModule);
    Py_DECREF(pHw);

    while (!allow_exit) {
        PyRun_SimpleString("pass");
    }

	return 0;
}

int _tmain(int argc, _TCHAR* argv[])
{
    HANDLE hThread;
    DWORD dwThreadId;
    
    hThread = ::CreateThread (
        NULL, 
        NULL, 
        ThreadProc,
        NULL,
        0,
        &dwThreadId);
    printf(" Now another thread has been created. ID = %d \n", dwThreadId);

    while (!py_init) {
        Sleep(1);
    }

    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    PyRun_SimpleString("print('i am main thread!')");
    PyGILState_Release(gstate);

    allow_exit = true;
    
    while(::WaitForSingleObject (hThread, 20) != WAIT_OBJECT_0) {}
    ::CloseHandle (hThread);

    return 0;
}
