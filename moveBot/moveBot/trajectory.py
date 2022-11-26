import rclpy
from rclpy.node import Node
from enum import Enum, auto
from rclpy.callback_groups import ReentrantCallbackGroup
from std_srvs.srv import Empty
import time
from movebot_interfaces.srv import IkGoalRqst, AddBox, GetPlanRqst
from movebot_interfaces.msg import IkGoalRqstMsg

class State(Enum):
    """Create a state machine to eventually implement planning the entire stored trajectory plan
    sequence, for executing it only once at the end.
    """
    IDLE = auto(),
    PLAN = auto(),
    EXECUTE = auto()

class TrajectoryCaller(Node):
    """Call the plan and execute services from simple_move."""
    def __init__(self):
        super().__init__("trajectory_node")
        self.cbgroup = ReentrantCallbackGroup()
        self.plan_client = self.create_client(GetPlanRqst,"call_plan",callback_group=self.cbgroup)
        self.execute_client = self.create_client(Empty,"call_execute",callback_group=self.cbgroup)
        self.request = GetPlanRqst.Request()
        self.state = State.IDLE

    def send_move_above_request(self):
        """Build the desired IkGoalRqstMsg to be sent over the client to make the robot plan and
        execute a trajectory. This request is the trajectory plan for moving above the object.
        """
        self.request.start_pos.position = []
        self.request.start_pos.orientation = []
        self.request.goal_pos.position = [] # placeholder values, replace with CV
        self.request.goal_pos.orientation = [3.14, 0.0, 1.0]
        self.request.is_xyzrpy = True
        self.request.execute_now = False
        self.future = self.cart_client.call_async(self.request)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

    def send_execute_request(self):
        """Execute the trajectory plan - used in each step of the entire trajectory sequence."""
        self.future = self.execute_client.call_async(Empty.Request())
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()


def main(args=None):
    rclpy.init(args=args)
    trajectory_client = TrajectoryCaller()
    trajectory_client.send_move_above_request()
    trajectory_client.send_execute_request()
    trajectory_client.send_move_down_request()
    trajectory_client.send_execute_request()
    time.sleep(1)
    trajectory_client.send_move_up_request()
    trajectory_client.send_execute_request()
    trajectory_client.send_move_home_request()
    trajectory_client.send_execute_request()
    trajectory_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()