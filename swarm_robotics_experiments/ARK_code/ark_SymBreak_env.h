#ifndef ARK_SYMB_ENV_H
#define ARK_SYMB_ENV_H

#include <QObject>
#include <QPointF>
#include <QVector>
#include <kilobotenvironment.h>
#include <QTime>
#include <QColor>

static const double MM_TO_PIXEL = 2000.0/2000.0;
static const double PIXEL_TO_MM = 2000.0/2000.0;

static const double M_TO_PIXEL = 1000.0;

struct option {
    unsigned int ID;
    float quality;
    float posX; // in pixel
    float posY; // in pixel
    unsigned int GPS_X; // in cells
    unsigned int GPS_Y; // in cells
    float rad;  // in pixel
    float rad_m;
    QColor color;

    float AppearanceTime=0;
    float DisappearanceTime=0;

    float QualityChangeTime=0;
    float QualityAfterChange;
    bool QualityChangeApplied=false;
};

enum EncounterTypes {
    SINGLE,
    MULTI
};



class mykilobotenvironment : public KilobotEnvironment
{
    Q_OBJECT
public:
    explicit mykilobotenvironment(QObject *parent = 0);
    QPoint PositionToGPS(QPointF position);
    float desNormAngle(float angle);

    // Current time (necessary to check about disappearance and quality swap)
    float m_time;

    // A vector containing the options
    QVector <option> m_options;

    bool m_time_for_updating_virtual_sensors;
    QVector <bool> m_update_messaging_queue;

    // Discovery variables
    bool m_virtual_sensors_need_update=false;
    QVector <unsigned int> m_single_discovery;
    QVector < QVector <unsigned int> > m_multi_discovery;

    QVector <unsigned int> m_prev_discovery;
    EncounterTypes m_encounter_type;

    // GPS variables
    uint8_t m_GPS_cells=32;
    float m_cell_length=0;
    QVector <bool> m_require_GPS;
    int GPS_max_x=15; // max GPS value on x axis (to correct orientation of robot colliding with walls)
    int GPS_max_y=15; // max GPS value on y axis (to correct orientation of robot colliding with walls)

    // For logging
    QVector <bool> m_going_resampling_list;
    unsigned int indexOptOfColour(lightColour kColor);

    // Message Queue
    QVector< QVector<kilobot_message> > m_messaging_queue;

signals:
    void errorMessage(QString);

public slots:
    void update();
    void updateVirtualSensor(Kilobot kilobot);

private:

};
#endif // ARK_SYMB_ENV_H
