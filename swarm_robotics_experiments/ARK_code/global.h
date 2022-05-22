#ifndef ARK_SCI_EXP_GLOBAL_H
#define ARK_SCI_EXP_GLOBAL_H

#include <QtCore/qglobal.h>

#if defined(ARK_SCI_EXP_LIBRARY)
#  define ARK_SCI_EXPSHARED_EXPORT Q_DECL_EXPORT
#else
#  define ARK_SCI_EXPSHARED_EXPORT Q_DECL_IMPORT
#endif

#endif // ARK_SCI_EXP_GLOBAL_H
