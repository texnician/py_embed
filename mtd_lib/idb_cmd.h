#ifndef _IDB_CMD_H_
#define _IDB_CMD_H_

#include <string>
#include <memory>
#include <map>

#define _CXX0X_ 1
#define SHARED_PTR std::shared_ptr

typedef std::string RecordSet;

typedef SHARED_PTR<RecordSet> RecordSetPtr;

class IHWDBEnv
{
public:
    virtual ~IHWDBEnv() {}

    virtual int Execute(const char* ) const = 0;
    
    virtual RecordSetPtr ExecuteRs(const char*) const = 0;
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
    
    static const HWDBRecordSet Empty;

    bool IsEmpty() const;

    HWDBRecordSet& SetRecordSet(const RecordSetPtr& rs);

#if defined(_CXX0X_)    
    HWDBRecordSet& SetRecordSet(RecordSetPtr&& rs);
#endif
    
    RecordSetPtr GetRecordSet() const;

    HWDBRecordSet& SetSubRecordSet(const char* task, const HWDBRecordSet& rs);

#if defined(_CXX0X_)
    HWDBRecordSet& SetSubRecordSet(const char* task, HWDBRecordSet&& rs);
#endif

    const HWDBRecordSet& GetSubRecordSet(const char* task) const;
    
private:
    RecordSetPtr rs_;
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

    HWSQLCmd& SetSubCmd(const char* task, const HWSQLCmd& other);

#if defined(_CXX0X_)    
    HWSQLCmd& SetSubCmd(const char* task, HWSQLCmd&& other);
#endif

    const HWSQLCmd& GetSubCmd(const char* task) const;

    HWSQLCmd& GetSubCmd(const char* task);

    HWDBResult Execute(IHWDBEnv* p_env) const;
    
    RecordSetPtr ExecuteRs(IHWDBEnv* db_env) const;

private:
    std::string sql_;
    typedef std::map<std::string, HWSQLCmd> SubMap;
    SubMap sub_map_;
};

#endif
