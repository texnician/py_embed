#ifndef _SWIG_H_
#define _SWIG_H_

#ifdef __cplusplus
extern "C"
#endif
MTD_API
#if PY_VERSION_HEX >= 0x03000000
PyObject*
#else
void
#endif
init_mtd_lib(void);

#endif
