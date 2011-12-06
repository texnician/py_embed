CXX ?= g++

CXXFLAGS := -g -Wall -pipe -std=c++0x

GUILE := guile-2.0
GUILE_CFLAGS := $(shell pkg-config --cflags guile-2.0)
GUILE_LDFLAGS := -L/usr/local/libs -lguile-2.0
#GUILE_LDFLAGS := $(shell pkg-config --libs guile-2.0)

STACKLESS_DIR := /usr/local/stow/stackless-271-export
STACKLESS_CFLAGS := -I$(STACKLESS_DIR)/include/python2.7

STACKLESS_LDFLAGS := -L$(STACKLESS_DIR)/lib/python2.7 -lpython2.7

LDFLAGS += $(STACKLESS_LDFLAGS)

CXXFLAGS += $(STACKLESS_CFLAGS)

THREAD_FLAG := -pthread

dep_dir := .deps

$(shell test -e $(dep_dir) || mkdir $(dep_dir))

CXXSUFFIX := cpp

SWIG := swig
SWIG_FLAGS := -c++ -python  -builtin -modern -O

SWIG_WRAPPER_NAME := py_interface_wrap
swig_wrapper := $(SWIG_WRAPPER_NAME).cxx

swig_srcs := $(swig_wrapper) 
swig_objs := $(SWIG_WRAPPER_NAME).o

srcs := $(wildcard *.$(CXXSUFFIX))
objs := $(subst .$(CXXSUFFIX),.o,$(srcs)) $(swig_objs)

deps := $(addprefix $(dep_dir)/,$(subst .$(CXXSUFFIX),.Tpo,$(srcs))) \
        $(addprefix $(dep_dir)/,$(subst .cxx,.Tpo,$(swig_srcs))) \
        $(addprefix $(dep_dir)/,$(SWIG_WRAPPER_NAME).Tps)

lib_stem := mtd

static_lib := libgm.a

bin := $(lib_stem)

shared_lib := lib$(lib_stem).so

PY_MODULE_NAME := mtd_lib
py_module_wrapper := $(PY_MODULE_NAME).py
py_module := _$(PY_MODULE_NAME).so

.PHONY: all clean

all: $(shared_lib) $(py_module)

-include $(deps)

# -DGC_NO_THREAD_REDIRECTS

$(swig_wrapper): $(PY_MODULE_NAME).i Makefile
	$(SWIG) $(SWIG_FLAGS) -MD -MF $(dir $@)$(dep_dir)/$(SWIG_WRAPPER_NAME).Tps -o $@ $<

%.o: %.$(CXXSUFFIX) Makefile
	$(CXX) $(CXXFLAGS) $(THREAD_FLAG) -fPIC -MD -MP -MF $(dir $@)$(dep_dir)/$(notdir $*).Tpo -c -o $@ $<

%.o: %.cxx Makefile
	$(CXX) -Wno-unused-variable $(CXXFLAGS) $(THREAD_FLAG) -fPIC -MD -MP -MF $(dir $@)$(dep_dir)/$(notdir $*).Tpo -c -o $@ $<

$(bin): $(objs)
	$(CXX) $(THREAD_FLAG) $(LDFLAGS) -o $@ $^

$(shared_lib): $(objs)
	$(CXX) -shared $(THREAD_FLAG) $(LDFLAGS) -o $@ $^

$(py_module): $(objs)
	$(CXX) -shared $(THREAD_FLAG) $(LDFLAGS) -o $@ $^

clean:
	rm -f *.o
	rm -f *.pyc
	rm -f $(swig_wrapper)
	rm -f $(py_module_wrapper)
	rm -f $(shared_lib)
	rm -f $(py_module)
	rm -f $(mtd_lib)
	rm -f $(static_lib)
	rm -f $(bin)


