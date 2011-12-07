#include "stdio.h"
#include "Python.h"
#include "stackless.h"
#include "stackless_api.h"
#include "stackless_client.h"

PyObject* StacklessClient::main_loop_ = NULL;

StacklessClient::StacklessClient(int roleid, PyObject* ch)
    : roleid_(roleid), channel_(ch), is_quit_(false)
{
    Py_INCREF(channel_);
}

StacklessClient::~StacklessClient()
{
    Py_XDECREF(channel_);
}

int StacklessClient::SetupTasklet()
{
    if (StacklessClient::main_loop_ == NULL) {
        PyObject* module = PyImport_ImportModule("mtd_lib");
        if (module) {
            PyObject* func = PyObject_GetAttrString(module, "MainLoop");
            if (func) {
                StacklessClient::main_loop_ = func;
                Py_XDECREF(module);
            }
            else {
                if (PyErr_Occurred()) {
                    PyErr_Print();
                }
                Py_XDECREF(module);
                return -1;
            }
        }
        else {
            if (PyErr_Occurred()) {
                PyErr_Print();
                return -1;
            }
        }
    }
    PyTaskletObject* task = PyTasklet_New(&PyTasklet_Type, StacklessClient::main_loop_);
    if (task) {
        PyObject *py_cli = SWIGNewStacklessClient(this);
        PyObject* args = Py_BuildValue("(O)", py_cli);
        if (PyTasklet_Setup(task, args, NULL) != 0) {
            if (PyErr_Occurred()) {
                PyErr_Print();
            }
            Py_XDECREF(args);
            Py_XDECREF(py_cli);
            Py_XDECREF(task);
            return -1;
        }
        else {
            Py_XDECREF(args);
            Py_XDECREF(py_cli);
            Py_XDECREF(task);
            return 0;
        }
    }
    else {
        if (PyErr_Occurred()) {
            PyErr_Print();
        }
        return -1;
    }
}

bool StacklessClient::IsQuit() const
{
    return is_quit_;
}

void StacklessClient::Quit()
{
    is_quit_ = true;
}

PyObject* StacklessClient::Receive()
{
    return PyObject_CallMethod(channel_, "receive", "()");
}

int StacklessClient::Send(PyObject* ev)
{
    PyObject_CallMethod(channel_, "send", "(O:cli_event)", ev);
    return 0;
}

int StacklessClient::RoleId()
{
    return roleid_;
}

void MainLoop(StacklessClient* self)
{
    while(!self->IsQuit()) {
        PyObject* py_ev = self->Receive();
        if (py_ev) {
            CliEvent *ev = SWIGConvertCliEvent(py_ev);
            switch (ev->type_) {
            case 0:
                self->Quit();
                printf("Normal quit %d\n", self->RoleId());
                break;
            default:
                // printf("%d type: %d, msg: %s\n", self->RoleId(), ev->type_, ev->msg_.c_str());
                break;
            }
            Py_XDECREF(py_ev);
        }
        else {
            self->Quit();
            return;
        }
    }
}
