import openvr
import json
import time
import websocket
import numpy as np
from scipy.spatial.transform import Rotation

vr_system = openvr.init(openvr.VRApplication_Other)

ws = websocket.WebSocket()
ws.connect("ws://localhost:9090")

def matrix34_to_pose(matrix34):
    """
    Convert a 3x4 transformation matrix to position (x, y, z) and quaternion (x, y, z, w).
    
    Args:
        matrix34 (numpy.ndarray): 3x4 matrix from OpenVR pose data
    
    Returns:
        tuple: (position, quaternion) where position is [x, y, z] and quaternion is [x, y, z, w]
    """
    transform = np.vstack((matrix34, [0, 0, 0, 1]))
    position = transform[:3, 3]
    rotation = Rotation.from_matrix(transform[:3, :3])
    quaternion = rotation.as_quat()  # Returns [x, y, z, w]
    return position, quaternion

#  parse Oculus signals and send JSON to ROSBridge
try:
    while True:
        current_time = time.time()
        timestamp = {"secs": int(current_time), "nsecs": int((current_time % 1) * 1e9)}

        poses = vr_system.getDeviceToAbsoluteTrackingPose(
            openvr.TrackingUniverseOrigin_Standing, 0
        )

        if poses[0].bPoseIsValid: 
            headset_matrix = np.array(poses[0].mDeviceToAbsoluteTracking.m)
            headset_pos, headset_quat = matrix34_to_pose(headset_matrix)

            headset_msg = {
                "op": "publish",
                "topic": "/oculus/headset_pose",
                "msg": {
                    "header": {
                        "stamp": timestamp,
                        "frame_id": "world"
                    },
                    "pose": {
                        "position": {
                            "x": float(headset_pos[0]),
                            "y": float(headset_pos[1]),
                            "z": float(headset_pos[2])
                        },
                        "orientation": {
                            "x": float(headset_quat[0]),
                            "y": float(headset_quat[1]),
                            "z": float(headset_quat[2]),
                            "w": float(headset_quat[3])
                        }
                    }
                }
            }
            ws.send(json.dumps(headset_msg))

        left_index = vr_system.getTrackedDeviceIndexForControllerRole(
            openvr.TrackedControllerRole_LeftHand
        )
        if (left_index != openvr.k_unTrackedDeviceIndexInvalid and 
            left_index < len(poses) and poses[left_index].bPoseIsValid):
            left_matrix = np.array(poses[left_index].mDeviceToAbsoluteTracking.m)
            left_pos, left_quat = matrix34_to_pose(left_matrix)

            left_msg = {
                "op": "publish",
                "topic": "/oculus/left_controller_pose",
                "msg": {
                    "header": {
                        "stamp": timestamp,
                        "frame_id": "world"
                    },
                    "pose": {
                        "position": {
                            "x": float(left_pos[0]),
                            "y": float(left_pos[1]),
                            "z": float(left_pos[2])
                        },
                        "orientation": {
                            "x": float(left_quat[0]),
                            "y": float(left_quat[1]),
                            "z": float(left_quat[2]),
                            "w": float(left_quat[3])
                        }
                    }
                }
            }
            ws.send(json.dumps(left_msg))

        right_index = vr_system.getTrackedDeviceIndexForControllerRole(
            openvr.TrackedControllerRole_RightHand
        )
        if (right_index != openvr.k_unTrackedDeviceIndexInvalid and 
            right_index < len(poses) and poses[right_index].bPoseIsValid):
            right_matrix = np.array(poses[right_index].mDeviceToAbsoluteTracking.m)
            right_pos, right_quat = matrix34_to_pose(right_matrix)

            right_msg = {
                "op": "publish",
                "topic": "/oculus/right_controller_pose",
                "msg": {
                    "header": {
                        "stamp": timestamp,
                        "frame_id": "world"
                    },
                    "pose": {
                        "position": {
                            "x": float(right_pos[0]),
                            "y": float(right_pos[1]),
                            "z": float(right_pos[2])
                        },
                        "orientation": {
                            "x": float(right_quat[0]),
                            "y": float(right_quat[1]),
                            "z": float(right_quat[2]),
                            "w": float(right_quat[3])
                        }
                    }
                }
            }
            ws.send(json.dumps(right_msg))

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Shutting down...")
finally:
    ws.close()
    openvr.shutdown()