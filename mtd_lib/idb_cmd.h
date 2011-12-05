#ifndef _IDB_CMD_H_
#define _IDB_CMD_H_

#include <string>
#include <memory>
#include <map>
#include "mtd_lib.h"
#if !defined(_SWIG_)
#define _CXX0X_ 1
#endif
#define SHARED_PTR std::shared_ptr

class IHWDBCursor;

typedef SHARED_PTR<IHWDBCursor> IHWDBCursorPtr;

class IHWDBEnv
{
public:
    virtual ~IHWDBEnv() {}

    virtual int Execute(const char* ) const = 0;
    
    virtual int ExecuteRs(const char*, IHWDBCursorPtr& rs) const = 0;
};

class IHWDBCursor
{
public:
    virtual ~IHWDBCursor() {};

    virtual int GetRecordCount(void) = 0;
    
    virtual int GetFieldCount(void) = 0;
    
    virtual bool GetRecord(void) = 0;
    
    virtual const char * GetFieldValue(int index) = 0;
    
    virtual int GetFieldLength(int index) = 0;

    virtual const char* GetFieldValueByName(const char *name) = 0;

    virtual int GetFieldLengthByName(const char *name) = 0;
};

class HWDBResult
{
public:
    HWDBResult();
    
    virtual ~HWDBResult()
        {}
    
    static const HWDBResult NoError;
    
    bool HasError() const;

    HWDBResult& SetResult(int result);

    int GetResult() const;
    
    HWDBResult& SetSubResult(const char* task, const HWDBResult& result);

#if defined(_CXX0X_)
    HWDBResult& SetSubResult(const char* task, HWDBResult&& result);
#endif
    const HWDBResult& GetSubResult(const char* task) const;

private:
    bool has_error_;
    int result_;
    typedef std::map<std::string, HWDBResult> SubResultMap;
    SubResultMap sub_result_map_;
};

class HWDBRecordSet : public HWDBResult
{
public:
    HWDBRecordSet();
    virtual ~HWDBRecordSet() {}
    
    static const HWDBRecordSet Empty;

    bool IsEmpty() const;

    HWDBRecordSet& SetCursor(const IHWDBCursorPtr& rs);

#if defined(_CXX0X_)    
    HWDBRecordSet& SetCursor(IHWDBCursorPtr&& rs);
#endif
    
    IHWDBCursorPtr GetCursor() const;

    HWDBRecordSet& SetSubRecordSet(const char* task, const HWDBRecordSet& rs);

#if defined(_CXX0X_)
    HWDBRecordSet& SetSubRecordSet(const char* task, HWDBRecordSet&& rs);
#endif

    const HWDBRecordSet& GetSubRecordSet(const char* task) const;
    
private:
    IHWDBCursorPtr cursor_;
    typedef std::map<std::string, HWDBRecordSet> SubRecordSetMap;
    SubRecordSetMap sub_rs_map_;
};

class HWSQLCmd
{
public:
    explicit HWSQLCmd(const char* sql = NULL);

    static const HWSQLCmd Null;
    
    virtual ~HWSQLCmd()
        {}

    bool IsNull() const;

    HWSQLCmd& Reset();

    HWSQLCmd& SetSQL(const char* sql);

    HWSQLCmd& SetSubCmd(const char* task, const HWSQLCmd& other);

#if defined(_CXX0X_)    
    HWSQLCmd& SetSubCmd(const char* task, HWSQLCmd&& other);
#endif

    const HWSQLCmd& GetSubCmd(const char* task) const;

    HWSQLCmd& GetSubCmd(const char* task);

    HWDBResult Execute(IHWDBEnv* p_env) const;
    
    HWDBRecordSet ExecuteRs(IHWDBEnv* db_env) const;

    std::string DumpSQL(const HWDBResult& result = HWDBResult::NoError,
                        const char* name = NULL, int level = 0) const;
    
private:
    std::string sql_;
    typedef std::map<std::string, HWSQLCmd> SubMap;
    SubMap sub_map_;
};

struct MTD_API SkillData
{
    int id;
    std::string name;
    std::vector<int> data;
};

struct MTD_API SkillResult
{
    int id;
    std::string result;
	std::vector<int> data;
};

class MTD_API ISkillCallback
{
public:
    virtual ~ISkillCallback()
    {}

    virtual SkillResult DoSkill(SkillData& data) = 0;

	virtual void DoVoid() = 0;
};

class MTD_API ScriptSkillCallback : public ISkillCallback
{
public:
	virtual ~ScriptSkillCallback()
	{

	}
};

class MTD_API SkillCaller
{
public:
    void TestString(const std::string& name)
    {}
    
    void SetCallback(SHARED_PTR<ISkillCallback>& cb)
    {
        cb_ = cb;
    }

	bool SetPyCallback(ScriptSkillCallback* cb)
	{
		cb_ = SHARED_PTR<ISkillCallback>(cb);
        return true;
	}
    SkillResult Call(SkillData& data)
    {
        if (cb_) return cb_->DoSkill(data);
		return SkillResult();
    }
    void CallVoid()
    {
        if (cb_) cb_->DoVoid();
    }
    
private:
    SHARED_PTR<ISkillCallback> cb_;
};

extern MTD_API SkillCaller* g_caller;

extern MTD_API SkillCaller* GetCaller();

extern MTD_API std::string StrFoo();

#endif
