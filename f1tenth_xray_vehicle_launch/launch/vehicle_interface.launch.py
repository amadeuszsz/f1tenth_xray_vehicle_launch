# Copyright 2023 Amadeusz Szymko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from yaml import safe_load

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    pkg_prefix = FindPackageShare('f1tenth_xray_vehicle_launch')
    vesc_driver_config = PathJoinSubstitution([pkg_prefix, 'config/vesc/vesc_driver.param.yaml'])
    vesc_interface_config = PathJoinSubstitution([pkg_prefix, 'config/vesc/vesc_interface.param.yaml'])

    vesc_driver_node = Node(
        name='vesc_driver',
        namespace='vesc',
        package='vesc_driver',
        executable='vesc_driver_node',
        parameters=[vesc_driver_config],
        remappings=[
            ('sensors/imu/raw', '/sensing/vesc/imu')
        ]
    )

    vesc_interface_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            launch_file_path=PathJoinSubstitution([
                FindPackageShare('vesc_interface'), 'launch', 'vesc_interface.launch.py'
            ]),
        ),
        launch_arguments={
            'vesc_interface_param_file': vesc_interface_config,
            'vehicle_param_file': LaunchConfiguration('vehicle_param_file')
        }.items()
    )

    return [
        vesc_driver_node,
        vesc_interface_launch
    ]


def generate_launch_description():
    declared_arguments = []

    def add_launch_arg(name: str, default_value: str = None):
        declared_arguments.append(
            DeclareLaunchArgument(name, default_value=default_value)
        )

    add_launch_arg('vehicle_param_file')

    return LaunchDescription([
        *declared_arguments,
        OpaqueFunction(function=launch_setup)
    ])