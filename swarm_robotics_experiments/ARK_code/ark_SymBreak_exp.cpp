#include <QDebug>
#include <QThread>
#include <QTime>
#include <time.h>

// widgets
#include <QPushButton>
#include <QSlider>
#include <QGroupBox>
#include <QFormLayout>
#include <QLabel>
#include <QFrame>
#include <QCheckBox>
#include <QtMath>
#include <QSpinBox>
#include <QDir>
#include <QFileDialog>
#include <QSettings>
#include <QTableWidgetItem>
#include <QPainter>
#include <QComboBox>
#include <QVector3D>
#include "ark_SymBreak_env.h"
#include "ark_SymBreak_exp.h"


// return pointer to interface!
// mykilobotexperiment can and should be completely hidden from the application
extern "C" ARK_SYMB_EXPSHARED_EXPORT KilobotExperiment *createExpt()
{
    return new mykilobotexperiment();
}

mykilobotexperiment::mykilobotexperiment()
{
    // setup the environments here
    connect(&m_options_env,SIGNAL(transmitKiloState(kilobot_message)), this, SLOT(signalKilobotExpt(kilobot_message)));
    connect(&m_DataRetrieval,SIGNAL(broadcastMessage(kilobot_broadcast)),this,SLOT(SendDataRetrievalProcessMessage(kilobot_broadcast)));
    connect(&m_DataRetrieval,SIGNAL(DataRetrievalProcessEnded()),this,SLOT(toggleDataRetrievalProcessEnded()));
    connect(&m_DataRetrieval,SIGNAL(SeekInformationAboutKilobotResponses(std::vector<lightColour>&)),this,SLOT(InformDataRetrievalProcessAboutRobotsColors(std::vector<lightColour>&)));
    this->serviceInterval = 100; // timestep in ms
}

// GUI creation function: Working properly

QWidget * mykilobotexperiment::createGUI() {
    QFrame * frame = new QFrame;
    QVBoxLayout * lay = new QVBoxLayout;
    frame->setLayout(lay);

    /** Eperiment recording check box */
    QCheckBox * saveImages_ckb = new QCheckBox("Record experiment");
    saveImages_ckb->setChecked(true);// make the box not checked by default
    toggleSaveImages(saveImages_ckb->isChecked());

    lay->addWidget(saveImages_ckb);

    /** Experiment logging check box */
    QCheckBox * logExp_ckb = new QCheckBox("Log experiment");
    logExp_ckb->setChecked(true); // make the box checked by default
    toggleLogExp(logExp_ckb->isChecked());

    lay->addWidget(logExp_ckb);

    /** Experiment index specification */
    // Add a field to specify the experiment no
    QGroupBox * formGroupExpno = new QGroupBox(tr("Expno:"));
    QFormLayout * layout2 = new QFormLayout;
    formGroupExpno->setLayout(layout2);
    QSpinBox* expno_spin = new QSpinBox();
    expno_spin->setMinimum(1);
    expno_spin->setMaximum(100);
    expno_spin->setValue(1);
    layout2->addRow(new QLabel(tr("Exp no:")), expno_spin);
    setExpNumber(expno_spin->value());

    lay->addWidget(formGroupExpno);

//    /** Data retrieval checkbox and frequency specification */
//    // Add fields to specify data retrieval params
//    QGroupBox * formGroupDataRetrieval = new QGroupBox(tr("Data Retrieval:"));
//    QFormLayout * layout3 = new QFormLayout;
//    formGroupDataRetrieval->setLayout(layout3);

//    // add a check box to enable/disable data retrieval
//    QCheckBox * logDataRetrieval_ckb = new QCheckBox("Data retrieval");
//    logDataRetrieval_ckb->setChecked(false);
//    layout3->addWidget(logDataRetrieval_ckb);
//    toggleDataRetrieval(logDataRetrieval_ckb->isChecked());

//    // add a field to specify the data retrieval period
//    QSpinBox* data_retrieval_spin = new QSpinBox();
//    data_retrieval_spin->setMinimum(1);
//    data_retrieval_spin->setMaximum(120);
//    data_retrieval_spin->setValue(10);
//    layout3->addRow(new QLabel(tr("DR-Frequency (s):")), data_retrieval_spin);
//    setDataRetrievalFrequency(data_retrieval_spin->value());

//    lay->addWidget(formGroupDataRetrieval);


    /** Experiment Parameters specification */
    // Add fields to specify experiment params
    QGroupBox * formGroupExpVariables = new QGroupBox(tr("Experiment params:"));
    QFormLayout * layout4 = new QFormLayout;
    formGroupExpVariables->setLayout(layout4);

    // number of options
    QSpinBox* number_of_options_spin = new QSpinBox();
    number_of_options_spin->setMinimum(2);
    number_of_options_spin->setMaximum(10);
    number_of_options_spin->setSingleStep(1);
    number_of_options_spin->setValue(m_number_of_options);
    layout4->addRow(new QLabel(tr("Number of options:")), number_of_options_spin);
    setNumberOfOptions(number_of_options_spin->value());

    // experiment length
    QSpinBox* experiment_length_spin = new QSpinBox();
    experiment_length_spin->setMinimum(0);
    experiment_length_spin->setMaximum(36000); // 10 hours
    experiment_length_spin->setSingleStep(1);
    experiment_length_spin->setValue(m_experiment_length);
    layout4->addRow(new QLabel(tr("Experiment length (sec):")), experiment_length_spin);
    setExperimentLength(experiment_length_spin->value());

    // go to site length
    QSpinBox* go_to_site_length_spin = new QSpinBox();
    go_to_site_length_spin->setMinimum(0);
    go_to_site_length_spin->setMaximum(1200); // 20 mins
    go_to_site_length_spin->setSingleStep(1);
    go_to_site_length_spin->setValue(m_go_to_site_length);
    layout4->addRow(new QLabel(tr("Go to site length (sec):")), go_to_site_length_spin);
    setGoToSiteLength(go_to_site_length_spin->value());

    // Number of phases
    QSpinBox* num_phases_offset_spin = new QSpinBox();
    num_phases_offset_spin->setMinimum(1);
    num_phases_offset_spin->setMaximum(3);
    num_phases_offset_spin->setSingleStep(1);
    num_phases_offset_spin->setValue(m_experiment_number_of_phases);
    layout4->addRow(new QLabel(tr("Number of phases")), num_phases_offset_spin);
    setNumPhases(num_phases_offset_spin->value());

    // Radius of the options
    QDoubleSpinBox* options_radius_spin = new QDoubleSpinBox();
    options_radius_spin->setMinimum(0.1);
    options_radius_spin->setMaximum(2.0);
    options_radius_spin->setSingleStep(0.05);
    options_radius_spin->setValue(m_option_radius);
    layout4->addRow(new QLabel(tr("Options radius")), options_radius_spin);
    setOptionsRadius(options_radius_spin->value());

    // X offset
    QSpinBox* x_offset_spin = new QSpinBox();
    x_offset_spin->setMinimum(-2000);
    x_offset_spin->setMaximum(+2000);
    x_offset_spin->setSingleStep(1);
    x_offset_spin->setValue(m_x_offset);
    layout4->addRow(new QLabel(tr("X offset")), x_offset_spin);
    setXoffset(x_offset_spin->value());


    // Y offset
    QSpinBox* y_offset_spin = new QSpinBox();
    y_offset_spin->setMinimum(-2000);
    y_offset_spin->setMaximum(+2000);
    y_offset_spin->setSingleStep(1);
    y_offset_spin->setValue(m_y_offset);
    layout4->addRow(new QLabel(tr("Y offset")), y_offset_spin);
    setYoffset(y_offset_spin->value());

    // Polygone radius
    QDoubleSpinBox* polygone_radius_spin = new QDoubleSpinBox();
    polygone_radius_spin->setMinimum(0.05);
    polygone_radius_spin->setMaximum(2.0);
    polygone_radius_spin->setSingleStep(0.05);
    polygone_radius_spin->setValue(m_polygone_radius);
    layout4->addRow(new QLabel(tr("Polygone radius")), polygone_radius_spin);
    setPolygoneRadius(polygone_radius_spin->value());

    // Highest quality
    QDoubleSpinBox* highest_quality_spin = new QDoubleSpinBox();
    highest_quality_spin->setMinimum(1);
    highest_quality_spin->setMaximum(10.0);
    highest_quality_spin->setSingleStep(1);
    highest_quality_spin->setValue(m_highest_quality);
    layout4->addRow(new QLabel(tr("Highest quality")), highest_quality_spin);
    setHighestQuality(highest_quality_spin->value());

    // quality distribution type
    QComboBox* quality_distribution_type_combo_box= new QComboBox();
    quality_distribution_type_combo_box->addItem("asym");
    quality_distribution_type_combo_box->addItem("sym");
    layout4->addRow( new QLabel(tr("Options' quality:")), quality_distribution_type_combo_box );
    setQualityDistType( quality_distribution_type_combo_box->currentText() );

    // options' size distribution type
    QComboBox* option_size_distribution_type_combo_box= new QComboBox();
    option_size_distribution_type_combo_box->addItem("asym");
    option_size_distribution_type_combo_box->addItem("sym");
    layout4->addRow( new QLabel(tr("Options' size:")), option_size_distribution_type_combo_box );
    setOptionSizeDistType( option_size_distribution_type_combo_box->currentText() );

//    // Quality-noise variance
//    QDoubleSpinBox* quality_noise_variance_spin = new QDoubleSpinBox();
//    quality_noise_variance_spin->setMinimum(0.0);
//    quality_noise_variance_spin->setMaximum(5.0);
//    quality_noise_variance_spin->setSingleStep(0.5);
//    quality_noise_variance_spin->setValue(m_quality_noise_variance);
//    layout4->addRow(new QLabel(tr("Noise variance:")), quality_noise_variance_spin);
//    setNoise(quality_noise_variance_spin->value());

    // inhibition type
    QComboBox* inhibition_type_combo_box= new QComboBox();
    inhibition_type_combo_box->addItem("cross");
    inhibition_type_combo_box->addItem("self");
    layout4->addRow(new QLabel(tr("Inhibition:")), inhibition_type_combo_box);
    setInhibitionType(inhibition_type_combo_box->currentText());

    // inhibition next phases
    QComboBox* inhibition_type_combo_box2= new QComboBox();
    inhibition_type_combo_box2->addItem("self");
    inhibition_type_combo_box2->addItem("cross");
    layout4->addRow(new QLabel(tr("Next phase inhib:")), inhibition_type_combo_box2);
    setInhibitionNextPhase(inhibition_type_combo_box2->currentText());

    // arena size
    QComboBox* arena_size_combo_box= new QComboBox();
    arena_size_combo_box->addItem("2x2 sq.m");
    arena_size_combo_box->addItem("1x1 sq.m");
    layout4->addRow(new QLabel(tr("Arena size:")), arena_size_combo_box);
    setArenaSize(arena_size_combo_box->currentText());

    // Trobot
    m_robot_speaking_time_spin = new QDoubleSpinBox();
    m_robot_speaking_time_spin->setMinimum(2.5);
    m_robot_speaking_time_spin->setMaximum(30.0);
    m_robot_speaking_time_spin->setSingleStep(2.5);
    m_robot_speaking_time_spin->setValue(m_Trobot);
    layout4->addRow(new QLabel(tr("Robots' speaking time:")), m_robot_speaking_time_spin);
    setTrobot(m_robot_speaking_time_spin->value());

    // Send Config
    QPushButton* send_config_button= new QPushButton();
    send_config_button->setText("Broadcast config");
    layout4->addRow(send_config_button);

    QPushButton* send_exp_end_button= new QPushButton();
    send_exp_end_button->setText("Broadcast Experiment End");
    layout4->addRow(send_exp_end_button);

    lay->addWidget(formGroupExpVariables);


    // signal-slot connections
    connect(saveImages_ckb, SIGNAL(toggled(bool)),this, SLOT(toggleSaveImages(bool)));
    connect(logExp_ckb, SIGNAL(toggled(bool)),this, SLOT(toggleLogExp(bool)));
    connect(expno_spin,SIGNAL(valueChanged(int)),this,SLOT(setExpNumber(int)));
    //connect(logDataRetrieval_ckb,SIGNAL(toggled(bool)),this,SLOT(toggleDataRetrieval(bool)));
    //connect(data_retrieval_spin,SIGNAL(valueChanged(int)),this,SLOT(setDataRetrievalFrequency(int)));
    connect(number_of_options_spin,SIGNAL(valueChanged(int)),this,SLOT(setNumberOfOptions(int)));
    connect(experiment_length_spin,SIGNAL(valueChanged(int)),this,SLOT(setExperimentLength(int)));
    connect(go_to_site_length_spin,SIGNAL(valueChanged(int)),this,SLOT(setGoToSiteLength(int)));
    connect(num_phases_offset_spin,SIGNAL(valueChanged(int)),this,SLOT(setNumPhases(int)));
    connect(options_radius_spin,SIGNAL(valueChanged(double)),this,SLOT(setOptionsRadius(double)));
    connect(highest_quality_spin,SIGNAL(valueChanged(double)),this,SLOT(setHighestQuality(double)));
    connect(quality_distribution_type_combo_box,SIGNAL(currentTextChanged(QString)),this,SLOT(setQualityDistType(QString)));
    connect(option_size_distribution_type_combo_box,SIGNAL(currentTextChanged(QString)),this,SLOT(setOptionSizeDistType(QString)));
    //connect(quality_noise_variance_spin,SIGNAL(valueChanged(double)),this,SLOT(setNoise(double)));
    connect(inhibition_type_combo_box,SIGNAL(currentTextChanged(QString)),this,SLOT(setInhibitionType(QString)));
    connect(inhibition_type_combo_box2,SIGNAL(currentTextChanged(QString)),this,SLOT(setInhibitionNextPhase(QString)));
    connect(arena_size_combo_box,SIGNAL(currentTextChanged(QString)),this,SLOT(setArenaSize(QString)));
    connect(m_robot_speaking_time_spin,SIGNAL(valueChanged(double)),this,SLOT(setTrobot(double)));
    connect(x_offset_spin,SIGNAL(valueChanged(int)),this,SLOT(setXoffset(int)));
    connect(y_offset_spin,SIGNAL(valueChanged(int)),this,SLOT(setYoffset(int)));
    connect(polygone_radius_spin,SIGNAL(valueChanged(double)),this,SLOT(setPolygoneRadius(double)));
    connect(send_config_button,SIGNAL(clicked(bool)),this,SLOT(broadcastConfig()));
    connect(send_exp_end_button,SIGNAL(clicked(bool)),this,SLOT(broadcastExpFinished()));

    lay->addStretch();

    connect(this,SIGNAL(destroyed(QObject*)), lay, SLOT(deleteLater()));

    return frame;
}

void mykilobotexperiment::broadcastConfig(){
    kilobot_broadcast msg;
    msg.type=10; // Configuration message
    msg.data.resize(9);
    msg.data[0]= m_options_env.m_options[0].ID; // OP ID
    msg.data[1]= (uint8_t) m_options_env.m_options[0].GPS_X; // OP X
    msg.data[2]= (uint8_t) m_options_env.m_options[0].GPS_Y; // OP Y
    if (m_experiment_phase == 1){
        msg.data[3]= (m_inhibition_type ==QString("cross"))? 0 : 1; // i.e., CROSS=0 and SELF=1
    } else {
        msg.data[3]= (m_inhibition_type_next_phase==QString("cross"))? 0 : 1; // i.e., CROSS=0 and SELF=1
    }
    msg.data[4]= (m_arena_size==QString("1x1 sq.m"))? m_options_env.m_GPS_cells/2 : m_options_env.m_GPS_cells;
    msg.data[5]= 2; // min distance for waypoint sampling

    emit broadcastMessage(msg);
    m_broadcasing=true;
    m_t_since=1;
}

void mykilobotexperiment::broadcastExpFinished(){
    kilobot_broadcast msg;
    msg.type=7; // Experiment finished
    emit broadcastMessage(msg);
    m_broadcasing=true;
    m_t_since=3;
}


// Initialization function: Working properly
void mykilobotexperiment::initialise(bool isResume) {
    //qDebug() << "Entered initializatioN%%%%";
    // Initialize variables
    m_DataRetrieval_ON=false;
    m_experiment_finished=false;
    m_experiment_phase=1;
    m_log_period=1;
    m_options_env.m_time_for_updating_virtual_sensors=false;
    m_options_env.m_cell_length=2000.0/m_options_env.m_GPS_cells;
    qDebug() <<"Cell Length: " << m_options_env.m_cell_length;

    // Generate Environments:
    setupEnvironments();

    // Initialize Kilobot States:
    if (!isResume) {
        // init stuff
        emit getInitialKilobotStates();
    } else
    {

    }

    emit setTrackingType(POS | LED | ROT);

    QThread::currentThread()->setPriority(QThread::HighestPriority);

    // Init Log File operations
    if (m_log_exp)
    {
        if (log_file.isOpen()){
            log_file.close(); // if it was open I close and re-open it (erasing old content!! )
        }

        QString log_foldername =(log_filename_prefix.arg(m_expno));
        QString log_filename = log_foldername+log_filename_suffix;
        if(!QDir(log_foldername).exists()){
            QDir().mkdir(log_foldername);
        }
        //        QString log_filename = log_filename_prefix + "_" + QDate::currentDate().toString("yyMMdd") + "_" + QTime::currentTime().toString("hhmmss") + ".txt";
        log_file.setFileName( log_filename );
        if ( !log_file.open(QIODevice::WriteOnly) ) { // open file
            qDebug() << "ERROR(!) in opening file " << log_filename;
        } else {
            qDebug () << "Log file " << log_file.fileName() << " opened.";
            log_stream.setDevice(&log_file);
        }

        /* save the option positions and behaviour in another file */
        QFile log_opts_file;
        QString log_opts_filename = log_foldername+log_opts_filename_suffix;
        log_opts_file.setFileName( log_opts_filename );
        if ( !log_opts_file.open(QIODevice::WriteOnly) ) { // open file
            qDebug() << "ERROR(!) in opening file " << log_opts_filename;
        } else {
            QTextStream log_opts_stream;
            log_opts_stream.setDevice(&log_opts_file);
            log_opts_stream << m_options_env.m_options.size();
            for (int i = 0; i < m_options_env.m_options.size(); ++i){
                option op = m_options_env.m_options[i];
                log_opts_stream << "\t" << op.ID << "\t" << op.posX << "\t" << op.posY
                           << "\t" << op.GPS_X << "\t" << op.GPS_Y << "\t" << op.rad << "\t" << op.quality << "\t"
                           << op.AppearanceTime << "\t" << op.DisappearanceTime << "\t"
                           << op.QualityChangeTime << "\t" << op.QualityAfterChange;
            }
            log_opts_stream << endl;
            log_opts_file.close();
            qDebug() << "Saved option info in file " << log_opts_filename;
        }
    }

    m_saved_images_counter = 0;
    this->m_time = 0;
    m_elapsed_time.start();
    m_RTID_elapsed_time=0;
    m_RTID_was_active=0;
    m_last_data_retrieval=0;

    //save initial image
    if (m_save_images) {
        emit saveImage(im_filename_prefix.arg(m_expno,1)+im_filename_suffix.arg(m_saved_images_counter++, 5,10, QChar('0')));
    }

    //log initial state of the robots
    if (m_log_exp)
    {
        m_last_log=m_time;
        log_stream << this->m_time;
        for (int i = 0; i < allKiloIDs.size(); ++i){
            kilobot_id kID = allKiloIDs[i];
            log_stream << "\t" << kID << "\t" << allKilos[kID].colour << "\t" << allKilos[kID].position.x() << "\t" << allKilos[kID].position.y() << "\t" << allKilos[kID].orientation << "\t" << m_options_env.m_going_resampling_list[kID];
        }
        log_stream << endl;
    }

    int count=0;
    int groupId=0;
    QVector<kilobot_id> group;
    for (int i = 0; i < allKiloIDs.size(); ++i){
        group.append(allKiloIDs.at(i));
        count++;
        if (count >= 50 || i==allKiloIDs.size()-1){
            m_kilo_group_for_messaging.append(group);
            count=0;
            groupId++;
            group.clear();
        }
    }
    if (m_kilo_group_for_messaging.size()>1){
        m_Trobot = m_Trobot/m_kilo_group_for_messaging.size();
        qDebug() << "The robot's speaking time (Trobot) has been re-sized to " << m_Trobot << " to accomodate " << m_kilo_group_for_messaging.size() << " message groups.";
    }

    clearDrawings();
}

// Stop function working properly
void mykilobotexperiment::stopExperiment() {
    if (log_file.isOpen()){
        qDebug() << "Closing file" << log_file.fileName();
        log_file.close();
    }
    m_options_env.m_options.clear();
    m_options_env.m_going_resampling_list.clear();
    m_msg_group = 0;
    m_kilo_group_for_messaging.clear();
    previousColourList.clear();
    m_number_of_config_msgs_sent=0;
    m_robot_speaking=false;
    m_configuration_msgs_sent=false;
    m_time=0;
    m_Trobot_last=0;
    m_Trobot = m_robot_speaking_time_spin->value();
}

void mykilobotexperiment::run()
{
    // Update Broadcasting state
    UpdateBroadcastingState();

    // Send configuration messages
    if(m_number_of_config_msgs_sent < m_options_env.m_options.size() && !m_broadcasing)
    {

        kilobot_broadcast msg;
        msg.type=10; // Configuration message
        msg.data.resize(9);
        msg.data[0]= m_options_env.m_options[m_number_of_config_msgs_sent].ID; // OP ID
        msg.data[1]= (uint8_t) m_options_env.m_options[m_number_of_config_msgs_sent].GPS_X; // OP X
        msg.data[2]= (uint8_t) m_options_env.m_options[m_number_of_config_msgs_sent].GPS_Y; // OP Y
        msg.data[3]= (m_inhibition_type==QString("cross"))? 0 : 1; // i.e., CROSS=0 and SELF=1
        msg.data[4]= (m_arena_size==QString("1x1 sq.m"))? m_options_env.m_GPS_cells/2 : m_options_env.m_GPS_cells;
        msg.data[5]= 2; // min distance for waypoint sampling
        msg.data[6]= 0; // empty
        msg.data[7]= 0; // empty
        msg.data[8]= 0; // empty

        //qDebug() << "*************************************** BROADCAST MSG 10 ***************************************";
        qDebug() << "Sending Config Msg No." << m_number_of_config_msgs_sent;
//        for (int i=0; i<9; i++){
//            qDebug() << "data["<<i<<"]=" << msg.data[i];
//        }

        emit broadcastMessage(msg);

        m_broadcasing=true;
        m_t_since=3;

        m_number_of_config_msgs_sent++;
    }

    if(m_number_of_config_msgs_sent == m_options_env.m_options.size() && !m_broadcasing && !m_configuration_msgs_sent )
    {

        qDebug() << "Asking robots to start speaking!";

        kilobot_broadcast msg;
        msg.type=6; // Comeback to speaking message
        emit broadcastMessage(msg);

        m_broadcasing=true;
        m_t_since=3;

        m_robot_speaking=true;
    }


    if(m_configuration_msgs_sent)
    {

        if(!this->runtimeIdentificationLock){
            // keep track of the time spent in RTID
            if (m_RTID_was_active==m_RTID_period_of_stopped_activity_after_active) { // this means this is the first timestep after active RTID
                m_RTID_elapsed_time += m_RTID_timer.elapsed();
                qDebug() << "RTID was active for a total of " << m_RTID_elapsed_time << "ms in the whole experiment.";
            }

            // Increment time
            if(!m_data_retrieval_running){
                this->m_time=(m_elapsed_time.elapsed() - m_RTID_elapsed_time)/1000.0; // time in seconds
                m_options_env.m_time=this->m_time;
                if (qRound((m_time-m_last_log2)*10.0f) >= 60*10.0f) { // every minute
                    m_last_log2=m_time;
                    qDebug() << "Running time: " << this->m_time <<" at " << QLocale("en_GB").toString( QDateTime::currentDateTime(), "hh:mm:ss.zzz");
                }
            }

            // Update Kilobot States:
            if (m_RTID_was_active==0) {
                emit updateKilobotStates();
            }

            //Save image and log data once every m_log_period seconds [we avoid to log data at the timestep that follows a RTID as it can contain spurious information]
            if (m_RTID_was_active==0) {
                //if (qRound(m_time*10.0f) % qRound(m_log_period*10.0f) == 0)
                if (qRound((m_time-m_last_log)*10.0f) >= m_log_period*10.0f)

                { // every m_log_period
                    m_last_log=m_time;
                    if (m_save_images) {
                        emit saveImage(im_filename_prefix.arg(m_expno,1)+im_filename_suffix.arg(m_saved_images_counter++, 5,10, QChar('0')));
                    }
                    if (m_log_exp)
                    {
                        log_stream << this->m_time;
                        for (int i = 0; i < allKiloIDs.size(); ++i){
                            kilobot_id kID = allKiloIDs[i];
                            log_stream << "\t" << kID << "\t" << allKilos[kID].colour << "\t" << allKilos[kID].position.x() << "\t" << allKilos[kID].position.y() << "\t" << allKilos[kID].orientation << "\t" << m_options_env.m_going_resampling_list[kID];
                        }
                        log_stream << endl;
                    }
                }
            } else {
                m_RTID_was_active -= 1;
            }

            // Check if it is time retrieve data
            if( m_DataRetrieval_ON && (qRound((m_time-m_last_data_retrieval)*10.0f) >= m_data_retrieval_period*10.0f || m_data_retrieval_running) ) {
                m_last_data_retrieval=m_time;
                if(m_data_retrieval_running)
                {
                    m_DataRetrieval.run();
                }
                else
                {
                    m_DataRetrieval.initialise(allKilos.size(),m_data_retrieval_method,1,3,true);
                    m_data_retrieval_running=true;
                }
                qDebug() << " * * * * * Data Retrieved: " << m_DataRetrieval.m_retrieved_data;
            }

            if(!m_data_retrieval_running) {

                //                qDebug() << "m_VirtualSensorsNeedUpdate=" <<m_optionsEnv.m_VirtualSensorsNeedUpdate;
                //                qDebug() << "m_time-Trobot_last=" <<m_time-Trobot_last;
                //                qDebug() << "broadcasing=" <<broadcasing;

                /* Check if the robots are required to stop speaking:  time to update virtual sensors */
                if ( m_time-m_Trobot_last >= m_Trobot ) {

                    m_Trobot_last=m_time;

                    /* if it is time to update the virtual-sensors and there is things to update for at least one robot */
                    if((m_options_env.m_virtual_sensors_need_update) && !m_broadcasing
                            && ((!m_stop_speaking_msg_sent && !m_options_env.m_time_for_updating_virtual_sensors) || m_experiment_finished ) ) {
                        //qDebug() << "Sending Stop speaking message";

                        kilobot_broadcast msg;
                        msg.type=5; // Stop speaking message
                        emit broadcastMessage(msg);

                        m_broadcasing=true;
                        m_t_since=1;

                        m_options_env.m_virtual_sensors_need_update=false;

                        m_stop_speaking_msg_sent=true;
//                        for(int i=0 ; i<m_options_env.m_update_messaging_queue.size(); i++){
//                            m_options_env.m_update_messaging_queue[i]=true;
//                        }
                        /* update the kilobot msg group */
                        m_msg_group = (m_msg_group+1)%m_kilo_group_for_messaging.size();
                        /* activate only robots within the msg group */
                        for(int i=0 ; i<m_kilo_group_for_messaging.at(m_msg_group).size(); i++){
                            m_options_env.m_update_messaging_queue[ m_kilo_group_for_messaging.at(m_msg_group).at(i) ]=true;
                        }
                    }
                }

                /* if the robot are quite, ARK can speak */
                if(m_stop_speaking_msg_sent && !m_broadcasing) {
                    //qDebug() << "Stop speaking message sent... now ARK can speak!";
                    m_there_are_msgs_to_send=true;
                    m_options_env.m_time_for_updating_virtual_sensors=true;
                    m_stop_speaking_msg_sent=false;
                }

                /* if all virtual-sensors of the robots has been updated, robot can return to speak */
                if(m_options_env.m_time_for_updating_virtual_sensors && !m_there_are_msgs_to_send && !m_experiment_finished) {
                    //qDebug() << "Sending come back speaking message";

                    // Ask the robots to resume speaking to each other
                    kilobot_broadcast msg;
                    msg.type=6; // Comeback to speaking message
                    emit broadcastMessage(msg);
                    m_broadcasing=true;
                    m_t_since=1;

                    m_options_env.m_time_for_updating_virtual_sensors=false;
                    m_Trobot_last=m_time;
                }

                /* if the experiment is finished, the robot stop speaking and move to the selected option */
                if( m_time >= (m_experiment_length*m_experiment_phase)+(m_go_to_site_length*(m_experiment_phase-1)) && !m_experiment_finished) {
                    m_experiment_finished = true;

                    qDebug() << "************************************************************************************************";
                    qDebug() << "************************************* EXPERIMENT FINISHED *************************************";
                    qDebug() << "************************************************************************************************";
                    qDebug() << "*************************************** BROADCAST MSG 7 ****************************************";
                    qDebug() << "************************************************************************************************";

                    // Inform the robot that the decision-time has terminated
                    kilobot_broadcast msg;
                    msg.type=7; // Experiment finished
                    emit broadcastMessage(msg);
                    m_broadcasing=true;
                    m_t_since=3;
                }

                /* if the experiment is finished and the robot had time to go to the area, MOVE TO THE NEXT PHASE */
                if( m_experiment_finished && m_time >= (m_experiment_length+m_go_to_site_length)*m_experiment_phase && m_experiment_phase < m_experiment_number_of_phases) {
                    m_experiment_finished = false;
                    m_experiment_phase = m_experiment_phase+1;

                    qDebug() << "************************************************************************************************";
                    qDebug() << "************************************* NEW EXPERIMENT PHASE *************************************";
                    qDebug() << "************************************************************************************************";
                    qDebug() << "*************************************** BROADCAST MSG 10 ***************************************";
                    qDebug() << "************************************************************************************************";

                    kilobot_broadcast msg;
                    msg.type=10; // Configuration message
                    msg.data.resize(9);
                    msg.data[0]= m_options_env.m_options[0].ID; // OP ID
                    msg.data[1]= (uint8_t) m_options_env.m_options[0].GPS_X; // OP X
                    msg.data[2]= (uint8_t) m_options_env.m_options[0].GPS_Y; // OP Y
                    msg.data[3]= (m_inhibition_type_next_phase==QString("cross"))? 0 : 1; // i.e., CROSS=0 and SELF=1
                    msg.data[4]= (m_arena_size==QString("1x1 sq.m"))? m_options_env.m_GPS_cells/2 : m_options_env.m_GPS_cells;
                    msg.data[5]= 2; // min distance for waypoint sampling

                    emit broadcastMessage(msg);
                    m_broadcasing=true;
                    m_t_since=1;

                    /* in phase 3, we set the option qualities to asym */
                    if (m_experiment_phase==3) {
                        for(size_t i=1; i<=m_number_of_options ; i++) {
                            m_options_env.m_options[i].quality = i*m_highest_quality/m_number_of_options;
                            qDebug() << "Quality of Option " << i << " has been set to " << m_options_env.m_options[i].quality;
                        }
                    }
                }
            }

            m_options_env.update(); // update the dynamic (virtual) environment

            /* plot virtual environment */
            clearDrawings();
            clearDrawingsOnRecordedImage();
            plotEnvironment();
        }
        else{
            if (m_RTID_was_active==0) { // it means this is the first timestep with active RTID
                m_RTID_timer.start();
            }
            m_RTID_was_active=m_RTID_period_of_stopped_activity_after_active; // flag used to avoid to log spurious data after RTID. We wait for RTID_periodOfStoppedActivityAfterActive loops
            clearDrawings();
            clearDrawingsOnRecordedImage();
        }
    }


}

// Setup the Initial Kilobot Environment:
//   This is run once for each kilobot after emitting getInitialKilobotStates() signal.
//   This assigns kilobots to an environment.
void mykilobotexperiment::setupInitialKilobotState(Kilobot kilobotCopy) {

    // Assigns all kilobots to environment pheroEnv:
    this->setCurrentKilobotEnvironment(&m_options_env);

    kilobot_id kID = kilobotCopy.getID();

    // create a necessary lists and variables
    if (kID > allKilos.size()-1)
    {
        allKilos.resize(kID+1);
        m_options_env.m_single_discovery.resize(kID+1);
        m_options_env.m_prev_discovery.resize(kID+1);
        m_options_env.m_require_GPS.resize(kID+1);
        m_options_env.m_messaging_queue.resize(kID+1);
        m_options_env.m_update_messaging_queue.resize(kID+1);
        previousColourList.resize(kID+1);
        m_options_env.m_going_resampling_list.resize(kID+1);
    }

    KiloLog kLog(kID, kilobotCopy.getPosition(), 0, OFF);
    allKilos[kID] = kLog;
    previousColourList[kID] = OFF;
    m_options_env.m_going_resampling_list[kID] = false;
    if (!allKiloIDs.contains(kID)) allKiloIDs.append(kID);

}

// run once for each kilobot after emitting updateKilobotStates() signal
void mykilobotexperiment::updateKilobotState(Kilobot kilobotCopy) {

    kilobot_id kID = kilobotCopy.getID();
    QPointF kPos = kilobotCopy.getPosition();
    lightColour kColor=kilobotCopy.getLedColour();

    lightColour commitment = kColor;
    if (commitment==OFF){ // if the tracker detects an OFF led, we use the previous detected colour (as in the compare method there are no uncommitted)
        commitment = previousColourList[kID];
    } else {
        // if the robot changed opinion it needs resampling (except if it is already within the option)
        if ( previousColourList[kID] != commitment && commitment!=OFF && previousColourList[kID]!=OFF) { // I use previousColourList[kID]!=OFF to avoid to initially cast all robots as needed resampling
            /* check if already within option, in this case, (we assume) no resamplind would be needed */
            unsigned int oidx = m_options_env.indexOptOfColour(commitment);
            int idx=-1;
            for (int i=0;i<m_options_env.m_options.size();i++ ) { if (m_options_env.m_options[i].ID==oidx) {idx=i;} }
            /* if not in the option area, set goingResamplingList[kID]=true */
            m_options_env.m_going_resampling_list[kID] = !(idx>=0 && (pow(kPos.x()-m_options_env.m_options[idx].posX,2)+pow(kPos.y()-m_options_env.m_options[idx].posY,2)) < pow(m_options_env.m_options[idx].rad,2) );
        }
        previousColourList[kID] = commitment;
    }

    // update values for logging
    if (m_log_exp){
        allKilos[kID].updateAllValues(kID, kPos, 0, kColor);
    }

}

// Setup Environment
void mykilobotexperiment::setupEnvironments( )
{

    qsrand(time(NULL));

    QVector<int> RandPosCopy,RandPos;

    for(size_t i=1; i<=m_number_of_options ; i++)
    {
        RandPosCopy.push_back(i);
    }

    for(size_t i=1; i<=m_number_of_options ; i++)
    {
        int rand=qrand()%m_number_of_options;

        while (RandPosCopy[rand]==0)
        {
            rand=qrand()%m_number_of_options;
        }

        RandPos.push_back(RandPosCopy[rand]);
        RandPosCopy[rand]=0;
    }


    option Op;

    /* These time-varying properties are not used in this experiment */
    Op.AppearanceTime=0.0;
    Op.DisappearanceTime=0.0;
    Op.QualityChangeTime=0.0;
    Op.QualityAfterChange=0.0;

    for(size_t i=1; i<=m_number_of_options ; i++) {
        Op.ID=i;

        /* set the option's quality */
        if(m_quality_dist_type == "asym") {
            Op.quality=i*m_highest_quality/m_number_of_options;
        }
        else if (m_quality_dist_type == "sym") {
            Op.quality=m_highest_quality;
        }

        /* set the option's detection range (Op.rad) */
        if(m_option_size_dist_type == "asym") {
            Op.rad=sqrt( (m_number_of_options+1.0-i)/m_number_of_options )*m_option_radius*M_TO_PIXEL;
        }
        else if (m_option_size_dist_type == "sym") {
            Op.rad=m_option_radius*M_TO_PIXEL;
        }

        /* Set option colours (only for visualisation) */
        switch (i){
            case 1: Op.color=QColor(255,0,0); break;
            case 2: Op.color=QColor(0,0,255); break;
            case 3: Op.color=QColor(0,255,0); break;
            case 4: Op.color=QColor(255,0,255); break;
            case 5: Op.color=QColor(0,255,255); break;
            case 6: Op.color=QColor(255,255,0); break;
            default: Op.color=QColor(255,255,255); break;
        }

        /* Compute option position */
        Op.posX=(m_polygone_radius*qCos((m_number_of_options-RandPos[i-1])*2*M_PI/m_number_of_options)+1)*M_TO_PIXEL+m_x_offset;
        Op.posY=(m_polygone_radius*qSin((m_number_of_options-RandPos[i-1])*2*M_PI/m_number_of_options)+1)*M_TO_PIXEL+m_y_offset;
        //        Op.color=QColor(255,255-Op.quality/m_HighestQuality*255,255-Op.quality/m_HighestQuality*255);

        /* Convert the pixel coordinates to GSP coordinates (discrete cells) */
        QPoint GPS_cords=m_options_env.PositionToGPS(QPointF(Op.posX,Op.posY));
        Op.GPS_X= (unsigned int) GPS_cords.x();
        Op.GPS_Y= 31-(unsigned int) GPS_cords.y();

        qDebug() << "Option=" << i << " Quality=" << Op.quality << " GPS.X="<<Op.GPS_X << " GPS.Y="<<Op.GPS_Y << " Size="<<Op.rad;

        // Add the options to the en
        m_options_env.m_options.push_back(Op);
    }

    plotEnvironment();
}

// Draw the options:
void mykilobotexperiment::plotEnvironment()
{
    option Op;
    for(int i=0;i<m_options_env.m_options.size();i++)
    {
        Op=m_options_env.m_options[i];

        if( Op.DisappearanceTime==0 || m_time < Op.DisappearanceTime)
        {
            drawCircle(QPointF(Op.posX, Op.posY),Op.rad, Op.color, 8,"",true);
        }
    }
}

// Slot to inform the data retrieval process about the color of the kilobots
void mykilobotexperiment::InformDataRetrievalProcessAboutRobotsColors(std::vector<lightColour>& infovector)
{
    infovector.clear();
    for(int i=0;i<allKilos.size();i++){
        infovector.push_back(allKilos[i].colour);
    }
}



void mykilobotexperiment::UpdateBroadcastingState()
{
    if(m_broadcasing){
        if(m_t_since>0){
            m_t_since--;
        }
        else {
            // STOP sending message
            kilobot_broadcast msg;
            msg.type = 250;
            emit broadcastMessage(msg);
            // Update broadcasting flag
            m_broadcasing=false;

            if(m_number_of_config_msgs_sent == m_options_env.m_options.size() && !m_configuration_msgs_sent && m_robot_speaking ){
                m_configuration_msgs_sent=true;
                qDebug() << "Done sending config messages!";
                qDebug() << "*********************************************";
            }
        }
    }
}
