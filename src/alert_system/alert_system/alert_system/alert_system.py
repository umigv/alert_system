import rclpy
from rclpy.node import Node
from alert_system_interfaces.msg import Alert
from alert_system_interfaces.srv import CreateAlert
from alert_system_interfaces.srv import ResolveAlert


class AlertSystem(Node):

    def __init__(self):
        super().__init__('alert_system')
        self.alert_id_counter = 0
        self.active_alerts = {}

        self.alert_publisher = self.create_publisher(Alert, 'alerts', 10)

        self.create_alert_services = self.create_service(
            CreateAlert, 'create_alert', self.create_alert_callback
        )

        self.resolve_alert_service = self.create_service(
            ResolveAlert, 'resolve_alert', self.resolve_alert_callback
        )

    def create_alert_callback(self, request, response):
        alert_id = self.create_alert(
            request.category,
            request.severity,
            request.source,
            request.message,
        )

        response.alert_id = alert_id
        return response

    def resolve_alert_callback(self, request, response):
        if request.alert_id in self.active_alerts:
            self.resolve_alert(request.alert_id)
            response.success = True
        else:
            self.get_logger().warn(f'Alert #{request.alert_id} does not exist')
            response.success = False
        return response

    def create_alert(self, category, severity, source, message):
        self.alert_id_counter += 1
        alert_id = self.alert_id_counter

        alert = {
            'id': alert_id,
            'category': category,
            'severity': severity,
            'source': source,
            'message': message,
            'resolved': False,
        }

        self.active_alerts[alert_id] = alert

        msg = Alert()
        msg.id = alert_id
        msg.category = category
        msg.severity = severity
        msg.source = source
        msg.message = message
        msg.resolved = False
        self.alert_publisher.publish(msg)

        self.get_logger().info(f'Alert #{alert_id} created: {msg}')
        return alert_id

    def resolve_alert(self, alert_id):
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert['resolved'] = True

            msg = Alert() 
            msg.id = alert_id
            msg.category = alert['category']
            msg.severity = alert['severity']
            msg.source = alert['source']
            msg.message = alert['message']
            msg.resolved = True
            self.alert_publisher.publish(msg)

            del self.active_alerts[alert_id]
            self.get_logger().info(f'Alert #{alert_id} resolved: {msg}')
        else:
            self.get_logger().info(f'Alert #{alert_id} does not exist')
    
        

def main(args=None):
    rclpy.init(args=args)
    alert_system = AlertSystem()
    rclpy.spin(alert_system)
    alert_system.destroy_node()
    rclpy.shutdown()        
        
        
