import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: root
    visible: true
    width: 800
    height: 600
    title: "Panel de Navegación Autónoma"

    // ── 1) Inicializar propiedades ─────────────────────────────
    property var usvPos: Qt.point(0, 0)    // evita undefined
    property var metaPos: Qt.point(0, 0)
    property var obsList: []               // lista vacía inicial

    // ── 2) Canvas para dibujar plano X–Y ────────────────────────
    Canvas {
        id: campo
        anchors.fill: parent

        onPaint: {
            var ctx = getContext("2d");
            ctx.reset();
            ctx.fillStyle = "#eef";
            ctx.fillRect(0, 0, width, height);

            var s = 1.0;  // ajuste si necesitas escalar

            function toCanvas(pt) {
                return { x: pt.x * s, y: height - pt.y * s };
            }

            // Dibujar obstáculos
            ctx.fillStyle = "black";
            for (var i = 0; i < obsList.length; ++i) {
                var p = toCanvas(obsList[i]);
                ctx.beginPath();
                ctx.arc(p.x, p.y, 5, 0, 2*Math.PI);
                ctx.fill();
            }

            // Dibujar meta
            ctx.fillStyle = "green";
            var mp = toCanvas(metaPos);
            ctx.beginPath();
            ctx.arc(mp.x, mp.y, 6, 0, 2*Math.PI);
            ctx.fill();

            // Dibujar USV
            ctx.fillStyle = "red";
            var up = toCanvas(usvPos);
            ctx.beginPath();
            ctx.arc(up.x, up.y, 6, 0, 2*Math.PI);
            ctx.fill();
        }
    }

    // ── 3) Fondo y textos ─────────────────────────────────────────
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

    // ── 4) Conexiones de cambio de propiedad ────────────────────
    Connections {
        target: root
        onUsvPosChanged:    campo.requestPaint()
        onMetaPosChanged:   campo.requestPaint()
        onObsListChanged:   campo.requestPaint()
    }
}
