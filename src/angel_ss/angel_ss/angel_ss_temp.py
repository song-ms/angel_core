from turtle import update
import psutil
import sys
import urllib.request #파이썬3에서
import threading
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Temperature
from std_msgs.msg import Float64MultiArray
from std_msgs.msg import Bool
import pymongo
import subprocess
import json
from std_msgs.msg import String

# apiKey = 'thingSpeak api-key for reading'
# baseURL = 'https://api.thingspeak.com/update?api_key='+apiKey+'&field1='

MONGO_HOSTNAME = '192.168.0.243'
MONGO_PORT = '27017'
MONGO_DB = 'wasp'

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('angel_core')
        subprocess.run(["chmod", "+x", "src/angel_ss/docker_pull.sh"])
        print("dd")
        timer_period2 = 2  # seconds
        # self.publisher_liveness = self.create_publisher(String, '/controller_version', 10)
        self.timer_liveness = self.create_timer(timer_period2, self.timer_callback_liveness)

        self.client = pymongo.MongoClient('mongodb://'+MONGO_HOSTNAME+':'+MONGO_PORT)
        self.subscription = self.create_subscription(
            Bool,
            '/topic/button/emr/bool',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.subscription_dbmanager = self.create_subscription(
            String, '/dbmanager_version',
            self.timer_callback_liveness,
            10)
        self.subscription_dbmanager  # prevent unused variable warning
        self.subscription_controller = self.create_subscription(
            String, '/controller_version',
            self.timer_callback_liveness,
            10)
        self.subscription_controller  # prevent unused variable warning
        self.subscription_bridge = self.create_subscription(
            String, '/bridge_version',
            self.timer_callback_liveness,
            10)
        self.subscription_bridge  # prevent unused variable warning

    def listener_callback(self, msg):
        db = self.client.wasp.button
        button_db = {"id" : "M30", "buttonstate" : msg.data}
        db.insert(button_db)
        if msg.data == True :
            collection = self.client.wasp.updatecommands
            update_button = collection.find_one({'id' : "M30"},sort=[('updatedAt', pymongo.DESCENDING)])
            print(update_button["buttonstate"])
            if update_button["buttonstate"] == True :
                subprocess.run(["src/angel_ss/docker_pull.sh", "arguments"], shell=True)
    
        self.get_logger().info('I heard: "%s"' % msg.data)

    def timer_callback_liveness(self, msg):
        db = self.client.wasp.dbmanager
        post = {"version" : {"id" : "M30", "db_manager" : msg.data }}
        
        self.get_logger().info('version: "%s"' % msg.data)

def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()