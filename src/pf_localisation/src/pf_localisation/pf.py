from geometry_msgs.msg import Pose, PoseArray, Quaternion
from pf_base import PFLocaliserBase
import math
import rospy

from util import rotateQuaternion, getHeading
from random import random

from time import time


class PFLocaliser(PFLocaliserBase):
       
    def __init__(self):
        # ----- Call the superclass constructor
        super(PFLocaliser, self).__init__()
        
        # ----- Set motion model parameters
        self.ODOM_ROTATION_NOISE=1
        self.ODOM_TRANSLATION_NOISE=1
        self.ODOM_DRIFT_NOISE=1
 
        # ----- Sensor model parameters
        self.NUMBER_PREDICTED_READINGS = 20     # Number of readings to predict
        
       
    def initialise_particle_cloud(self, initialpose):
        """
        Set particle cloud to initialpose plus noise

        Called whenever an initialpose message is received (to change the
        starting location of the robot), or a new occupancy_map is received.
        self.particlecloud can be initialised here. Initial pose of the robot
        is also set here.
        
        :Args:
            | initialpose: the initial pose estimate
        :Return:
            | (geometry_msgs.msg.PoseArray) poses of the particles
        """
	#print("Entering to initialise cloud")
	poses= PoseArray()  #initialising pose array
	for num in range (0,self.NUMBER_PREDICTED_READINGS):
		p= Pose()	#initialising pose

		xNoise=self.ODOM_TRANSLATION_NOISE*np.random.normal(0,0.1)	#noise calculations
		yNoise=self.ODOM_DRIFT_NOISE*np.random.normal(0,0.1)
		zNoise=0
		random_angular_noise=self.ODOM_ROTATION_NOISE*np.random.normal(0,0.1)

		p.position.x=initialpose.pose.pose.position.x + xNoise		#pose positions+noise
		p.position.y=initialpose.pose.pose.position.y + yNoise
		p.position.z=initialpose.pose.pose.position.z + zNoise
		p.orientation=rotateQuaternion(initialpose.pose.pose.orientation,random_angular_noise)
		
		poses.poses.append(p)		
		#print(num, p.orientation)
        	#print(self.INIT_X, self.INIT_Y,self.INIT_Z,self.INIT_HEADING)
	#poses.header.seq   left it blank
	poses.header.stamp=rospy.Time.now()		#defining the header of the pose array
	poses.header.frame_id="/map"
	#print("Returning after initialising cloud")
       return poses



    def rank_particles(self, scan):
	#function to find the particles witht the highest weights 
    	all_poses = {}
    	for pose in self.particlecloud:
   		weight = sensor_model.get_weight(self, scan, pose)
    		all_poses[pose] = weight
    	#sort the dictionary 
    	ranked_poses = sorted(all_poses.items(), reverse=True)
    	return ranked_poses
    			
    def averageParticles(particles):
	#helper function to average a particle cloud 
	new_pose = Pose() 
	num_particles = particles.size()
			
	avX, avY, avZ, avW = 0 
	for particle in particles:
		avX += particle.pose.pose.position.x
		avY += particle.pose.pose.position.y
		avZ += particle.pose.pose.position.z
		avW += particle.pose.pose.orientation 
	avX = avX / num_particles
	avY = avY / num_particles
	avZ = avZ / num_particles
	avW = avW / num_particles
			
	new_pose.pose.pose.x, new_pose.pose.pose.y, new_pose.pose.pose.z, new_pose.pose.pose.w = avX, avY, avZ, avW
	return new_pose
		
    def update_particle_cloud(self, scan):
        """
        This should use the supplied laser scan to update the current
        particle cloud. i.e. self.particlecloud should be updated.
        
        :Args:
            | scan (sensor_msgs.msg.LaserScan): laser scan to use for update

         """
	#TODO: update the particle cloud 
	#TODO: sample from the particle cloud 
	
	ranked = rank_particles(self, scan)
        best_particle = ranked[0] 
        
	pass

    def estimate_pose(self):
        """
        This should calculate and return an updated robot pose estimate based
        on the particle cloud (self.particlecloud).
        
        Create new estimated pose, given particle cloud
        E.g. just average the location and orientation values of each of
        the particles and return this.
        
        Better approximations could be made by doing some simple clustering,
        e.g. taking the average location of half the particles after 
        throwing away any which are outliers

        :Return:
            | (geometry_msgs.msg.Pose) robot's estimated pose.
         """
	new_pose = Pose()
         
         
        #Solution 1: take the 'best' particle 
        new_pose = best_particle
         
        #Solution 2: take the average of all particles
        new_pose = averageParticles(self.particlecloud)
					         
         
        #solution 3: find clusters in the particle and take the average of the densest cluster 
		
	return new_pose		
        pass


