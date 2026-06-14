from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    default_param_file = PathJoinSubstitution([
        get_package_share_directory('object_tracker'),
        'config',
        'tracker.yaml'
    ])
    
    namespace = LaunchConfiguration('namespace', default='')
    color = LaunchConfiguration('color', default='yellow')
    param_file_path = LaunchConfiguration('param_file_path', default=default_param_file)

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value='',
            description='ROS namespace for the object_tracker node'
        ),
        DeclareLaunchArgument(
            'color',
            default_value='yellow',
            description='Color name for object detection: yellow, red_lower, red_upper, orange, green, blue',
            choices = ['yellow', 'red_lower', 'red_upper', 'orange', 'green', 'blue']
        ),
        DeclareLaunchArgument(
            'param_file_path',
            default_value=default_param_file,
            description='Path to the parameters YAML file'
        ),
        Node(
            package='object_tracker',
            executable='object_tracker',
            name='object_tracker',
            namespace=namespace,
            parameters=[
                param_file_path,
                {   
                    'color': color,
                }
            ],
            output='screen'
        )
    ])
