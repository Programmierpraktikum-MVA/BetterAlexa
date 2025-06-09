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
import QtQuick.Templates 2.12 as T
import QtQuick.Controls 2.12
import QtQuick.Controls.impl 2.12
import QtQuick.Controls.Fusion 2.12
import QtQuick.Controls.Fusion.impl 2.12

T.RoundButton {
    id: control

    implicitWidth: Math.max(implicitBackgroundWidth + leftInset + rightInset,
                            implicitContentWidth + leftPadding + rightPadding)
    implicitHeight: Math.max(implicitBackgroundHeight + topInset + bottomInset,
                             implicitContentHeight + topPadding + bottomPadding)

    padding: 6
    spacing: 6

    icon.width: 16
    icon.height: 16

    contentItem: IconLabel {
        spacing: control.spacing
        mirrored: control.mirrored
        display: control.display

        icon: control.icon
        text: control.text
        font: control.font
        color: control.palette.buttonText
    }

    background: Rectangle {
        implicitWidth: 32
        implicitHeight: 32
        visible: !control.flat || control.down || control.checked

        gradient: Gradient {
            GradientStop {
                position: 0
                color: control.down || control.checked ? Fusion.buttonColor(control.palette, control.highlighted, control.down || control.checked, control.hovered)
                                                       : Fusion.gradientStart(Fusion.buttonColor(control.palette, control.highlighted, control.down, control.hovered))
            }
            GradientStop {
                position: 1
                color: control.down || control.checked ? Fusion.buttonColor(control.palette, control.highlighted, control.down || control.checked, control.hovered)
                                                       : Fusion.gradientStop(Fusion.buttonColor(control.palette, control.highlighted, control.down, control.hovered))
            }
        }

        radius: control.radius
        border.color: Fusion.buttonOutline(control.palette, control.highlighted || control.visualFocus, control.enabled)

        Rectangle {
            x: 1; y: 1
            width: parent.width - 2
            height: parent.height - 2
            border.color: Fusion.innerContrastLine
            color: "transparent"
            radius: control.radius
        }
    }
}
