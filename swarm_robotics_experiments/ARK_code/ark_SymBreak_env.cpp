#include "ark_SymBreak_env.h"

#include <QVector>
#include <QLineF>
#include <QDebug>
#include <QtMath>

#include "kilobot.h"

mykilobotenvironment::mykilobotenvironment(QObject *parent) : KilobotEnvironment(parent) {
    qDebug() << "Environment is up and running. :-)";
}

// Update the dynamic environment:
void mykilobotenvironment::update() {
    for(int i=0; i<m_options.size(); ++i) {
        if (!m_options[i].QualityChangeApplied && m_options[i].QualityChangeTime != 0.0 && this->m_time >= m_options[i].QualityChangeTime)
        {
            qDebug() << "**** QUALITY CHANGE **** Option " << i+1 << "had quality "<< m_options[i].quality << ", now its quality is" << m_options[i].QualityAfterChange;
            m_options[i].quality=m_options[i].QualityAfterChange;
            m_options[i].QualityChangeApplied = true;
        }
    }
}

// return the option ID for a given kilobot colour
unsigned int mykilobotenvironment::indexOptOfColour(lightColour kColor) {
    switch(kColor){
    case RED:
        return 1;
    case GREEN:
        return 3;
    case BLUE:
        return 2;
    default:
        return 0;
    }
}

// generate virtual sensor readings & send to KB
void mykilobotenvironment::updateVirtualSensor(Kilobot kilobot) {
    kilobot_id kID = kilobot.getID();
    QPointF kPos = kilobot.getPosition();

    //     qDebug() << "UpdateMessagingQueue: " << UpdateMessagingQueue[kID];

    if(m_update_messaging_queue[kID])
    {
        m_update_messaging_queue[kID]=false;

        kilobot_message msg;

        uint8_t m_message_type;

        /* Update virtual-GPS */
        if (m_require_GPS[kID]==true)
        {

            // Get robot's GPS coordinates
            QPoint GPS_cords=PositionToGPS(kPos);
            uint8_t GPS_y = 31-GPS_cords.y();

            // Set msg type
            m_message_type=1; // Message types: 1 for GPS and 0 for Discovery

            // Get robot's orientation
            // if the robot has hit a wall, the tracking orientation can be wrong and therefore we manually correct it
            double orientDegrees = qRadiansToDegrees(qAtan2(-kilobot.getVelocity().y(),kilobot.getVelocity().x()));
            double velocityLength = qSqrt( qPow(kilobot.getVelocity().x(),2) + qPow(kilobot.getVelocity().y(),2) );
            if (velocityLength < 0.5){ // if the robot is not moving
                if (GPS_cords.x()==0){
                    orientDegrees = 180;
                } else if (GPS_y==0){
                    orientDegrees = 270;
                } else if (GPS_cords.x()==GPS_max_x) {
                    orientDegrees = 0;
                } else if (GPS_y==GPS_max_y) {
                    orientDegrees = 90;
                }
            }
            orientDegrees=desNormAngle(orientDegrees);

            msg.id= kID<<2 | m_message_type;
            msg.type= ( (uint8_t) GPS_cords.x() >> 1) & 0x0F;
            msg.data= ( (((uint8_t) GPS_cords.x() ) << 9 ) & 0x200) |
                      ( ( GPS_y << 4 ) & 0x1F0) |
                      ( (uint8_t) floor((orientDegrees+11.25)/22.5) );

            m_messaging_queue[kID].push_back(msg);
            //qDebug() << "Sending GPS (" << GPS_cords.x() << "," << GPS_y << ")[o:" << ( (uint8_t) floor((orientDegrees+11.25)/22.5) ) << ":" << orientDegrees << "] to robot " << kID;
            m_require_GPS[kID]=false;

        }

        /* Update option virtual sensor (Discovery: location and quality) */
        if(m_single_discovery[kID]!=0 )
        {
            m_message_type=0;
            msg.id= (kID << 2) | m_message_type;
            msg.type= ( (uint8_t) m_options[m_single_discovery[kID]-1].GPS_X >> 1) & 0x0F;
            msg.data= ( (((uint8_t) m_options[m_single_discovery[kID]-1].GPS_X ) << 9 ) & 0x200) |
                      ( (((uint8_t) m_options[m_single_discovery[kID]-1].GPS_Y ) << 4 ) & 0x1F0) |
                      ( (uint8_t) m_options[m_single_discovery[kID]-1].quality );
            m_messaging_queue[kID].push_back(msg);
            //qDebug() << "Sending discovery " << m_single_discovery[kID] << " pos: " << m_options[m_single_discovery[kID]-1].GPS_X << "," << m_options[m_single_discovery[kID]-1].GPS_Y << " and q: " << m_options[m_single_discovery[kID]-1].quality << " to robot " << kID;
            m_single_discovery[kID]=0;

        }

    }

    //qDebug() << "m_TimeForUpdatingVirtualSensors " << m_TimeForUpdatingVirtualSensors << " MessagingQueue[kID].size=" << MessagingQueue[kID].size() << " and for kID " << kID << " UpdateMessagingQueue[kID]=" << UpdateMessagingQueue[kID];
    if(m_time_for_updating_virtual_sensors && !m_messaging_queue[kID].empty())
    {
        //qDebug()<<"Sending message " << MessagingQueue[kID].front().type << ", " << MessagingQueue[kID].front().data;
        emit transmitKiloState(m_messaging_queue[kID].front());
        m_messaging_queue[kID].pop_front();
    }

    kilobot_colour kColor = kilobot.getLedColour();
    option Op;

    // Check discovery virtual-sensor
    for (int i=0; i<m_options.size(); i++ )
    {
        Op=m_options[i];
        float rad=Op.rad;
        float x=Op.posX;
        float y=Op.posY;
        //Check if the robot is inside an option for discovery
        if((pow(kPos.x()-x,2)+pow(kPos.y()-y,2)) < pow(rad,2) )
        {
            m_single_discovery[kID]=Op.ID;
            m_virtual_sensors_need_update=true;

            // if robot is within the option and it wanted to resample, deactivate the resampling toggle
            if (Op.ID == indexOptOfColour(kColor)) {
                m_going_resampling_list[kID] = false;
            }
        }
    }

    //    if( kLed == BLUE )
    //    {
    m_require_GPS[kID]=true;
    m_virtual_sensors_need_update=true;
    //    }
}


QPoint mykilobotenvironment::PositionToGPS(QPointF position){
    return QPoint((unsigned int) std::ceil(position.x()/m_cell_length )-1, (unsigned int) std::ceil(position.y()/m_cell_length )-1);
}

float mykilobotenvironment::desNormAngle(float angle){
    while (angle > 360) angle = angle - 360;
    while (angle < 0) angle = 360 + angle;
    return angle;
}
