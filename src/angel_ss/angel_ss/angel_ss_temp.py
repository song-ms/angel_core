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


# apiKey = 'thingSpeak api-key for reading'
# baseURL = 'https://api.thingspeak.com/update?api_key='+apiKey+'&field1='

MONGO_HOSTNAME = '192.168.0.243'
MONGO_PORT = '27017'
MONGO_DB = 'wasp'

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('angel_core')
        subprocess.run(["chmod", "+x", "/angel_core/src/angel_ss/update_command.sh"])
        print("angel_core is activated")
        self.client = pymongo.MongoClient('mongodb://'+MONGO_HOSTNAME+':'+MONGO_PORT)
        self.subscription = self.create_subscription(
            Bool,
            '/topic/button/emr/bool',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        

    def listener_callback(self, msg):
        db = self.client.wasp.button
        print(msg.data)
        button_db = {"id" : "M30", "buttonstate" : msg.data}
        db.insert_one(button_db)
        if msg.data == True :
            collection = self.client.wasp.updatecommands
            update_button = collection.find_one({'id' : "M30"},sort=[('updatedAt', pymongo.DESCENDING)])
            print(update_button["buttonstate"])
            if update_button["buttonstate"] == True :
                subprocess.run(["/angel_core/src/angel_ss/update_command.sh", "arguments"], shell=True)
    
        self.get_logger().info('I heard: "%s"' % msg.data)

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