/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of the Qt Quick Controls 2 module of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
**
**
**
**
**
**
**
**
**
**
**
**
**
**
**
****************************************************************************/

import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Controls.impl 2.12
import QtQuick.Controls.Fusion 2.12
import QtQuick.Controls.Fusion.impl 2.12

Rectangle {
    id: indicator

    property Item control
    readonly property color pressedColor: Fusion.mergedColors(control.palette.base, control.palette.windowText, 85)
    readonly property color checkMarkColor: Qt.darker(control.palette.text, 1.2)

    implicitWidth: 40
    implicitHeight: 16

    radius: 2
    border.color: Fusion.outline(control.palette)

    gradient: Gradient {
        GradientStop {
            position: 0
            color: Qt.darker(Fusion.grooveColor(indicator.control.palette), 1.1)
        }
        GradientStop {
            position: 1
            color: Qt.lighter(Fusion.grooveColor(indicator.control.palette), 1.1)
        }
    }

    Rectangle {
        x: indicator.control.mirrored ? handle.x : 0
        width: indicator.control.mirrored ? parent.width - handle.x : handle.x + handle.width
        height: parent.height

        opacity: indicator.control.checked ? 1 : 0
        Behavior on opacity {
            enabled: !indicator.control.down
            NumberAnimation { duration: 80 }
        }

        radius: 2
        border.color: Qt.darker(Fusion.highlightedOutline(indicator.control.palette), 1.1)
        border.width: indicator.control.enabled ? 1 : 0

        gradient: Gradient {
            GradientStop {
                position: 0
                color: Fusion.highlight(indicator.control.palette)
            }
            GradientStop {
                position: 1
                color: Qt.lighter(Fusion.highlight(indicator.control.palette), 1.2)
            }
        }
    }

    Rectangle {
        id: handle
        x: Math.max(0, Math.min(parent.width - width, indicator.control.visualPosition * parent.width - (width / 2)))
        y: (parent.height - height) / 2
        width: 20
        height: 16
        radius: 2

        gradient: Gradient {
            GradientStop {
                position: 0
                color: Fusion.gradientStart(Fusion.buttonColor(indicator.control.palette, indicator.control.visualFocus, indicator.control.pressed, indicator.control.hovered))
            }
            GradientStop {
                position: 1
                color: Fusion.gradientStop(Fusion.buttonColor(indicator.control.palette, indicator.control.visualFocus, indicator.control.pressed, indicator.control.hovered))
            }
        }
        border.width: 1
        border.color: "transparent"

        Rectangle {
            width: parent.width
            height: parent.height
            border.color: indicator.control.visualFocus ? Fusion.highlightedOutline(indicator.control.palette) : Fusion.outline(indicator.control.palette)
            color: "transparent"
            radius: 2

            Rectangle {
                x: 1; y: 1
                width: parent.width - 2
                height: parent.height - 2
                border.color: Fusion.innerContrastLine
                color: "transparent"
                radius: 2
            }
        }

        Behavior on x {
            enabled: !indicator.control.down
            SmoothedAnimation { velocity: 200 }
        }
    }
}
