import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15

Window {
    id: root
    width: 1100
    height: 650
    visible: true
    title: "AI Pothole Detection System"

    color: "#0B0D12"

    signal startCamera()
    signal stopCamera()

    property bool cameraRunning: false

    function updateFrame(frame) {
        cameraRunning = true
        cameraView.source = frame
    }

    function clearFrame() {
        cameraRunning = false
        cameraView.source = ""
    }

    Rectangle {
        anchors.fill: parent
        color: "#0B0D12"
    }

    Rectangle {
        id: glassPanel
        anchors.centerIn: parent
        width: parent.width * 0.88
        height: parent.height * 0.88
        radius: 28
        color: "#1A1D29"
        border.color: "#2A2E3F"
        border.width: 1

        Column {
            anchors.fill: parent
            anchors.margins: 24
            spacing: 20

            Text {
                text: "AI Pothole Detection System"
                color: "white"
                font.pixelSize: 28
                font.weight: Font.DemiBold
                horizontalAlignment: Text.AlignHCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Rectangle {
                id: cameraContainer
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width
                height: parent.height * 0.65
                radius: 20
                color: "#0F121A"

                Image {
                    id: cameraView
                    anchors.fill: parent
                    fillMode: Image.PreserveAspectFit
                }

                Text {
                    visible: !cameraRunning
                    anchors.centerIn: parent
                    text: "Camera is OFF"
                    color: "#6C738F"
                    font.pixelSize: 18
                }
            }

            Row {
                spacing: 20
                anchors.horizontalCenter: parent.horizontalCenter

                Button {
                    text: "Start Camera"
                    enabled: !cameraRunning
                    onClicked: root.startCamera()
                }

                Button {
                    text: "Stop Camera"
                    enabled: cameraRunning
                    onClicked: root.stopCamera()
                }
            }
        }
    }
}
