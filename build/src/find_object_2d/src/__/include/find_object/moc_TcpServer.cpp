/****************************************************************************
** Meta object code from reading C++ file 'TcpServer.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.9.5)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../../../../../../../src/src/find_object_2d/include/find_object/TcpServer.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'TcpServer.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.9.5. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_find_object__TcpServer_t {
    QByteArrayData data[15];
    char stringdata0[217];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_find_object__TcpServer_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_find_object__TcpServer_t qt_meta_stringdata_find_object__TcpServer = {
    {
QT_MOC_LITERAL(0, 0, 22), // "find_object::TcpServer"
QT_MOC_LITERAL(1, 23, 9), // "addObject"
QT_MOC_LITERAL(2, 33, 0), // ""
QT_MOC_LITERAL(3, 34, 7), // "cv::Mat"
QT_MOC_LITERAL(4, 42, 12), // "removeObject"
QT_MOC_LITERAL(5, 55, 12), // "detectObject"
QT_MOC_LITERAL(6, 68, 20), // "publishDetectionInfo"
QT_MOC_LITERAL(7, 89, 26), // "find_object::DetectionInfo"
QT_MOC_LITERAL(8, 116, 4), // "info"
QT_MOC_LITERAL(9, 121, 9), // "addClient"
QT_MOC_LITERAL(10, 131, 16), // "readReceivedData"
QT_MOC_LITERAL(11, 148, 12), // "displayError"
QT_MOC_LITERAL(12, 161, 28), // "QAbstractSocket::SocketError"
QT_MOC_LITERAL(13, 190, 11), // "socketError"
QT_MOC_LITERAL(14, 202, 14) // "connectionLost"

    },
    "find_object::TcpServer\0addObject\0\0"
    "cv::Mat\0removeObject\0detectObject\0"
    "publishDetectionInfo\0find_object::DetectionInfo\0"
    "info\0addClient\0readReceivedData\0"
    "displayError\0QAbstractSocket::SocketError\0"
    "socketError\0connectionLost"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_find_object__TcpServer[] = {

 // content:
       7,       // revision
       0,       // classname
       0,    0, // classinfo
       8,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       3,       // signalCount

 // signals: name, argc, parameters, tag, flags
       1,    3,   54,    2, 0x06 /* Public */,
       4,    1,   61,    2, 0x06 /* Public */,
       5,    1,   64,    2, 0x06 /* Public */,

 // slots: name, argc, parameters, tag, flags
       6,    1,   67,    2, 0x0a /* Public */,
       9,    0,   70,    2, 0x08 /* Private */,
      10,    0,   71,    2, 0x08 /* Private */,
      11,    1,   72,    2, 0x08 /* Private */,
      14,    0,   75,    2, 0x08 /* Private */,

 // signals: parameters
    QMetaType::Void, 0x80000000 | 3, QMetaType::Int, QMetaType::QString,    2,    2,    2,
    QMetaType::Void, QMetaType::Int,    2,
    QMetaType::Void, 0x80000000 | 3,    2,

 // slots: parameters
    QMetaType::Void, 0x80000000 | 7,    8,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, 0x80000000 | 12,   13,
    QMetaType::Void,

       0        // eod
};

void find_object::TcpServer::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        TcpServer *_t = static_cast<TcpServer *>(_o);
        Q_UNUSED(_t)
        switch (_id) {
        case 0: _t->addObject((*reinterpret_cast< const cv::Mat(*)>(_a[1])),(*reinterpret_cast< int(*)>(_a[2])),(*reinterpret_cast< const QString(*)>(_a[3]))); break;
        case 1: _t->removeObject((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 2: _t->detectObject((*reinterpret_cast< const cv::Mat(*)>(_a[1]))); break;
        case 3: _t->publishDetectionInfo((*reinterpret_cast< const find_object::DetectionInfo(*)>(_a[1]))); break;
        case 4: _t->addClient(); break;
        case 5: _t->readReceivedData(); break;
        case 6: _t->displayError((*reinterpret_cast< QAbstractSocket::SocketError(*)>(_a[1]))); break;
        case 7: _t->connectionLost(); break;
        default: ;
        }
    } else if (_c == QMetaObject::IndexOfMethod) {
        int *result = reinterpret_cast<int *>(_a[0]);
        {
            typedef void (TcpServer::*_t)(const cv::Mat & , int , const QString & );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&TcpServer::addObject)) {
                *result = 0;
                return;
            }
        }
        {
            typedef void (TcpServer::*_t)(int );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&TcpServer::removeObject)) {
                *result = 1;
                return;
            }
        }
        {
            typedef void (TcpServer::*_t)(const cv::Mat & );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&TcpServer::detectObject)) {
                *result = 2;
                return;
            }
        }
    }
}

const QMetaObject find_object::TcpServer::staticMetaObject = {
    { &QTcpServer::staticMetaObject, qt_meta_stringdata_find_object__TcpServer.data,
      qt_meta_data_find_object__TcpServer,  qt_static_metacall, nullptr, nullptr}
};


const QMetaObject *find_object::TcpServer::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *find_object::TcpServer::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_find_object__TcpServer.stringdata0))
        return static_cast<void*>(this);
    return QTcpServer::qt_metacast(_clname);
}

int find_object::TcpServer::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QTcpServer::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 8)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 8;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 8)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 8;
    }
    return _id;
}

// SIGNAL 0
void find_object::TcpServer::addObject(const cv::Mat & _t1, int _t2, const QString & _t3)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(&_t1)), const_cast<void*>(reinterpret_cast<const void*>(&_t2)), const_cast<void*>(reinterpret_cast<const void*>(&_t3)) };
    QMetaObject::activate(this, &staticMetaObject, 0, _a);
}

// SIGNAL 1
void find_object::TcpServer::removeObject(int _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(&_t1)) };
    QMetaObject::activate(this, &staticMetaObject, 1, _a);
}

// SIGNAL 2
void find_object::TcpServer::detectObject(const cv::Mat & _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(&_t1)) };
    QMetaObject::activate(this, &staticMetaObject, 2, _a);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
