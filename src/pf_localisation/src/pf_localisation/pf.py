from geometry_msgs.msg import Pose, PoseArray, Quaternion
from pf_base import PFLocaliserBase
import math
import rospy
import numpy as np
from util import rotateQuaternion, getHeading
from random import random
from collections import OrderedDict
from time import time
from sklearn.cluster import KMeans, AffinityPropagation, DBSCAN
import matplotlib.pyplot as py
from scipy import stats
from sklearn.neighbors import NearestNeighbors


class PFLocaliser(PFLocaliserBase):
   
    def __init__(self):
        # ----- Call the superclass constructor
        super(PFLocaliser, self).__init__()
        
        # ----- Set motion model parameters
        self.ODOM_ROTATION_NOISE=1
        self.ODOM_TRANSLATION_NOISE=1
        self.ODOM_DRIFT_NOISE=1
 
        # ----- Sensor model parameters
        self.NUMBER_PREDICTED_READINGS = 200     # Number of readings to predict
        self.plotted=False
	self.errorList=np.asarray([])
	self.count=0
       
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
        
        poses= PoseArray()  #initialising pose array
        for num in range (0,self.NUMBER_PREDICTED_READINGS):
            p= Pose()	#initialising pose

            xNoise=self.ODOM_TRANSLATION_NOISE*np.random.normal(0,0.8)	#noise calculations
            yNoise=self.ODOM_DRIFT_NOISE*np.random.normal(0,0.8)
            zNoise=0
            random_angular_noise=self.ODOM_ROTATION_NOISE*np.random.normal(0,0.8)

            p.position.x=initialpose.pose.pose.position.x + xNoise		#pose positions+noise
            p.position.y=initialpose.pose.pose.position.y + yNoise
            p.position.z=initialpose.pose.pose.position.z + zNoise
            p.orientation=rotateQuaternion(initialpose.pose.pose.orientation,random_angular_noise)

            poses.poses.append(p)
        #poses.header.seq   left it blank
        poses.header.stamp=rospy.Time.now()		#defining the header of the pose array
        poses.header.frame_id="/map"
	initialPose= Pose()
	initialPose.position.x=initialpose.pose.pose.position.x 		
        initialPose.position.y=initialpose.pose.pose.position.y
        initialPose.position.z=initialpose.pose.pose.position.z
	initialPose.orientation=initialpose.pose.pose.orientation
	self.initial_pose=initialPose
	self.particlecloud=poses
	print("Initialising particle cloud to length ",len(self.particlecloud.poses))
        return poses

    def choose(self,choice): #returns from the cumulative weight dictionary the resampled particle
	#print("-----------")
	#for key in self.weighted_dist:
	#	print(key)
	#print("-----------")
	saved=None
	for key in self.weighted_dist:
		if key<choice:
			saved=self.weighted_dist[key] #save the particle if threshold not reached
			continue
		if key>=choice: #return particle if threshold reached
			if saved==None:
				saved=self.weighted_dist[key] #deals with the case if the first particle is to be returned
			return saved
    
    def update_particle_cloud(self, scan):
        """
        This should use the supplied laser scan to update the current
        particle cloud. i.e. self.particlecloud should be updated.
        
        :Args:
            | scan (sensor_msgs.msg.LaserScan): laser scan to use for update

         """
	self._latest_scan=scan
	#print(scan)
	#print("Entering update ",len(self.particlecloud.poses))
	self.weighted_dist=OrderedDict() #set up an ordered dictionary of the cumulative weights as the key and the particles as the value
	cumulative_weight=0
        for particle in self.particlecloud.poses:
		#print(scan)
		#print(self.sensor_model.get_weight(scan,particle))
		self.weighted_dist[self.sensor_model.get_weight(scan,particle)+cumulative_weight]=particle
		cumulative_weight+=self.sensor_model.get_weight(scan,particle)

	new_PC=PoseArray()
	choice=0
	increment=cumulative_weight/self.NUMBER_PREDICTED_READINGS #choose increment for resampling
	#print("choice", choice, "cumulative weight", cumulative_weight)
	while(choice<cumulative_weight):
		random_choice=np.random.uniform(0,1,1)
		#print("random choice",random_choice)
		p=Pose()
		sampled_particle=self.choose(choice)  #get the resampled particle
		if (random_choice<0.9):						
            		p.position.x=sampled_particle.position.x 		
            		p.position.y=sampled_particle.position.y 
            		p.position.z=sampled_particle.position.z   					
			p.orientation=sampled_particle.orientation
			#print("0.95")
			#print("0.95 ",p.position.x)
		else:
			xNoise=self.ODOM_TRANSLATION_NOISE*np.random.normal(0,2)	#with a small probability generate a sample further away to deal with the kidnapped robot problem
            		yNoise=self.ODOM_DRIFT_NOISE*np.random.normal(0,2)
            		zNoise=0
            		random_angular_noise=self.ODOM_ROTATION_NOISE*np.random.normal(0,0.5)

            		p.position.x=sampled_particle.position.x + xNoise		#pose positions+noise
            		p.position.y=sampled_particle.position.y + yNoise
            		p.position.z=sampled_particle.position.z + zNoise
            		p.orientation=rotateQuaternion(sampled_particle.orientation,random_angular_noise)
			#print("0.05")
			#print("0.05 ",p.position.x)
		#print("Appending to new_PC ",p.position.x)
            	new_PC.poses.append(p) #add particle to new particle cloud
		choice=choice+increment #increment for next resampled particle
	#print("Length of new particle cloud ", len(new_PC.poses))
	self.particlecloud=new_PC #set new particle cloud

    def getPoints(self,clustNum, labels_array, full_arr):  #given a cluster number, the array of cluster labels and the full data, returns the data points in the specified cluster
    	indices= np.where(labels_array == clustNum)[0]
    	return np.asarray([full_arr[i] for i in indices])

    def largest_cluster(self,labels_array):  #find the mode of the cluster label array to find the largest cluster
    	return stats.mode(labels_array)[0]

    def get_estimate(self,arr,eps_val): #given the data and eps_val (needed for DBSCAN), finds the largest cluster, the particles in it, and finds/returns the average position and heading
    	clustering = DBSCAN(eps=eps_val, min_samples=2).fit(arr)
    	largest=self.largest_cluster(clustering.labels_)
    	points=self.getPoints(largest,clustering.labels_,arr)
	q_list=np.asarray([])
	q_mean=Quaternion()


	for pose in self.particlecloud.poses:
		if np.asarray([pose.position.x,pose.position.y]) in points:
			q_list=np.append(q_list,np.asarray([pose.orientation]))
	q_mean.x=np.mean(np.asarray([q.x for q in q_list]))
	q_mean.y=np.mean(np.asarray([q.y for q in q_list]))
	q_mean.z=np.mean(np.asarray([q.z for q in q_list]))
	q_mean.w=np.mean(np.asarray([q.w for q in q_list]))
    	return np.asarray([points[:,0].mean(),points[:,1].mean()]),q_mean
	
    def get_arrow_directions(self,arr,eps_val):  #given the data and the eps_val, gets the headings of each particle and returns the directional data
	clustering = DBSCAN(eps=eps_val, min_samples=2).fit(arr)
    	largest=self.largest_cluster(clustering.labels_)
    	points=self.getPoints(largest,clustering.labels_,arr)
	q_list=np.asarray([])

	
	for pose in self.particlecloud.poses:
		if np.asarray([pose.position.x,pose.position.y]) in points:
			q_list=np.append(q_list,np.asarray([pose.orientation]))
	radian=np.asarray([getHeading(q) for q in q_list])
	u = np.asarray([np.cos(r) for r in radian])
	v = np.asarray([np.sin(r) for r in radian])
	return u,v

    def getError(self,p):
	map_range=self.sensor_model.calc_map_range(p.position.x,p.position.y,0)
	#print("MAP RANGE: ",map_range)
	obs_range=self._latest_scan
	#print("OBS_RANGE max: ",np.max(obs_range.ranges)-np.min(obs_range.ranges), type(np.max(obs_range.ranges)))
	error= self.sensor_model.predict(np.max(obs_range.ranges)-np.min(obs_range.ranges),map_range)
	print("ERROR: ",error)
	return error

    def plotError(self):
	print("ERROR GRAPH!")
	py.scatter(np.asarray([i for i in range(1,len(self.errorList)+1)]),self.errorList)
	py.show(block=False)
	self.plotted=True

    def plotArrows(self,eps_val,pos_clustering,q):
	#debugging data/ takes a snap shot of the system at the start and plots an arrow graph of headings and positions and marks the estimated spot
	#clusters=KMeans(n_clusters=3,precompute_distances=True).fit(pos_clustering)
	#clusters=AffinityPropagation(affinity='euclidean',preference=None,damping=0.5).fit(pos_clustering)
	clusters=DBSCAN(eps=eps_val, min_samples=2).fit(pos_clustering)
	py.figure()
	u,v=self.get_arrow_directions(pos_clustering,eps_val)

	colours=np.asarray([])					#need to make sure all values in color param in quiver is >0
	min_val=np.min(clusters.labels_.astype(float))
	if min_val<0:
		colours=np.asarray([c+ np.abs(min_val) for c in clusters.labels_.astype(float)])
	if min_val==0:
		colours=np.asarray([c+ 1 for c in clusters.labels_.astype(float)])
	else:
		colours=clusters.labels_.astype(float)

	py.quiver(pos_clustering[:,0],pos_clustering[:,1],u,v,colours)   #plot quiver graph
	mean_point,q_mean=self.get_estimate(pos_clustering,eps_val)
	#print(pos_clustering)
	py.quiver(mean_point[0],mean_point[1],np.cos(getHeading(q)),np.sin(getHeading(q)),color='red')	#plot mean	
	py.show(block=False)
	self.plotted=True	

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
	#print("Estimating pose")
	pos_clustering=np.empty((0,2),float) #get the particle postion data
	quaternion_cluster=np.asarray([])
	#print(self.particlecloud.poses)
	if(len(self.particlecloud.poses)==0):
		print("Particle clous not initialised")
		return
	for pose in self.particlecloud.poses:
		pos_clustering=np.concatenate((pos_clustering,np.asarray([[pose.position.x,pose.position.y]])),axis=0)
	#print(self.particlecloud.poses)
	nbrs = NearestNeighbors(n_neighbors=5, algorithm='auto',metric='euclidean').fit(pos_clustering)  #using the third furthest nearest neighbour as the eps_val for the DBSCAN (read the heuristic)
	distances, indices = nbrs.kneighbors(pos_clustering)
	eps_val=np.sort(distances[:,1])[len(pos_clustering)-3]		
	
	clusters=DBSCAN(eps=eps_val, min_samples=2).fit(pos_clustering)  #run DBSCAN to get the clusters
	mean_point, q=self.get_estimate(pos_clustering,eps_val)         # get the average position and quaternion from the largest cluster from DBSCAN

	p=Pose()

        p.position.x=mean_point[0]		#set new pose with average data (estimated pose)
        p.position.y=mean_point[1]
        p.position.z=0  					
	p.orientation=q 

	error=self.getError(p)
	self.errorList=np.concatenate((self.errorList,np.asarray([error])),axis=0)
	if(len(self.errorList)==30):
		self.plotError()

	#if (self.plotted==False and self.count==5):    
		#self.plotArrows(eps_val,pos_clustering,q)
	self.count+=1
        return p







