import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: root
    visible: true
    width: 800
    height: 600
    title: "Panel de Navegación Autónoma"

    property var usvPos: Qt.point(0, 0)
    property var metaPos: Qt.point(0, 0)
    property var obsList: []    // { x, y, tipo }

    Canvas {
        id: campo
        anchors.fill: parent

        onPaint: {
            var ctx = getContext("2d");
            ctx.reset();
            ctx.fillStyle = "#eef";
            ctx.fillRect(0, 0, width, height);

            var s = 1.0;
            function toCanvas(pt) {
                return { x: pt.x * s, y: height - pt.y * s };
            }

            // Obstáculos
            for (var i = 0; i < obsList.length; ++i) {
                var ob = obsList[i];
                var p  = toCanvas(ob);
                ctx.beginPath();
                switch (ob.tipo) {
                    case "piedra":
                        ctx.fillStyle = "gray";
                        ctx.arc(p.x, p.y, 5, 0, 2*Math.PI);
                        ctx.fill();
                        break;
                    case "barco":
                        ctx.fillStyle = "blue";
                        ctx.fillRect(p.x-5, p.y-5, 10, 10);
                        break;
                    case "boya":
                        ctx.fillStyle = "orange";
                        ctx.moveTo(p.x, p.y-6);
                        ctx.lineTo(p.x+5, p.y+4);
                        ctx.lineTo(p.x-5, p.y+4);
                        ctx.closePath();
                        ctx.fill();
                        break;
                    default:
                        ctx.fillStyle = "black";
                        ctx.arc(p.x, p.y, 4, 0, 2*Math.PI);
                        ctx.fill();
                }
            }

            // Meta
            ctx.fillStyle = "green";
            var m = toCanvas(metaPos);
            ctx.beginPath();
            ctx.arc(m.x, m.y, 6, 0, 2*Math.PI);
            ctx.fill();

            // USV
            ctx.fillStyle = "red";
            var u = toCanvas(usvPos);
            ctx.beginPath();
            ctx.arc(u.x, u.y, 6, 0, 2*Math.PI);
            ctx.fill();
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "transparent"
        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: 20
            spacing: 10

            Text {
                text: "Estado del USV"
                font.pixelSize: 30
                color: "white"
            }
            Text {
                id: alertaText
                text: estadoUSV.estadoTexto
                font.pixelSize: 20
                color: "orange"
            }
        }
    }

    Connections {
        target: simuladorAPF

        // actualiza posición interna del USV
        onPosicionInterna: function(x, y) {
            usvPos = Qt.point(x, y);
            campo.requestPaint();
        }

        // actualiza posición interna de la meta
        onMetaInterna: function(x, y) {
            metaPos = Qt.point(x, y);
            campo.requestPaint();
        }

        // actualiza lista de obstáculos
        onActualizarObstaculos: function(lista) {
            obsList = [];
            for (var i = 0; i < lista.length; ++i) {
                var t = lista[i];
                // lista[i] == [x, y, tipo]
                obsList.push({ x: t[0], y: t[1], tipo: t[2] });
            }
            campo.requestPaint();
        }

        // actualiza la alerta de texto
        onAlertaActualizada: function(msj) {
            estadoUSV.estadoTexto = msj;
        }
    }
}
