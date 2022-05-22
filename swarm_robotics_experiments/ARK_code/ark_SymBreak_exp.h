#ifndef ARK_SYMB_LIB_H
#define ARK_SYMB_LIB_H

#include "global.h"

//
#include <QObject>
#include <QFile>
//#include <QTextStream>

// Project includes
#include "kilobot.h"
#include "kilobotexperiment.h"
#include "kilobotenvironment.h"
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <QTableWidget>
#include <QSpinBox>
#include "ark_SymBreak_env.h"


using namespace cv;

class KiloLog {
public:
    // constructors
    KiloLog() {}
    KiloLog(kilobot_id id, QPointF pos, double rot, kilobot_colour col) : id(id), position(pos), orientation(rot), colour(col) {}

    // methods
    void updateAllValues(kilobot_id id, QPointF pos, double rot, kilobot_colour col){
        this->id = id;
        this->position = pos;
        this->orientation = rot;
        this->colour = col;
    }
    void setPos(QPointF pos){
        this->position = pos;
    }
    void setOrientation(double rot){
        this->orientation = rot;
    }
    void setCol(kilobot_colour col){
        this->colour = col;
    }

    // variables
    kilobot_id id;
    QPointF position;
    double orientation;
    kilobot_colour colour;
};

class ARK_SYMB_EXPSHARED_EXPORT mykilobotexperiment : public KilobotExperiment
{
    Q_OBJECT
public:
    mykilobotexperiment();
    virtual ~mykilobotexperiment() {}

    QWidget * createGUI();

    //
    QVector < Kilobot * > mykilobot;

signals:
    void errorMessage(QString);
    //    void setExptImage(QPixmap);

public slots:
    void initialise(bool);
    void run();
    void stopExperiment();
    void UpdateBroadcastingState();

    //    void setupExperiment();
    void toggleSaveImages(bool toggle) { m_save_images = toggle; }
    void toggleLogExp(bool toggle){ m_log_exp = toggle; }
    void toggleDataRetrieval(bool toggle){ m_DataRetrieval_ON = toggle; }
    void setExpNumber(int value){m_expno=value;}
    void setNumberOfOptions(int value){m_number_of_options=value;}
    void setExperimentLength(int value){m_experiment_length=value;}
    void setGoToSiteLength(int value){m_go_to_site_length=value;}
    void setNumPhases(int value){m_experiment_number_of_phases=value;}
    void setHighestQuality(double value){m_highest_quality=value;}
    void setOptionsRadius(double value){m_option_radius=value;}
    //void setNoise(double value){m_quality_noise_variance=value;}
    void setInhibitionType(QString value){m_inhibition_type=value;}
    void setInhibitionNextPhase(QString value){m_inhibition_type_next_phase=value;}
    void setArenaSize(QString value){m_arena_size=value;}
    void setQualityDistType(QString value){m_quality_dist_type=value;}
    void setOptionSizeDistType(QString value){m_option_size_dist_type=value;}
    void setTrobot(double value){m_Trobot=value;}
    void setXoffset(int value){m_x_offset=value;}
    void setYoffset(int value){m_y_offset=value;}
    void setPolygoneRadius(double value){m_polygone_radius=value;}
    void setDataRetrievalFrequency(int value){m_data_retrieval_period=value;}
    void InformDataRetrievalProcessAboutRobotsColors(std::vector<lightColour>& infovector);
    void broadcastConfig();
    void broadcastExpFinished();


private:
    void updateKilobotState(Kilobot kilobotCopy);
    void setupInitialKilobotState(Kilobot kilobotCopy);

    //
    void setupEnvironments();
    void plotEnvironment();

    //
    mykilobotenvironment m_options_env;

    // Experiment number
    unsigned int m_expno=0;

    //Image saving variables
    bool m_save_images;
    int m_saved_images_counter = 0;
    QString im_filename_prefix="/home/salah/data_SCI/run%1";
    QString im_filename_suffix="/sci_frame_%1.jpg";

    //discovery update period in seconds
    float m_virtual_sensor_update_period;


    //Logging period in seconds
    float m_log_period;
    float m_last_log=0, m_last_log2=0;

    //Log variables
    bool m_log_exp;
    QFile log_file;
    QString log_filename_prefix="/home/salah/data_SCI/run%1";
    QString log_filename_suffix="/log_sci.txt";
    QString log_opts_filename_suffix="/log_optionPositionAndQuality.txt";
    QTextStream log_stream;
    QVector < kilobot_id >  allKiloIDs;
    QVector <KiloLog> allKilos;
    QVector<lightColour> previousColourList;

    // GUI objects
    QTableWidget * tableofoptions;

    // Configuration messages
    bool m_configuration_msgs_sent=false;
    int m_number_of_config_msgs_sent=0;
    bool m_robot_speaking=false;

    // broadcasting management
    bool m_broadcasing=false;
    int m_t_since;
    bool m_stop_speaking_msg_sent=false;

    // virtual sensors messages management
    int m_msg_group;
    QVector<QVector<kilobot_id> > m_kilo_group_for_messaging;
    float m_Trobot=4.0;
    float m_Trobot_last=0.0;
    QDoubleSpinBox* m_robot_speaking_time_spin;

    // Env setup
    unsigned int m_number_of_options=6;
    float m_highest_quality=8.0;
    float m_option_radius=0.32;
    //float m_quality_noise_variance=1.0;
    int m_x_offset=0;
    int m_y_offset=0;
    float m_polygone_radius=0.66;
    QString m_inhibition_type;
    QString m_inhibition_type_next_phase;
    QString m_quality_dist_type;
    QString m_option_size_dist_type;
    QString m_arena_size;

    QTime m_elapsed_time;
    QTime m_RTID_timer;
    int m_RTID_elapsed_time; // in milliseconds
    int m_RTID_was_active;
    int m_RTID_period_of_stopped_activity_after_active=7;

    unsigned int m_experiment_length=1800; // 30 minutes
    unsigned int m_go_to_site_length=300; // 5 minutes
    bool m_experiment_finished;
    unsigned int m_experiment_number_of_phases = 1;
    unsigned int m_experiment_phase;

};

#endif // ARK_SYMB_LIB_H
