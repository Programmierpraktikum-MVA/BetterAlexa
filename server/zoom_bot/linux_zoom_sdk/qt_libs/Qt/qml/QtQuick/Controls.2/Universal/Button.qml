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
import QtQuick.Controls.Universal 2.12

T.Button {
    id: control

    implicitWidth: Math.max(implicitBackgroundWidth + leftInset + rightInset,
                            implicitContentWidth + leftPadding + rightPadding)
    implicitHeight: Math.max(implicitBackgroundHeight + topInset + bottomInset,
                             implicitContentHeight + topPadding + bottomPadding)

    padding: 8
    verticalPadding: padding - 4
    spacing: 8

    icon.width: 20
    icon.height: 20
    icon.color: Color.transparent(Universal.foreground, enabled ? 1.0 : 0.2)

    property bool useSystemFocusVisuals: true

    contentItem: IconLabel {
        spacing: control.spacing
        mirrored: control.mirrored
        display: control.display

        icon: control.icon
        text: control.text
        font: control.font
        color: Color.transparent(control.Universal.foreground, enabled ? 1.0 : 0.2)
    }

    background: Rectangle {
        implicitWidth: 32
        implicitHeight: 32

        visible: !control.flat || control.down || control.checked || control.highlighted
        color: control.down ? control.Universal.baseMediumLowColor :
               control.enabled && (control.highlighted || control.checked) ? control.Universal.accent :
                                                                             control.Universal.baseLowColor

        Rectangle {
            width: parent.width
            height: parent.height
            color: "transparent"
            visible: control.hovered
            border.width: 2 // ButtonBorderThemeThickness
            border.color: control.Universal.baseMediumLowColor
        }
    }
}
