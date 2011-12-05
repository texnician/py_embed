#ifndef _STACKLESS_CLIENT_
#define _STACKLESS_CLIENT_

#include "mtd_lib.h"
#include "Python.h"
#include "stackless.h"

class MTD_API StacklessClient
{
private:
    static PyObject *main_loop_;
    PyObject* channel_;
    int roleid_;
    bool is_quit_;
public:
    StacklessClient(int roleid, PyObject* ch);
    
    virtual ~StacklessClient();

    int SetupTasklet();

    bool IsQuit() const;

    PyObject* Receive();

    int Send(PyObject* ev);
    
    void Quit();
};

class CliEvent
{
public:
    virtual ~CliEvent()
        {}
    int type_;
    std::string msg_;
};

void MTD_API MainLoop(StacklessClient* self);

MTD_API PyObject* SWIGNewCliEvent(CliEvent* ev);
MTD_API CliEvent* SWIGConvertCliEvent(PyObject* py_ev);
MTD_API PyObject* SWIGNewStacklessClient(StacklessClient* cli);


#endif  // _STACKLESS_CLIENT_
