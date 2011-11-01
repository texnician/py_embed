// mtd_test.cpp : 定义控制台应用程序的入口点。
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
int _tmain(int argc, _TCHAR* argv[])
{
	int64_t a = 111111;

    auto x = strtoul("4294967295", (char **)NULL, 10);
    
	{
		std::vector<int> vci(GetConstIntVec());
	}
	{
		std::vector<int> vi(GetIntVec());
	}
	{
		std::vector<std::string> v2 = GetConstStringVec();
	}
	{
		std::vector<std::string> v1 = GetStringVec();
	}

    PyObject *pName, *pModule, *pDict, *pFunc;
    
    Py_Initialize();
	init_mtd_lib();
	// SWIG_init();
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
    
	return 0;
}
