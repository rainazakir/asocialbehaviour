#-------------------------------------------------
#
# Project created by QtCreator 2017-02-08T11:35:48
#
#-------------------------------------------------

QT       -= gui

QT += widgets

TARGET = ark_SymBreak
TEMPLATE = lib

DEFINES += ark_SymBreakEXP_LIBRARY

SOURCES += \
    kilobot.cpp \
    ark_SymBreak_env.cpp \
    ark_SymBreak_exp.cpp

HEADERS +=\
    kilobot.h \
    kilobotexperiment.h \
    kilobotenvironment.h \
    ark_SymBreak_env.h \
    ark_SymBreak_exp.h \
    global.h

unix {
    target.path = /usr/lib
    INSTALLS += target
}

INCLUDEPATH += /usr/local/include/
LIBS += -L/usr/local/lib \
        -lopencv_core
