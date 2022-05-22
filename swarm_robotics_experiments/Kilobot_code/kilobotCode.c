#include "kilolib.h"
#define DEBUG
//#define ARGOS
#ifdef ARGOS
#include <stdio.h> // Only for ARGoS DEBUGGING INFORMATION
#include "agentCDCIlocal.h" // Only for ARGoS DEBUGGING INFORMATION
#endif
#include "debug.h"
#include <stdlib.h>
#include <math.h>
#include <float.h>

#define PI 3.14159265358979323846

#define UNCOMMITTED 0
#define	AGENT_MSG 21

/* Enum for different motion types */
typedef enum {
    STOP = 0,
    FORWARD,
    TURN_LEFT,
    TURN_RIGHT,
} motion_t;

/* Enum for boolean flags */
typedef enum {
    false = 0,
    true = 1,
} bool;

/* Enum for received message type*/
typedef enum {
	UNCOMMITTED_MSG=0,
	RECRUITMENT_MSG,
	INHIBITION_MSG,
} received_message_type;

/* Enum for type of inhibition used in this experiment */
typedef enum {
	CROSSINHIBITION = 0,
	DIRECTSWITCH
} inhibition_type;

/* Flag for successful message sent */
bool message_sent = false;

/* Flag for decision to broadcast a message */
bool broadcast_msg = false;

/* Flag for ARK/Kbs Speaking Management */
bool broadcast_flag=false;

/* current motion type */
motion_t current_motion_type = STOP;

/* current LED color */
uint16_t current_LED_color=RGB(0,0,0);

/* current commitment */
uint8_t my_commitment;
uint8_t my_option_GPS_X;
uint8_t my_option_GPS_Y;
uint8_t my_option_quality;

/* counters for motion, turning, broadcasting and status-update */
unsigned int turning_ticks = 0;
uint32_t last_motion_ticks = 0;
const float rotation_speed=38.0;
const uint32_t broadcast_ticks = 16;
uint32_t last_broadcast_ticks = 0;
uint32_t update_ticks = 1000; /* about 30 seconds: how often performing the commitment update. a tick here is every ~31ms */
uint32_t last_update_ticks = 0;

/* counters for random walk using open loop */
const uint8_t max_turning_ticks = 150; /* constant to allow a maximum rotation of 180 degrees with \omega=\pi/5 */
const uint32_t fixed_straight_ticks = 300;

/* Variables for outgoing messages */
message_t message;
inhibition_type experiment_inhibition_type;

/* Variables for incoming messages from another robot */
uint8_t received_option_GPS_X;
uint8_t received_option_GPS_Y;
bool received_message;
received_message_type received_msg_type;

/* Variables for Smart Arena messages */
unsigned int sa_type;

/* Noise variables */
const double standard_deviation=1.0;

/* Robot GPS variables */
uint8_t robot_GPS_X;
uint8_t robot_GPS_Y;
double robot_orientation;
bool new_sa_msg_gps;
uint8_t GPS_maxcell=10; // information received from ARK config message
uint8_t minDist; // information received from ARK config message

/* Robot Goal variables*/
uint8_t goal_GPS_X;
uint8_t goal_GPS_Y;
uint32_t last_waypoint_ticks;
const uint32_t max_waypoint_ticks=3600; // about 2 minutes

/* Wall Avoidance manouvers */
uint32_t wall_avoidance_counter; // to decide when the robot is stuck on a wall...

/* Options lookup table*/
uint8_t options_IDs[10];
uint8_t options_GPS_X[10];
uint8_t options_GPS_Y[10];
uint8_t options_qualities[10];
uint8_t number_of_options=0;

/* Robot states */
bool zealot;
uint8_t num_zealots=0; // it will be set through ARK (config msg.type 10)

/* RTID variables */
bool runtime_identification=false;
uint32_t backup_kiloticks;
uint16_t backup_LED;
motion_t backup_motion=STOP;


/*-------------------------------------------------------------------*/
/* Function to sample a random number form a Gaussian distribution   */
/*-------------------------------------------------------------------*/
double generateGaussianNoise(const double mu, const double std_dev )
{
    const double epsilon = DBL_MIN;
    const double two_pi = 2.0*PI;
    double u1, u2;
    do
    {
        u1 = rand() * (1.0 / RAND_MAX);
        u2 = rand() * (1.0 / RAND_MAX);
    }
    while ( u1 <= epsilon );

    double z0;
    z0 = sqrt(-2.0 * log(u1)) * cos(two_pi * u2);
    //        z1 = sqrt(-2.0 * log(u1)) * sin(two_pi * u2);
    return z0 * std_dev + mu;
}


/*-------------------------------------------------------------------*/
/* Normalise degree angle in range [-180,180]                        */
/*-------------------------------------------------------------------*/
void normaliseAngle(double* angle)
{
    while(*angle>180){
        *angle=*angle-360;
    }
    while(*angle<-180){
        *angle=*angle+360;
    }
}

/*-------------------------------------------------------------------*/
/* Compute angle to Goal                                             */
/*-------------------------------------------------------------------*/
double angle_to_goal() {
    normaliseAngle(&robot_orientation);
    double angletogoal=atan2(goal_GPS_Y-robot_GPS_Y,goal_GPS_X-robot_GPS_X)/PI*180-robot_orientation;
    normaliseAngle(&angletogoal);
    return angletogoal;
}

/*-------------------------------------------------------------------*/
/* Coordinates to option ID                                          */
/*-------------------------------------------------------------------*/
uint8_t coordsToID(uint8_t option_GPS_X,uint8_t option_GPS_Y)
{
    int i;
    for(i=0;i<number_of_options;i++){
        if( (option_GPS_X==options_GPS_X[i]) && (option_GPS_Y==options_GPS_Y[i]) )
        {
            return options_IDs[i];
        }
    }
    return UNCOMMITTED;
}


/*-------------------------------------------------------------------*/
/* Get option's quality from coordinates                             */
/*-------------------------------------------------------------------*/
uint8_t get_opt_quality(uint8_t option_GPS_X,uint8_t option_GPS_Y)
{
    int i;
    for(i=0;i<number_of_options;i++){
        if( (option_GPS_X==options_GPS_X[i]) && (option_GPS_Y==options_GPS_Y[i]) )
        {
            return options_qualities[i];
        }
    }
    return 0;
}

/*-------------------------------------------------------------------*/
/* Function for setting the motor speed                              */
/*-------------------------------------------------------------------*/
void set_motion( motion_t new_motion_type ) {
    if( current_motion_type != new_motion_type )
    {
        current_motion_type = new_motion_type;

        int calibrated = true;
        switch( new_motion_type )
        {
        case FORWARD:
            if(!runtime_identification)
                spinup_motors();
            if (calibrated){
                if(!runtime_identification){
                	set_motors(kilo_straight_left,kilo_straight_right);
                }
            }
            else
            {
                if(!runtime_identification){
                	set_motors(67,67);
                }
            }
            break;
        case TURN_LEFT:
            if(!runtime_identification)
                spinup_motors();
            if (calibrated)
            {
                if(!runtime_identification) {
                    uint8_t leftStrenght = kilo_turn_left;
                    uint8_t i;
                    for (i=3; i <= 18; i += 3){
                        if (wall_avoidance_counter >= i){
                            leftStrenght+=2;
                        }
                    }
                    set_motors(leftStrenght,0);
//                    set_motors(kilo_turn_left,0);
                }
            }
            else{
                if(!runtime_identification){
                	set_motors(70,0);
                }
            }
            break;
        case TURN_RIGHT:
            if(!runtime_identification)
                spinup_motors();
            if (calibrated){
                if(!runtime_identification) {
                    uint8_t rightStrenght = kilo_turn_right;
                    uint8_t i;
                    for (i=3; i <= 18; i += 3){
                        if (wall_avoidance_counter >= i){
                            rightStrenght+=2;
                        }
                    }
                    set_motors(0,rightStrenght);
//                    set_motors(0,kilo_turn_right);
                }
            }
            else{
                if(!runtime_identification){
                	set_motors(0,70);
                }
            }
            break;
        case STOP:
        default:
            set_motors(0,0);
        }

        if(current_motion_type!=STOP){
            backup_motion=current_motion_type;
        }
    }
}


/*-------------------------------------------------------------------*/
/* Function for setting the the new commitment state                 */
/*-------------------------------------------------------------------*/
void set_commitment( uint8_t new_option_GPS_X, uint8_t new_option_GPS_Y, uint8_t new_quality) {

    /* update the commitment state varieable */
    my_option_GPS_X = new_option_GPS_X;
    my_option_GPS_Y = new_option_GPS_Y;
    my_option_quality = new_quality;
    my_commitment=coordsToID(new_option_GPS_X,new_option_GPS_Y);
}

/*-----------------------------------------------------------------------------------*/
/* Function implementing the uncorrelated random walk with the random waypoint model */
/*-----------------------------------------------------------------------------------*/
void random_walk_waypoint_model(bool selectNewWaypoint){
	/* if the robot arrived to the destination, OR too much time has passed, a new goal is selected */
	if ( selectNewWaypoint || ((robot_GPS_X==goal_GPS_X) && (robot_GPS_Y==goal_GPS_Y)) || kilo_ticks >= last_waypoint_ticks + max_waypoint_ticks) {
		last_waypoint_ticks = kilo_ticks;

		int random;
		do {
			uint8_t padding = 1;
			// getting a random number in the range [padding,GPS_maxcell-padding] to avoid the border cells
#ifdef ARGOS
		    int i; for (i=0;i<rand()%10;i+=1){
		    	rand(); // there's an issue with getting two times a rand value...
		    }
#endif
			random = rand()%( GPS_maxcell-(padding*2));
			goal_GPS_X=random+padding;
			random = rand()%( GPS_maxcell-(padding*2));
			goal_GPS_Y=random+padding;
			if ( abs(robot_GPS_X-goal_GPS_X) >= minDist || abs(robot_GPS_Y-goal_GPS_Y) >= minDist ){ // if the selected cell is enough distant from the current location, it's good
				break;
			}
		} while(true);
	}
}

/*-------------------------------------------------------------------*/
/* Init function                                                     */
/*-------------------------------------------------------------------*/
void setup()
{
    /* Initialise commitment */
    set_commitment(0 , 0 , 0);

    /* Initialise robot states */
    zealot=false;

    /* Initialise motors */
    set_motors(0,0);

    /* Initialise random seed */
    uint8_t seed = rand_hard();
    rand_seed(seed);
    seed = rand_hard();
    srand(seed);

    /* Initialise motion variables */
    set_motion( FORWARD );
    last_motion_ticks = rand() % fixed_straight_ticks + 1;
    wall_avoidance_counter=0;

    /* Initialise broadcast variables */
    last_broadcast_ticks = rand() % broadcast_ticks + 1;

    /* Initialise update variables and counters */
    last_update_ticks= rand() % update_ticks;

    /* Initialise received message variables */
    received_message = false;
    new_sa_msg_gps=false;
    received_option_GPS_X=0;
    received_option_GPS_Y=0;

    /* Intialize time to 0 */
    kilo_ticks=0;

    /* initialise the GSP to the middle of the environment, to avoid to trigger wall avoidance immediately */
    robot_GPS_X = GPS_maxcell/2;
    robot_GPS_Y = GPS_maxcell/2;
    minDist = 1;
    random_walk_waypoint_model(true);

}


/*-------------------------------------------------------------------*/
/* Function to parse the ARK messages into variables                 */
/*-------------------------------------------------------------------*/
void parse_ARK_message( uint8_t byte1, uint8_t byte2) {
    // unpack type
    sa_type = (byte1 >> 6) & 0x03;
    if(sa_type==1){ /* GPS message */
        // unpack payload
        robot_GPS_X = ( byte1 >> 1 ) & 0x1F;
        robot_GPS_Y = ( (byte1 & 0x01) << 4) | ((byte2>>4) & 0x0F) ;
        robot_orientation = (byte2 & 0x0F);//*22.5;
        robot_orientation = robot_orientation*22.5;
        normaliseAngle(&robot_orientation);
        new_sa_msg_gps = true;
    }
}

/*-------------------------------------------------------------------*/
/* Callback function for message reception                           */
/*-------------------------------------------------------------------*/
void message_rx( message_t *msg, distance_measurement_t *d ) {
    /** ARK MESSAGE **/
	if (msg->type == 0) {
        // unpack message
        int id1 = msg->data[0];
        int id2 = msg->data[3];
        int id3 = msg->data[6];

        if (id1 == kilo_uid) {
            parse_ARK_message(msg->data[1],msg->data[2]);
        }
        if (id2 == kilo_uid) {
            parse_ARK_message(msg->data[4],msg->data[5]);
        }
        if (id3 == kilo_uid) {
            parse_ARK_message(msg->data[7],msg->data[8]);
        }
    }
	/** ARK Config File **/
    else if (msg->type == 10) {
        // Options lookup table
        if(number_of_options==0 || msg->data[0]!=options_IDs[number_of_options-1]){
            options_IDs[number_of_options] = msg->data[0];
            options_GPS_X[number_of_options] = msg->data[1];
            options_GPS_Y[number_of_options] = msg->data[2];
            options_qualities[number_of_options] = msg->data[3];
            GPS_maxcell=msg->data[4];
            minDist=msg->data[5];
            num_zealots=msg->data[6];

            /* initialise the GSP to the middle of the environment, to avoid to trigger wall avoidance immediately */
            robot_GPS_X = rand()%GPS_maxcell;
            robot_GPS_Y = rand()%GPS_maxcell;
            random_walk_waypoint_model(true);

            number_of_options++;

            //printf("Received info. GPS-size: %d , minDist: %d , exp-type: %d , O%d : (%d,%d) \n", GPS_maxcell, minDist, experiment_inhibition_type, options_IDs[number_of_options-1], options_GPS_X[number_of_options-1], options_GPS_Y[number_of_options-1] );
            uint8_t quality = (uint8_t) ( 10 * (  generateGaussianNoise( options_qualities[kilo_uid%number_of_options], standard_deviation) ) );
            if(quality>100){ quality=100; }
            if(quality<0){ quality=0; }
            set_commitment(options_GPS_X[kilo_uid%number_of_options], options_GPS_Y[kilo_uid%number_of_options], quality);
            if (kilo_uid < num_zealots){
            	zealot=true;
            }
            if (number_of_options==2){
            	printf("[%u] Set comm %u q:%u [z:%u]\n",kilo_uid, kilo_uid%number_of_options, my_option_quality, zealot);
            }
            //latent_state=true;
        }
        experiment_inhibition_type = msg->data[7];
    }
	/** ARK ID identification **/
    else if (msg->type == 120) {
        int id = (msg->data[0] << 8) | msg->data[1];
        if (id == kilo_uid) {
            set_color(RGB(0,0,3));
        } else {
            set_color(RGB(3,0,0));
        }
    }
	/** ARK Runtime identification **/
    else if (msg->type == 119) {
        // runtime identification
        int id = (msg->data[0] << 8) | msg->data[1];
        if (id >= 0){ // runtime identification ongoing
            set_motion(STOP);
            runtime_identification = true;
            if (id == kilo_uid) {
                set_color(RGB(0,0,3));
            } else {
                set_color(RGB(3,0,0));
            }
        } else { // runtime identification ended
            kilo_ticks=backup_kiloticks;
            //set_color(current_LED_color);
            runtime_identification = false;
            set_motion(backup_motion);
        }
    }
	/** ARK Disable robot broadcasting **/
    else if (msg->type == 5) {
        broadcast_flag=false;
    }
	/** ARK Enable robot broadcasting **/
    else if (msg->type == 6) {
        broadcast_flag=true;
        last_broadcast_ticks = kilo_ticks - (rand()%broadcast_ticks); // de-synch the broadcasting
    }
        /** ARK Experiment finished - Go to selected area **/
    else if (msg->type == 7) {
        broadcast_flag=false;
        //experiment_finished=true;
        goal_GPS_X=my_option_GPS_X;
        goal_GPS_Y=my_option_GPS_Y;
    }
	/** Message from another robot **/
    else if (msg->type == AGENT_MSG) {
//    	if ( my_option_GPS_X==0 && my_option_GPS_Y==0 && !latent_state){
//    		printf("[%u]%u Uncomm received msg \n",kilo_uid,kilo_ticks);
//    	}
        // the received message is from another KB
        received_option_GPS_X = msg->data[0];
        received_option_GPS_Y = msg->data[1];
        received_msg_type = (received_message_type) msg->data[2];
        received_message = (bool) msg->data[3];
    }

}


/*--------------------------------------------------------------------------*/
/* Function for updating the commitment state (wrt to the received message) */
/*--------------------------------------------------------------------------*/
void update_commitment() {

	if(runtime_identification) { return; }
	/* Updating the commitment only each update_ticks */
	if ( kilo_ticks > last_update_ticks + update_ticks ) {
		last_update_ticks = kilo_ticks;

		/* if the agent is uncommitted, it can do discovery or recruitment */
		if ( my_option_GPS_X==0 && my_option_GPS_Y==0){

			/* RECRUITMENT*/
			if (received_message && (received_msg_type==RECRUITMENT_MSG) && ( (received_option_GPS_X!=0) || (received_option_GPS_Y!=0) ))
			{
				/* the agent gets recruited a new option*/
				uint8_t quality = (uint8_t) ( 10 * (  generateGaussianNoise( get_opt_quality(received_option_GPS_X, received_option_GPS_Y), standard_deviation) ) );
				if(quality>100){ quality=100; }
				if(quality<0){ quality=0; }
				set_commitment(received_option_GPS_X, received_option_GPS_Y, quality);

			}
		}
		/* if the agent is committed */
		else {
			/* I receive a message from another agent */
			/* the other agent must be: (i) committed and (ii) with option different than mine  */
			if (received_message && ( (my_option_GPS_X!=received_option_GPS_X) || (my_option_GPS_Y!=received_option_GPS_Y) ) ) {
				/* INHIBITION */
				if (experiment_inhibition_type==CROSSINHIBITION){
					set_commitment(0, 0, 0);
				}
				/* DIRECT SWITCH */
				else if (experiment_inhibition_type==DIRECTSWITCH ) {
					// resampling from the nominal quality (which is stored for simplicity)
					uint8_t quality = (uint8_t) ( 10 * (  generateGaussianNoise( get_opt_quality(received_option_GPS_X, received_option_GPS_Y), standard_deviation) ) );
					if(quality>100){ quality=100; }
					if(quality<0){ quality=0; }
					set_commitment(received_option_GPS_X, received_option_GPS_Y, quality);
				}
			}
		}

		received_message = false;
	}
}


/*-------------------------------------------------------------------*/
/* Function to go to the Goal location (e.g. to resample an option)  */
/*-------------------------------------------------------------------*/
void go_to_goal_location(){
    if(new_sa_msg_gps){
        new_sa_msg_gps=false;

        double angleToGoal = angle_to_goal();
        if(fabs(angleToGoal) <= 25)
        {
        	set_motion(FORWARD);
        	last_motion_ticks = kilo_ticks;
        }
        else{
        	if(angleToGoal>0){
        		set_motion(TURN_LEFT);
        		last_motion_ticks = kilo_ticks;
        		turning_ticks=(unsigned int) ( fabs(angleToGoal)/rotation_speed*(32.0+(rand()%6)) );
        		//                    debug_print("In need to turn left for: %d\n", turning_ticks );
        	}
        	else{
        		set_motion(TURN_RIGHT);
        		last_motion_ticks = kilo_ticks;
        		turning_ticks=(unsigned int) ( fabs(angleToGoal)/rotation_speed*(32.0+(rand()%6)) );
        		//                    debug_print("In need to turn right for: %d\n", turning_ticks );
        	}
        }
    }

    switch( current_motion_type ) {
    case TURN_LEFT:
        if( kilo_ticks > last_motion_ticks + turning_ticks ) {
            /* start moving forward */
            last_motion_ticks = kilo_ticks;  // fixed time FORWARD
            //	last_motion_ticks = rand() % fixed_straight_ticks + 1;  // random time FORWARD
            set_motion(FORWARD);
        }
        break;
    case TURN_RIGHT:
        if( kilo_ticks > last_motion_ticks + turning_ticks ) {
            /* start moving forward */
            last_motion_ticks = kilo_ticks;  // fixed time FORWARD
            //	last_motion_ticks = rand() % fixed_straight_ticks + 1;  // random time FORWARD
            set_motion(FORWARD);
        }
        break;
    case FORWARD:
        break;

    case STOP:
    default:
        set_motion(STOP);
    }

}

/*-------------------------------------------------------------------*/
/* Function to broadcast the commitment message                     */
/*-------------------------------------------------------------------*/
void broadcast() {
	if ( ( kilo_ticks > last_broadcast_ticks + broadcast_ticks ) && (broadcast_flag==true) ) {
		last_broadcast_ticks = kilo_ticks + (rand()%3);

		if ( my_option_GPS_X!=0 || my_option_GPS_Y!=0 )
		{
			/* start composing the message */
			message.data[0] = my_option_GPS_X;
			message.data[1] = my_option_GPS_Y;

			/* Recruitment message */
			message.data[2] = RECRUITMENT_MSG;

			/* Probabilistically decides if the message to send will be active or not */
			/* drawing a random number */
			int randomInt = RAND_MAX;
			while (randomInt > 30000){
				randomInt = rand();
			}
			unsigned int RANGE_RND = 10000;
			unsigned int random = randomInt % RANGE_RND + 1;

			double prob_share_commitment = my_option_quality / 100.0;
			unsigned int prob_share_commitment_int= (unsigned int)(prob_share_commitment*RANGE_RND)+1;;

			if (prob_share_commitment > 0 && random <= prob_share_commitment_int){
				message.data[3] = 1; // active message
			}
			else {
				message.data[3] = 0; // inactive message
			}

			/* complete the message */
			message.type = AGENT_MSG;
			message.crc  = message_crc(&message);

			/* set broadcast flag for transmission */
			broadcast_msg = true;
		}
		else {
			/* set broadcast flag for transmission */
			broadcast_msg = false;
			message.data[3] = 0; // inactive message
		}
	}
	if (runtime_identification || !broadcast_flag) { broadcast_msg = false; }
}


/*-------------------------------------------------------------------*/
/* Callback function for message transmission                        */
/*-------------------------------------------------------------------*/
message_t *message_tx() {
    if( broadcast_msg ) {
        return &message;
    }
    return 0;
}


/*-------------------------------------------------------------------*/
/* Callback function for successful transmission                     */
/*-------------------------------------------------------------------*/
void tx_message_success() {
    broadcast_msg = false;
}


/*---------------------------------------------------------------------------------------------*/
/* Counter for the number of consecutive steps in which the robot's location is against a wall */
/*---------------------------------------------------------------------------------------------*/
void check_if_against_a_wall(){
    if ( robot_GPS_X==0 || robot_GPS_X>=GPS_maxcell-1 || robot_GPS_Y==0 || robot_GPS_Y>=GPS_maxcell-1 ){
        if (wall_avoidance_counter<18)
            wall_avoidance_counter += 1;
        else
            wall_avoidance_counter = 1;
    } else {
        wall_avoidance_counter = 0;
    }
}

/*-------------------------------------------------------------------*/
/* Function to set the LED colour as a function of my_commitment     */
/*-------------------------------------------------------------------*/
void set_commitment_colour(){
	if (my_option_quality==0 && my_commitment!=0) {
		set_color(RGB(0,3,3));
		return;
	}
//	if (!latent_state) {
//		set_color(RGB(3,3,3));
//		return;
//	}
    switch( my_commitment ) {
    case 6:
        set_color(RGB(3,3,0));
        break;
    case 5:
        set_color(RGB(0,3,3));
        break;
    case 4:
        set_color(RGB(3,0,3));
        break;
    case 3:
        set_color(RGB(zealot,3,0));
        break;
    case 2:
        set_color(RGB(0,zealot,3));
        break;
    case 1:
        set_color(RGB(3,zealot,0));
        break;
    case 0:
        set_color(RGB(0,0,0));
        break;
    default:
        set_color(RGB(3,3,3));
        break;
    }
}

/*-------------------------------------------------------------------*/
/* Main loop                                                         */
/*-------------------------------------------------------------------*/
void loop() {
    if(!runtime_identification)
    {
        backup_kiloticks=kilo_ticks; // which we restore after runtime_identification

        if (new_sa_msg_gps == true) {
            check_if_against_a_wall();
        }

        if (!zealot && received_message ){ // update commitment at every received message
        	update_commitment();
        }

        if (new_sa_msg_gps) { // if not going to resample
        	random_walk_waypoint_model(false); // update waypoint when it is reached
        }
        go_to_goal_location();

        broadcast();

        /* Set LED color*/
        set_commitment_colour();

    }

#ifdef ARGOS
    debug_info_set(commitment, my_commitment); // Only for ARGoS DEBUGGING INFORMATION
#endif
}


/*-------------------------------------------------------------------*/
/* Main function                                                     */
/*-------------------------------------------------------------------*/
int main()
{
    kilo_init();
#ifndef ARGOS
    debug_init();
#endif
    kilo_message_tx = message_tx;
    kilo_message_tx_success = tx_message_success;
    kilo_message_rx=message_rx;
#ifdef ARGOS
    debug_info_create(); // Only for ARGoS DEBUGGING INFORMATION
#endif

    kilo_start(setup, loop);
    return 0;
}
