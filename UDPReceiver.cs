using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class UDPReceiver : MonoBehaviour
{
    public int port = 8080; 
    private UdpClient udpClient;
    private Thread receiveThread;
    private string lastReceivedData = "";

    [System.Serializable]
    private class VRData
    {
        public DeviceData headset;
        public DeviceData left_controller;
        public DeviceData right_controller;
    }

    [System.Serializable]
    private class DeviceData
    {
        public float[] position;
        public float[] orientation;
    }

    public GameObject headsetObject; 
    public GameObject leftControllerObject; 
    public GameObject rightControllerObject; 

    void Start()
    {
        udpClient = new UdpClient(port);
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
        Debug.Log("UDP Receiver started on port " + port);
    }

    private void ReceiveData()
    {
        while (true)
        {
            try
            {
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                byte[] data = udpClient.Receive(ref anyIP);
                string text = Encoding.UTF8.GetString(data);
                lastReceivedData = text;
            }
            catch (System.Exception e)
            {
                Debug.LogError("UDP Receive Error: " + e.ToString());
            }
        }
    }

    void Update()
    {
        if (!string.IsNullOrEmpty(lastReceivedData))
        {
            try
            {
                VRData data = JsonUtility.FromJson<VRData>(lastReceivedData);
                
                if (data.headset != null && headsetObject != null)
                {
                    headsetObject.transform.position = new Vector3(data.headset.position[0], data.headset.position[1], data.headset.position[2]);
                    headsetObject.transform.rotation = new Quaternion(data.headset.orientation[0], data.headset.orientation[1], data.headset.orientation[2], data.headset.orientation[3]);
                }
                
                if (data.left_controller != null && leftControllerObject != null)
                {
                    leftControllerObject.transform.position = new Vector3(data.left_controller.position[0], data.left_controller.position[1], data.left_controller.position[2]);
                    leftControllerObject.transform.rotation = new Quaternion(data.left_controller.orientation[0], data.left_controller.orientation[1], data.left_controller.orientation[2], data.left_controller.orientation[3]);
                }
                
                if (data.right_controller != null && rightControllerObject != null)
                {
                    rightControllerObject.transform.position = new Vector3(data.right_controller.position[0], data.right_controller.position[1], data.right_controller.position[2]);
                    rightControllerObject.transform.rotation = new Quaternion(data.right_controller.orientation[0], data.right_controller.orientation[1], data.right_controller.orientation[2], data.right_controller.orientation[3]);
                }
            }
            catch (System.Exception e)
            {
                Debug.LogError("JSON Parse Error: " + e.ToString());
            }
            lastReceivedData = ""; 
        }
    }

    void OnApplicationQuit()
    {
        if (receiveThread != null)
            receiveThread.Abort();
        if (udpClient != null)
            udpClient.Close();
    }
}